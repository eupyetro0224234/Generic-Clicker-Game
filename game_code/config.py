import pygame, json, os
from game_assets.game_assets_packed import load_image

class FullSettingsMenu:
    def __init__(self, screen, window_width, window_height):
        self.screen = screen
        self.width = window_width
        self.height = window_height

        self.bg_color = (255, 182, 193)
        self.text_color = (47, 24, 63)
        self.option_height = 50
        self.option_radius = 20
        self.padding_x = 20
        self.padding_y = 15
        self.spacing_x = 15
        self.spacing_y = 12
        self.options_per_row = 2

        self.content_margin = 60

        appdata_roaming = os.getenv("APPDATA")
        self.game_folder = os.path.join(appdata_roaming, "genericclickergame")
        os.makedirs(self.game_folder, exist_ok=True)
        self.config_path = os.path.join(self.game_folder, "config.json")

        self.default_config = {
            "Clique Esquerdo": True,
            "Clique Direito": True,
            "Clique Botão do Meio": False,
            "Rolagem do Mouse": False,
            "Ativar Mods": False,
            "Verificar atualizações": True,
            "Mostrar descrição de conquistas bloqueadas": False,
            "Menu vertical": False,
            "Mostrar sequência": True,
            "Volume Conquistas": 100,
            "Volume Mini Evento": 100,
            "Brilho do fundo": 100,
            "Exibir imagens": True,
        }

        self.visible = False
        self.options = {}
        self.load_config()

        self.valor_original_update = self.options.get("Verificar atualizações", True)
        self.valor_original_mods = self.options.get("Ativar Mods", False)
        self.precisa_reiniciar = False

        self.title_font = pygame.font.SysFont(None, 38)
        self.font = pygame.font.SysFont(None, 28)
        self.emoji_font = pygame.font.SysFont("segoeuiemoji", 24)

        self.hovered_option = None
        self.button_rects = []
        self.slider_rects = []

        self.console_ativo = False
        self.image_viewed = False

        self.close_button_rect = pygame.Rect(self.width - 80, 15, 40, 40)

        try:
            self.close_image = load_image("close.png")
            self.close_image = pygame.transform.smoothscale(self.close_image, (40, 40))
        except Exception:
            self.close_image = None

        self.search_button_rect = pygame.Rect(25, 25, 40, 40)

        self.dragging_slider = None
        self.dragging_start_x = None

        self.scroll_y = 0
        self.scroll_speed = 30
        self.max_scroll = 0
        self.scrollbar_width = 12
        self.scrollbar_rect = None
        self.is_scrolling = False
        self.scroll_drag_start = 0

        self.statistics_menu = None

        # ── animação de hover por botão ───────────────────────────────────────
        # chave: key da opção, valor: alpha da sombra (0-40) e escala (1.0-1.04)
        self._btn_shadow = {}
        self._btn_scale  = {}
        # para sliders usamos o key também
        self._slider_shadow = {}
        self._slider_scale  = {}

    # ── helpers ──────────────────────────────────────────────────────────────

    def _content_x(self):
        return self.content_margin

    def _content_width(self):
        return self.width - 2 * self.content_margin

    def is_click_allowed(self, button):
        if button == 1:
            return self.options.get("Clique Esquerdo", True)
        elif button == 2:
            return self.options.get("Clique Botão do Meio", False)
        elif button == 3:
            return self.options.get("Clique Direito", True)
        elif button in (4, 5):
            return self.options.get("Rolagem do Mouse", False)
        return False

    def load_config(self):
        try:
            if os.path.isfile(self.config_path):
                with open(self.config_path, "r", encoding="utf-8") as f:
                    loaded_options = json.load(f)
                    self.options = {**self.default_config}
                    for key in loaded_options:
                        if key in self.default_config or key == "Manter console aberto":
                            self.options[key] = loaded_options[key]
            else:
                self.options = self.default_config.copy()
                self.save_config()
        except Exception:
            self.options = self.default_config.copy()

    def save_config(self):
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.options, f, indent=4, ensure_ascii=False)
        except Exception:
            pass

    def get_option(self, key):
        return self.options.get(key, False)

    def set_option(self, key, value):
        self.options[key] = bool(value)
        self.save_config()

    def add_console_option(self):
        if not self.console_ativo:
            self.console_ativo = True
            if "Manter console aberto" not in self.options:
                self.options["Manter console aberto"] = False
                self.save_config()

    def remove_console_option(self):
        if self.console_ativo:
            self.console_ativo = False
            if "Manter console aberto" in self.options:
                del self.options["Manter console aberto"]
                self.save_config()

    # ── animação helper ───────────────────────────────────────────────────────

    def _animate(self, store_alpha, store_scale, key, is_hovered):
        """Atualiza e retorna (cur_alpha, cur_scale) para um botão/slider."""
        alpha = store_alpha.get(key, 0)
        alpha = min(40, alpha + 6) if is_hovered else max(0, alpha - 6)
        store_alpha[key] = alpha

        scale = store_scale.get(key, 1.0)
        target = 1.03 if is_hovered else 1.0
        scale += (target - scale) * 0.2
        if abs(scale - target) < 0.001:
            scale = target
        store_scale[key] = scale

        return alpha, scale

    def _draw_animated_box(self, surf_or_screen, rect, alpha, scale, radius, is_surface=False):
        """
        Desenha a caixa (com sombra e fundo animados) numa Surface separada
        e faz blit escalado no centro do rect original.
        Retorna o scaled_rect para posicionamento de texto.
        """
        w, h = rect.width, rect.height
        cx   = rect.centerx
        cy   = rect.centery

        # renderiza na surface base
        card = pygame.Surface((w, h), pygame.SRCALPHA)
        blend = alpha / 40.0
        color = (int(255 - blend * 10), int(255 - blend * 10), int(255 - blend * 5))
        pygame.draw.rect(card, color,         (0, 0, w, h), border_radius=radius)
        pygame.draw.rect(card, (150, 150, 150), (0, 0, w, h), width=2, border_radius=radius)

        sw = int(w * scale)
        sh = int(h * scale)
        scaled = pygame.transform.smoothscale(card, (sw, sh))

        dx = cx - sw // 2
        dy = cy - sh // 2

        # sombra escala junto com o card
        if alpha > 0:
            pad = int(3 * scale)
            shadow = pygame.Surface((sw + pad * 2, sh + pad * 2), pygame.SRCALPHA)
            pygame.draw.rect(shadow, (0, 0, 0, alpha),
                             (0, 0, sw + pad * 2, sh + pad * 2),
                             border_radius=int(radius * scale))
            surf_or_screen.blit(shadow, (dx - pad, dy - pad))

        surf_or_screen.blit(scaled, (dx, dy))
        return pygame.Rect(dx, dy, sw, sh)

    # ── conteúdo / scrollbar ─────────────────────────────────────────────────

    def calculate_content_height(self):
        section_h = 45 + 10
        row_h     = self.option_height + self.spacing_y

        outros_keys_count = 6
        console_visivel = self.console_ativo and "Manter console aberto" in self.options

        if console_visivel:
            outros_keys_count = 7

        total = 85
        total += section_h
        total += 2 * row_h
        total += 35
        total += section_h
        total += 2 * row_h
        total += 35
        total += section_h
        total += row_h
        total += 20
        outros_rows = (outros_keys_count + self.options_per_row - 1) // self.options_per_row
        total += outros_rows * row_h
        total += 30

        if console_visivel:
            self.max_scroll = max(0, total - self.height)
        else:
            self.max_scroll = 0
        return total

    def draw_scrollbar(self):
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

    # ── draw helpers ─────────────────────────────────────────────────────────

    def draw_section_title(self, title, x, y):
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

    def draw_slider_option(self, key, x, y, width):
        mouse_pos        = pygame.mouse.get_pos()
        container_height = self.option_height
        draw_y           = y - self.scroll_y
        container_rect   = pygame.Rect(x, draw_y, width, container_height)

        if container_rect.bottom < 0 or container_rect.top > self.height:
            return y + container_height + self.spacing_y

        is_hovered = container_rect.collidepoint(mouse_pos) or self.dragging_slider == key
        alpha, scale = self._animate(self._slider_shadow, self._slider_scale, key, is_hovered)
        scaled_rect  = self._draw_animated_box(self.screen, container_rect, alpha, scale, self.option_radius)

        # texto da label
        text_surf = self.font.render(key, True, self.text_color)
        text_rect = text_surf.get_rect(midleft=(scaled_rect.x + 20, scaled_rect.centery))
        self.screen.blit(text_surf, text_rect)

        slider_width  = 180
        slider_height = 16
        slider_x      = scaled_rect.x + scaled_rect.width - slider_width - 25
        slider_y      = scaled_rect.y + (scaled_rect.height - slider_height) // 2
        track_rect    = pygame.Rect(slider_x, slider_y, slider_width, slider_height)
        pygame.draw.rect(self.screen, (200, 200, 200), track_rect, border_radius=10)
        pygame.draw.rect(self.screen, (100, 100, 100), track_rect, width=1, border_radius=10)

        current_value = self.options.get(key, 100)
        if key == "Brilho do fundo":
            display_value = max(35, current_value)
            slider_pos    = slider_x + int((display_value / 100) * slider_width)
        else:
            display_value = current_value
            slider_pos    = slider_x + int((current_value / 100) * slider_width)

        handle_rect  = pygame.Rect(slider_pos - 6, slider_y - 2, 12, slider_height + 4)
        handle_color = (100, 150, 255) if (handle_rect.collidepoint(mouse_pos) or self.dragging_slider == key) else (70, 130, 230)
        pygame.draw.rect(self.screen, handle_color, handle_rect, border_radius=8)
        pygame.draw.rect(self.screen, (50, 100, 180), handle_rect, width=1, border_radius=8)

        if key == "Brilho do fundo":
            value_text = "35% (mínimo)" if current_value < 35 else f"{display_value}%"
        else:
            value_text = f"{current_value}%"
        value_surf = self.font.render(value_text, True, self.text_color)
        value_rect = value_surf.get_rect(midright=(slider_x - 8, scaled_rect.centery))
        self.screen.blit(value_surf, value_rect)

        self.slider_rects.append((track_rect, handle_rect, key))
        return y + container_height + self.spacing_y

    def draw_options(self, keys, x, y):
        mouse_pos    = pygame.mouse.get_pos()
        total_width  = self._content_width()
        button_width = (total_width - (self.options_per_row - 1) * self.spacing_x) // self.options_per_row

        for i, key in enumerate(keys):
            val      = self.options.get(key, False)
            row      = i // self.options_per_row
            col      = i % self.options_per_row
            option_x = x + col * (button_width + self.spacing_x)
            option_y = y + row * (self.option_height + self.spacing_y)
            draw_oy  = option_y - self.scroll_y

            option_rect = pygame.Rect(option_x, draw_oy, button_width, self.option_height)
            self.button_rects.append((option_rect, key))

            if option_rect.bottom < 0 or option_rect.top > self.height:
                continue

            is_hovered = option_rect.collidepoint(mouse_pos)
            alpha, scale = self._animate(self._btn_shadow, self._btn_scale, key, is_hovered)
            scaled_rect  = self._draw_animated_box(self.screen, option_rect, alpha, scale, self.option_radius)

            text_surf = self.font.render(key, True, self.text_color)
            text_rect = text_surf.get_rect(midleft=(scaled_rect.x + 18, scaled_rect.centery))
            self.screen.blit(text_surf, text_rect)

            val_text = "Ativado" if val else "Desativado"
            val_surf = self.font.render(val_text, True, self.text_color)
            val_rect = val_surf.get_rect(midright=(scaled_rect.x + scaled_rect.width - 18, scaled_rect.centery))
            self.screen.blit(val_surf, val_rect)

        total_rows = (len(keys) + self.options_per_row - 1) // self.options_per_row
        return y + total_rows * (self.option_height + self.spacing_y)

    def draw_close_button(self):
        if self.close_image:
            image_rect = self.close_image.get_rect(center=self.close_button_rect.center)
            self.screen.blit(self.close_image, image_rect)
        else:
            pygame.draw.rect(self.screen, (255, 100, 100), self.close_button_rect, border_radius=8)
            center_x, center_y = self.close_button_rect.center
            line_length = 15
            pygame.draw.line(self.screen, (255, 255, 255),
                             (center_x - line_length, center_y - line_length),
                             (center_x + line_length, center_y + line_length), 2)
            pygame.draw.line(self.screen, (255, 255, 255),
                             (center_x - line_length, center_y + line_length),
                             (center_x + line_length, center_y - line_length), 2)

    # ── draw principal ────────────────────────────────────────────────────────

    def draw(self):
        if not self.visible:
            return
        self.button_rects = []
        self.slider_rects = []
        self.screen.fill(self.bg_color)

        self.calculate_content_height()
        self.scroll_y = max(0, min(self.scroll_y, self.max_scroll))

        x            = self._content_x()
        slider_width = self._content_width()

        title_font = pygame.font.SysFont(None, 44)
        title_surf = title_font.render("Configurações", True, self.text_color)
        title_rect = title_surf.get_rect(center=(self.width // 2, 35))
        self.screen.blit(title_surf, title_rect)

        self.draw_close_button()

        pygame.draw.rect(self.screen, (120, 180, 255), self.search_button_rect, border_radius=20)
        pygame.draw.rect(self.screen, (60, 120, 180), self.search_button_rect, 2, border_radius=20)
        search_surf = self.emoji_font.render("🔍", True, (255, 255, 255))
        search_surf = pygame.transform.scale(search_surf, (22, 22))
        search_rect = search_surf.get_rect(center=self.search_button_rect.center)
        self.screen.blit(search_surf, search_rect)

        y = 85
        y = self.draw_section_title("Controles", x, y)
        controles_keys = [
            "Clique Esquerdo",
            "Clique Direito",
            "Clique Botão do Meio",
            "Rolagem do Mouse"
        ]
        y = self.draw_options(controles_keys, x, y)
        y += 35
        y = self.draw_section_title("Som", x, y)
        y = self.draw_slider_option("Volume Conquistas", x, y, slider_width)
        y = self.draw_slider_option("Volume Mini Evento", x, y, slider_width)
        y += 35
        y = self.draw_section_title("Outros", x, y)
        y = self.draw_slider_option("Brilho do fundo", x, y, slider_width)
        y += 20

        outros_keys = [
            "Ativar Mods",
            "Verificar atualizações",
            "Mostrar descrição de conquistas bloqueadas",
            "Menu vertical",
            "Mostrar sequência",
        ]
        if self.image_viewed:
            outros_keys.append("Exibir imagens")
        if self.console_ativo and "Manter console aberto" in self.options:
            outros_keys.append("Manter console aberto")

        y = self.draw_options(outros_keys, x, y)

        if self.max_scroll > 0:
            self.draw_scrollbar()

        if self.precisa_reiniciar:
            restart_font = pygame.font.SysFont(None, 26)
            restart_text = restart_font.render("Reinicie o jogo para aplicar mudanças", True, (200, 0, 0))
            restart_rect = restart_text.get_rect(center=(self.width // 2, self.height - 25))
            self.screen.blit(restart_text, restart_rect)

    # ── eventos ───────────────────────────────────────────────────────────────

    def handle_event(self, event):
        if not self.visible:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.visible = False
                return True
            elif event.key == pygame.K_UP:
                self.scroll_y = max(0, self.scroll_y - self.scroll_speed)
                return True
            elif event.key == pygame.K_DOWN:
                self.scroll_y = min(self.max_scroll, self.scroll_y + self.scroll_speed)
                return True
            elif event.key == pygame.K_PAGEUP:
                self.scroll_y = max(0, self.scroll_y - self.height // 2)
                return True
            elif event.key == pygame.K_PAGEDOWN:
                self.scroll_y = min(self.max_scroll, self.scroll_y + self.height // 2)
                return True
            elif event.key == pygame.K_HOME:
                self.scroll_y = 0
                return True
            elif event.key == pygame.K_END:
                self.scroll_y = self.max_scroll
                return True
            return True

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos

            if event.button == 1 and self.close_button_rect.collidepoint(mouse_pos):
                self.visible = False
                return True

            if event.button == 1 and self.search_button_rect.collidepoint(mouse_pos):
                if self.statistics_menu:
                    self.statistics_menu.show()
                return True

            if event.button == 1 and self.scrollbar_rect and self.scrollbar_rect.collidepoint(mouse_pos):
                self.is_scrolling = True
                self.scroll_drag_start = mouse_pos[1] - self.scrollbar_rect.y
                return True

            if event.button == 4:
                self.scroll_y = max(0, self.scroll_y - self.scroll_speed * 2)
                return True
            elif event.button == 5:
                self.scroll_y = min(self.max_scroll, self.scroll_y + self.scroll_speed * 2)
                return True

            for track_rect, handle_rect, key in self.slider_rects:
                if event.button == 1 and (handle_rect.collidepoint(mouse_pos) or track_rect.collidepoint(mouse_pos)):
                    self.dragging_slider = key
                    self.dragging_start_x = mouse_pos[0]
                    relative_x = mouse_pos[0] - track_rect.left
                    percentage = max(0, min(100, int((relative_x / track_rect.width) * 100)))
                    if key == "Brilho do fundo":
                        percentage = max(35, percentage)
                    self.options[key] = percentage
                    self.save_config()
                    return True

            for rect, key in self.button_rects:
                if event.button == 1 and rect.collidepoint(mouse_pos):
                    self.options[key] = not self.options[key]
                    self.save_config()
                    if key == "Verificar atualizações":
                        self.precisa_reiniciar = self.options[key] != self.valor_original_update
                    elif key == "Ativar Mods":
                        self.precisa_reiniciar = self.options[key] != self.valor_original_mods
                    return True

            return True

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging_slider  = None
                self.dragging_start_x = None
                self.is_scrolling     = False

        elif event.type == pygame.MOUSEMOTION:
            if self.is_scrolling and self.scrollbar_rect and self.max_scroll > 0:
                mouse_y            = event.pos[1]
                scroll_area_height = self.height - 100
                thumb_height       = self.scrollbar_rect.height
                min_y              = 80
                max_y              = min_y + scroll_area_height - thumb_height
                new_thumb_y        = max(min_y, min(max_y, mouse_y - self.scroll_drag_start))
                scroll_ratio       = (new_thumb_y - min_y) / max(1, scroll_area_height - thumb_height)
                self.scroll_y      = int(scroll_ratio * self.max_scroll)
                return True

            if self.dragging_slider:
                for track_rect, handle_rect, key in self.slider_rects:
                    if key == self.dragging_slider:
                        relative_x = event.pos[0] - track_rect.left
                        percentage = max(0, min(100, int((relative_x / track_rect.width) * 100)))
                        if key == "Brilho do fundo":
                            percentage = max(35, percentage)
                        self.options[key] = percentage
                        self.save_config()
                        return True

        return False

    # ── visibilidade ──────────────────────────────────────────────────────────

    def show(self):
        self.visible = True
        self.scroll_y = 0
        self.valor_original_update = self.options.get("Verificar atualizações", True)
        self.valor_original_mods   = self.options.get("Ativar Mods", False)
        self.precisa_reiniciar     = False

    def hide(self):
        self.visible  = False
        self.scroll_y = 0

    def toggle(self):
        if self.visible:
            self.hide()
        else:
            self.show()

    # ── getters ───────────────────────────────────────────────────────────────

    def get_click_settings(self):
        return {
            "left_click":   self.options.get("Clique Esquerdo", True),
            "right_click":  self.options.get("Clique Direito", True),
            "middle_click": self.options.get("Clique Botão do Meio", False),
            "mouse_scroll": self.options.get("Rolagem do Mouse", False)
        }

    def get_volume_settings(self):
        return {
            "achievement_volume": self.options.get("Volume Conquistas", 100) / 100.0,
            "minievent_volume":   self.options.get("Volume Mini Evento", 100) / 100.0
        }

    def get_brightness_settings(self):
        brightness = self.options.get("Brilho do fundo", 100)
        return max(35, brightness) / 100.0