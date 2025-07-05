import pygame
import time

class AchievementsMenu:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height

        self.visible = False

        # Dicionário das conquistas: id, (nome, descrição)
        self.achievements = {
            "first_click": ("Primeiro Clique", "Você fez seu primeiro clique!"),
            "hundred_points": ("100 Pontos", "Você atingiu 100 pontos!"),
            "reset_score": ("Reset", "Você resetou sua pontuação."),
        }
        self.unlocked = set()

        # Variáveis para o aviso visual
        self.alert_active = False
        self.alert_start_time = 0
        self.alert_duration = 3  # duração em segundos
        self.alert_text = ""
        self.font = pygame.font.SysFont(None, 32)
        self.bg_color = (180, 210, 255)
        self.text_color = (40, 40, 60)
        self.box_rect = pygame.Rect(self.width//2 - 150, self.height//2 - 180, 300, 50)
    
    def load_achievements(self, unlocked_ids):
        self.unlocked = set(unlocked_ids)

    def get_unlocked_ids(self):
        return list(self.unlocked)

    def unlock(self, achievement_id):
        if achievement_id in self.achievements and achievement_id not in self.unlocked:
            self.unlocked.add(achievement_id)
            # Inicia o alerta visual
            self.alert_text = f"Conquista desbloqueada: {self.achievements[achievement_id][0]}"
            self.alert_active = True
            self.alert_start_time = time.time()
            return True
        return False

    def update_alert(self):
        if self.alert_active:
            elapsed = time.time() - self.alert_start_time
            if elapsed > self.alert_duration:
                self.alert_active = False

    def draw_alert(self):
        if not self.alert_active:
            return
        # Caixa semi-transparente arredondada
        s = pygame.Surface((self.box_rect.width, self.box_rect.height), pygame.SRCALPHA)
        s.fill((self.bg_color[0], self.bg_color[1], self.bg_color[2], 230))
        pygame.draw.rect(s, self.bg_color, s.get_rect(), border_radius=12)
        self.screen.blit(s, self.box_rect.topleft)

        # Texto centralizado
        text_surface = self.font.render(self.alert_text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.box_rect.center)
        self.screen.blit(text_surface, text_rect)

    # Caso queira implementar tela completa de conquistas
    def draw(self):
        if self.visible:
            pass  # Implemente interface detalhada aqui

    def handle_event(self, event):
        if not self.visible:
            return False
        return False
