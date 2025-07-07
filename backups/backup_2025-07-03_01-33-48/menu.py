import pygame
import os
import urllib.request

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

        self.show_controls = False  # Flag para mostrar menu controles

        # ícone
        localappdata = os.getenv("LOCALAPPDATA")
        self.assets_folder = os.path.join(localappdata, ".assests")
        os.makedirs(self.assets_folder, exist_ok=True)

        self.icon_url = "https://i.postimg.cc/hGf3VRqY/image-removebg-preview-5.png"
        self.icon_path = os.path.join(self.assets_folder, "config_icon.png")

        if not os.path.isfile(self.icon_path):
            try:
                urllib.request.urlretrieve(self.icon_url, self.icon_path)
            except Exception as e:
                print("Erro ao baixar ícone de configurações:", e)

        self.icon_image = None
        try:
            self.icon_image = pygame.image.load(self.icon_path).convert_alpha()
            self.icon_image = pygame.transform.smoothscale(self.icon_image, (42, 42))
        except Exception as e:
            print("Erro ao carregar ícone:", e)

        self.icon_rect = self.icon_image.get_rect() if self.icon_image else pygame.Rect(0, 0, 48, 48)
        self.icon_rect.topright = (window_width - 6, 6)

        self.options = ["Volume: [•••••]", "Tema: Claro", "Controles"]

        self.max_height = len(self.options) * (self.option_height + self.spacing)

        # Controles a mostrar no submenu
        self.controls_list = [
            ("Clique Esquerdo", "Aumenta pontos"),
            ("R", "Reseta pontos"),
            ("Clique Direito", "Configurações"),
            ("ESC", "Fecha menus"),
        ]

    def draw_icon(self):
        if self.icon_image:
            self.screen.blit(self.icon_image, self.icon_rect)
        else:
            pygame.draw.rect(self.screen, (70, 130, 180), self.icon_rect)

    def update_animation(self):
        if self.is_open or self.show_controls:
            self.animation_progress = min(1.0, self.animation_progress + self.animation_speed)
        else:
            self.animation_progress = max(0.0, self.animation_progress - self.animation_speed)

    def draw_menu(self):
        self.update_animation()
        if self.animation_progress <= 0:
            return

        if self.show_controls:
            self._draw_controls_menu()
        else:
            self._draw_options_menu()

    def _draw_options_menu(self):
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

    def _draw_controls_menu(self):
        width = 260
        vertical_padding = 8
        line_height = 30
        height = (line_height * len(self.controls_list)) + vertical_padding * 2

        margin_right = 4
        x = self.screen.get_width() - width - margin_right
        y = self.icon_rect.bottom + 6

        menu_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(menu_surface, self.bg_color, (0, 0, width, height), border_radius=12)

        for i, (key, desc) in enumerate(self.controls_list):
            oy = vertical_padding + i * line_height

            # Caixa para o nome da tecla
            key_rect = pygame.Rect(10, oy, 100, 24)
            pygame.draw.rect(menu_surface, self.option_color, key_rect, border_radius=6)
            pygame.draw.rect(menu_surface, self.option_border, key_rect, width=1, border_radius=6)

            key_text = self.font.render(key, True, self.text_color)
            key_text_rect = key_text.get_rect(center=key_rect.center)
            menu_surface.blit(key_text, key_text_rect)

            # Texto da descrição
            desc_text = self.font.render(desc, True, self.text_color)
            desc_text_rect = desc_text.get_rect(midleft=(key_rect.right + 10, key_rect.centery))
            menu_surface.blit(desc_text, desc_text_rect)

        self.screen.blit(menu_surface, (x, y))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.icon_rect.collidepoint(event.pos):
                if self.show_controls:
                    self.show_controls = False
                else:
                    self.is_open = not self.is_open
                return True

            if self.is_open and not self.show_controls:
                width = 180
                vertical_padding = 6
                full_height = len(self.options) * (self.option_height + self.spacing) - self.spacing + vertical_padding * 2
                height = int(full_height * self.animation_progress)
                margin_right = 4
                x = self.screen.get_width() - width - margin_right
                y = self.icon_rect.bottom + 6
                rect = pygame.Rect(x, y, width, height)

                if rect.collidepoint(event.pos):
                    # Detecta qual opção foi clicada
                    relative_y = event.pos[1] - y - vertical_padding
                    index = relative_y // (self.option_height + self.spacing)
                    if 0 <= index < len(self.options):
                        selected = self.options[index]
                        if selected == "Controles":
                            self.is_open = False
                            self.show_controls = True
                    return True
                else:
                    self.is_open = False
                    return True

            elif self.show_controls:
                # Fecha controles se clicar fora
                width = 260
                vertical_padding = 8
                line_height = 30
                height = (line_height * len(self.controls_list)) + vertical_padding * 2
                margin_right = 4
                x = self.screen.get_width() - width - margin_right
                y = self.icon_rect.bottom + 6
                rect = pygame.Rect(x, y, width, height)
                if not rect.collidepoint(event.pos):
                    self.show_controls = False
                    return True

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.show_controls:
                    self.show_controls = False
                    return True
                if self.is_open:
                    self.is_open = False
                    return True
        return False
