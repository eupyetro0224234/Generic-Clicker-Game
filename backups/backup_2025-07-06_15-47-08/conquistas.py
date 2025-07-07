import pygame
import time

class Achievement:
    def __init__(self, title, description, threshold):
        self.title = title
        self.description = description
        self.threshold = threshold
        self.unlocked = False

class AchievementTracker:
    def __init__(self, screen):
        self.screen = screen
        self.achievements = [
            Achievement("Primeiro Clique", "Dê seu primeiro clique", 1),
            Achievement("10 Cliques", "Alcance 10 cliques", 10),
            Achievement("50 Cliques", "Alcance 50 cliques", 50),
            Achievement("100 Cliques", "Alcance 100 cliques", 100),
        ]
        self.unlocked = set()
        self.popup_text = ""
        self.popup_time = 0
        self.popup_duration = 3.0
        self.font = pygame.font.SysFont(None, 28)
        self.bg_color = (255, 192, 203)  # rosa claro

    def check(self, score):
        for ach in self.achievements:
            if not ach.unlocked and score >= ach.threshold:
                ach.unlocked = True
                self.unlocked.add(ach.title)
                self.popup_text = f"Conquista desbloqueada: {ach.title}"
                self.popup_time = time.time()

    def draw_popup(self):
        if self.popup_text:
            elapsed = time.time() - self.popup_time
            if elapsed > self.popup_duration:
                self.popup_text = ""
            else:
                w, h = 400, 50
                x = (self.screen.get_width() - w) // 2
                y = 80
                rect = pygame.Rect(x, y, w, h)
                pygame.draw.rect(self.screen, self.bg_color, rect, border_radius=12)
                pygame.draw.rect(self.screen, (200, 150, 150), rect, 2, border_radius=12)
                surf = self.font.render(self.popup_text, True, (60, 20, 60))
                self.screen.blit(surf, surf.get_rect(center=rect.center))

class AchievementsMenu:
    BADGE_RECT = pygame.Rect(50, 100, 160, 50)  # posição/size da badge

    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height

        self.font = pygame.font.SysFont(None, 26)
        self.title_font = pygame.font.SysFont(None, 36, bold=True)
        self.bg_color = (245, 225, 240)  
        self.text_color = (80, 0, 60)
        self.border_color = (180, 150, 180)

        self.visible = False
        self.details_visible = False
        self.tracker = None  # atribuído no app.py

    def draw(self):
        if not self.visible or not self.tracker:
            return

        if not self.details_visible:
            # Modo compacto
            badge = AchievementsMenu.BADGE_RECT
            pygame.draw.rect(self.screen, (255, 224, 230), badge, border_radius=8)
            pygame.draw.rect(self.screen, (200, 150, 170), badge, 2, border_radius=8)
            count = len(self.tracker.unlocked)
            txt = self.font.render(f"Conquistas: {count}", True, self.text_color)
            self.screen.blit(txt, txt.get_rect(center=badge.center))
        else:
            # Modo detalhado
            w, h = 500, 300
            x = (self.width - w) // 2
            y = (self.height - h) // 2
            rect = pygame.Rect(x, y, w, h)
            pygame.draw.rect(self.screen, self.bg_color, rect, border_radius=16)
            pygame.draw.rect(self.screen, self.border_color, rect, 2, border_radius=16)

            title = self.title_font.render("Conquistas", True, self.text_color)
            self.screen.blit(title, (x + 20, y + 20))

            start_y = y + 70
            line_h = 30
            for i, ach in enumerate(self.tracker.achievements):
                status = "✓" if ach.title in self.tracker.unlocked else "✗"
                color = (40, 180, 100) if status == "✓" else (120, 120, 120)
                line = f"{status} {ach.title}"
                self.screen.blit(self.font.render(line, True, color),
                                 (x + 30, start_y + i*line_h))
                desc = self.font.render(ach.description, True, (100, 100, 100))
                self.screen.blit(desc, (x + 50, start_y + i*line_h + 18))

    def handle_event(self, event):
        if not self.visible or not self.tracker:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            if not self.details_visible:
                # Abre detalhes ao clicar na badge
                if AchievementsMenu.BADGE_RECT.collidepoint(pos):
                    self.details_visible = True
                    return True
            else:
                # Fecha ao clicar fora do box detalhado
                w, h = 500, 300
                x = (self.width - w) // 2
                y = (self.height - h) // 2
                if not pygame.Rect(x, y, w, h).collidepoint(pos):
                    self.details_visible = False
                    self.visible = False
                    return True

        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if self.details_visible:
                self.details_visible = False
            else:
                self.visible = False
            return True

        return False
