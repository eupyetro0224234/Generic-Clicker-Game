import pygame
import time

class AchievementsMenu:
    def __init__(self, screen, window_width, window_height):
        self.screen = screen
        self.width = window_width
        self.height = window_height

        self.font = pygame.font.SysFont(None, 28)
        self.bg_color = (245, 225, 240)  # rosa claro para fundo do menu
        self.text_color = (80, 0, 60)    # rosa escuro para texto
        self.border_color = (200, 150, 190)

        self.visible = False

        self.achievements = []  # lista de conquistas desbloqueadas

        # Aviso para conquistas desbloqueadas
        self.showing_achievement = False
        self.achievement_text = ""
        self.achievement_start_time = 0
        self.achievement_duration = 3  # segundos

    def add_achievement(self, achievement_name):
        if achievement_name not in self.achievements:
            self.achievements.append(achievement_name)
            self.achievement_text = f"Conquista desbloqueada: {achievement_name}!"
            self.showing_achievement = True
            self.achievement_start_time = time.time()

    def draw(self):
        # Desenha menu de conquistas
        if self.visible:
            menu_w = 300
            menu_h = 400
            menu_x = (self.width - menu_w) // 2
            menu_y = (self.height - menu_h) // 2

            menu_rect = pygame.Rect(menu_x, menu_y, menu_w, menu_h)
            pygame.draw.rect(self.screen, self.bg_color, menu_rect, border_radius=15)
            pygame.draw.rect(self.screen, self.border_color, menu_rect, width=3, border_radius=15)

            title_surf = self.font.render("Conquistas", True, self.text_color)
            title_rect = title_surf.get_rect(center=(menu_x + menu_w//2, menu_y + 30))
            self.screen.blit(title_surf, title_rect)

            # Lista de conquistas
            start_y = menu_y + 70
            line_height = 30
            for i, ach in enumerate(self.achievements):
                ach_surf = self.font.render(f"- {ach}", True, self.text_color)
                self.screen.blit(ach_surf, (menu_x + 20, start_y + i * line_height))

        # Desenha aviso temporário de conquista (caixa rosa)
        if self.showing_achievement:
            now = time.time()
            if now - self.achievement_start_time > self.achievement_duration:
                self.showing_achievement = False
            else:
                # Caixa rosa clara no topo
                box_w, box_h = 380, 50
                box_x = (self.width - box_w) // 2
                box_y = 10

                box_rect = pygame.Rect(box_x, box_y, box_w, box_h)
                pygame.draw.rect(self.screen, (255, 192, 203), box_rect, border_radius=12)  # rosa claro

                text_surf = self.font.render(self.achievement_text, True, (100, 0, 70))  # rosa escuro
                text_rect = text_surf.get_rect(center=box_rect.center)
                self.screen.blit(text_surf, text_rect)

    def handle_event(self, event):
        # Fecha menu com ESC ou clique fora do menu
        if not self.visible:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.visible = False
                return True

        if event.type == pygame.MOUSEBUTTONDOWN:
            # Fecha se clicar fora da área do menu
            menu_w = 300
            menu_h = 400
            menu_x = (self.width - menu_w) // 2
            menu_y = (self.height - menu_h) // 2
            menu_rect = pygame.Rect(menu_x, menu_y, menu_w, menu_h)
            if not menu_rect.collidepoint(event.pos):
                self.visible = False
                return True

        return False
