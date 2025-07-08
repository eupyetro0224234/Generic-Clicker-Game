import pygame
import time
import os
import math

class Achievement:
    def __init__(self, id, name, description, threshold=-1):
        self.id = id
        self.name = name
        self.description = description
        self.threshold = threshold
        self.unlocked = False
        self.show_time = 0
        self.animation_state = 0  # 0=escondido, 1=entrando, 2=visível, 3=saindo
        self.animation_progress = 0  # 0 a 1

class AchievementTracker:
    def __init__(self, screen):
        self.screen = screen
        self.achievements = [
            Achievement("first_click", "Primeiro Clique", "Dê seu primeiro clique", 1),
            Achievement("ten_clicks", "10 Cliques", "Alcance 10 cliques", 10),
            Achievement("hundred_points", "100 Pontos", "Chegue a 100 pontos", 100),
            Achievement("console", "Ativar Console", "Você descobriu o console secreto!")
        ]
        self.unlocked = set()
        self.achievement_queue = []
        self.current_achievement = None
        self.font = pygame.font.SysFont(None, 28)
        self.bg_color = (255, 192, 203)
        self.sound = None
        self.animation_speed = 0.05
        self.popup_duration = 3.0  # 3 segundos visível

    def load_sound(self):
        try:
            localappdata = os.getenv("LOCALAPPDATA") or "."
            sound_path = os.path.join(localappdata, ".assets", "complete-quest.ogg")
            self.sound = pygame.mixer.Sound(sound_path)
        except Exception as e:
            print(f"Erro ao carregar som de conquista: {e}")

    def load_unlocked(self, saved_ids):
        for ach in self.achievements:
            if ach.id in saved_ids:
                ach.unlocked = True
                self.unlocked.add(ach.id)

    def check_unlock(self, score):
        new_achievements = []
        for ach in self.achievements:
            if not ach.unlocked and ach.threshold > 0 and score >= ach.threshold:
                ach.unlocked = True
                self.unlocked.add(ach.id)
                new_achievements.append(ach)
        
        if new_achievements:
            self.achievement_queue.extend(new_achievements)
            self._start_next_achievement()

    def unlock_secret(self, id):
        for ach in self.achievements:
            if ach.id == id and not ach.unlocked:
                ach.unlocked = True
                self.unlocked.add(ach.id)
                self.achievement_queue.append(ach)
                self._start_next_achievement()

    def _start_next_achievement(self):
        if self.current_achievement is None and self.achievement_queue:
            self.current_achievement = self.achievement_queue.pop(0)
            self.current_achievement.show_time = time.time()
            self.current_achievement.animation_state = 1  # Entrando
            self.current_achievement.animation_progress = 0
            if self.sound:
                self.sound.play()

    def _update_animation(self):
        if self.current_achievement:
            ach = self.current_achievement
            
            if ach.animation_state == 1:  # Entrando
                ach.animation_progress += self.animation_speed
                if ach.animation_progress >= 1:
                    ach.animation_progress = 1
                    ach.animation_state = 2  # Visível
            
            elif ach.animation_state == 2:  # Visível
                if time.time() - ach.show_time > self.popup_duration:
                    ach.animation_state = 3  # Saindo
            
            elif ach.animation_state == 3:  # Saindo
                ach.animation_progress -= self.animation_speed
                if ach.animation_progress <= 0:
                    ach.animation_progress = 0
                    ach.animation_state = 0  # Escondido
                    self.current_achievement = None
                    self._start_next_achievement()

    def draw_popup(self):
        self._update_animation()
        
        if not self.current_achievement or self.current_achievement.animation_state == 0:
            return

        ach = self.current_achievement
        alpha = int(ach.animation_progress * 255)
        
        w, h = 460, 50
        x = (self.screen.get_width() - w) // 2
        y = 80
        
        popup_surface = pygame.Surface((w, h), pygame.SRCALPHA)
        
        bg_with_alpha = (*self.bg_color, alpha)
        pygame.draw.rect(popup_surface, bg_with_alpha, (0, 0, w, h), border_radius=12)
        pygame.draw.rect(popup_surface, (200, 150, 150, alpha), (0, 0, w, h), 2, border_radius=12)
        
        text_color = (60, 20, 60, alpha)
        text_surf = self.font.render(f"Conquista desbloqueada: {ach.name}", True, text_color)
        text_rect = text_surf.get_rect(center=(w//2, h//2))
        popup_surface.blit(text_surf, text_rect)
        
        self.screen.blit(popup_surface, (x, y))

class AchievementsMenu:
    def __init__(self, screen, width, height, config_menu=None):
        self.screen = screen
        self.width = width
        self.height = height
        self.visible = False
        self.achievements = []
        self.unlocked = set()
        self.config_menu = config_menu
        self.bg_color = (245, 225, 240)
        self.text_color = (60, 0, 60)
        self.border_color = (180, 150, 180)
        self.title_font = pygame.font.SysFont(None, 36, bold=True)
        self.font = pygame.font.SysFont(None, 24)
        self.desc_font = pygame.font.SysFont(None, 20)
        self.box_width = 560
        self.box_height = 340
        self.padding = 20
        self.line_height = 55
        self.box_color = (230, 210, 230)
        self.unlocked_color = (40, 180, 100)
        self.lock_color = (120, 120, 120)
        self.hidden_color = (150, 150, 150)

    def update(self, tracker):
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
        
        # Verifica se deve mostrar conquistas ocultas
        show_hidden = False
        if self.config_menu and hasattr(self.config_menu, 'settings_menu'):
            show_hidden = self.config_menu.settings_menu.get_option("Mostrar conquistas ocultas")
        
        # Filtra conquistas para mostrar
        shown_achievements = [
            ach for ach in self.achievements 
            if show_hidden or ach.unlocked
        ]

        for i, ach in enumerate(shown_achievements):
            ach_y = start_y + i * self.line_height
            ach_rect = pygame.Rect(x + self.padding, ach_y, self.box_width - 2 * self.padding, self.line_height - 10)
            pygame.draw.rect(self.screen, self.box_color, ach_rect, border_radius=12)
            
            # Define cores com base no status
            if ach.unlocked:
                border_col = self.unlocked_color
                icon = "✓"
                icon_color = self.unlocked_color
                name_color = self.unlocked_color
                desc_color = (180, 180, 200)
            else:
                border_col = self.hidden_color
                icon = "?"
                icon_color = self.hidden_color
                name_color = self.hidden_color
                desc_color = (110, 110, 130)

            pygame.draw.rect(self.screen, border_col, ach_rect, 2, border_radius=12)

            # Renderiza ícone
            icon_surf = self.font.render(icon, True, icon_color)
            icon_rect = icon_surf.get_rect()
            icon_rect.centery = ach_rect.centery
            icon_rect.left = ach_rect.left + 15
            self.screen.blit(icon_surf, icon_rect)

            # Renderiza nome
            name_surf = self.font.render(ach.name, True, name_color)
            name_rect = name_surf.get_rect()
            name_rect.topleft = (icon_rect.right + 15, ach_rect.top + 10)
            self.screen.blit(name_surf, name_rect)

            # Renderiza descrição
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