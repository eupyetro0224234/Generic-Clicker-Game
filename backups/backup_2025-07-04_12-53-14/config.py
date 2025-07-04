import pygame
import json
import os

class FullSettingsMenu:
    def __init__(self, screen, window_width, window_height):
        self.screen = screen
        self.width = window_width
        self.height = window_height

        self.bg_color = (200, 220, 255)  # Fundo azul clarinho
        self.text_color = (40, 40, 60)
        self.option_height = 48
        self.option_radius = 14
        self.padding_x = 24
        self.padding_y = 24
        self.spacing = 18
        self.title_box_color = (150, 180, 230)  # Cor da caixinha dos títulos

        # Pasta e arquivo config.json
        localappdata = os.getenv("LOCALAPPDATA")
        self.assets_folder = os.path.join(localappdata, ".assests")
        os.makedirs(self.assets_folder, exist_ok=True)
        self.config_path = os.path.join(self.assets_folder, "config.json")

        # Configurações padrões iniciais (sem 'Controles')
        self.default_config = {
            "Clique Esquerdo": True,
            "Clique Direito": True,
            "Clique Botão do Meio": True,
            "Scroll Mouse": True,
            "Ativar Mods": False,
            "Ativar Texturas": False
        }

        self.visible = False
        self.options = {}
        self.load_config()

        # Preparar fonte
        self.font = pygame.font.SysFont(None, 30)
        self.title_font = pygame.font.SysFont(None, 38, bold=True)

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

        # Fundo tela cheia
        self.screen.fill(self.bg_color)

        x = self.padding_x
        y = self.padding_y

        # Título principal centralizado no topo
        title_surf = self.title_font.render("Configurações", True, self.text_color)
        title_rect = title_surf.get_rect(center=(self.width // 2, y + title_surf.get_height() // 2))
        self.screen.blit(title_surf, title_rect)
        y += title_surf.get_height() + 40

        # Desenhar seção "Controles"
        y = self.draw_section("Controles", x, y)

        controles_keys = [
            "Clique Esquerdo",
            "Clique Direito",
            "Clique Botão do Meio",
            "Scroll Mouse"
        ]
        y = self.draw_options(controles_keys, x, y)

        # Espaço extra entre seções
        y += 30

        # Desenhar seção "Outros"
        y = self.draw_section("Outros", x, y)

        outros_keys = [
            "Ativar Mods",
            "Ativar Texturas"
        ]
        y = self.draw_options(outros_keys, x, y)

    def draw_section(self, title, x, y):
        # Caixinha colorida para título da seção, alinhada mais à esquerda (menos padding)
        box_width = 220
        box_height = 42
        box_rect = pygame.Rect(x - 8, y, box_width, box_height)
        pygame.draw.rect(self.screen, self.title_box_color, box_rect, border_radius=10)

        title_surf = self.font.render(title, True, (15, 15, 40))
        title_rect = title_surf.get_rect(midleft=(x + 4, y + box_height // 2))
        self.screen.blit(title_surf, title_rect)

        return y + box_height + 12

    def draw_options(self, keys, x, y):
        for key in keys:
            val = self.options.get(key, False)

            # Ajustar o texto para as opções que precisam da explicação entre parênteses
            display_key = key
            if key == "Clique Botão do Meio":
                display_key += " (clique da rodinha do mouse)"
            elif key == "Scroll Mouse":
                display_key += " (rodinha do mouse)"

            option_rect = pygame.Rect(x, y, self.width - 2 * x, self.option_height)
            # Sombra leve
            shadow_rect = option_rect.move(4, 4)
            shadow_surf = pygame.Surface((option_rect.width, option_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(shadow_surf, (0, 0, 0, 40), shadow_surf.get_rect(), border_radius=self.option_radius)
            self.screen.blit(shadow_surf, shadow_rect.topleft)
            # Fundo branco e borda
            pygame.draw.rect(self.screen, (255, 255, 255), option_rect, border_radius=self.option_radius)
            pygame.draw.rect(self.screen, (150, 150, 150), option_rect, width=2, border_radius=self.option_radius)

            # Texto da opção
            text_surf = self.font.render(display_key, True, self.text_color)
            text_rect = text_surf.get_rect(midleft=(x + 16, option_rect.centery))
            self.screen.blit(text_surf, text_rect)

            # Texto do valor ativado/desativado
            val_text = "Ativado" if val else "Desativado"
            val_color = (30, 140, 30) if val else (180, 30, 30)
            val_surf = self.font.render(val_text, True, val_color)
            val_rect = val_surf.get_rect(midright=(self.width - x - 20, option_rect.centery))
            self.screen.blit(val_surf, val_rect)

            y += self.option_height + self.spacing

        return y

    def handle_event(self, event):
        if not self.visible:
            return False

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.visible = False
            return True

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            x = self.padding_x
            y = self.padding_y + 38 + 40  # espaço do título principal

            # Posição inicial para "Controles"
            y = self.handle_options_click([
                "Clique Esquerdo",
                "Clique Direito",
                "Clique Botão do Meio",
                "Scroll Mouse"
            ], mouse_pos, x, y)

            y += 30  # Espaço extra entre seções

            # Posição inicial para "Outros"
            y = self.handle_options_click([
                "Ativar Mods",
                "Ativar Texturas"
            ], mouse_pos, x, y)

            return True

        return False

    def handle_options_click(self, keys, mouse_pos, x, y):
        for key in keys:
            option_rect = pygame.Rect(x, y, self.width - 2 * x, self.option_height)
            if option_rect.collidepoint(mouse_pos):
                self.options[key] = not self.options[key]
                self.save_config()
                # Depois de um clique válido, retorna para parar mais checagens
                return y + self.option_height + self.spacing
            y += self.option_height + self.spacing
        return y
