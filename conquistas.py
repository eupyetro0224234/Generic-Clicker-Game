import pygame
import time

class Achievement:
    def __init__(self, id, name, description, threshold=-1):
        self.id = id
        self.name = name
        self.description = description
        self.threshold = threshold
        self.unlocked = False

class AchievementTracker:
    def __init__(self, screen):
        self.screen = screen
        self.achievements = [
            Achievement("first_click", "Primeiro Clique", "Dê seu primeiro clique", 1),
            Achievement("ten_clicks", "10 Cliques", "Alcance 10 cliques", 10),
            Achievement("hundred_points", "100 Pontos", "Chegue a 100 pontos", 100),
            Achievement("console", "Ativar Console", "Você descobriu o console secreto!")  # conquista secreta
        ]
        self.unlocked = set()
        self.popup_text = ""
        self.popup_time = 0.0
        self.popup_duration = 3.0
        self.font = pygame.font.SysFont(None, 28)
        self.bg_color = (255, 192, 203)

    def load_unlocked(self, saved_ids):
        for ach in self.achievements:
            if ach.id in saved_ids:
                ach.unlocked = True
                self.unlocked.add(ach.id)

    def check_unlock(self, score):
        for ach in self.achievements:
            if not ach.unlocked and ach.threshold > 0 and score >= ach.threshold:
                ach.unlocked = True
                self.unlocked.add(ach.id)
                self.popup_text = f"Conquista desbloqueada: {ach.name}"
                self.popup_time = time.time()

    def unlock_secret(self, id):
        for ach in self.achievements:
            if ach.id == id and not ach.unlocked:
                ach.unlocked = True
                self.unlocked.add(ach.id)
                self.popup_text = f"Conquista desbloqueada: {ach.name}"
                self.popup_time = time.time()

    def unlock_console_achievement(self):
        self.unlock_secret("console")

    def reset_achievements(self):
        """Reseta todas as conquistas."""
        for ach in self.achievements:
            ach.unlocked = False
        self.unlocked.clear()
        self.popup_text = "Conquistas resetadas!"
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
        self.achievements = []  # Lista de Achievement
        self.unlocked = set()

        self.bg_color = (245, 225, 240)
        self.text_color = (60, 0, 60)
        self.border_color = (180, 150, 180)
        self.title_font = pygame.font.SysFont(None, 36, bold=True)
        self.font = pygame.font.SysFont(None, 24)
        self.desc_font = pygame.font.SysFont(None, 20)

        # Layout
        self.box_width = 560
        self.box_height = 340
        self.padding = 20
        self.line_height = 55
        self.box_color = (230, 210, 230)
        self.unlocked_color = (40, 180, 100)
        self.lock_color = (120, 120, 120)

    def update(self, tracker):
        """Atualiza as conquistas com base no estado do AchievementTracker."""
        self.achievements = tracker.achievements
        self.unlocked = tracker.unlocked

    def draw(self):
        if not self.visible:
            return

        x = (self.width - self.box_width) // 2
        y = (self.height - self.box_height) // 2
        box = pygame.Rect(x, y, self.box_width, self.box_height)
        pygame.draw.rect(self.screen, self.bg_color, box, border_radius=16)
        pygame.draw.rect(self.screen, self.border_color, box, 2, border_radius=16)

        title_surf = self.title_font.render("Conquistas", True, self.text_color)
        self.screen.blit(title_surf, (x + self.padding, y + self.padding))

        start_y = y + self.padding + 50

        # Mostra somente conquistas normais ou as secretas desbloqueadas
        shown_achievements = [
            ach for ach in self.achievements if ach.unlocked or ach.threshold >= 0
        ]

        for i, ach in enumerate(shown_achievements):
            ach_y = start_y + i * self.line_height

            ach_rect = pygame.Rect(x + self.padding, ach_y, self.box_width - 2 * self.padding, self.line_height - 10)
            pygame.draw.rect(self.screen, self.box_color, ach_rect, border_radius=12)

            border_col = self.unlocked_color if ach.id in self.unlocked else self.lock_color
            pygame.draw.rect(self.screen, border_col, ach_rect, 2, border_radius=12)

            icon = "✓" if ach.id in self.unlocked else "🔒"
            icon_color = self.unlocked_color if ach.id in self.unlocked else self.lock_color
            icon_surf = self.font.render(icon, True, icon_color)
            icon_rect = icon_surf.get_rect()
            icon_rect.centery = ach_rect.centery
            icon_rect.left = ach_rect.left + 15
            self.screen.blit(icon_surf, icon_rect)

            name_color = self.unlocked_color if ach.id in self.unlocked else self.lock_color
            name_surf = self.font.render(ach.name, True, name_color)
            name_rect = name_surf.get_rect()
            name_rect.topleft = (icon_rect.right + 15, ach_rect.top + 10)
            self.screen.blit(name_surf, name_rect)

            desc_color = (180, 180, 200) if ach.id in self.unlocked else (110, 110, 130)
            desc_surf = self.desc_font.render(ach.description, True, desc_color)
            desc_rect = desc_surf.get_rect()
            desc_rect.topleft = (icon_rect.right + 15, name_rect.bottom + 4)
            self.screen.blit(desc_surf, desc_rect)

    def handle_event(self, event):
        if not self.visible:
            return False
        if event.type == pygame.MOUSEBUTTONDOWN:
            x = (self.width - self.box_width) // 2
            y = (self.height - self.box_height) // 2
            if not pygame.Rect(x, y, self.box_width, self.box_height).collidepoint(event.pos):
                self.visible = False
                return True
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.visible = False
            return True
        return False
