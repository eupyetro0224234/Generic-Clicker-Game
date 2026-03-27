import requests, json, pygame
from datetime import datetime
from game_assets.game_assets_packed import load_image


# ─────────────────────────────────────────────────────────────────────────────
#  Evento  (sem alterações)
# ─────────────────────────────────────────────────────────────────────────────

class Evento:
    def __init__(self, nome, data_inicio, hora_inicio, data_final, hora_final,
                 tipo="normal", id=None):
        self.nome        = nome
        self.data_inicio = data_inicio
        self.hora_inicio = hora_inicio
        self.data_final  = data_final
        self.hora_final  = hora_final
        self.tipo        = tipo
        self.id          = id or nome.lower().replace(" ", "_")
        self.ativo       = False

    def verificar_ativo(self):
        try:
            agora  = datetime.now()
            inicio = datetime.strptime(f"{self.data_inicio} {self.hora_inicio}", "%d/%m/%Y %H:%M")
            final  = datetime.strptime(f"{self.data_final} {self.hora_final}",   "%d/%m/%Y %H:%M")
            self.ativo = inicio <= agora <= final
            return self.ativo
        except Exception:
            self.ativo = False
            return False

    def get_tempo_restante(self):
        if not self.ativo:
            return "Evento inativo"
        try:
            final     = datetime.strptime(f"{self.data_final} {self.hora_final}", "%d/%m/%Y %H:%M")
            agora     = datetime.now()
            if agora > final:
                return "Evento finalizado"
            diferenca = final - agora
            dias      = diferenca.days
            horas     = diferenca.seconds // 3600
            minutos   = (diferenca.seconds % 3600) // 60
            if dias > 0:
                return f"{dias}d {horas}h {minutos}m"
            elif horas > 0:
                return f"{horas}h {minutos}m"
            else:
                return f"{minutos}m"
        except Exception:
            return "Erro no cálculo"

    def get_icone(self):
        return ""

    def get_descricao(self):
        descricoes = {
            "pontos_duplos":       "Ganhe o DOBRO de pontos por clique!",
            "bonus_click":         "Bonus extra em cada clique!",
            "velocidade_trabalhador": "Trabalhadores mais rapidos!",
            "preco_reduzido":      "Upgrades com desconto!",
            "evento_raro":         "Evento especial raro ativo!",
            "normal":              "Evento especial ativo!",
        }
        return descricoes.get(self.tipo, "Evento especial ativo!")

    def aplicar_efeito_pontos(self, pontos_base):
        if not self.ativo:
            return pontos_base
        multiplicadores = {
            "pontos_duplos": 2.0,
            "bonus_click":   1.5,
            "evento_raro":   3.0,
            "normal":        1.0,
        }
        return int(pontos_base * multiplicadores.get(self.tipo, 1.0))

    def aplicar_efeito_trabalhador(self, velocidade_base):
        if not self.ativo:
            return velocidade_base
        multiplicadores = {"velocidade_trabalhador": 2.0, "evento_raro": 1.5}
        return velocidade_base * multiplicadores.get(self.tipo, 1.0)

    def aplicar_desconto_upgrades(self, preco_base):
        if not self.ativo:
            return preco_base
        multiplicadores = {"preco_reduzido": 0.5, "evento_raro": 0.7}
        return preco_base * multiplicadores.get(self.tipo, 1.0)


# ─────────────────────────────────────────────────────────────────────────────
#  GerenciadorEventos  (sem alterações)
# ─────────────────────────────────────────────────────────────────────────────

