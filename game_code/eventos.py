import requests, json, pygame, os, sys, numpy as np
from datetime import datetime, timedelta

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class Evento:
    def __init__(self, nome, data_inicio, hora_inicio, data_final, hora_final, tipo="normal", id=None):
        self.nome = nome
        self.data_inicio = data_inicio
        self.hora_inicio = hora_inicio
        self.data_final = data_final
        self.hora_final = hora_final
        self.tipo = tipo
        self.id = id or nome.lower().replace(" ", "_")
        self.ativo = False
        
    def verificar_ativo(self):
        try:
            agora = datetime.now()
            inicio_str = f"{self.data_inicio} {self.hora_inicio}"
            inicio = datetime.strptime(inicio_str, "%d/%m/%Y %H:%M")
            final_str = f"{self.data_final} {self.hora_final}"
            final = datetime.strptime(final_str, "%d/%m/%Y %H:%M")
            self.ativo = inicio <= agora <= final
            return self.ativo
        except Exception:
            self.ativo = False
            return False
    
    def get_tempo_restante(self):
        if not self.ativo:
            return "Evento inativo"
        try:
            final_str = f"{self.data_final} {self.hora_final}"
            final = datetime.strptime(final_str, "%d/%m/%Y %H:%M")
            agora = datetime.now()
            if agora > final:
                return "Evento finalizado"
            diferenca = final - agora
            dias = diferenca.days
            horas = diferenca.seconds // 3600
            minutos = (diferenca.seconds % 3600) // 60
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
            "pontos_duplos": "Ganhe o DOBRO de pontos por clique!",
            "bonus_click": "Bonus extra em cada clique!",
            "velocidade_trabalhador": "Trabalhadores mais rapidos!",
            "preco_reduzido": "Upgrades com desconto!",
            "evento_raro": "Evento especial raro ativo!",
            "normal": "Evento especial ativo!"
        }
        return descricoes.get(self.tipo, "Evento especial ativo!")
    
    def aplicar_efeito_pontos(self, pontos_base):
        if not self.ativo:
            return pontos_base
        multiplicadores = {
            "pontos_duplos": 2.0,
            "bonus_click": 1.5,
            "evento_raro": 3.0,
            "normal": 1.0
        }
        multiplicador = multiplicadores.get(self.tipo, 1.0)
        return int(pontos_base * multiplicador)
    
    def aplicar_efeito_trabalhador(self, velocidade_base):
        if not self.ativo:
            return velocidade_base
        multiplicadores = {
            "velocidade_trabalhador": 2.0,
            "evento_raro": 1.5
        }
        multiplicador = multiplicadores.get(self.tipo, 1.0)
        return velocidade_base * multiplicador
    
    def aplicar_desconto_upgrades(self, preco_base):
        if not self.ativo:
            return preco_base
        multiplicadores = {
            "preco_reduzido": 0.5,
            "evento_raro": 0.7
        }
        multiplicador = multiplicadores.get(self.tipo, 1.0)
        return preco_base * multiplicador

