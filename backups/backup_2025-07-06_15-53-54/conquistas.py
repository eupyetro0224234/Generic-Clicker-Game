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
            Achievement("100 Pontos", "Chegue a 100 pontos", 100),
        ]
        self.unlocked = set()
        self.popup_text = ""
        self.popup_time = 0
        self.popup_duration = 3.0
        self.font = pygame.font.SysFont(None, 28)
        self.bg_color = (255, 192, 203)  # rosa claro

    def load_unlocked(self, titles: list[str]):
        for ach in self.achievements:
            if ach.title in titles:
                ach.unlocked = True
                self.unlocked.add(ach.title)

    def check(self, score):
        for ach in self.achievements:
            if not ach.unlocked and score >= ach.threshold:
                ach.unlocked = True
                self.unlocked.add(ach.title)
                self.popup_text = f"Conquista desbloqueada: {ach.title}"
                self.popup_time = time.time()

    def draw_popup(self):
        if not self.popup_text:
            return
        elapsed = time.time() - self.popup_time
        if elapsed > self.popup_duration:
            self.popup_text = ""
            return

        w, h = 460, 50
        x = (self.screen.get_width() - w) // 2
        y = 80
        rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(self.screen, self.bg_color, rect, border_radius=12)
        pygame.draw.rect(self.screen, (200, 150, 150), rect, 2, border_radius=12)
        surf = self.font.render(self.popup_text, True, (60, 20, 60))
        self.screen.blit(surf, surf.get_rect(center=rect.center))

class AchievementsMenu:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        self.visible = False
        self.tracker = None  # será definido no app.py

        self.title_font = pygame.font.SysFont(None, 36, bold=True)
        self.font = pygame.font.SysFont(None, 24)
        self.desc_font = pygame.font.SysFont(None, 20)
        self.bg_color = (245, 225, 240)
        self.text_color = (60, 0, 60)
        self.border_color = (180, 150, 180)

    def draw(self):
        if not self.visible or not self.tracker:
            return

        w, h = 560, 340
        x = (self.width - w) // 2
        y = (self.height - h) // 2
        box = pygame.Rect(x, y, w, h)
        pygame.draw.rect(self.screen, self.bg_color, box, border_radius=16)
        pygame.draw.rect(self.screen, self.border_color, box, 2, border_radius=16)

        title = self.title_font.render("Conquistas", True, self.text_color)
        self.screen.blit(title, (x + 20, y + 20))

        start_y = y + 70
        spacing_y = 55

        for i, ach in enumerate(self.tracker.achievements):
            status = "✓" if ach.unlocked else "✗"
            status_color = (40, 180, 100) if ach.unlocked else (120, 120, 120)

            # Título da conquista
            title_text = f"{status} {ach.title}"
            title_surface = self.font.render(title_text, True, status_color)
            self.screen.blit(title_surface, (x + 30, start_y + i * spacing_y))

            # Descrição menor e mais clara
            desc_surface = self.desc_font.render(ach.description, True, (100, 100, 100))
            self.screen.blit(desc_surface, (x + 50, start_y + i * spacing_y + 25))

    def handle_event(self, event):
        if not self.visible:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN:
            # Fecha se clicar fora da janela
            w, h = 560, 340
            x = (self.width - w) // 2
            y = (self.height - h) // 2
            if not pygame.Rect(x, y, w, h).collidepoint(event.pos):
                self.visible = False
                return True

        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.visible = False
            return True

        return False