class GerenciadorEventos:
    def __init__(self):
        self.eventos              = []
        self.url_json             = (
            "https://raw.githack.com/eupyetro0224234/Generic-Clicker-Game/"
            "main/github_assets/eventos.json"
        )
        self.ultima_verificacao   = None
        self.intervalo_verificacao = 300_000
        self.tipos_mapeados       = set()

    def carregar_eventos(self):
        try:
            response = requests.get(self.url_json, timeout=10)
            response.raise_for_status()
            dados = response.json()
            self.eventos.clear()
            self.tipos_mapeados.clear()
            for ed in dados.get("eventos", []):
                evento = Evento(
                    nome        = ed.get("nome", ""),
                    data_inicio = ed.get("data_inicio", ""),
                    hora_inicio = ed.get("hora_inicio", ""),
                    data_final  = ed.get("data_final", ""),
                    hora_final  = ed.get("hora_final", ""),
                    tipo        = ed.get("tipo", "normal"),
                    id          = ed.get("id"),
                )
                self.eventos.append(evento)
                self.tipos_mapeados.add(evento.tipo)
            self.ultima_verificacao = pygame.time.get_ticks()
            return True
        except Exception:
            return False

    def atualizar_eventos(self):
        current_time = pygame.time.get_ticks()
        if (self.ultima_verificacao is None or
                current_time - self.ultima_verificacao > self.intervalo_verificacao):
            self.carregar_eventos()
        return [e for e in self.eventos if e.verificar_ativo()]

    def get_eventos_ativos(self):
        return [e for e in self.eventos if e.ativo]

    def get_eventos_por_tipo(self, tipo):
        return [e for e in self.eventos if e.ativo and e.tipo == tipo]

    def get_proximo_evento(self):
        try:
            agora          = datetime.now()
            eventos_futuros = []
            for evento in self.eventos:
                try:
                    inicio = datetime.strptime(
                        f"{evento.data_inicio} {evento.hora_inicio}", "%d/%m/%Y %H:%M"
                    )
                    if inicio > agora:
                        eventos_futuros.append((evento, inicio))
                except Exception:
                    continue
            if eventos_futuros:
                eventos_futuros.sort(key=lambda x: x[1])
                return eventos_futuros[0][0]
            return None
        except Exception:
            return None

    def aplicar_efeitos_pontos(self, pontos_base):
        pontos_finais = pontos_base
        for e in self.get_eventos_ativos():
            pontos_finais = e.aplicar_efeito_pontos(pontos_finais)
        return pontos_finais

    def aplicar_efeitos_trabalhador(self, velocidade_base):
        v = velocidade_base
        for e in self.get_eventos_ativos():
            v = e.aplicar_efeito_trabalhador(v)
        return v

    def aplicar_descontos_upgrades(self, preco_base):
        p = preco_base
        for e in self.get_eventos_ativos():
            p = e.aplicar_desconto_upgrades(p)
        return p

    def get_estatisticas_eventos(self):
        eventos_ativos  = self.get_eventos_ativos()
        eventos_futuros = []
        eventos_passados = []
        agora = datetime.now()
        for evento in self.eventos:
            try:
                inicio = datetime.strptime(
                    f"{evento.data_inicio} {evento.hora_inicio}", "%d/%m/%Y %H:%M"
                )
                if inicio > agora:
                    eventos_futuros.append(evento)
                elif not evento.ativo:
                    eventos_passados.append(evento)
            except Exception:
                continue
        return {
            "total":        len(self.eventos),
            "ativos":       len(eventos_ativos),
            "futuros":      len(eventos_futuros),
            "passados":     len(eventos_passados),
            "tipos_unicos": list(self.tipos_mapeados),
        }


# ─────────────────────────────────────────────────────────────────────────────
#  EventosMenu  — estilo idêntico ao StatisticsMenu
# ─────────────────────────────────────────────────────────────────────────────

