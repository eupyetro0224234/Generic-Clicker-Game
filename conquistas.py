import pygame
import time
import os

class Achievement:
    def __init__(self, id, name, description, threshold=-1):
        self.id = id
        self.name = name
        self.description = description
        self.threshold = threshold
        self.unlocked = False
        self.show_time = 0
        self.animation_state = 0
        self.animation_progress = 0

class AchievementTracker:
    def __init__(self, screen):
        self.screen = screen
        self.achievements = [
            Achievement("first_click", "Primeiro Clique", "Dê seu primeiro clique", 1),
            Achievement("ten_clicks", "10 Cliques", "Alcance 10 cliques", 10),
            Achievement("hundred_points", "100 Pontos", "Chegue a 100 pontos", 100),
            Achievement("console", "Ativar Console", "Você descobriu o console secreto!"),
            Achievement("mini_event_1", "Mini Evento: Primeiro Clique", "Clique pela primeira vez no mini evento", 1),
            Achievement("mini_event_10", "Mini Evento: 10 Cliques", "Clique 10 vezes no mini evento", 10),
            Achievement("mini_event_100", "Mini Evento: 100 Cliques", "Clique 100 vezes no mini evento", 100),
            Achievement(
                "manual_phase",
                "Antes de Automação, vem a fase manual",
                "Compre o upgrade de clique manual (segurar botão)"
            ),
            Achievement(
                "perfeicao_15",
                "Perfeição 1.5",
                "Complete todas as conquistas"
            )
        ]
        self.unlocked = set()
        self.achievement_queue = []
        self.current_achievement = None
        self.font = pygame.font.SysFont("Arial", 24, bold=True)
        self.desc_font = pygame.font.SysFont("Arial", 18)
        self.icon_font = pygame.font.SysFont("Segoe UI Emoji", 30)
        self.sound = None
        self.animation_speed = 0.08
        self.popup_duration = 3.0
        self.normal_clicks = 0
        self.mini_event_clicks = 0

    def load_sound(self):
        try:
            localappdata = os.getenv("LOCALAPPDATA") or "."
            sound_path = os.path.join(localappdata, ".assets", "complete-quest.ogg")
            self.sound = pygame.mixer.Sound(sound_path)
        except Exception:
            pass

    def load_unlocked(self, saved_ids):
        for ach in self.achievements:
            if ach.id in saved_ids:
                ach.unlocked = True
                self.unlocked.add(ach.id)

    def add_normal_click(self):
        self.normal_clicks += 1
        self._check_click_achievements("normal")

    def add_mini_event_click(self):
        self.mini_event_clicks += 1
        self._check_click_achievements("mini_event")

    def _check_click_achievements(self, click_type):
        new_achievements = []
        for ach in self.achievements:
            if ach.unlocked:
                continue
            if click_type == "normal":
                if ach.id == "first_click" and self.normal_clicks >= 1:
                    ach.unlocked = True
                elif ach.id == "ten_clicks" and self.normal_clicks >= 10:
                    ach.unlocked = True
            elif click_type == "mini_event":
                if ach.id == "mini_event_1" and self.mini_event_clicks >= 1:
                    ach.unlocked = True
                elif ach.id == "mini_event_10" and self.mini_event_clicks >= 10:
                    ach.unlocked = True
                elif ach.id == "mini_event_100" and self.mini_event_clicks >= 100:
                    ach.unlocked = True
            if ach.unlocked:
                self.unlocked.add(ach.id)
                new_achievements.append(ach)
        if new_achievements:
            self.achievement_queue.extend(new_achievements)
            self._start_next_achievement()
            self.check_all_achievements_completed()

    def check_unlock(self, score):
        new_achievements = []
        for ach in self.achievements:
            if not ach.unlocked and ach.id == "hundred_points" and score >= ach.threshold:
                ach.unlocked = True
                self.unlocked.add(ach.id)
                new_achievements.append(ach)
        if new_achievements:
            self.achievement_queue.extend(new_achievements)
            self._start_next_achievement()
            self.check_all_achievements_completed()

    def unlock_secret(self, id):
        for ach in self.achievements:
            if ach.id == id and not ach.unlocked:
                ach.unlocked = True
                self.unlocked.add(ach.id)
                self.achievement_queue.append(ach)
                self._start_next_achievement()
                self.check_all_achievements_completed()

    def check_all_achievements_completed(self):
        all_unlocked = all(
            ach.unlocked for ach in self.achievements if ach.id != "perfeicao_15"
        )
        perfeicao_ach = next((ach for ach in self.achievements if ach.id == "perfeicao_15"), None)
        if all_unlocked and perfeicao_ach and not perfeicao_ach.unlocked:
            perfeicao_ach.unlocked = True
            self.unlocked.add("perfeicao_15")
            self.achievement_queue.append(perfeicao_ach)
            self._start_next_achievement()

    def _start_next_achievement(self):
        if self.current_achievement is None and self.achievement_queue:
            self.current_achievement = self.achievement_queue.pop(0)
            self.current_achievement.show_time = time.time()
            self.current_achievement.animation_state = 1
            self.current_achievement.animation_progress = 0
            if self.sound:
                self.sound.play()

    def _update_animation(self):
        if self.current_achievement:
            ach = self.current_achievement
            if ach.animation_state == 1:
                ach.animation_progress += self.animation_speed
                if ach.animation_progress >= 1:
                    ach.animation_progress = 1
                    ach.animation_state = 2
            elif ach.animation_state == 2:
                if time.time() - ach.show_time > self.popup_duration:
                    ach.animation_state = 3
            elif ach.animation_state == 3:
                ach.animation_progress -= self.animation_speed
                if ach.animation_progress <= 0:
                    ach.animation_progress = 0
                    ach.animation_state = 0
                    self.current_achievement = None
                    self._start_next_achievement()

    def draw_popup(self):
        self._update_animation()

        if not self.current_achievement or self.current_achievement.animation_state == 0:
            return

        ach = self.current_achievement
        eased_progress = 1 - (1 - ach.animation_progress) ** 2
        alpha = int(eased_progress * 255)

        popup_text = f"Conquista desbloqueada: {ach.name}"
        font = pygame.font.SysFont("Arial", 28, bold=True)
        text_surface = font.render(popup_text, True, (47, 24, 63))
        text_width = text_surface.get_width()
        text_height = text_surface.get_height()

        padding_x = 35
        padding_y = 18
        w = text_width + padding_x * 2
        h = text_height + padding_y
        x = (self.screen.get_width() - w) // 2
        y = int(25 + (1 - eased_progress) * 20)

        shadow_offset = 5
        shadow_surface = pygame.Surface((w + shadow_offset, h + shadow_offset), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, (150, 120, 130, alpha // 2), (shadow_offset, shadow_offset, w, h), border_radius=20)
        self.screen.blit(shadow_surface, (x - 3, y - 3))

        popup_surface = pygame.Surface((w, h), pygame.SRCALPHA)

        bg_color = (230, 178, 186, alpha)
        pygame.draw.rect(popup_surface, bg_color, (0, 0, w, h), border_radius=20)

        border_color = (190, 100, 110, alpha)
        pygame.draw.rect(popup_surface, border_color, (0, 0, w, h), 2, border_radius=20)

        popup_surface.blit(text_surface, ((w - text_width) // 2, (h - text_height) // 2))

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

        self.bg_color = (235, 225, 240, 230)
        self.box_color = (255, 255, 255)
        self.text_color = (40, 50, 70)
        self.border_color = (180, 190, 210)
        self.unlocked_color = (45, 160, 90)
        self.locked_color = (160, 160, 160)
        self.shadow_color = (0, 0, 0, 25)

        self.title_font = pygame.font.SysFont("Arial", 32)
        self.item_font = pygame.font.SysFont("Arial", 20)
        self.desc_font = pygame.font.SysFont("Arial", 16)
        self.icon_font = pygame.font.SysFont("Segoe UI Emoji", 28)

        self.radius = 12

    def update(self, tracker):
        self.achievements = tracker.achievements
        self.unlocked = tracker.unlocked

    def draw(self):
        if not self.visible:
            return

        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill(self.bg_color)
        self.screen.blit(overlay, (0, 0))

        show_hidden = False
        if self.config_menu and hasattr(self.config_menu, 'settings_menu'):
            show_hidden = self.config_menu.settings_menu.get_option("Mostrar conquistas ocultas")

        filtered = [a for a in self.achievements if a.unlocked or show_hidden]

        cols = 2
        spacing_x = 30
        spacing_y = 20
        card_width = (self.width - spacing_x * (cols + 1)) // cols
        card_height = 60
        start_y = 90

        for i, ach in enumerate(filtered):
            row = i // cols
            col = i % cols
            x = spacing_x + col * (card_width + spacing_x)
            y = start_y + row * (card_height + spacing_y)

            rect = pygame.Rect(x, y, card_width, card_height)

            border_color = self.unlocked_color if ach.unlocked else self.locked_color
            bg_color = (250, 245, 255) if ach.unlocked else (240, 230, 245)

            pygame.draw.rect(self.screen, bg_color, rect, border_radius=self.radius)
            pygame.draw.rect(self.screen, border_color, rect, 2, border_radius=self.radius)

            icon = "⭐" if ach.unlocked else "☆"
            icon_surf = self.icon_font.render(icon, True, border_color)
            self.screen.blit(icon_surf, (rect.left + 10, rect.top + 8))

            name_color = self.text_color if ach.unlocked else self.locked_color
            name_surf = self.item_font.render(ach.name, True, name_color)
            desc_color = (110, 110, 110) if ach.unlocked else (140, 140, 140)
            desc_surf = self.desc_font.render(ach.description, True, desc_color)

            max_text_width = card_width - 60

            if name_surf.get_width() > max_text_width:
                trimmed = ach.name
                while name_surf.get_width() > max_text_width and len(trimmed) > 0:
                    trimmed = trimmed[:-1]
                    name_surf = self.item_font.render(trimmed + "…", True, name_color)

            if desc_surf.get_width() > max_text_width:
                trimmed = ach.description
                while desc_surf.get_width() > max_text_width and len(trimmed) > 0:
                    trimmed = trimmed[:-1]
                    desc_surf = self.desc_font.render(trimmed + "…", True, desc_color)

            self.screen.blit(name_surf, (rect.left + 45, rect.top + 6))
            self.screen.blit(desc_surf, (rect.left + 45, rect.top + 30))

        title_text = "🏆 Conquistas"
        title_surf = self.title_font.render(title_text, True, (60, 50, 80))
        self.screen.blit(title_surf, (self.width // 2 - title_surf.get_width() // 2, 25))

    def handle_event(self, event):
        if not self.visible:
            return False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.visible = False
            return True
        if event.type == pygame.MOUSEBUTTONDOWN:
            return True
        return False