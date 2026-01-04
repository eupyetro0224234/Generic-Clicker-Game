import pygame, json, os, sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class FullSettingsMenu:
    def __init__(self, screen, window_width, window_height):
        self.screen = screen
        self.width = window_width
        self.height = window_height

        self.bg_color = (255, 182, 193)
        self.text_color = (47, 24, 63)
        self.option_height = 60
        self.option_radius = 15
        self.padding_x = 20
        self.padding_y = 20
        self.spacing_x = 20
        self.spacing_y = 20
        self.options_per_row = 2

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
            "Mostrar sequência": True,  # Alterado de "Mostrar tempo de jogo" para "Mostrar sequência" e padrão True
            "Volume Conquistas": 100,
            "Volume Mini Evento": 100,
            "Brilho do fundo": 100
        }

        self.visible = False
        self.options = {}
        self.load_config()

        self.valor_original_update = self.options.get("Verificar atualizações", True)
        self.precisa_reiniciar = False

        self.title_font = pygame.font.SysFont(None, 42)
        self.font = pygame.font.SysFont(None, 32)
        self.emoji_font = pygame.font.SysFont("segoeuiemoji", 28)
        
        self.hovered_option = None
        self.button_rects = []
        self.slider_rects = []
        
        self.console_ativo = False
        
        # Botão de fechar igual ao do primeiro código
        self.close_button_rect = pygame.Rect(self.width - 80, 15, 40, 40)
        try:
            close_image_path = resource_path("game_assets/close.png")
            if not os.path.exists(close_image_path):
                close_image_path = os.path.join("..", "game_assets", "close.png")
            self.close_image = pygame.image.load(close_image_path).convert_alpha()
            # Tamanho reduzido para 40x40 pixels
            target_size = (40, 40)
            self.close_image = pygame.transform.smoothscale(self.close_image, target_size)
        except Exception:
            self.close_image = None
            
        self.search_button_rect = pygame.Rect(25, 25, 40, 40)
        
        self.dragging_slider = None
        self.dragging_start_x = None
        
        # Referência ao menu de estatísticas
        self.statistics_menu = None

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
        except Exception as e:
            self.options = self.default_config.copy()

    def save_config(self):
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.options, f, indent=4, ensure_ascii=False)
        except Exception as e:
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

    def draw_section_title(self, title, x, y):
        box_width = self.width - 2 * x
        box_height = self.option_height
        box_rect = pygame.Rect(x, y, box_width, box_height)

        azul_claro = (200, 190, 255, 230)
        pygame.draw.rect(self.screen, azul_claro, box_rect, border_radius=self.option_radius)
        pygame.draw.rect(self.screen, (150, 150, 150), box_rect, width=2, border_radius=self.option_radius)

        title_surf = self.title_font.render(title, True, self.text_color)
        title_rect = title_surf.get_rect(center=box_rect.center)
        self.screen.blit(title_surf, title_rect)

        return y + box_height + self.spacing_y

    def draw_slider_option(self, key, x, y, width):
        mouse_pos = pygame.mouse.get_pos()
        
        container_height = self.option_height
        container_rect = pygame.Rect(x, y, width, container_height)
        
        shadow_surface = pygame.Surface((width + 6, container_height + 6), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, (0, 0, 0, 20), (0, 0, width + 6, container_height + 6), border_radius=15)
        self.screen.blit(shadow_surface, (x - 3, y - 3))
        
        color = (220, 235, 255) if container_rect.collidepoint(mouse_pos) else (255, 255, 255)
        pygame.draw.rect(self.screen, color, container_rect, border_radius=self.option_radius)
        pygame.draw.rect(self.screen, (150, 150, 150), container_rect, width=2, border_radius=self.option_radius)
        
        text_surf = self.font.render(key, True, self.text_color)
        text_rect = text_surf.get_rect(midleft=(x + 20, y + container_height // 2))
        self.screen.blit(text_surf, text_rect)
        
        slider_width = 200
        slider_height = 20
        slider_x = x + width - slider_width - 30
        slider_y = y + (container_height - slider_height) // 2
        
        track_rect = pygame.Rect(slider_x, slider_y, slider_width, slider_height)
        pygame.draw.rect(self.screen, (200, 200, 200), track_rect, border_radius=10)
        pygame.draw.rect(self.screen, (100, 100, 100), track_rect, width=1, border_radius=10)
        
        current_value = self.options.get(key, 100)
        
        if key == "Brilho do fundo":
            display_value = max(35, current_value)
            slider_pos = slider_x + int((display_value / 100) * slider_width)
        else:
            slider_pos = slider_x + int((current_value / 100) * slider_width)
            
        handle_rect = pygame.Rect(slider_pos - 6, slider_y - 3, 12, slider_height + 6)
        
        handle_color = (100, 150, 255) if (handle_rect.collidepoint(mouse_pos) or self.dragging_slider == key) else (70, 130, 230)
        pygame.draw.rect(self.screen, handle_color, handle_rect, border_radius=6)
        pygame.draw.rect(self.screen, (50, 100, 180), handle_rect, width=1, border_radius=6)
        
        if key == "Brilho do fundo":
            display_value = max(35, current_value)
            if current_value < 35:
                value_text = "35% (mínimo)"
            else:
                value_text = f"{display_value}%"
        else:
            value_text = f"{current_value}%"
            
        value_surf = self.font.render(value_text, True, self.text_color)
        value_rect = value_surf.get_rect(midright=(slider_x - 10, y + container_height // 2))
        self.screen.blit(value_surf, value_rect)
        
        self.slider_rects.append((track_rect, handle_rect, key))
        
        return container_rect.bottom + self.spacing_y

    def draw_options(self, keys, x, y):
        mouse_pos = pygame.mouse.get_pos()
        button_width = (self.width - 2 * x - (self.options_per_row - 1) * self.spacing_x) // self.options_per_row

        for i, key in enumerate(keys):
            val = self.options.get(key, False)
            row = i // self.options_per_row
            col = i % self.options_per_row

            option_x = x + col * (button_width + self.spacing_x)
            option_y = y + row * (self.option_height + self.spacing_y)

            option_rect = pygame.Rect(option_x, option_y, button_width, self.option_height)
            self.button_rects.append((option_rect, key))

            shadow_surface = pygame.Surface((button_width + 6, self.option_height + 6), pygame.SRCALPHA)
            pygame.draw.rect(shadow_surface, (0, 0, 0, 20), (0, 0, button_width + 6, self.option_height + 6), border_radius=15)
            self.screen.blit(shadow_surface, (option_x - 3, option_y - 3))

            color = (220, 235, 255) if option_rect.collidepoint(mouse_pos) else (255, 255, 255)

            pygame.draw.rect(self.screen, color, option_rect, border_radius=self.option_radius)
            pygame.draw.rect(self.screen, (150, 150, 150), option_rect, width=2, border_radius=self.option_radius)

            text_surf = self.font.render(key, True, self.text_color)
            text_rect = text_surf.get_rect(midleft=(option_x + 20, option_rect.centery))
            self.screen.blit(text_surf, text_rect)

            val_text = "Ativado" if val else "Desativado"
            val_surf = self.font.render(val_text, True, self.text_color)
            val_rect = val_surf.get_rect(midright=(option_x + button_width - 20, option_rect.centery))
            self.screen.blit(val_surf, val_rect)

        total_rows = (len(keys) + self.options_per_row - 1) // self.options_per_row
        return y + total_rows * (self.option_height + self.spacing_y)

    def draw_close_button(self):
        """Desenha o botão de fechar igual ao do primeiro código"""
        if self.close_image:
            image_rect = self.close_image.get_rect(center=self.close_button_rect.center)
            self.screen.blit(self.close_image, image_rect)
        else:
            # Fallback se a imagem não carregar
            pygame.draw.rect(self.screen, (255, 100, 100), self.close_button_rect, border_radius=6)
            center_x, center_y = self.close_button_rect.center
            line_length = 15
            pygame.draw.line(self.screen, (255, 255, 255), (center_x - line_length, center_y - line_length),
                            (center_x + line_length, center_y + line_length), 2)
            pygame.draw.line(self.screen, (255, 255, 255), (center_x - line_length, center_y + line_length),
                            (center_x + line_length, center_y - line_length), 2)

    def draw(self):
        if not self.visible:
            return

        self.button_rects = []
        self.slider_rects = []

        self.screen.fill(self.bg_color)

        x = self.padding_x
        y = self.padding_y

        title_font = pygame.font.SysFont(None, 48)
        title_surf = title_font.render("Configurações", True, self.text_color)
        title_rect = title_surf.get_rect(center=(self.width // 2, 35))
        self.screen.blit(title_surf, title_rect)

        # Desenhar botão de fechar igual ao do primeiro código
        self.draw_close_button()

        pygame.draw.rect(self.screen, (120, 180, 255), self.search_button_rect, border_radius=20)
        pygame.draw.rect(self.screen, (60, 120, 180), self.search_button_rect, 2, border_radius=20)
        
        search_surf = self.emoji_font.render("🔍", True, (255, 255, 255))
        search_surf = pygame.transform.scale(search_surf, (24, 24))
        search_rect = search_surf.get_rect(center=self.search_button_rect.center)
        self.screen.blit(search_surf, search_rect)

        y = 90

        y = self.draw_section_title("Controles", x, y)
        controles_keys = [
            "Clique Esquerdo",
            "Clique Direito",
            "Clique Botão do Meio",
            "Rolagem do Mouse"
        ]
        y = self.draw_options(controles_keys, x, y)

        y += 40

        y = self.draw_section_title("Som", x, y)
        slider_width = self.width - 2 * x
        
        y = self.draw_slider_option("Volume Conquistas", x, y, slider_width)
        
        y = self.draw_slider_option("Volume Mini Evento", x, y, slider_width)

        y += 40

        y = self.draw_section_title("Outros", x, y)
        slider_width = self.width - 2 * x
        
        y = self.draw_slider_option("Brilho do fundo", x, y, slider_width)
        
        y += 20
        
        outros_keys = [
            "Ativar Mods",
            "Verificar atualizações",
            "Mostrar descrição de conquistas bloqueadas",
            "Menu vertical",
            "Mostrar sequência"  # Alterado de "Mostrar tempo de jogo" para "Mostrar sequência"
        ]

        if self.console_ativo and "Manter console aberto" in self.options:
            if "Manter console aberto" in outros_keys:
                outros_keys.remove("Manter console aberto")
            outros_keys.append("Manter console aberto")

        self.draw_options(outros_keys, x, y)

        if self.precisa_reiniciar:
            restart_font = pygame.font.SysFont(None, 28)
            restart_text = restart_font.render("Reinicie o jogo para aplicar as mudanças de atualização", True, (200, 0, 0))
            restart_rect = restart_text.get_rect(center=(self.width // 2, self.height - 40))
            self.screen.blit(restart_text, restart_rect)

    def handle_event(self, event):
        if not self.visible:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.visible = False
                return True
            return True

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            
            # Verificar clique no botão de fechar (apenas botão esquerdo)
            if event.button == 1 and self.close_button_rect.collidepoint(mouse_pos):
                self.visible = False
                return True

            # Modificação: abrir menu de estatísticas ao clicar na lupa
            if event.button == 1 and self.search_button_rect.collidepoint(mouse_pos):
                if self.statistics_menu:
                    self.statistics_menu.show()
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
                        if self.options[key] != self.valor_original_update:
                            self.precisa_reiniciar = True
                        else:
                            self.precisa_reiniciar = False
                    return True

            return True

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging_slider = None
                self.dragging_start_x = None

        elif event.type == pygame.MOUSEMOTION and self.dragging_slider:
            for track_rect, handle_rect, key in self.slider_rects:
                if key == self.dragging_slider:
                    mouse_pos = event.pos
                    relative_x = mouse_pos[0] - track_rect.left
                    percentage = max(0, min(100, int((relative_x / track_rect.width) * 100)))
                    
                    if key == "Brilho do fundo":
                        percentage = max(35, percentage)
                    
                    self.options[key] = percentage
                    self.save_config()
                    return True

        return False

    def show(self):
        self.visible = True
        self.valor_original_update = self.options.get("Verificar atualizações", True)
        self.precisa_reiniciar = False

    def hide(self):
        self.visible = False

    def toggle(self):
        if self.visible:
            self.hide()
        else:
            self.show()

    def get_click_settings(self):
        return {
            "left_click": self.options.get("Clique Esquerdo", True),
            "right_click": self.options.get("Clique Direito", True),
            "middle_click": self.options.get("Clique Botão do Meio", False),
            "mouse_scroll": self.options.get("Rolagem do Mouse", False)
        }

    def get_volume_settings(self):
        return {
            "achievement_volume": self.options.get("Volume Conquistas", 100) / 100.0,
            "minievent_volume": self.options.get("Volume Mini Evento", 100) / 100.0
        }

    def get_brightness_settings(self):
        brightness = self.options.get("Brilho do fundo", 100)
        return max(35, brightness) / 100.0