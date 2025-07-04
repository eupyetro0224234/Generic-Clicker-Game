import pygame
import os
import urllib.request
from controles import ControlsMenu  # Importa menu controles

class ConfigMenu:
    def __init__(self, screen, window_width, window_height):
        self.screen = screen
        self.font = pygame.font.SysFont(None, 24)
        self.bg_color = (180, 210, 255)
        self.option_color = (255, 255, 255)
        self.option_border = (200, 220, 250)
        self.text_color = (40, 40, 60)

        self.option_height = 38
        self.option_radius = 10
        self.padding_x = 6
        self.spacing = 5

        self.is_open = False
        self.animation_progress = 0.0
        self.animation_speed = 0.12

        # Pasta para assets
        localappdata = os.getenv("LOCALAPPDATA")
        self.assets_folder = os.path.join(localappdata, ".assests")
        os.makedirs(self.assets_folder, exist_ok=True)

        self.icon_url = "https://i.postimg.cc/hGf3VRqY/image-removebg-preview-5.png"
        self.icon_path = os.path.join(self.assets_folder, "config_icon.png")

        # Baixa ícone se não existir
        if not os.path.isfile(self.icon_path):
            try:
                urllib.request.urlretrieve(self.icon_url, self.icon_path)
            except Exception as e:
                print("Erro ao baixar ícone de configurações:", e)

        # Carrega ícone
        self.icon_image = None
        try:
            self.icon_image = pygame.image.load(self.icon_path).convert_alpha()
            self.icon_image = pygame.transform.smoothscale(self.icon_image, (42, 42))
        except Exception as e:
            print("Erro ao carregar ícone:", e)

        self.icon_rect = self.icon_image.get_rect() if self.icon_image else pygame.Rect(0, 0, 48, 48)
        self.icon_rect.topright = (window_width - 6, 6)

        self.options = ["Configurações", "Volume: [•••••]", "Tema: Claro", "Controles"]

        self.max_height = len(self.options) * (self.option_height + self.spacing)

        # Cria menu controles
        self.controls_menu = ControlsMenu(screen, window_width, window_height)

    def draw_icon(self):
        if self.icon_image:
            self.screen.blit(self.icon_image, self.icon_rect)
        else:
            pygame.draw.rect(self.screen, (70, 130, 180), self.icon_rect)

    def update_animation(self):
        if self.is_open:
            self.animation_progress = min(1.0, self.animation_progress + self.animation_speed)
        else:
            self.animation_progress = max(0.0, self.animation_progress - self.animation_speed)

    def draw_menu(self):
        self.update_animation()
        if self.animation_progress <= 0 or self.controls_menu.visible:
            return

        width = 180
        vertical_padding = 6
        full_height = len(self.options) * (self.option_height + self.spacing) - self.spacing + vertical_padding * 2
        height = int(full_height * self.animation_progress)

        margin_right = 4
        x = self.screen.get_width() - width - margin_right
        y = self.icon_rect.bottom + 6

        menu_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(menu_surface, self.bg_color, (0, 0, width, height), border_radius=12)

        for i, option in enumerate(self.options):
            oy = vertical_padding + i * (self.option_height + self.spacing)
            if oy + self.option_height > height:
                break

            option_rect = pygame.Rect(
                self.padding_x,
                oy,
                width - self.padding_x * 2,
                self.option_height
            )
            pygame.draw.rect(menu_surface, self.option_color, option_rect, border_radius=self.option_radius)
            pygame.draw.rect(menu_surface, self.option_border, option_rect, width=1, border_radius=self.option_radius)

            text_surf = self.font.render(option, True, self.text_color)
            text_rect = text_surf.get_rect(center=option_rect.center)
            menu_surface.blit(text_surf, text_rect)

        self.screen.blit(menu_surface, (x, y))

    def handle_event(self, event):
        # Passa evento para o menu controles, se aberto
        if self.controls_menu.visible:
            if self.controls_menu.handle_event(event):
                return True

        if event.type == pygame.MOUSEBUTTONDOWN:
            # Clicar no ícone abre/fecha menu pequeno
            if self.icon_rect.collidepoint(event.pos):
                self.is_open = not self.is_open
                return True

            # Se menu aberto, verificar clique nas opções
            if self.is_open:
                width = 180
                vertical_padding = 6
                full_height = len(self.options) * (self.option_height + self.spacing) - self.spacing + vertical_padding * 2
                height = int(full_height * self.animation_progress)
                margin_right = 4
                x = self.screen.get_width() - width - margin_right
                y = self.icon_rect.bottom + 6
                rect = pygame.Rect(x, y, width, height)

                if rect.collidepoint(event.pos):
                    relative_y = event.pos[1] - y - vertical_padding
                    index = relative_y // (self.option_height + self.spacing)
                    if 0 <= index < len(self.options):
                        selected = self.options[index]
                        if selected == "Controles":
                            # Toggle menu controles
                            self.is_open = False
                            self.controls_menu.visible = not self.controls_menu.visible
                        elif selected == "Configurações":
                            # Aqui você pode abrir o menu de configurações fullscreen se quiser
                            self.is_open = False
                    return True
                else:
                    # Clique fora fecha menu pequeno, mas não fecha controles
                    self.is_open = False
                    return True

        elif event.type == pygame.KEYDOWN:
            # ESC fecha menus abertos (controles ou pequeno)
            if event.key == pygame.K_ESCAPE:
                if self.controls_menu.visible:
                    self.controls_menu.visible = False
                    return True
                if self.is_open:
                    self.is_open = False
                    return True

        return False
