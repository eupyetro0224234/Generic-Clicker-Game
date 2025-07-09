import pygame
import os
from controles import ControlsMenu
from config import FullSettingsMenu
from exit_handler import ExitHandler
from conquistas import AchievementsMenu
from console import Console

class ConfigMenu:
    def __init__(self, screen, window_width, window_height, loading_callback=None, score_manager=None):
        self.screen = screen
        self.font = pygame.font.SysFont(None, 26)
        self.bg_color = (180, 210, 255, 230)
        self.option_color = (255, 255, 255)
        self.option_hover_color = (200, 220, 255)
        self.option_border = (150, 180, 230)
        self.text_color = (40, 40, 60)

        self.option_height = 40
        self.option_radius = 12
        self.padding_x = 10
        self.spacing_x = 12
        self.spacing_y = 10
        self.options_per_row = 2

        self.is_open = False
        self.animation_progress = 0.0
        self.animation_speed = 0.15

        self.console_enabled = False
        self.console_instance = None

        localappdata = os.getenv("LOCALAPPDATA")
        self.assets_folder = os.path.join(localappdata, ".assets")
        os.makedirs(self.assets_folder, exist_ok=True)

        self.icon_path = os.path.join(self.assets_folder, "menu.png")

        try:
            self.icon_image = pygame.image.load(self.icon_path).convert_alpha()
            self.icon_image = pygame.transform.smoothscale(self.icon_image, (42, 42))
        except Exception:
            self.icon_image = None

        self.icon_rect = self.icon_image.get_rect() if self.icon_image else pygame.Rect(0, 0, 48, 48)
        self.icon_rect.topright = (window_width - 6, 6)

        self.base_options = ["Configurações", "Controles", "Conquistas", "Sair"]
        self.options = list(self.base_options)

        self.controls_menu = ControlsMenu(screen, window_width, window_height)
        self.settings_menu = FullSettingsMenu(screen, window_width, window_height)
        self.achievements_menu = AchievementsMenu(screen, window_width, window_height, self)
        self.exit_handler = ExitHandler(screen, window_width, window_height)

        self.extra_icons = []
        self.score_manager = score_manager
        self.get_score_callback = None
        self.set_score_callback = None

        if hasattr(self.settings_menu, 'get_option') and self.settings_menu.get_option("Manter console aberto"):
            self.enable_console()

        self.hovered_index = None

    def set_score_accessors(self, get_score_func, set_score_func):
        self.get_score_callback = get_score_func
        self.set_score_callback = set_score_func

    def enable_console(self, add_option=False):
        if not self.console_enabled:
            self.console_enabled = True
            if "Console" not in self.options:
                self.options.insert(len(self.options)-1, "Console")

            if self.console_instance is None and self.get_score_callback and self.set_score_callback:
                self.console_instance = Console(
                    self.screen,
                    self.screen.get_width(),
                    self.screen.get_height(),
                    on_exit_callback=lambda: self.disable_console(remove_option=True),
                    tracker=getattr(self.achievements_menu, 'tracker', None),
                    config_menu=self,
                    upgrade_manager=None
                )
                self.console_instance.set_score_accessors(
                    self.get_score_callback,
                    self.set_score_callback
                )

            if add_option and hasattr(self, 'settings_menu'):
                self.settings_menu.add_console_option()

        if self.console_instance:
            self.console_instance.visible = True

    def disable_console(self, remove_option=False):
        if self.console_enabled:
            self.console_enabled = False
            if "Console" in self.options:
                self.options.remove("Console")
            if self.console_instance:
                self.console_instance.visible = False

            if remove_option and hasattr(self, 'settings_menu'):
                self.settings_menu.remove_console_option()

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

        unlocked_count = len(self.achievements_menu.tracker.unlocked) if hasattr(self.achievements_menu, "tracker") else 0

        display = [
            f"Conquistas ({unlocked_count})" if opt == "Conquistas" else opt
            for opt in self.options
        ]

        width = 420
        vertical_padding = 14
        rows = (len(display) + self.options_per_row - 1) // self.options_per_row
        full_h = rows * (self.option_height + self.spacing_y) - self.spacing_y + vertical_padding * 2
        height = int(full_h * self.animation_progress)
        x = self.screen.get_width() - width - 6
        y = self.icon_rect.bottom + 8

        surf = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(surf, self.bg_color, (0, 0, width, height), border_radius=18)

        mouse_pos = pygame.mouse.get_pos()
        self.hovered_index = None

        for i, opt in enumerate(display):
            row = i // self.options_per_row
            col = i % self.options_per_row

            button_width = (width - self.padding_x * 2 - self.spacing_x) // self.options_per_row
            button_x = self.padding_x + col * (button_width + self.spacing_x)
            button_y = vertical_padding + row * (self.option_height + self.spacing_y)

            button_rect = pygame.Rect(button_x, button_y, button_width, self.option_height)

            if button_rect.collidepoint(mouse_pos):
                color = self.option_hover_color
                self.hovered_index = i
            else:
                color = self.option_color

            pygame.draw.rect(surf, color, button_rect, border_radius=self.option_radius)
            pygame.draw.rect(surf, self.option_border, button_rect, width=2, border_radius=self.option_radius)

            txt = self.font.render(opt, True, self.text_color)
            txt_rect = txt.get_rect(center=button_rect.center)
            surf.blit(txt, txt_rect)

        self.screen.blit(surf, (x, y))

    def draw(self):
        self.draw_menu()
        if self.controls_menu.visible:
            self.controls_menu.draw()
        if self.settings_menu.visible:
            self.settings_menu.draw()
        if self.achievements_menu.visible:
            self.achievements_menu.draw()
        if self.console_instance and self.console_instance.visible:
            self.console_instance.draw()
        self.exit_handler.draw()

    def handle_event(self, event):
        if self.console_instance and self.console_instance.visible:
            if self.console_instance.handle_event(event):
                return True

        if self.exit_handler.active:
            result = self.exit_handler.handle_event(event)

            if self.exit_handler.detected_console:
                self.enable_console(add_option=True)
                if hasattr(self.achievements_menu, 'tracker'):
                    self.achievements_menu.tracker.unlock_secret("console")
                self.exit_handler.detected_console = False
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
                width = 420
                vertical_padding = 14
                rows = (len(self.options) + self.options_per_row - 1) // self.options_per_row
                full_h = rows * (self.option_height + self.spacing_y) - self.spacing_y + vertical_padding * 2
                height = int(full_h * self.animation_progress)
                x = self.screen.get_width() - width - 6
                y = self.icon_rect.bottom + 8
                menu_rect = pygame.Rect(x, y, width, height)

                if menu_rect.collidepoint(event.pos):
                    rel_x = event.pos[0] - x - self.padding_x
                    rel_y = event.pos[1] - y - vertical_padding

                    button_width = (width - self.padding_x * 2 - self.spacing_x) // self.options_per_row
                    col = rel_x // (button_width + self.spacing_x)
                    row = rel_y // (self.option_height + self.spacing_y)
                    idx = int(row * self.options_per_row + col)

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
                            if self.console_instance:
                                self.console_instance.open()
                            else:
                                if self.get_score_callback and self.set_score_callback:
                                    self.enable_console(add_option=True)
                                    if self.console_instance:
                                        self.console_instance.open()
                        self.is_open = False
                        return True
                else:
                    self.is_open = False
                    return True

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if self.console_instance and self.console_instance.visible:
                self.console_instance.visible = False
                return True
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