import pygame
import os
import urllib.request
from controles import ControlsMenu
from config import FullSettingsMenu

class ExitHandler:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.fade_surface = pygame.Surface((width, height))
        self.fade_surface.fill((0, 0, 0))
        self.alpha = 0
        self.fading_out = False

    def start_fade_out(self):
        self.alpha = 0
        self.fading_out = True

    def update_fade_out(self):
        if self.fading_out:
            self.alpha += 10
            if self.alpha >= 255:
                self.alpha = 255
                self.screen.blit(self.fade_surface, (0, 0))
                pygame.display.flip()
                pygame.quit()
                sys.exit()
            self.fade_surface.set_alpha(self.alpha)
            self.screen.blit(self.fade_surface, (0, 0))
            pygame.display.flip()
            pygame.time.delay(30)
            return True
        return False

class ConfigMenu:
    def __init__(self, screen, window_width, window_height, loading_callback=None):
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

        self.exit_handler = ExitHandler(screen, window_width, window_height)

        localappdata = os.getenv("LOCALAPPDATA")
        self.assets_folder = os.path.join(localappdata, ".assests")
        os.makedirs(self.assets_folder, exist_ok=True)

        self.icon_url = "https://i.postimg.cc/hGf3VRqY/image-removebg-preview-5.png"
        self.icon_path = os.path.join(self.assets_folder, "config_icon.png")

        if not os.path.isfile(self.icon_path):
            try:
                if loading_callback:
                    loading_callback(20, "Baixando ícone...")
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

        self.options = ["Configurações", "Controles", "Sair"]
        self.max_height = len(self.options) * (self.option_height + self.spacing)

        self.controls_menu = ControlsMenu(screen, window_width, window_height)
        self.settings_menu = FullSettingsMenu(screen, window_width, window_height)

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
        if self.animation_progress <= 0:
            return

        width = 190
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

    def draw(self):
        self.draw_menu()
        if self.controls_menu.visible:
            self.controls_menu.draw()
        if self.settings_menu.visible:
            self.settings_menu.draw()

    def handle_event(self, event):
        if self.settings_menu.visible and self.settings_menu.handle_event(event):
            return True
        if self.controls_menu.visible and self.controls_menu.handle_event(event):
            return True

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.icon_rect.collidepoint(event.pos):
                self.is_open = not self.is_open
                return True

            if self.is_open:
                width = 190
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
                            self.controls_menu.visible = not self.controls_menu.visible
                            self.settings_menu.visible = False
                        elif selected == "Configurações":
                            self.settings_menu.visible = not self.settings_menu.visible
                            self.controls_menu.visible = False
                        elif selected == "Sair":
                            from tkinter import messagebox, Tk
                            root = Tk()
                            root.withdraw()
                            if messagebox.askyesno("Sair", "Tem certeza que deseja sair?"):
                                self.exit_handler.start_fade_out()
                    return True
                else:
                    self.is_open = False
                    return True

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.settings_menu.visible:
                    self.settings_menu.visible = False
                    return True
                if self.controls_menu.visible:
                    self.controls_menu.visible = False
                    return True
                if self.is_open:
                    self.is_open = False
                    return True

        return False
