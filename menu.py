import os
import pygame
import json
from datetime import datetime
from controles import ControlsMenu
from config import FullSettingsMenu
from exit_handler import ExitHandler
from conquistas import AchievementsMenu
from console import Console
from eventos import EventManager

class ConfigMenu:
    def __init__(self, screen, window_width, window_height, loading_callback=None, score_manager=None):
        self.screen = screen
        self.window_width = window_width
        self.window_height = window_height
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

        self.base_options = ["Configurações", "Controles", "Conquistas", "Eventos", "Sair"]
        self.options = list(self.base_options)

        self.controls_menu = ControlsMenu(screen, window_width, window_height)
        self.settings_menu = FullSettingsMenu(screen, window_width, window_height)
        self.achievements_menu = AchievementsMenu(screen, window_width, window_height, self)
        self.exit_handler = ExitHandler(screen, window_width, window_height)
        self.event_manager = EventManager(screen, window_width, window_height)

        self.console_instance = Console(
            screen,
            window_width,
            window_height,
            on_exit_callback=self.disable_console,
            on_open_callback=self.enable_console,
            tracker=getattr(self.achievements_menu, 'tracker', None),
            config_menu=self,
            upgrade_manager=None
        )

        self.extra_icons = []
        self.score_manager = score_manager
        self.get_score_callback = None
        self.set_score_callback = None
        self.menu_rects = []

        if hasattr(self.settings_menu, 'get_option') and self.settings_menu.get_option("Manter console aberto"):
            self.enable_console(add_option=True)

    def set_score_accessors(self, get_score_func, set_score_func):
        self.get_score_callback = get_score_func
        self.set_score_callback = set_score_func

    def enable_console(self, add_option=False):
        if not self.console_enabled:
            self.console_enabled = True
            if "Console" not in self.options:
                self.options.insert(len(self.options)-1, "Console")
            if self.console_instance:
                self.console_instance.open()
            if add_option and hasattr(self.settings_menu, 'add_console_option'):
                self.settings_menu.add_console_option()

    def disable_console(self, remove_option=False):
        if self.console_enabled:
            self.console_enabled = False
            if "Console" in self.options:
                self.options.remove("Console")
            if self.console_instance:
                self.console_instance.visible = False
            if remove_option and hasattr(self.settings_menu, 'remove_console_option'):
                self.settings_menu.remove_console_option()

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

        unlocked_count = len(self.achievements_menu.tracker.unlocked) if hasattr(self.achievements_menu, "tracker") else 0

        # Preparar itens do menu
        menu_items = [
            ("Configurações", False),
            ("Controles", False),
            (f"Conquistas ({unlocked_count})", False),
            ("Eventos", False)
        ]

        if self.console_enabled:
            menu_items.append(("Console", False))

        # "Sair" só ocupa largura total se o console estiver ativado
        menu_items.append(("Sair", self.console_enabled))

        vertical_menu = False
        if hasattr(self.settings_menu, "get_option"):
            vertical_menu = self.settings_menu.get_option("Menu vertical")

        # Configurações comuns
        button_height = self.option_height
        vertical_padding = 14
        horizontal_padding = self.padding_x
        button_spacing = self.spacing_y
        button_width = 200  # Largura padrão dos botões
        
        mouse_pos = pygame.mouse.get_pos()
        self.menu_rects = []

        if vertical_menu:
            # Modo vertical - todas as opções em uma coluna
            menu_width = button_width + 2 * horizontal_padding
            total_height = len(menu_items) * (button_height + button_spacing) - button_spacing + 2 * vertical_padding
            height = int(total_height * self.animation_progress)
            
            x_pos = self.window_width - menu_width - 6
            y_pos = self.icon_rect.bottom + 8
            
            surf = pygame.Surface((menu_width, height), pygame.SRCALPHA)
            pygame.draw.rect(surf, self.bg_color, (0, 0, menu_width, height), border_radius=18)
            
            for i, (text, full_width) in enumerate(menu_items):
                current_width = menu_width - 2 * horizontal_padding if full_width else button_width
                button_x = (menu_width - current_width) // 2  # Centraliza o botão
                button_y = vertical_padding + i * (button_height + button_spacing)
                
                abs_rect = pygame.Rect(
                    x_pos + button_x,
                    y_pos + button_y,
                    current_width,
                    button_height
                )
                self.menu_rects.append((abs_rect, text))

                color = self.option_hover_color if abs_rect.collidepoint(mouse_pos) else self.option_color
                pygame.draw.rect(surf, color, (button_x, button_y, current_width, button_height), border_radius=10)
                pygame.draw.rect(surf, self.option_border, (button_x, button_y, current_width, button_height), 2, border_radius=10)

                txt = self.font.render(text, True, self.text_color)
                txt_rect = txt.get_rect(center=(button_x + current_width // 2, button_y + button_height // 2))
                surf.blit(txt, txt_rect)
        else:
            # Modo horizontal - 2 colunas
            menu_width = 2 * button_width + self.spacing_x + 2 * horizontal_padding
            
            # Calcular número de linhas
            num_regular_items = len(menu_items) - 1  # Todos exceto Sair
            num_rows = (num_regular_items + 1) // 2  # Arredonda para cima
            
            # Se Sair ocupa largura total, adiciona mais uma linha
            if menu_items[-1][1]:  # Se último item tem full_width=True
                num_rows += 1
            
            total_height = num_rows * (button_height + button_spacing) - button_spacing + 2 * vertical_padding
            height = int(total_height * self.animation_progress)
            
            x_pos = self.window_width - menu_width - 6
            y_pos = self.icon_rect.bottom + 8
            
            surf = pygame.Surface((menu_width, height), pygame.SRCALPHA)
            pygame.draw.rect(surf, self.bg_color, (0, 0, menu_width, height), border_radius=18)
            
            # Desenhar itens regulares (todos exceto Sair)
            for i, (text, full_width) in enumerate(menu_items[:-1]):  # Todos exceto o último (Sair)
                col = i % 2
                row = i // 2
                
                button_x = horizontal_padding + col * (button_width + self.spacing_x)
                button_y = vertical_padding + row * (button_height + button_spacing)
                
                abs_rect = pygame.Rect(
                    x_pos + button_x,
                    y_pos + button_y,
                    button_width,
                    button_height
                )
                self.menu_rects.append((abs_rect, text))

                color = self.option_hover_color if abs_rect.collidepoint(mouse_pos) else self.option_color
                pygame.draw.rect(surf, color, (button_x, button_y, button_width, button_height), border_radius=10)
                pygame.draw.rect(surf, self.option_border, (button_x, button_y, button_width, button_height), 2, border_radius=10)

                txt = self.font.render(text, True, self.text_color)
                txt_rect = txt.get_rect(center=(button_x + button_width // 2, button_y + button_height // 2))
                surf.blit(txt, txt_rect)
            
            # Desenhar Sair (último item)
            sair_text, sair_full_width = menu_items[-1]
            row = num_rows - 1
            
            if sair_full_width:
                # Sair ocupa linha completa
                button_x = horizontal_padding
                button_width_sair = menu_width - 2 * horizontal_padding
            else:
                # Sair ocupa espaço normal (metade)
                button_x = horizontal_padding + ((num_regular_items % 2) * (button_width + self.spacing_x))
                button_width_sair = button_width
            
            button_y = vertical_padding + row * (button_height + button_spacing)
            
            abs_rect = pygame.Rect(
                x_pos + button_x,
                y_pos + button_y,
                button_width_sair,
                button_height
            )
            self.menu_rects.append((abs_rect, sair_text))

            color = self.option_hover_color if abs_rect.collidepoint(mouse_pos) else self.option_color
            pygame.draw.rect(surf, color, (button_x, button_y, button_width_sair, button_height), border_radius=10)
            pygame.draw.rect(surf, self.option_border, (button_x, button_y, button_width_sair, button_height), 2, border_radius=10)

            txt = self.font.render(sair_text, True, self.text_color)
            txt_rect = txt.get_rect(center=(button_x + button_width_sair // 2, button_y + button_height // 2))
            surf.blit(txt, txt_rect)

        self.screen.blit(surf, (x_pos, y_pos))

    def draw(self):
        self.draw_menu()
        if self.controls_menu.visible:
            self.controls_menu.draw()
        if self.settings_menu.visible:
            self.settings_menu.draw()
        if self.achievements_menu.visible:
            self.achievements_menu.draw()
        if self.event_manager.events_menu.visible:
            self.event_manager.draw()
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
                self.exit_handler.active = False
                return True
            return result

        if self.settings_menu.visible:
            return self.settings_menu.handle_event(event)

        if self.event_manager.events_menu.visible:
            return self.event_manager.handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.icon_rect.collidepoint(event.pos):
                self.is_open = not self.is_open
                return True

            if self.is_open:
                for rect, text in self.menu_rects:
                    if rect.collidepoint(event.pos):
                        if text == "Configurações":
                            self.settings_menu.visible = True
                        elif text == "Controles":
                            self.controls_menu.visible = True
                        elif text.startswith("Conquistas"):
                            self.achievements_menu.visible = True
                        elif text == "Eventos":
                            self.event_manager.show_events_menu()
                        elif text == "Sair":
                            self.exit_handler.start()
                        elif text == "Console":
                            if self.console_instance:
                                self.console_instance.open()
                            else:
                                self.enable_console()
                                if self.console_instance:
                                    self.console_instance.open()
                        self.is_open = False
                        return True

                self.is_open = False
                return True

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
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
                if self.event_manager.events_menu.visible:
                    self.event_manager.events_menu.visible = False
                    return True
                if self.is_open:
                    self.is_open = False
                    return True

        return False