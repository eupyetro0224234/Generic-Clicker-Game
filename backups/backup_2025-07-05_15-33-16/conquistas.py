import pygame
import time

class AchievementsMenu:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        self.font = pygame.font.SysFont(None, 28)
        self.visible = False

        self.achievements = []  # conquistas desbloqueadas (strings)
        self.new_achievement = None
        self.new_achievement_time = 0
        self.achievement_display_duration = 3.0  # segundos

    def add_achievement(self, achievement_name):
        if achievement_name not in self.achievements:
            self.achievements.append(achievement_name)
            self.new_achievement = achievement_name
            self.new_achievement_time = time.time()

    def draw(self):
        if not self.visible:
            return

        # Desenhar lista de conquistas no menu (exemplo simples)
        bg_rect = pygame.Rect(50, 50, self.width - 100, self.height - 100)
        pygame.draw.rect(self.screen, (255, 240, 245), bg_rect, border_radius=10)  # fundo rosa bem claro
        pygame.draw.rect(self.screen, (255, 105, 180), bg_rect, 3, border_radius=10)  # borda rosa

        title = self.font.render("Conquistas", True, (120, 0, 60))
        self.screen.blit(title, (bg_rect.x + 20, bg_rect.y + 20))

        for i, ach in enumerate(self.achievements):
            text = self.font.render(f"• {ach}", True, (80, 0, 40))
            self.screen.blit(text, (bg_rect.x + 40, bg_rect.y + 60 + i * 30))

        # Desenho da notificação rosa claro no canto inferior esquerdo
        if self.new_achievement:
            elapsed = time.time() - self.new_achievement_time
            if elapsed < self.achievement_display_duration:
                notif_width, notif_height = 300, 50
                notif_x = 20
                notif_y = self.height - notif_height - 20
                notif_rect = pygame.Rect(notif_x, notif_y, notif_width, notif_height)
                pygame.draw.rect(self.screen, (255, 182, 193), notif_rect, border_radius=12)  # rosa claro fundo
                pygame.draw.rect(self.screen, (255, 105, 180), notif_rect, 3, border_radius=12)  # borda rosa forte

                notif_text = self.font.render(f"Conquista desbloqueada: {self.new_achievement}", True, (120, 0, 60))
                text_rect = notif_text.get_rect(center=notif_rect.center)
                self.screen.blit(notif_text, text_rect)
            else:
                self.new_achievement = None