class EventosMenu:
    def __init__(self, screen, window_width, window_height):
        self.screen        = screen
        self.width         = window_width
        self.height        = window_height
        self.visible       = False

        # ── paleta (igual ao StatisticsMenu) ─────────────────────────────────
        self.bg_color      = (255, 182, 193)
        self.text_color    = (47, 24, 63)
        self.option_radius = 28
        self.spacing_y     = 12

        # cores de status dos eventos
        self.cor_ativo   = (180, 120, 0)   # dourado escuro (legível no branco)
        self.cor_futuro  = (50, 100, 200)  # azul escuro
        self.cor_passado = (120, 120, 120) # cinza

        # ── área central (igual ao StatisticsMenu) ────────────────────────────
        self.content_margin = 60

        # ── fontes ────────────────────────────────────────────────────────────
        self.title_font = pygame.font.SysFont(None, 38)
        self.font       = pygame.font.SysFont(None, 28)
        self.small_font = pygame.font.SysFont(None, 22)

        # ── card / opção ──────────────────────────────────────────────────────
        self.option_height = 58
        self.card_spacing  = self.spacing_y

        # ── scroll ────────────────────────────────────────────────────────────
        self.scroll_y        = 0
        self.scroll_speed    = 30
        self.max_scroll      = 0
        self.scrollbar_width = 12
        self.scrollbar_rect  = None
        self.is_scrolling    = False
        self.scroll_drag_start = 0

        # ── botão fechar ──────────────────────────────────────────────────────
        self.close_button_rect = pygame.Rect(self.width - 80, 15, 40, 40)
        try:
            self.close_image = load_image("close.png")
            self.close_image = pygame.transform.smoothscale(self.close_image, (40, 40))
        except Exception:
            self.close_image = None

        self.gerenciador = None

        # ── animação de sombra e escala por card ──────────────────────────────
        # chave: índice do evento, valor: alpha atual (0-40)
        self._shadow_alpha = {}
        # chave: índice do evento, valor: escala atual (1.0 - 1.04)
        self._card_scale = {}

    # ── helpers de layout ─────────────────────────────────────────────────────

    def _content_x(self):
        return self.content_margin

    def _content_width(self):
        return self.width - 2 * self.content_margin

    # ── set gerenciador ───────────────────────────────────────────────────────

    def set_gerenciador(self, gerenciador):
        self.gerenciador = gerenciador

    # ── draw helpers ─────────────────────────────────────────────────────────

    def draw_section_title(self, title, x, y):
        """Idêntico ao StatisticsMenu.draw_section_title."""
        box_width  = self._content_width()
        box_height = 45
        box_rect   = pygame.Rect(x, y - self.scroll_y, box_width, box_height)
        if box_rect.bottom < 0 or box_rect.top > self.height:
            return y + box_height + 10
        azul_claro = (200, 190, 255, 230)
        pygame.draw.rect(self.screen, azul_claro, box_rect, border_radius=self.option_radius)
        pygame.draw.rect(self.screen, (150, 150, 150), box_rect, width=2, border_radius=self.option_radius)
        title_surf = self.title_font.render(title, True, self.text_color)
        title_rect = title_surf.get_rect(center=box_rect.center)
        self.screen.blit(title_surf, title_rect)
        return y + box_height + 10

    def draw_evento_card(self, evento, x, y, cor_status, card_index=0):
        """
        Card de evento no mesmo visual de draw_stat_option (StatisticsMenu):
        sombra suave, fundo branco / hover azul claro, borda cinza.
        """
        mouse_pos  = pygame.mouse.get_pos()
        width      = self._content_width()
        height     = self.option_height
        rect       = pygame.Rect(x, y - self.scroll_y, width, height)

        if rect.bottom < 0 or rect.top > self.height:
            return y + height + self.card_spacing

        # ── animação: alpha da sombra e escala ───────────────────────────────
        is_hovered = rect.collidepoint(mouse_pos)

        cur_alpha = self._shadow_alpha.get(card_index, 0)
        cur_alpha = min(40, cur_alpha + 6) if is_hovered else max(0, cur_alpha - 6)
        self._shadow_alpha[card_index] = cur_alpha

        cur_scale = self._card_scale.get(card_index, 1.0)
        target_scale = 1.04 if is_hovered else 1.0
        cur_scale += (target_scale - cur_scale) * 0.2
        if abs(cur_scale - target_scale) < 0.001:
            cur_scale = target_scale
        self._card_scale[card_index] = cur_scale

        # ── renderiza o card numa surface e escala ela (zoom centrado) ────────
        card_surf = pygame.Surface((width, height), pygame.SRCALPHA)

        blend = cur_alpha / 40.0
        color = (int(255 - blend * 10), int(255 - blend * 10), int(255 - blend * 5))
        pygame.draw.rect(card_surf, color, (0, 0, width, height), border_radius=self.option_radius)
        pygame.draw.rect(card_surf, (150, 150, 150), (0, 0, width, height), width=2, border_radius=self.option_radius)

        cy_top = height // 3
        cy_bot = (height * 2) // 3

        nome_surf = self.font.render(evento.nome, True, self.text_color)
        card_surf.blit(nome_surf, nome_surf.get_rect(center=(width // 2, cy_top)))

        desc_surf = self.small_font.render(evento.get_descricao(), True, self.text_color)
        card_surf.blit(desc_surf, desc_surf.get_rect(midleft=(18, cy_bot)))

        periodo = f"{evento.data_inicio} {evento.hora_inicio} -> {evento.data_final} {evento.hora_final}"
        periodo_surf = self.small_font.render(periodo, True, self.text_color)
        periodo_rect = periodo_surf.get_rect(midright=(width - 18, cy_top))
        card_surf.blit(periodo_surf, periodo_rect)

        if evento.ativo:
            status_text = f"Ativo · {evento.get_tempo_restante()}"
        else:
            try:
                inicio = datetime.strptime(
                    f"{evento.data_inicio} {evento.hora_inicio}", "%d/%m/%Y %H:%M"
                )
                status_text = "Em breve" if inicio > datetime.now() else "Finalizado"
            except Exception:
                status_text = "Finalizado"

        status_surf = self.small_font.render(status_text, True, cor_status)
        # centralizado abaixo da data, usando o centro horizontal do período como referência
        periodo_center_x = periodo_rect.centerx
        card_surf.blit(status_surf, status_surf.get_rect(midtop=(periodo_center_x, cy_top + periodo_surf.get_height() // 2 + 2)))

        # escala a surface e centraliza no mesmo ponto
        s_width  = int(width  * cur_scale)
        s_height = int(height * cur_scale)
        scaled = pygame.transform.smoothscale(card_surf, (s_width, s_height))

        cx       = x + width // 2
        cy_center = rect.y + height // 2
        dest_x   = cx - s_width // 2
        dest_y   = cy_center - s_height // 2

        # sombra escala junto com o card
        if cur_alpha > 0:
            pad = int(3 * cur_scale)
            shadow = pygame.Surface((s_width + pad * 2, s_height + pad * 2), pygame.SRCALPHA)
            pygame.draw.rect(shadow, (0, 0, 0, cur_alpha),
                             (0, 0, s_width + pad * 2, s_height + pad * 2),
                             border_radius=int(self.option_radius * cur_scale))
            self.screen.blit(shadow, (dest_x - pad, dest_y - pad))

        self.screen.blit(scaled, (dest_x, dest_y))

        return y + height + self.card_spacing

    def draw_scrollbar(self):
        """Idêntico ao StatisticsMenu.draw_scrollbar."""
        if self.max_scroll <= 0:
            return
        scroll_area_x    = self.width - self.scrollbar_width - 5
        scroll_area_rect = pygame.Rect(scroll_area_x, 80, self.scrollbar_width, self.height - 100)
        visible_ratio    = self.height / (self.max_scroll + self.height)
        thumb_height     = max(30, visible_ratio * (self.height - 100))
        scroll_ratio     = self.scroll_y / self.max_scroll
        thumb_y          = 80 + scroll_ratio * ((self.height - 100) - thumb_height)
        self.scrollbar_rect = pygame.Rect(scroll_area_x, thumb_y, self.scrollbar_width, thumb_height)
        pygame.draw.rect(self.screen, (200, 200, 200, 150), scroll_area_rect, border_radius=6)
        pygame.draw.rect(self.screen, (100, 100, 100, 200), self.scrollbar_rect, border_radius=6)
        pygame.draw.rect(self.screen, (70, 70, 70), self.scrollbar_rect, 1, border_radius=6)

    def draw_close_button(self):
        if self.close_image:
            image_rect = self.close_image.get_rect(center=self.close_button_rect.center)
            self.screen.blit(self.close_image, image_rect)
        else:
            pygame.draw.rect(self.screen, (255, 100, 100), self.close_button_rect, border_radius=8)
            cx, cy = self.close_button_rect.center
            ll = 15
            pygame.draw.line(self.screen, (255, 255, 255), (cx - ll, cy - ll), (cx + ll, cy + ll), 2)
            pygame.draw.line(self.screen, (255, 255, 255), (cx - ll, cy + ll), (cx + ll, cy - ll), 2)

    # ── cálculo de altura total do conteúdo ───────────────────────────────────

    def _split_eventos(self):
        """Separa os eventos nas três categorias."""
        if not self.gerenciador:
            return [], [], []
        ativos   = self.gerenciador.get_eventos_ativos()
        futuros  = []
        passados = []
        agora = datetime.now()
        for e in self.gerenciador.eventos:
            if e.ativo:
                continue
            try:
                inicio = datetime.strptime(
                    f"{e.data_inicio} {e.hora_inicio}", "%d/%m/%Y %H:%M"
                )
                (futuros if inicio > agora else passados).append(e)
            except Exception:
                passados.append(e)
        return ativos, futuros, passados

    def calculate_content_height(self):
        section_h  = 45 + 10   # título de seção + gap
        card_h     = self.option_height + self.card_spacing
        ativos, futuros, passados = self._split_eventos()

        total = 90  # espaço do título principal
        for grupo in (ativos, futuros, passados):
            if grupo:
                total += section_h + len(grupo) * card_h + 35  # 35 = gap entre seções
        self.max_scroll = max(0, total - self.height)
        return total

    # ── draw principal ────────────────────────────────────────────────────────

    def draw(self):
        if not self.visible or not self.gerenciador:
            return

        self.gerenciador.atualizar_eventos()
        self.calculate_content_height()
        self.scroll_y = max(0, min(self.scroll_y, self.max_scroll))

        self.screen.fill(self.bg_color)

        # título
        title_font = pygame.font.SysFont(None, 44)
        title_surf = title_font.render("Eventos do Jogo", True, self.text_color)
        title_rect = title_surf.get_rect(center=(self.width // 2, 35))
        self.screen.blit(title_surf, title_rect)

        x = self._content_x()
        y = 85

        ativos, futuros, passados = self._split_eventos()

        # ── Eventos Ativos ────────────────────────────────────────────────────
        if ativos:
            y = self.draw_section_title("Eventos Ativos", x, y)
            for i, e in enumerate(ativos):
                y = self.draw_evento_card(e, x, y, self.cor_ativo, card_index=i)
            y += 35

        # ── Próximos Eventos ──────────────────────────────────────────────────
        if futuros:
            y = self.draw_section_title("Próximos Eventos", x, y)
            for i, e in enumerate(futuros):
                y = self.draw_evento_card(e, x, y, self.cor_futuro, card_index=1000 + i)
            y += 35

        # ── Eventos Passados ──────────────────────────────────────────────────
        if passados:
            y = self.draw_section_title("Eventos Passados", x, y)
            for i, e in enumerate(passados):
                y = self.draw_evento_card(e, x, y, self.cor_passado, card_index=2000 + i)

        # ── vazio ─────────────────────────────────────────────────────────────
        if not ativos and not futuros and not passados:
            empty_surf = self.font.render("Nenhum evento encontrado", True, self.text_color)
            empty_rect = empty_surf.get_rect(center=(self.width // 2, self.height // 2))
            self.screen.blit(empty_surf, empty_rect)

        if self.max_scroll > 0:
            self.draw_scrollbar()
        self.draw_close_button()

    # ── eventos de input ──────────────────────────────────────────────────────

    def handle_event(self, event):
        if not self.visible:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.visible = False
            elif event.key == pygame.K_UP:
                self.scroll_y = max(0, self.scroll_y - self.scroll_speed)
            elif event.key == pygame.K_DOWN:
                self.scroll_y = min(self.max_scroll, self.scroll_y + self.scroll_speed)
            elif event.key == pygame.K_PAGEUP:
                self.scroll_y = max(0, self.scroll_y - self.height // 2)
            elif event.key == pygame.K_PAGEDOWN:
                self.scroll_y = min(self.max_scroll, self.scroll_y + self.height // 2)
            elif event.key == pygame.K_HOME:
                self.scroll_y = 0
            elif event.key == pygame.K_END:
                self.scroll_y = self.max_scroll
            return True

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.close_button_rect.collidepoint(event.pos):
                    self.visible = False
                    return True
                if self.scrollbar_rect and self.scrollbar_rect.collidepoint(event.pos):
                    self.is_scrolling    = True
                    self.scroll_drag_start = event.pos[1] - self.scrollbar_rect.y
                    return True
            if event.button == 4:
                self.scroll_y = max(0, self.scroll_y - self.scroll_speed * 2)
            elif event.button == 5:
                self.scroll_y = min(self.max_scroll, self.scroll_y + self.scroll_speed * 2)
            return True

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.is_scrolling = False
            return True

        elif event.type == pygame.MOUSEMOTION:
            if self.is_scrolling and self.scrollbar_rect:
                mouse_y            = event.pos[1]
                scroll_area_height = self.height - 100
                thumb_height       = self.scrollbar_rect.height
                min_y, max_y       = 80, 80 + scroll_area_height - thumb_height
                new_thumb_y        = max(min_y, min(max_y, mouse_y - self.scroll_drag_start))
                scroll_ratio       = (new_thumb_y - min_y) / (scroll_area_height - thumb_height)
                self.scroll_y      = int(scroll_ratio * self.max_scroll)
                return True

        elif event.type == pygame.MOUSEWHEEL:
            self.scroll_y = max(0, min(self.max_scroll,
                                       self.scroll_y - event.y * self.scroll_speed))
            return True

        return False

    # ── visibilidade ──────────────────────────────────────────────────────────

    def show(self):
        self.visible  = True
        self.scroll_y = 0

    def hide(self):
        self.visible  = False
        self.scroll_y = 0

    def toggle(self):
        if self.visible:
            self.hide()
        else:
            self.show()