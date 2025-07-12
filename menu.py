import os
import pygame
from controles import ControlsMenu
from config import FullSettingsMenu
from exit_handler import ExitHandler
from conquistas import AchievementsMenu
from console import Console
import json

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

        # Opções base incluindo "Restaurar dados"
        self.base_options = ["Configurações", "Controles", "Conquistas", "Restaurar dados", "Sair"]
        self.options = list(self.base_options)

        self.controls_menu = ControlsMenu(screen, window_width, window_height)
        self.settings_menu = FullSettingsMenu(screen, window_width, window_height)
        self.achievements_menu = AchievementsMenu(screen, window_width, window_height, self)
        self.exit_handler = ExitHandler(screen, window_width, window_height)

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

        menu_items = []
        menu_items.append(("Configurações", False))
        menu_items.append(("Controles", False))
        menu_items.append((f"Conquistas ({unlocked_count})", False))
        
        if self.console_enabled:
            menu_items.append(("Console", False))
        
        menu_items.append(("Restaurar dados", False))
        menu_items.append(("Sair", self.console_enabled))

        width = 420
        vertical_padding = 14
        button_height = self.option_height
        button_spacing = self.spacing_y

        num_items = len(menu_items)
        num_rows = (num_items + 1) // 2  # calcula linhas para 2 colunas

        total_height = num_rows * (button_height + button_spacing) - button_spacing + 2 * vertical_padding
        height = int(total_height * self.animation_progress)
        x_pos = self.window_width - width - 6
        y_pos = self.icon_rect.bottom + 8

        surf = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(surf, self.bg_color, (0, 0, width, height), border_radius=18)

        mouse_pos = pygame.mouse.get_pos()
        self.menu_rects = []

        for i, (text, center) in enumerate(menu_items):
            button_width = (width - 2 * self.padding_x - self.spacing_x) // 2
            col = i % 2
            row = i // 2
            button_x = self.padding_x + col * (button_width + self.spacing_x)
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
            txt_rect = txt.get_rect(center=(button_x + button_width//2, button_y + button_height//2))
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
                        elif text == "Restaurar dados":
                            self.confirmar_restaurar_dados()
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
                if self.is_open:
                    self.is_open = False
                    return True

        return False

    def confirmar_restaurar_dados(self):
        # Import local para evitar importação circular
        from app import show_confirmation_dialog

        confirmed = show_confirmation_dialog(
            self.screen, self.window_width, self.window_height,
            "Deseja realmente restaurar os dados do backup? Isso substituirá os dados atuais."
        )
        if confirmed:
            self.restaurar_dados()

    def restaurar_dados(self):
        if not self.score_manager:
            print("[Erro] ScoreManager não está configurado no ConfigMenu.")
            return

        backup_path = os.path.join(os.getenv("LOCALAPPDATA") or ".", ".assets", "old.json")
        if not os.path.exists(backup_path):
            print("[Info] Backup old.json não encontrado.")
            return
        
        try:
            with open(backup_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            score = data.get("score", 0)
            controls_visible = data.get("controls_visible", False)
            achievements = data.get("achievements", [])
            upgrades = data.get("upgrades", {})
            mini_event_click_count = data.get("mini_event_click_count", 0)

            print("Dados restaurados do backup:")
            print(f"Pontos: {score}")
            print(f"Conquistas: {achievements}")
            print(f"Upgrades: {upgrades}")
            print(f"Mini event clicks: {mini_event_click_count}")

            # Atualize os dados na memória do jogo
            self.score_manager.save_data(score, controls_visible, achievements, upgrades, mini_event_click_count)

            # Aqui, faça o reload dos dados para as variáveis do jogo, se necessário.
            # Exemplo:
            # game_instance.score = score
            # game_instance.achievements = achievements
            # game_instance.upgrades = upgrades
            # game_instance.mini_event_click_count = mini_event_click_count

            os.remove(backup_path)
            print("[Sucesso] Dados restaurados e backup apagado.")

        except Exception as e:
            print(f"[Erro] Falha ao restaurar dados: {e}")