class GerenciadorEventos:
    def __init__(self):
        self.eventos = []
        self.url_json = "https://raw.githack.com/eupyetro0224234/Generic-Clicker-Game/main/github_assets/eventos.json"
        self.ultima_verificacao = None
        self.intervalo_verificacao = 300000
        self.tipos_mapeados = set()
        
    def carregar_eventos(self):
        try:
            response = requests.get(self.url_json, timeout=10)
            response.raise_for_status()
            dados = response.json()
            self.eventos.clear()
            self.tipos_mapeados.clear()
            for evento_data in dados.get("eventos", []):
                evento = Evento(
                    nome=evento_data.get("nome", ""),
                    data_inicio=evento_data.get("data_inicio", ""),
                    hora_inicio=evento_data.get("hora_inicio", ""),
                    data_final=evento_data.get("data_final", ""),
                    hora_final=evento_data.get("hora_final", ""),
                    tipo=evento_data.get("tipo", "normal"),
                    id=evento_data.get("id")
                )
                self.eventos.append(evento)
                self.tipos_mapeados.add(evento.tipo)
            self.ultima_verificacao = pygame.time.get_ticks()
            return True
        except requests.exceptions.RequestException:
            return False
        except json.JSONDecodeError:
            return False
        except Exception:
            return False
    
    def atualizar_eventos(self):
        current_time = pygame.time.get_ticks()
        if (self.ultima_verificacao is None or 
            current_time - self.ultima_verificacao > self.intervalo_verificacao):
            self.carregar_eventos()
        eventos_ativos = []
        for evento in self.eventos:
            if evento.verificar_ativo():
                eventos_ativos.append(evento)
        return eventos_ativos
    
    def get_eventos_ativos(self):
        return [evento for evento in self.eventos if evento.ativo]
    
    def get_eventos_por_tipo(self, tipo):
        return [evento for evento in self.eventos if evento.ativo and evento.tipo == tipo]
    
    def get_proximo_evento(self):
        try:
            agora = datetime.now()
            eventos_futuros = []
            for evento in self.eventos:
                try:
                    inicio_str = f"{evento.data_inicio} {evento.hora_inicio}"
                    inicio = datetime.strptime(inicio_str, "%d/%m/%Y %H:%M")
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
        eventos_ativos = self.get_eventos_ativos()
        for evento in eventos_ativos:
            pontos_finais = evento.aplicar_efeito_pontos(pontos_finais)
        return pontos_finais
    
    def aplicar_efeitos_trabalhador(self, velocidade_base):
        velocidade_final = velocidade_base
        eventos_ativos = self.get_eventos_ativos()
        for evento in eventos_ativos:
            velocidade_final = evento.aplicar_efeito_trabalhador(velocidade_final)
        return velocidade_final
    
    def aplicar_descontos_upgrades(self, preco_base):
        preco_final = preco_base
        eventos_ativos = self.get_eventos_ativos()
        for evento in eventos_ativos:
            preco_final = evento.aplicar_desconto_upgrades(preco_final)
        return preco_final
    
    def get_estatisticas_eventos(self):
        eventos_ativos = self.get_eventos_ativos()
        eventos_futuros = []
        eventos_passados = []
        agora = datetime.now()
        for evento in self.eventos:
            try:
                inicio_str = f"{evento.data_inicio} {evento.hora_inicio}"
                inicio = datetime.strptime(inicio_str, "%d/%m/%Y %H:%M")
                if inicio > agora:
                    eventos_futuros.append(evento)
                elif not evento.ativo:
                    eventos_passados.append(evento)
            except:
                continue
        return {
            "total": len(self.eventos),
            "ativos": len(eventos_ativos),
            "futuros": len(eventos_futuros),
            "passados": len(eventos_passados),
            "tipos_unicos": list(self.tipos_mapeados)
        }

