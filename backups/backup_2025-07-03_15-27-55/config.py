import pygame
import os
import json

class FullSettingsMenu:
    def __init__(self, screen, window_width, window_height):
        self.screen = screen
        self.window_width = window_width
        self.window_height = window_height
        self.visible = False
        self.font = pygame.font.SysFont(None, 32)
        self.title_font = pygame.font.SysFont(None, 48)

        self.config_file = os.path.join(os.getenv("LOCALAPPDATA"), ".assests", "config.json")
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)

        self.settings = self.load_config()

        self.sections = {
            "Configurações Gerais": [
                "clicks sobem com o botão direito",
                "clicks sobem com o botão esquerdo",
                "clicks sobem com o click botão de rolagem do mouse",
                "clicks sobem com a rolagem do mouse"
            ],
            "Mods e Texturas": [
                "ativar mods",
                "ativar texturas"
            ]
        }

        self.toggle_boxes = []
        self.create_toggle_boxes()

    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "clicks sobem com o botão direito": True,
            "clicks sobem com o botão esquerdo": True,
            "clicks sobem com o click botão de rolagem do mouse": True,
            "clicks sobem com a rolagem do mouse": True,
            "ativar mods": False,
            "ativar texturas": False
        }

    def save_config(self):
        with open(self.config_file, "w") as f:
            json.dump(self.settings, f, indent=4)

    def create_toggle_boxes(self):
        self.toggle_boxes.clear()
        x = 80
        y = 100
        box_w, box_h = 24, 24
        spacing_y = 50

        for section, options in self.sections.items():
            self.toggle_boxes.append(("title", section, x, y))
            y += spacing_y
            for key in options:
                self.toggle_boxes.append(("option", key, x, y, box_w, box_h))
                y += spacing_y
            y += spacing_y // 2

    def draw(self):
        if not self.visible:
            return

        overlay = pygame.Surface((self.window_width, self.window_height))
        overlay.set_alpha(235)
        overlay.fill((240, 245, 255))
        self.screen.blit(overlay, (0, 0))

        for item in self.toggle_boxes:
            if item[0] == "title":
                _, title, x, y = item
                text = self.title_font.render(title, True, (50, 50, 80))
                self.screen.blit(text, (x, y))
            elif item[0] == "option":
                _, key, x, y, w, h = item
                value = self.settings.get(key, False)
                pygame.draw.rect(self.screen, (255, 255, 255), (x, y, w, h), border_radius=4)
                pygame.draw.rect(self.screen, (100, 100, 150), (x, y, w, h), width=2, border_radius=4)
                if value:
                    pygame.draw.line(self.screen, (0, 120, 0), (x+4, y+h//2), (x+w//2, y+h-5), 3)
                    pygame.draw.line(self.screen, (0, 120, 0), (x+w//2, y+h-5), (x+w-4, y+4), 3)

                label = self.font.render(key, True, (30, 30, 50))
                self.screen.blit(label, (x + w + 14, y - 4))

    def handle_event(self, event):
        if not self.visible:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN:
            for item in self.toggle_boxes:
                if item[0] == "option":
                    _, key, x, y, w, h = item
                    rect = pygame.Rect(x, y, w, h)
                    if rect.collidepoint(event.pos):
                        self.settings[key] = not self.settings.get(key, False)
                        self.save_config()
                        return True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.visible = False
                return True

        return False
