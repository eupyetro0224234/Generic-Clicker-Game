import pygame
import os
import json

class AchievementsMenu:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height

        self.font = pygame.font.SysFont(None, 26)
        self.title_font = pygame.font.SysFont(None, 36, bold=True)

        self.bg_color = (230, 230, 255)
        self.text_color = (40, 40, 60)
        self.option_height = 40
        self.option_spacing = 8
        self.padding = 15
        self.visible = False

        self.achievements = {
            "first_click": {"name": "Primeiro Clique", "desc": "Dê seu primeiro clique", "unlocked": False},
            "hundred_points": {"name": "100 Pontos", "desc": "Alcance 100 pontos", "unlocked": False},
            "reset_score": {"name": "Recomeço", "desc": "Resete sua pontuação", "unlocked": False},
        }

        self.alert_active = False
        self.alert_alpha = 0
        self.alert_fade_speed = 8
        self.alert_text = ""
        self.alert_rect = pygame.Rect(self.width//2 - 220, 50, 440, 60)  # maior caixa

        # Caixa rosa para alerta
        self.alert_bg_color = (255, 182, 193)  # rosa claro (lightpink)
        self.alert_text_color = (90, 0, 30)

    def load_achievements(self, unlocked_ids):
        for aid in unlocked_ids:
            if aid in self.achievements:
                self.achievements[aid]["unlocked"] = True

    def get_unlocked_ids(self):
        return [aid for aid, val in self.achievements.items() if val["unlocked"]]

    def unlock(self, achievement_id):
        if achievement_id in self.achievements and not self.achievements[achievement_id]["unlocked"]:
            self.achievements[achievement_id]["unlocked"] = True
            self.alert_text = f"Conquista desbloqueada: {self.achievements[achievement_id]['name']}!"
            self.alert_active = True
            self.alert_alpha = 255

    def update_alert(self):
        if self.alert_active:
            self.alert_alpha -= self.alert_fade_speed
            if self.alert_alpha <= 0:
                self.alert_alpha = 0
                self.alert_active = False

    def draw_alert(self):
        if not self.alert_active:
            return
        s = pygame.Surface((self.alert_rect.width, self.alert_rect.height), pygame.SRCALPHA)
        s.fill((*self.alert_bg_color, self.alert_alpha))
        self.screen.blit(s, self.alert_rect.topleft)

        text_surf = self.font.render(self.alert_text, True, self.alert_text_color)
        text_rect = text_surf.get_rect(center=self.alert_rect.center)
        self.screen.blit(text_surf, text_rect)

    def draw(self):
        if not self.visible:
            return

        # Fundo e borda
        w = 420
        h = len(self.achievements) * (self.option_height + self.option_spacing) + self.padding * 2 + 40
        x = (self.width - w) // 2
        y = (self.height - h) // 2

        menu_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(menu_surf, self.bg_color, (0, 0, w, h), border_radius=14)
        pygame.draw.rect(menu_surf, (180, 180, 220), (0, 0, w, h), width=2, border_radius=14)

        # Título
        title_surf = self.title_font.render("Conquistas", True, self.text_color)
        title_rect = title_surf.get_rect(center=(w//2, self.padding + 20))
        menu_surf.blit(title_surf, title_rect)

        # Lista conquistas
        start_y = self.padding + 50
        for i, (aid, info) in enumerate(self.achievements.items()):
            oy = start_y + i * (self.option_height + self.option_spacing)
            rect = pygame.Rect(self.padding, oy, w - self.padding*2, self.option_height)

            # Cor de fundo para desbloqueadas
            bg_col = (200, 255, 200) if info["unlocked"] else (220, 220, 220)
            pygame.draw.rect(menu_surf, bg_col, rect, border_radius=8)
            pygame.draw.rect(menu_surf, (150, 150, 150), rect, 1, border_radius=8)

            # Nome da conquista
            name_surf = self.font.render(info["name"], True, self.text_color)
            menu_surf.blit(name_surf, (rect.x + 10, rect.y + 5))

            # Descrição em menor fonte
            desc_font = pygame.font.SysFont(None, 20)
            desc_surf = desc_font.render(info["desc"], True, (80, 80, 80))
            menu_surf.blit(desc_surf, (rect.x + 10, rect.y + 22))

        self.screen.blit(menu_surf, (x, y))

    def handle_event(self, event):
        if not self.visible:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.visible = False
                return True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Fecha ao clicar fora da área da janela
            w = 420
            h = len(self.achievements) * (self.option_height + self.option_spacing) + self.padding * 2 + 40
            x = (self.width - w) // 2
            y = (self.height - h) // 2
            rect = pygame.Rect(x, y, w, h)

            if not rect.collidepoint(event.pos):
                self.visible = False
                return True

        return False