class EventosMenu:
    def __init__(self, screen, window_width, window_height):
        self.screen = screen
        self.window_width = window_width
        self.window_height = window_height
        self.visible = False
        self.bg_color = (255, 182, 193)
        self.text_color = (47, 24, 63)
        self.option_color = (255, 255, 255)
        self.hover_color = (220, 235, 255)
        self.border_color = (150, 150, 150)
        self.section_color = (200, 190, 255, 230)
        self.cor_ativo = (255, 215, 0)
        self.cor_futuro = (100, 150, 255)
        self.cor_passado = (150, 150, 150)
        self.scrollbar_color = (100, 100, 120, 180)
        self.scrollbar_hover_color = (80, 80, 100, 200)
        self.title_font = pygame.font.SysFont(None, 48)
        self.section_font = pygame.font.SysFont(None, 42)
        self.normal_font = pygame.font.SysFont(None, 32)
        self.small_font = pygame.font.SysFont(None, 24)
        self.padding_x = 20
        self.padding_y = 20
        self.option_height = 60
        self.card_height = 80
        self.option_radius = 15
        self.spacing_y = 20
        self.scroll_offset = 0
        self.max_scroll = 0
        self.scroll_speed = 25
        self.scrollbar_width = 12
        self.scrollbar_padding = 5
        self.is_scrolling = False
        self.scrollbar_rect = None
        self.scrollbar_handle_rect = None
        self.gerenciador = None
        
        # Carregar e redimensionar a imagem de fechar - tamanho muito menor
        try:
            close_image_path = resource_path("game_assets/close.png")
            if not os.path.exists(close_image_path):
                close_image_path = os.path.join("..", "game_assets", "close.png")
            self.close_image = pygame.image.load(close_image_path).convert_alpha()
            # Tamanho reduzido para 40x40 pixels (era 60x60)
            target_size = (40, 40)
            self.close_image = pygame.transform.smoothscale(self.close_image, target_size)
        except Exception:
            self.close_image = None
            
        # Posição ajustada para ficar muito mais à esquerda
        # window_width - 60: 60 pixels da borda direita (era 80)
        # 15: 15 pixels do topo (era 10)
        self.close_button_rect = pygame.Rect(self.window_width - 80, 15, 40, 40)
        
    def set_gerenciador(self, gerenciador):
        self.gerenciador = gerenciador
        
    def handle_event(self, event):
        if not self.visible:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.visible = False
                return True
            elif event.key == pygame.K_UP:
                self.scroll_offset = max(0, self.scroll_offset - self.scroll_speed)
                return True
            elif event.key == pygame.K_DOWN:
                self.scroll_offset = min(self.max_scroll, self.scroll_offset + self.scroll_speed)
                return True
            elif event.key == pygame.K_PAGEUP:
                self.scroll_offset = max(0, self.scroll_offset - self.window_height // 2)
                return True
            elif event.key == pygame.K_PAGEDOWN:
                self.scroll_offset = min(self.max_scroll, self.scroll_offset + self.window_height // 2)
                return True
        
        # Modificação: Só funciona com botão esquerdo do mouse (button == 1)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Apenas botão esquerdo
                if self.close_button_rect.collidepoint(event.pos):
                    self.visible = False
                    return True
                if self.scrollbar_handle_rect and self.scrollbar_handle_rect.collidepoint(event.pos):
                    self.is_scrolling = True
                    self.scrollbar_mouse_offset = event.pos[1] - self.scrollbar_handle_rect.top
                    return True
                elif self.scrollbar_rect and self.scrollbar_rect.collidepoint(event.pos):
                    if event.pos[1] < self.scrollbar_handle_rect.top:
                        self.scroll_offset = max(0, self.scroll_offset - self.window_height // 2)
                    else:
                        self.scroll_offset = min(self.max_scroll, self.scroll_offset + self.window_height // 2)
                    return True
        
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Apenas botão esquerdo
                self.is_scrolling = False
        
        if event.type == pygame.MOUSEMOTION:
            if self.is_scrolling:
                mouse_y = event.pos[1] - self.scrollbar_mouse_offset
                scrollbar_top = self.scrollbar_rect.top
                scrollbar_bottom = self.scrollbar_rect.bottom - self.scrollbar_handle_rect.height
                if scrollbar_bottom > scrollbar_top:
                    percent = (mouse_y - scrollbar_top) / (scrollbar_bottom - scrollbar_top)
                    percent = max(0, min(1, percent))
                    self.scroll_offset = int(percent * self.max_scroll)
                return True
        
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_offset = max(0, min(self.max_scroll, self.scroll_offset - event.y * self.scroll_speed))
            return True
        
        return False
        
    def calculate_content_height(self):
        if not self.gerenciador:
            return 0
        height = 90
        eventos_ativos = self.gerenciador.get_eventos_ativos()
        eventos_futuros = []
        eventos_passados = []
        for evento in self.gerenciador.eventos:
            if evento.ativo:
                continue
            try:
                inicio_str = f"{evento.data_inicio} {evento.hora_inicio}"
                inicio = datetime.strptime(inicio_str, "%d/%m/%Y %H:%M")
                agora = datetime.now()
                if inicio > agora:
                    eventos_futuros.append(evento)
                else:
                    eventos_passados.append(evento)
            except:
                eventos_passados.append(evento)
        if eventos_ativos:
            height += self.option_height + self.spacing_y
            height += len(eventos_ativos) * (self.card_height + self.spacing_y)
        if eventos_futuros:
            height += self.option_height + self.spacing_y
            height += len(eventos_futuros) * (self.card_height + self.spacing_y)
        if eventos_passados:
            height += self.option_height + self.spacing_y
            height += len(eventos_passados) * (self.card_height + self.spacing_y)
        return height
        
    def draw_section_title(self, title, x, y, width):
        box_rect = pygame.Rect(x, y, width, self.option_height)
        pygame.draw.rect(self.screen, self.section_color, box_rect, border_radius=self.option_radius)
        pygame.draw.rect(self.screen, self.border_color, box_rect, width=2, border_radius=self.option_radius)
        title_surf = self.section_font.render(title, True, self.text_color)
        title_rect = title_surf.get_rect(center=box_rect.center)
        self.screen.blit(title_surf, title_rect)
        return y + self.option_height + self.spacing_y
        
    def draw_evento_card(self, evento, x, y, width, cor_status):
        card_rect = pygame.Rect(x, y, width, self.card_height)
        mouse_pos = pygame.mouse.get_pos()
        if card_rect.bottom < 0 or card_rect.top > self.window_height:
            return self.card_height + self.spacing_y
        shadow_surface = pygame.Surface((width + 6, self.card_height + 6), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, (0, 0, 0, 20), (0, 0, width + 6, self.card_height + 6), border_radius=15)
        self.screen.blit(shadow_surface, (x - 3, y - 3))
        color = self.hover_color if card_rect.collidepoint(mouse_pos) else self.option_color
        pygame.draw.rect(self.screen, color, card_rect, border_radius=self.option_radius)
        pygame.draw.rect(self.screen, self.border_color, card_rect, width=2, border_radius=self.option_radius)
        nome_surf = self.normal_font.render(evento.nome, True, self.text_color)
        self.screen.blit(nome_surf, (x + 15, y + 12))
        desc_surf = self.small_font.render(evento.get_descricao(), True, self.text_color)
        self.screen.blit(desc_surf, (x + 15, y + 40))
        periodo = f"{evento.data_inicio} {evento.hora_inicio} - {evento.data_final} {evento.hora_final}"
        periodo_surf = self.small_font.render(periodo, True, self.text_color)
        periodo_rect = periodo_surf.get_rect(right=x + width - 15, top=y + 12)
        self.screen.blit(periodo_surf, periodo_rect)
        if evento.ativo:
            status_text = f"Ativo - {evento.get_tempo_restante()}"
        else:
            try:
                inicio_str = f"{evento.data_inicio} {evento.hora_inicio}"
                inicio = datetime.strptime(inicio_str, "%d/%m/%Y %H:%M")
                agora = datetime.now()
                status_text = "Em breve" if inicio > agora else "Finalizado"
            except:
                status_text = "Finalizado"
        status_surf = self.small_font.render(status_text, True, cor_status)
        status_rect = status_surf.get_rect(right=x + width - 15, top=y + 40)
        self.screen.blit(status_surf, status_rect)
        return self.card_height + self.spacing_y
    
    def draw_scrollbar(self):
        content_height = self.calculate_content_height()
        visible_height = self.window_height
        if content_height <= visible_height:
            self.max_scroll = 0
            self.scroll_offset = 0
            return
        self.max_scroll = content_height - visible_height
        self.scroll_offset = min(self.scroll_offset, self.max_scroll)
        scrollbar_x = self.window_width - self.scrollbar_width - self.scrollbar_padding
        self.scrollbar_rect = pygame.Rect(scrollbar_x, 0, self.scrollbar_width, visible_height)
        handle_height = max(30, (visible_height / content_height) * visible_height)
        handle_ratio = self.scroll_offset / self.max_scroll
        handle_y = handle_ratio * (visible_height - handle_height)
        self.scrollbar_handle_rect = pygame.Rect(scrollbar_x, handle_y, self.scrollbar_width, handle_height)
        mouse_pos = pygame.mouse.get_pos()
        handle_color = self.scrollbar_hover_color if self.scrollbar_handle_rect.collidepoint(mouse_pos) else self.scrollbar_color
        pygame.draw.rect(self.screen, (200, 200, 200, 50), self.scrollbar_rect, border_radius=6)
        pygame.draw.rect(self.screen, handle_color, self.scrollbar_handle_rect, border_radius=6)
        
    def draw_close_button(self):
        if self.close_image:
            image_rect = self.close_image.get_rect(center=self.close_button_rect.center)
            self.screen.blit(self.close_image, image_rect)
        else:
            pygame.draw.rect(self.screen, (255, 100, 100), self.close_button_rect, border_radius=6)
            center_x, center_y = self.close_button_rect.center
            # Reduzido proporcionalmente para combinar com o novo tamanho (40x40)
            line_length = 15  # Reduzido de 20 para 15
            pygame.draw.line(self.screen, (255, 255, 255), (center_x - line_length, center_y - line_length),
                            (center_x + line_length, center_y + line_length), 2)  # Espessura reduzida de 3 para 2
            pygame.draw.line(self.screen, (255, 255, 255), (center_x - line_length, center_y + line_length),
                            (center_x + line_length, center_y - line_length), 2)  # Espessura reduzida de 3 para 2
    
    def draw(self):
        if not self.visible or not self.gerenciador:
            return
        self.gerenciador.atualizar_eventos()
        content_y_start = -self.scroll_offset
        self.screen.fill(self.bg_color)
        title_surf = self.title_font.render("Eventos do Jogo", True, self.text_color)
        title_rect = title_surf.get_rect(center=(self.window_width // 2, 35))
        self.screen.blit(title_surf, title_rect)
        self.draw_close_button()
        content_width = self.window_width - 2 * self.padding_x - self.scrollbar_width - self.scrollbar_padding
        y_position = 90 + content_y_start
        eventos_ativos = self.gerenciador.get_eventos_ativos()
        eventos_futuros = []
        eventos_passados = []
        for evento in self.gerenciador.eventos:
            if evento.ativo:
                continue
            try:
                inicio_str = f"{evento.data_inicio} {evento.hora_inicio}"
                inicio = datetime.strptime(inicio_str, "%d/%m/%Y %H:%M")
                agora = datetime.now()
                if inicio > agora:
                    eventos_futuros.append(evento)
                else:
                    eventos_passados.append(evento)
            except:
                eventos_passados.append(evento)
        if eventos_ativos:
            section_y = y_position
            if section_y + self.option_height > 0 and section_y < self.window_height:
                y_position = self.draw_section_title("Eventos Ativos", self.padding_x, section_y, content_width)
            else:
                y_position += self.option_height + self.spacing_y
            for evento in eventos_ativos:
                card_y = y_position
                if card_y + self.card_height > 0 and card_y < self.window_height:
                    card_height_used = self.draw_evento_card(evento, self.padding_x, card_y, content_width, self.cor_ativo)
                    y_position += card_height_used
                else:
                    y_position += self.card_height + self.spacing_y
        if eventos_futuros:
            section_y = y_position
            if section_y + self.option_height > 0 and section_y < self.window_height:
                y_position = self.draw_section_title("Proximos Eventos", self.padding_x, section_y, content_width)
            else:
                y_position += self.option_height + self.spacing_y
            for evento in eventos_futuros:
                card_y = y_position
                if card_y + self.card_height > 0 and card_y < self.window_height:
                    card_height_used = self.draw_evento_card(evento, self.padding_x, card_y, content_width, self.cor_futuro)
                    y_position += card_height_used
                else:
                    y_position += self.card_height + self.spacing_y
        if eventos_passados:
            section_y = y_position
            if section_y + self.option_height > 0 and section_y < self.window_height:
                y_position = self.draw_section_title("Eventos Passados", self.padding_x, section_y, content_width)
            else:
                y_position += self.option_height + self.spacing_y
            for evento in eventos_passados:
                card_y = y_position
                if card_y + self.card_height > 0 and card_y < self.window_height:
                    card_height_used = self.draw_evento_card(evento, self.padding_x, card_y, content_width, self.cor_passado)
                    y_position += card_height_used
                else:
                    y_position += self.card_height + self.spacing_y
        if not eventos_ativos and not eventos_futuros and not eventos_passados:
            empty_y = self.window_height // 2 + content_y_start
            if empty_y > 0 and empty_y < self.window_height:
                empty_text = self.normal_font.render("Nenhum evento encontrado", True, self.text_color)
                empty_rect = empty_text.get_rect(center=(self.window_width // 2, empty_y))
                self.screen.blit(empty_text, empty_rect)
        self.draw_scrollbar()
    
    def show(self):
        self.visible = True
        self.scroll_offset = 0
        
    def hide(self):
        self.visible = False
        
    def toggle(self):
        if self.visible:
            self.hide()
        else:
            self.show()