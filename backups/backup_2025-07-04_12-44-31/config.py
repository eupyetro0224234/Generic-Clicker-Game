import pygame
import json
import os

class FullSettingsMenu:
    def __init__(self, screen, window_width, window_height):
        self.screen = screen
        self.width = window_width
        self.height = window_height

        self.bg_color = (180, 210, 255)
        self.text_color = (40, 40, 60)
        self.option_height = 42
        self.option_radius = 12
        self.padding_x = 12
        self.padding_y = 12
        self.spacing = 14

        # Pasta e arquivo config.json
        localappdata = os.getenv("LOCALAPPDATA")
        self.assets_folder = os.path.join(localappdata, ".assests")
        os.makedirs(self.assets_folder, exist_ok=True)
        self.config_path = os.path.join(self.assets_folder, "config.json")

        # Configurações padrões iniciais
        self.default_config = {
            "Clique Esquerdo": True,
            "Clique Direito": True,
            "Clique Botão do Meio": True,
            "Scroll Mouse": True,
            "Ativar Mods": False,
            "Ativar Texturas": False,
            "Controles": True
        }

        self.visible = False
        self.options = {}
        self.load_config()

        # Preparar fonte
        self.font = pygame.font.SysFont(None, 28)

    def load_config(self):
        if os.path.isfile(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for k, v in self.default_config.items():
                        self.options[k] = data.get(k, v)
            except Exception as e:
                print("Erro ao carregar config.json:", e)
                self.options = self.default_config.copy()
        else:
            self.options = self.default_config.copy()
            self.save_config()

    def save_config(self):
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.options, f, indent=4)
        except Exception as e:
            print("Erro ao salvar config.json:", e)

    def get_option(self, key):
        return self.options.get(key, False)

    def set_option(self, key, value):
        self.options[key] = bool(value)
        self.save_config()

    def is_click_allowed(self, button):
        """
        Verifica se determinado botão do mouse está habilitado para contar pontos.
        """
        if button == 1:  # Esquerdo
            return self.get_option("Clique Esquerdo")
        elif button == 3:  # Direito
            return self.get_option("Clique Direito")
        elif button == 2:  # Botão do Meio
            return self.get_option("Clique Botão do Meio")
        elif button == 4 or button == 5:  # Scroll
            return self.get_option("Scroll Mouse")
        return False

    def draw(self):
        if not self.visible:
            return

        self.screen.fill(self.bg_color)

        y = self.padding_y
        x = self.padding_x

        title_font = pygame.font.SysFont(None, 36)
        title_surf = title_font.render("Configurações", True, self.text_color)
        self.screen.blit(title_surf, (x, y))
        y += title_surf.get_height() + 20

        for key in self.options:
            val = self.options[key]
            option_rect = pygame.Rect(x, y, self.width - 2 * x, self.option_height)
            pygame.draw.rect(self.screen, (255, 255, 255), option_rect, border_radius=self.option_radius)
            pygame.draw.rect(self.screen, (150, 150, 150), option_rect, width=2, border_radius=self.option_radius)

            text_surf = self.font.render(key, True, self.text_color)
            text_rect = text_surf.get_rect(midleft=(x + 12, option_rect.centery))
            self.screen.blit(text_surf, text_rect)

            val_text = "Ativado" if val else "Desativado"
            val_surf = self.font.render(val_text, True, self.text_color)
            val_rect = val_surf.get_rect(midright=(self.width - x - 20, option_rect.centery))
            self.screen.blit(val_surf, val_rect)

            y += self.option_height + self.spacing

    def handle_event(self, event):
        if not self.visible:
            return False

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.visible = False
            return True

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            x = self.padding_x
            y = self.padding_y + 36 + 20  # espaço do título

            for key in self.options:
                option_rect = pygame.Rect(x, y, self.width - 2 * x, self.option_height)
                if option_rect.collidepoint(mouse_pos):
                    self.options[key] = not self.options[key]
                    self.save_config()
                    return True
                y += self.option_height + self.spacing

        return False
