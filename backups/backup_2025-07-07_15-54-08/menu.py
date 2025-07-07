import pygame
import os
import urllib.request
from controles import ControlsMenu
from config import FullSettingsMenu
from exit_handler import ExitHandler
from conquistas import AchievementsMenu

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

        self.console_enabled = False  # Flag para ativar opção Console

        localappdata = os.getenv("LOCALAPPDATA")
        self.assets_folder = os.path.join(localappdata, ".assets")
        os.makedirs(self.assets_folder, exist_ok=True)

        self.icon_url = "https://i.postimg.cc/hGf3VRqY/image-removebg-preview-5.png"
        self.icon_path = os.path.join(self.assets_folder, "config_icon.png")
        if not os.path.isfile(self.icon_path):
            try:
                if loading_callback:
                    loading_callback(0, "Baixando ícone de configurações...")
                urllib.request.urlretrieve(self.icon_url, self.icon_path)
                if loading_callback:
                    loading_callback(100, "Ícone baixado!")
            except Exception as e:
                print("Erro ao baixar ícone de configurações:", e)

        try:
            self.icon_image = pygame.image.load(self.icon_path).convert_alpha()
            self.icon_image = pygame.transform.smoothscale(self.icon_image, (42, 42))
        except:
            self.icon_image = None

        self.icon_rect = (
            self.icon_image.get_rect() if self.icon_image else pygame.Rect(0, 0, 48, 48)
        )
        self.icon_rect.topright = (window_width - 6, 6)

        self.base_options = ["Configurações", "Controles", "Conquistas", "Sair"]
        self.options = list(self.base_options)

        self.controls_menu = ControlsMenu(screen, window_width, window_height)
        self.settings_menu = FullSettingsMenu(screen, window_width, window_height)
        self.achievements_menu = AchievementsMenu(screen, window_width, window_height)
        self.exit_handler = ExitHandler(screen, window_width, window_height)

        self.extra_icons = []

    def enable_console(self):
        if not self.console_enabled:
            self.console_enabled = True
            # Insere "Console" antes da opção "Sair"
            if "Console" not in self.options:
                idx_sair = self.options.index("Sair") if "Sair" in self.options else len(self.options)
                self.options.insert(idx_sair, "Console")

    def add_extra_icon(self, icon_rect, toggle_function):
        self.extra_icons.append((icon_rect, toggle_function))

    def draw_icon(self):
        if self.icon_image:
            self.screen.blit(self.icon_image, self.icon_rect)
        else:
            pygame.draw.rect(self.screen, (70, 130, 180), self.icon_rect)

        for rect, _ in self.extra_icons:
            pygame.draw.rect(self.screen, (80, 80, 140), rect, border_radius=8)

    def update_animation(self):
        if self.is_open:
            self.animation_progress = min(1.0, self.animation_progress + self.animation_speed)
        else:
            self.animation_progress = max(0.0, self.animation_progress - self.animation_speed)

    def draw_menu(self):
        self.update_animation()
        if self.animation_progress <= 0:
            return

        unlocked_count = (
            len(self.achievements_menu.tracker.unlocked)
            if hasattr(self.achievements_menu, "tracker")
            else 0
        )

        display = [
            f"Conquistas ({unlocked_count})" if opt == "Conquistas" else opt
            for opt in self.options
        ]

        width = 190
        vertical_padding = 6
        full_h = len(display) * (self.option_height + self.spacing) - self.spacing + vertical_padding * 2
        height = int(full_h * self.animation_progress)
        x = self.screen.get_width() - width - 4
        y = self.icon_rect.bottom + 6

        surf = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(surf, self.bg_color, (0, 0, width, height), border_radius=12)

        for i, opt in enumerate(display):
            oy = vertical_padding + i * (self.option_height + self.spacing)
            if oy + self.option_height > height:
                break
            rect = pygame.Rect(self.padding_x, oy, width - 2 * self.padding_x, self.option_height)
            pygame.draw.rect(surf, self.option_color, rect, border_radius=self.option_radius)
            pygame.draw.rect(surf, self.option_border, rect, width=1, border_radius=self.option_radius)
            txt = self.font.render(opt, True, self.text_color)
            surf.blit(txt, txt.get_rect(center=rect.center))

        self.screen.blit(surf, (x, y))

    def draw(self):
        self.draw_menu()
        if self.controls_menu.visible:
            self.controls_menu.draw()
        if self.settings_menu.visible:
            self.settings_menu.draw()
        if self.achievements_menu.visible:
            self.achievements_menu.draw()
        self.exit_handler.draw()

    def handle_event(self, event):
        if self.exit_handler.active:
            result = self.exit_handler.handle_event(event)

            # Usa flag detectada no ExitHandler para ativar Console
            if getattr(self.exit_handler, 'detected_console', False):
                self.enable_console()
                self.exit_handler.detected_console = False
                self.exit_handler.active = False
                return True

            return result

        if self.settings_menu.visible and self.settings_menu.handle_event(event):
            return True
        if self.controls_menu.visible and self.controls_menu.handle_event(event):
            return True
        if self.achievements_menu.visible and self.achievements_menu.handle_event(event):
            return True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.icon_rect.collidepoint(event.pos):
                self.is_open = not self.is_open
                return True

            for rect, toggle_func in self.extra_icons:
                if rect.collidepoint(event.pos):
                    toggle_func()
                    return True

            if self.is_open:
                width = 190
                vertical_padding = 6
                full_h = len(self.options) * (self.option_height + self.spacing) - self.spacing + vertical_padding * 2
                height = int(full_h * self.animation_progress)
                x = self.screen.get_width() - width - 4
                y = self.icon_rect.bottom + 6
                menu_rect = pygame.Rect(x, y, width, height)

                if menu_rect.collidepoint(event.pos):
                    rel_y = event.pos[1] - y - vertical_padding
                    idx = rel_y // (self.option_height + self.spacing)
                    if 0 <= idx < len(self.options):
                        sel = self.options[idx]
                        if sel == "Configurações":
                            self.settings_menu.visible = True
                        elif sel == "Controles":
                            self.controls_menu.visible = True
                        elif sel == "Conquistas":
                            self.achievements_menu.visible = True
                        elif sel == "Sair":
                            self.exit_handler.start()
                        elif sel == "Console":
                            try:
                                from console import open_console
                                open_console()
                            except Exception as e:
                                print("Erro ao abrir console:", e)
                        self.is_open = False
                        return True
                else:
                    # Clique fora fecha menu
                    self.is_open = False
                    return True

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if self.exit_handler.active:
                self.exit_handler.active = False
                return True
            if self.settings_menu.visible:
                self.settings_menu.visible = False
                return True
            if self.controls_menu.visible:
                self.controls_menu.visible = False
                return True
            if self.achievements_menu.visible:
                self.achievements_menu.visible = False
                return True
            if self.is_open:
                self.is_open = False
                return True

        return False
