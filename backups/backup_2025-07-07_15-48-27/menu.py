import pygame
import os
import sys
import subprocess
from controles import ControlsMenu
from config import FullSettingsMenu
from conquistas import AchievementsMenu
from exit_handler import ExitHandler

class ConfigMenu:
    def __init__(self, screen, width, height, loading_callback=None):
        self.screen = screen
        self.width = width
        self.height = height
        self.is_open = False
        self.animation_progress = 0.0
        self.animation_speed = 0.12
        self.icon_size = 42
        self.icon_rect = pygame.Rect(width - self.icon_size - 10, 10, self.icon_size, self.icon_size)
        self.bg_color = (180, 210, 255)
        self.option_color = (255, 255, 255)
        self.option_border = (200, 220, 250)
        self.text_color = (40, 40, 60)
        self.option_height = 38
        self.option_radius = 10
        self.padding_x = 6
        self.spacing = 5
        self.width_box = 280
        self.options = ["Configurações", "Controles", "Conquistas", "Sair"]
        self.extra_options = []
        self.font = pygame.font.SysFont(None, 24)

        self.settings_menu = FullSettingsMenu(screen, width, height)
        self.controls_menu = ControlsMenu(screen, width, height)
        self.achievements_menu = AchievementsMenu(screen, width, height)
        self.exit_handler = ExitHandler(screen, width, height)

    def toggle(self):
        self.is_open = not self.is_open

    def draw_icon(self):
        pygame.draw.rect(self.screen, (255, 255, 255), self.icon_rect, border_radius=6)
        pygame.draw.rect(self.screen, (200, 200, 200), self.icon_rect, 2, border_radius=6)
        pygame.draw.circle(self.screen, (100, 100, 220), self.icon_rect.center, 6)
        pygame.draw.circle(self.screen, (100, 100, 220), (self.icon_rect.centerx - 10, self.icon_rect.centery), 6)
        pygame.draw.circle(self.screen, (100, 100, 220), (self.icon_rect.centerx + 10, self.icon_rect.centery), 6)

    def update_animation(self):
        if self.is_open:
            self.animation_progress = min(1.0, self.animation_progress + self.animation_speed)
        else:
            self.animation_progress = max(0.0, self.animation_progress - self.animation_speed)

    def draw(self):
        self.update_animation()
        if self.animation_progress <= 0:
            return

        unlocked = len(self.achievements_menu.tracker.unlocked) if hasattr(self.achievements_menu, "tracker") else 0

        display_options = []
        for opt in self.options:
            if opt == "Conquistas":
                display_options.append(f"{opt} ({unlocked})")
            else:
                display_options.append(opt)
        display_options += self.extra_options

        total_h = len(display_options) * (self.option_height + self.spacing) - self.spacing + 12
        height = int(total_h * self.animation_progress)
        panel = pygame.Surface((self.width_box, height), pygame.SRCALPHA)
        pygame.draw.rect(panel, self.bg_color, (0, 0, self.width_box, height), border_radius=12)

        for i, opt in enumerate(display_options):
            oy = 6 + i * (self.option_height + self.spacing)
            if oy + self.option_height > height:
                break
            rect = pygame.Rect(self.padding_x, oy, self.width_box - 2 * self.padding_x, self.option_height)
            pygame.draw.rect(panel, self.option_color, rect, border_radius=self.option_radius)
            pygame.draw.rect(panel, self.option_border, rect, width=1, border_radius=self.option_radius)
            txt = self.font.render(opt, True, self.text_color)
            panel.blit(txt, txt.get_rect(center=rect.center))

        self.screen.blit(panel, (self.width - self.width_box - 10, 60))

        if self.exit_handler.active:
            self.exit_handler.draw()

    def handle_event(self, event):
        if self.exit_handler.active:
            handled = self.exit_handler.handle_event(event)
            if self.exit_handler.detected_console:
                if "Console" not in self.extra_options:
                    self.extra_options.append("Console")
                self.exit_handler.detected_console = False
            return handled

        if self.settings_menu.visible:
            return self.settings_menu.handle_event(event)
        if self.controls_menu.visible:
            return self.controls_menu.handle_event(event)
        if self.achievements_menu.visible:
            return self.achievements_menu.handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.icon_rect.collidepoint(event.pos):
                self.toggle()
                return True

            if self.is_open:
                display_options = []
                for opt in self.options:
                    if opt == "Conquistas":
                        display_options.append(f"{opt} ({len(self.achievements_menu.tracker.unlocked)})")
                    else:
                        display_options.append(opt)
                display_options += self.extra_options

                for i, opt in enumerate(display_options):
                    oy = 6 + i * (self.option_height + self.spacing)
                    rect = pygame.Rect(
                        self.width - self.width_box - 10 + self.padding_x,
                        60 + oy,
                        self.width_box - 2 * self.padding_x,
                        self.option_height
                    )
                    if rect.collidepoint(event.pos):
                        real_opt = self.options[i] if i < len(self.options) else self.extra_options[i - len(self.options)]
                        if real_opt == "Configurações":
                            self.settings_menu.visible = True
                            self.is_open = False
                        elif real_opt == "Controles":
                            self.controls_menu.visible = True
                            self.is_open = False
                        elif real_opt.startswith("Conquistas"):
                            self.achievements_menu.visible = True
                            self.is_open = False
                        elif real_opt == "Sair":
                            self.exit_handler.start()
                            self.is_open = False
                        elif real_opt == "Console":
                            subprocess.Popen([sys.executable, os.path.join(os.getcwd(), "console.py")])
                            self.is_open = False
                        return True
        return False
