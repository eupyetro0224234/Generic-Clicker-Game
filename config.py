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
            "Verificar atualizações": True    # <-- NOVA OPÇÃO
        }

        self.visible = False
        self.options = {}
        self.precisa_reiniciar = False  # Flag para avisar reinício ao mudar opção
        self.load_config()

        self.title_font = pygame.font.SysFont(None, 36)
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
        if button == 1:
            return self.get_option("Clique Esquerdo")
        elif button == 3:
            return self.get_option("Clique Direito")
        elif button == 2:
            return self.get_option("Clique Botão do Meio")
        elif button == 4 or button == 5:
            return self.get_option("Rolagem do Mouse")
        return False

    def draw_section_title(self, title, x, y):
        box_width = self.width - 2 * x
        box_height = self.option_height
        box_rect = pygame.Rect(x, y, box_width, box_height)

        pink = (255, 182, 193)  # LightPink
        pygame.draw.rect(self.screen, pink, box_rect, border_radius=self.option_radius)
        pygame.draw.rect(self.screen, (150, 150, 150), box_rect, width=2, border_radius=self.option_radius)

        title_surf = self.title_font.render(title, True, self.text_color)
        title_rect = title_surf.get_rect(center=box_rect.center)
        self.screen.blit(title_surf, title_rect)

        return y + box_height + self.spacing

    def draw_options(self, keys, x, y):
        for key in keys:
            val = self.options.get(key, False)

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

        return y

    def draw(self):
        if not self.visible:
            return

        self.screen.fill(self.bg_color)

        x = self.padding_x
        y = self.padding_y

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
            "Ativar Texturas",
            "Verificar atualizações"  # <-- adicionada na sessão "Outros"
        ]
        y = self.draw_options(outros_keys, x, y)

    def handle_event(self, event):
        if not self.visible:
            return False

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.visible = False
            return True

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            x = self.padding_x

            y = self.padding_y
            title_surf = self.title_font.render("Configurações", True, self.text_color)
            y += title_surf.get_height() + 40

            y = self._handle_options_click([
                "Clique Esquerdo",
                "Clique Direito",
                "Clique Botão do Meio",
                "Rolagem do Mouse"
            ], mouse_pos, x, y + self.option_height + self.spacing)

            y += 30

            y = self._handle_options_click([
                "Ativar Mods",
                "Ativar Texturas",
                "Verificar atualizações"  # <-- clicável também
            ], mouse_pos, x, y + self.option_height + self.spacing)

            return True

        return False

    def _handle_options_click(self, keys, mouse_pos, x, y):
        for key in keys:
            option_rect = pygame.Rect(x, y, self.width - 2 * x, self.option_height)
            if option_rect.collidepoint(mouse_pos):
                # Se mudar a opção "Verificar atualizações", sinaliza que precisa reiniciar
                if key == "Verificar atualizações":
                    self.precisa_reiniciar = True
                self.options[key] = not self.options[key]
                self.save_config()
                break
            y += self.option_height + self.spacing
        return y
