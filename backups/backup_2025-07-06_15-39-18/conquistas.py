import pygame
import time

class Achievement:
    def __init__(self, title, threshold):
        self.title = title
        self.threshold = threshold

class AchievementTracker:
    def __init__(self, screen):
        self.screen = screen
        self.achievements = [
            Achievement("Primeiro Clique!", 1),
            Achievement("10 Cliques!", 10),
            Achievement("50 Cliques!", 50),
            Achievement("100 Cliques!", 100),
            Achievement("500 Cliques!", 500),
        ]
        self.unlocked = set()
        self.popup_message = ""
        self.popup_timer = 0
        self.font = pygame.font.SysFont(None, 28)
        self.bg_color = (255, 192, 203)  # Rosa claro

    def check(self, score):
        for ach in self.achievements:
            if ach.title not in self.unlocked and score >= ach.threshold:
                self.unlocked.add(ach.title)
                self.popup_message = f"Conquista desbloqueada: {ach.title}"
                self.popup_timer = time.time()

    def draw_popup(self, screen):
        if self.popup_message and time.time() - self.popup_timer < 3.5:
            width = 400
            height = 60
            x = (screen.get_width() - width) // 2
            y = 120
            pygame.draw.rect(screen, self.bg_color, (x, y, width, height), border_radius=12)
            pygame.draw.rect(screen, (200, 150, 150), (x, y, width, height), 2, border_radius=12)

            text = self.font.render(self.popup_message, True, (60, 20, 60))
            screen.blit(text, text.get_rect(center=(x + width // 2, y + height // 2)))
        elif self.popup_message:
            self.popup_message = ""

class AchievementsMenu:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        self.visible = False
        self.tracker = None  # será atribuído pelo menu principal
        self.font = pygame.font.SysFont(None, 30)
        self.title_font = pygame.font.SysFont(None, 40)
        self.bg_color = (250, 235, 250)

    def draw(self):
        if not self.visible or not self.tracker:
            return

        padding = 20
        box_width = 500
        box_height = 300
        box_x = (self.width - box_width) // 2
        box_y = (self.height - box_height) // 2

        pygame.draw.rect(self.screen, self.bg_color, (box_x, box_y, box_width, box_height), border_radius=16)
        pygame.draw.rect(self.screen, (180, 150, 200), (box_x, box_y, box_width, box_height), 2, border_radius=16)

        title = self.title_font.render("Conquistas", True, (60, 30, 90))
        self.screen.blit(title, (box_x + 20, box_y + 20))

        for i, ach in enumerate(self.tracker.achievements):
            status = "✓" if ach.title in self.tracker.unlocked else "✗"
            text = f"{status} {ach.title}"
            color = (40, 180, 100) if status == "✓" else (120, 120, 120)
            ach_surf = self.font.render(text, True, color)
            self.screen.blit(ach_surf, (box_x + 30, box_y + 70 + i * 35))

    def handle_event(self, event):
        # Pode implementar fechar com ESC futuramente
        return False
