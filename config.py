import pygame
import json
import os

class FullSettingsMenu:
    def __init__(self, screen, window_width, window_height):
        self.screen = screen
        self.width = window_width
        self.height = window_height

        self.bg_color = (180, 210, 255, 220)
        self.text_color = (40, 40, 60)
        self.option_height = 44
        self.option_radius = 12
        self.padding_x = 14
        self.padding_y = 14
        self.spacing_x = 14
        self.spacing_y = 14
        self.options_per_row = 2

        localappdata = os.getenv("LOCALAPPDATA")
        self.assets_folder = os.path.join(localappdata, ".assets")
        os.makedirs(self.assets_folder, exist_ok=True)
        self.config_path = os.path.join(self.assets_folder, "config.json")

        self.default_config = {
            "Clique Esquerdo": True,
            "Clique Direito": True,
            "Clique Botão do Meio": True,
            "Rolagem do Mouse": True,
            "Ativar Mods": False,
            "Ativar Texturas": False,
            "Verificar atualizações": True,
            "Mostrar conquistas ocultas": False,
            "Pular o loading": False,
            "Menu vertical": False
        }

        self.visible = False
        self.options = {}
        self.load_config()

        self.valor_original_update = self.options.get("Verificar atualizações", True)
        self.precisa_reiniciar = False

        self.title_font = pygame.font.SysFont(None, 36)
        self.font = pygame.font.SysFont(None, 28)

        self.hovered_option = None
        self.button_rects = []
        
        self.console_ativo = False
        self.close_button_rect = None
        self.close_button_hover = False

    def is_click_allowed(self, button):
        if button == 1:
            return self.options.get("Clique Esquerdo", True)
        elif button == 2:
            return self.options.get("Clique Botão do Meio", True)
        elif button == 3:
            return self.options.get("Clique Direito", True)
        elif button in (4, 5):
            return self.options.get("Rolagem do Mouse", True)
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
                json.dump(self.options, f, indent=4)
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

    def draw_section_title(self, title, x, y):
        box_width = self.width - 2 * x
        box_height = self.option_height
        box_rect = pygame.Rect(x, y, box_width, box_height)

        pink = (255, 182, 193)
        pygame.draw.rect(self.screen, pink, box_rect, border_radius=self.option_radius)
        pygame.draw.rect(self.screen, (150, 150, 150), box_rect, width=2, border_radius=self.option_radius)

        title_surf = self.title_font.render(title, True, self.text_color)
        title_rect = title_surf.get_rect(center=box_rect.center)
        self.screen.blit(title_surf, title_rect)

        return y + box_height + self.spacing_y

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

            color = (220, 235, 255) if option_rect.collidepoint(mouse_pos) else (255, 255, 255)

            pygame.draw.rect(self.screen, color, option_rect, border_radius=self.option_radius)
            pygame.draw.rect(self.screen, (150, 150, 150), option_rect, width=2, border_radius=self.option_radius)

            text_surf = self.font.render(key, True, self.text_color)
            text_rect = text_surf.get_rect(midleft=(option_x + 14, option_rect.centery))
            self.screen.blit(text_surf, text_rect)

            val_text = "Ativado" if val else "Desativado"
            val_surf = self.font.render(val_text, True, self.text_color)
            val_rect = val_surf.get_rect(midright=(option_x + button_width - 14, option_rect.centery))
            self.screen.blit(val_surf, val_rect)

        total_rows = (len(keys) + self.options_per_row - 1) // self.options_per_row
        return y + total_rows * (self.option_height + self.spacing_y)

    def draw_close_button(self):
        """Desenha o botão de fechar estilizado no canto superior direito"""
        button_size = 36
        margin = 20
        self.close_button_rect = pygame.Rect(
            self.width - button_size - margin, 
            margin, 
            button_size, 
            button_size
        )
        
        mouse_pos = pygame.mouse.get_pos()
        self.close_button_hover = self.close_button_rect.collidepoint(mouse_pos)
        
        button_color = (255, 80, 80) if self.close_button_hover else (255, 120, 120)
        pygame.draw.rect(self.screen, button_color, self.close_button_rect, border_radius=button_size//2)
        
        border_color = (200, 40, 40) if self.close_button_hover else (180, 60, 60)
        pygame.draw.rect(self.screen, border_color, self.close_button_rect, width=2, border_radius=button_size//2)
        
        if self.close_button_hover:
            shadow = pygame.Surface((button_size, button_size), pygame.SRCALPHA)
            pygame.draw.rect(shadow, (0, 0, 0, 30), (0, 0, button_size, button_size), border_radius=button_size//2)
            self.screen.blit(shadow, (self.close_button_rect.x, self.close_button_rect.y))
        
        x_size = 20
        line_width = 3
        center_x = self.close_button_rect.centerx
        center_y = self.close_button_rect.centery
        
        pygame.draw.line(self.screen, (255, 255, 255), 
                        (center_x - x_size//2, center_y - x_size//2),
                        (center_x + x_size//2, center_y + x_size//2), 
                        line_width)
        pygame.draw.line(self.screen, (255, 255, 255), 
                        (center_x + x_size//2, center_y - x_size//2),
                        (center_x - x_size//2, center_y + x_size//2), 
                        line_width)

    def draw(self):
        if not self.visible:
            return

        self.button_rects = []

        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(overlay, self.bg_color, (0, 0, self.width, self.height), border_radius=self.option_radius)
        self.screen.blit(overlay, (0, 0))

        self.draw_close_button()

        x = self.padding_x
        y = self.padding_y + 50

        title_surf = self.title_font.render("Configurações", True, self.text_color)
        title_rect = title_surf.get_rect(center=(self.width // 2, y + title_surf.get_height() // 2))
        self.screen.blit(title_surf, title_rect)

        y += title_surf.get_height() + 40

        y = self.draw_section_title("Controles", x, y)
        controles_keys = [
            "Clique Esquerdo",
            "Clique Direito",
            "Clique Botão do Meio",
            "Rolagem do Mouse"
        ]
        y = self.draw_options(controles_keys, x, y)

        y += 30

        y = self.draw_section_title("Outros", x, y)
        outros_keys = [
            "Ativar Mods",
            "Verificar atualizações",
            "Mostrar conquistas ocultas",
            "Pular o loading",
            "Menu vertical"
        ]

        if self.console_ativo and "Manter console aberto" in self.options:
            outros_keys.append("Manter console aberto")

        self.draw_options(outros_keys, x, y)

    def handle_event(self, event):
        if not self.visible:
            return False

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.visible = False
            return True

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos

            if self.close_button_rect and self.close_button_rect.collidepoint(mouse_pos):
                self.visible = False
                return True

            for rect, key in self.button_rects:
                if rect.collidepoint(mouse_pos):
                    self.options[key] = not self.options[key]
                    self.save_config()

                    if key == "Verificar atualizações":
                        if self.options[key] != self.valor_original_update:
                            self.precisa_reiniciar = True
                        else:
                            self.precisa_reiniciar = False
                    return True

            return True

        return False