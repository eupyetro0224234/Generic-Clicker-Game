import pygame, time, os, sys, pytz, io
from datetime import datetime
from game_assets.game_assets_packed import load_image_raw, load_image, load_sound

class Achievement:
    def __init__(self, id, name, description, threshold=-1):
        self.id = id
        self.name = name
        self.description = description
        self.threshold = threshold
        self.unlocked = False
        self.unlock_date = None
        self.show_time = 0
        self.animation_state = 0
        self.animation_progress = 0

class AchievementTracker:
    def __init__(self, screen, game=None):
        self.screen = screen
        self.game = game
        self.achievements = [
            Achievement("first_click", "Primeiro ponto", "Dê seu primeiro clique", 1),
            Achievement("hundred_points", "100 Pontos", "Chegue a cem pontos", 100),
            Achievement("thousand_points", "1.000 Pontos", "Chegue a mil pontos", 1000),
            Achievement("million_points", "1.000.000 Pontos", "Chegue a um milhão de pontos", 1000000),
            Achievement("billion_points", "1.000.000.000 Pontos", "Chegue a um bilhão de pontos (parabéns)", 1000000000),
            Achievement("console", "Ativar Console", "Você descobriu o console secreto!"),
            Achievement("mini_event_1", "Mini Evento: Primeiro Clique", "Clique pela primeira vez no mini evento", 1),
            Achievement("mini_event_10", "Mini Evento: 10 Cliques", "Clique 10 vezes no mini evento", 10),
            Achievement("mini_event_100", "Mini Evento: 100 Cliques", "Clique 100 vezes no mini evento", 100),
            Achievement("manual_phase", "Antes da automação, vem a fase manual", "Compre o upgrade Click ao Segurar"),
            Achievement("automatico", "Finalmente a fase da automação", "Compre o upgrade de auto click"),
            Achievement("triple_unlock", "Desbloqueio Triplo", "Desbloqueie 3 conquistas em 5 segundos"),
            Achievement("tudo_ativo", "Tudo Ativo", "Compre todos os upgrades disponíveis"),
            Achievement("sem_controles", "Determinação Inútil", "Tente clicar sem nenhum controle ativado"),
            Achievement("streak_3", "Três dias seguidos", "Acesse o jogo por 3 dias consecutivos", 3),
            Achievement("streak_10", "Dez dias seguidos", "Acesse o jogo por 10 dias consecutivos", 10),
            Achievement("streak_30", "Um mês de dedicação", "Acesse o jogo por 30 dias consecutivos", 30),
            Achievement("streak_100", "Cem dias invicto", "Acesse o jogo por 100 dias consecutivos", 100),
            Achievement("perfeicao_15", "Perfeição 1.5", "Complete todas as conquistas")
        ]
        self.unlocked = set()
        self.achievement_queue = []
        self.current_achievement = None
        self.font = pygame.font.SysFont("None", 100, bold=True)
        self.desc_font = pygame.font.SysFont("None", 100)
        self.icon_font = pygame.font.SysFont("Segoe UI Emoji", 30)
        self.sound = None
        self.achievement_sound = None
        self.animation_speed = 0.08
        self.popup_duration = 3.0
        self.normal_clicks = 0
        self.mini_event_clicks = 0
        
        self.last_unlock_time = None
        self.unlock_count = 0
        self.triple_unlock_triggered = False
        
        self.volume = 1.0
        self.load_sound()

    def set_volume(self, volume):
        self.volume = max(0.0, min(1.0, volume))
        if self.achievement_sound:
            try:
                self.achievement_sound.set_volume(self.volume)
            except Exception:
                pass

    def reset_achievements(self):
        self.unlocked.clear()
        for ach in self.achievements:
            ach.unlocked = False
            ach.unlock_date = None
            ach.show_time = 0
            ach.animation_state = 0
            ach.animation_progress = 0
        self.last_unlock_time = None
        self.unlock_count = 0
        self.triple_unlock_triggered = False
        self.achievement_queue = []
        self.current_achievement = None

    def load_sound(self):
        try:
            self.achievement_sound = load_sound("complete-quest.ogg")
            self.achievement_sound.set_volume(self.volume)
        except Exception:
            self.achievement_sound = None

    def load_unlocked(self, saved_data):
        for ach in self.achievements:
            ach.unlocked = False
            ach.unlock_date = None
        self.unlocked.clear()
        
        if not saved_data:
            return
            
        if isinstance(saved_data, dict):
            for ach_id, unlock_date in saved_data.items():
                for ach in self.achievements:
                    if ach.id == ach_id:
                        ach.unlocked = True
                        ach.unlock_date = unlock_date
                        self.unlocked.add(ach.id)
                        break
        elif isinstance(saved_data, list):
            for ach_id in saved_data:
                for ach in self.achievements:
                    if ach.id == ach_id:
                        ach.unlocked = True
                        ach.unlock_date = self._get_current_datetime()
                        self.unlocked.add(ach.id)
                        break

    def _get_current_datetime(self):
        tz_brasilia = pytz.timezone('America/Sao_Paulo')
        return datetime.now(tz_brasilia).strftime("%d/%m/%Y - %H:%M")

    def _check_triple_unlock(self):
        if self.triple_unlock_triggered:
            return
        current_time = time.time()
        if self.last_unlock_time is None:
            self.last_unlock_time = current_time
            self.unlock_count = 1
            return
        if current_time - self.last_unlock_time > 5:
            self.last_unlock_time = current_time
            self.unlock_count = 1
            return
        self.unlock_count += 1
        self.last_unlock_time = current_time
        if self.unlock_count >= 3:
            self._unlock_triple_achievement()

    def _unlock_triple_achievement(self):
        triple_ach = next((ach for ach in self.achievements if ach.id == "triple_unlock"), None)
        if triple_ach and not triple_ach.unlocked:
            triple_ach.unlocked = True
            triple_ach.unlock_date = self._get_current_datetime()
            self.unlocked.add("triple_unlock")
            self.achievement_queue.append(triple_ach)
            self._start_next_achievement()
            self.triple_unlock_triggered = True

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
                    ach.unlock_date = self._get_current_datetime()
            elif click_type == "mini_event":
                session_total = 0
                if self.game:
                    session_total = self.game.mini_event1_session + self.game.mini_event2_session
                if ach.id == "mini_event_1" and session_total >= 1:
                    ach.unlocked = True
                    ach.unlock_date = self._get_current_datetime()
                elif ach.id == "mini_event_10" and session_total >= 10:
                    ach.unlocked = True
                    ach.unlock_date = self._get_current_datetime()
                elif ach.id == "mini_event_100" and session_total >= 100:
                    ach.unlocked = True
                    ach.unlock_date = self._get_current_datetime()
            if ach.unlocked:
                self.unlocked.add(ach.id)
                new_achievements.append(ach)
        if new_achievements:
            self.achievement_queue.extend(new_achievements)
            self._start_next_achievement()
            for _ in new_achievements:
                self._check_triple_unlock()
            self.check_all_achievements_completed()

    def check_unlock(self, score):
        new_achievements = []
        for ach in self.achievements:
            if not ach.unlocked:
                if ach.id == "first_click" and score >= ach.threshold:
                    ach.unlocked = True
                    ach.unlock_date = self._get_current_datetime()
                elif ach.id == "hundred_points" and score >= ach.threshold:
                    ach.unlocked = True
                    ach.unlock_date = self._get_current_datetime()
                elif ach.id == "thousand_points" and score >= ach.threshold:
                    ach.unlocked = True
                    ach.unlock_date = self._get_current_datetime()
                elif ach.id == "million_points" and score >= ach.threshold:
                    ach.unlocked = True
                    ach.unlock_date = self._get_current_datetime()
                elif ach.id == "billion_points" and score >= ach.threshold:
                    ach.unlocked = True
                    ach.unlock_date = self._get_current_datetime()
                if ach.unlocked:
                    self.unlocked.add(ach.id)
                    new_achievements.append(ach)
        if new_achievements:
            self.achievement_queue.extend(new_achievements)
            self._start_next_achievement()
            for _ in new_achievements:
                self._check_triple_unlock()
            self.check_all_achievements_completed()
        return new_achievements

    def unlock_secret(self, id):
        for ach in self.achievements:
            if ach.id == id and not ach.unlocked:
                ach.unlocked = True
                ach.unlock_date = self._get_current_datetime()
                self.unlocked.add(ach.id)
                self.achievement_queue.append(ach)
                self._start_next_achievement()
                self._check_triple_unlock()
                self.check_all_achievements_completed()

    def try_unlock_sem_controles(self):
        self.unlock_secret("sem_controles")

    def check_streak_achievements(self, current_streak):
        streak_ids = {
            "streak_3":   3,
            "streak_10":  10,
            "streak_30":  30,
            "streak_100": 100,
        }
        new_achievements = []
        for ach in self.achievements:
            if ach.unlocked:
                continue
            threshold = streak_ids.get(ach.id)
            if threshold is not None and current_streak >= threshold:
                ach.unlocked = True
                ach.unlock_date = self._get_current_datetime()
                self.unlocked.add(ach.id)
                new_achievements.append(ach)
        if new_achievements:
            self.achievement_queue.extend(new_achievements)
            self._start_next_achievement()
            for _ in new_achievements:
                self._check_triple_unlock()
            self.check_all_achievements_completed()

    def check_all_upgrades_purchased(self, upgrade_menu):
        tudo_ativo_ach = next((ach for ach in self.achievements if ach.id == "tudo_ativo"), None)
        if tudo_ativo_ach and not tudo_ativo_ach.unlocked:
            required_upgrades = ["hold_click", "auto_click", "double", "mega", "mini_event"]
            all_purchased = all(upgrade_menu.purchased.get(uid, 0) > 0 for uid in required_upgrades)
            if all_purchased and len(upgrade_menu.trabalhadores) == 0:
                all_purchased = False
            if all_purchased:
                tudo_ativo_ach.unlocked = True
                tudo_ativo_ach.unlock_date = self._get_current_datetime()
                self.unlocked.add("tudo_ativo")
                self.achievement_queue.append(tudo_ativo_ach)
                self._start_next_achievement()
                self._check_triple_unlock()
                return True
        return False

    def check_all_achievements_completed(self):
        all_unlocked = all(ach.unlocked for ach in self.achievements if ach.id not in ("perfeicao_15", "console"))
        perfeicao_ach = next((ach for ach in self.achievements if ach.id == "perfeicao_15"), None)
        if all_unlocked and perfeicao_ach and not perfeicao_ach.unlocked:
            perfeicao_ach.unlocked = True
            perfeicao_ach.unlock_date = self._get_current_datetime()
            self.unlocked.add("perfeicao_15")
            self.achievement_queue.append(perfeicao_ach)
            self._start_next_achievement()

    def get_achievements_with_dates(self):
        achievements_dict = {}
        for ach in self.achievements:
            if ach.unlocked and ach.id in self.unlocked:
                if ach.unlock_date is None:
                    ach.unlock_date = self._get_current_datetime()
                achievements_dict[ach.id] = ach.unlock_date
        return achievements_dict

    def _start_next_achievement(self):
        if self.current_achievement is None and self.achievement_queue:
            self.current_achievement = self.achievement_queue.pop(0)
            self.current_achievement.show_time = time.time()
            self.current_achievement.animation_state = 1
            self.current_achievement.animation_progress = 0
            if self.achievement_sound:
                try:
                    self.achievement_sound.set_volume(self.volume)
                    self.achievement_sound.play()
                except Exception:
                    pass

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

    def _draw_rounded_rect_aa(self, surface, color, rect, radius):
        temp_surface = pygame.Surface((rect[2] + 4, rect[3] + 4), pygame.SRCALPHA)
        temp_surface.fill((0, 0, 0, 0))
        temp_rect = pygame.Rect(2, 2, rect[2], rect[3])
        pygame.draw.rect(temp_surface, color, temp_rect, border_radius=radius)
        surface.blit(temp_surface, (rect[0] - 2, rect[1] - 2))

    def _create_glass_popup(self, width, height, alpha):
        glass_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        glass_surface.fill((0, 0, 0, 0))
        bg_color = (230, 178, 186, int(alpha * 0.7))
        self._draw_rounded_rect_aa(glass_surface, bg_color, (0, 0, width, height), 20)
        highlight = pygame.Surface((width, height), pygame.SRCALPHA)
        highlight.fill((0, 0, 0, 0))
        for i in range(height):
            line_alpha = int((50 * (1 - i / height * 0.6)) * (alpha / 255))
            pygame.draw.line(highlight, (255, 255, 255, line_alpha), (0, i), (width, i))
        mask = pygame.Surface((width, height), pygame.SRCALPHA)
        mask.fill((0, 0, 0, 0))
        self._draw_rounded_rect_aa(mask, (255, 255, 255, 255), (0, 0, width, height), 20)
        highlight.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        glass_surface.blit(highlight, (0, 0))
        border_color = (190, 100, 110, int(alpha * 0.63))
        border_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        border_surface.fill((0, 0, 0, 0))
        pygame.draw.rect(border_surface, border_color, (0, 0, width, height), width=2, border_radius=20)
        glass_surface.blit(border_surface, (0, 0))
        return glass_surface

    def draw_popup(self):
        self._update_animation()
        if not self.current_achievement or self.current_achievement.animation_state == 0:
            return
        ach = self.current_achievement
        eased_progress = 1 - (1 - ach.animation_progress) ** 2
        alpha = int(eased_progress * 255)
        popup_text = f"Conquista desbloqueada: {ach.name}"
        font = pygame.font.SysFont("None", 28, bold=True)
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
        pygame.draw.rect(shadow_surface, (150, 120, 130, alpha // 2),
                         (shadow_offset, shadow_offset, w, h), border_radius=20)
        self.screen.blit(shadow_surface, (x - 3, y - 3))
        popup_surface = self._create_glass_popup(w, h, alpha)
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
        self.tracker = None
        
        self.bg_color = (255, 182, 193)
        self.text_color = (47, 24, 63)
        self.box_color = (255, 255, 255)
        self.border_color = (180, 190, 210)
        self.unlocked_color = (45, 160, 90)
        self.locked_color = (160, 160, 160)
        self.shadow_color = (0, 0, 0, 25)
        
        self.title_font = pygame.font.SysFont(None, 48)
        self.item_font = pygame.font.SysFont("None", 28, bold=True)
        self.desc_font = pygame.font.SysFont("None", 22)
        self.date_font = pygame.font.SysFont("None", 18)
        self.icon_font = pygame.font.SysFont("Segoe UI Emoji", 60)
        self.filter_font = pygame.font.SysFont("None", 18, bold=True)
        self.instruction_font = pygame.font.SysFont("None", 22)
        self.small_font = pygame.font.SysFont("None", 18)
        self.question_font = pygame.font.SysFont("None", 36, bold=True)
        self.radius = 20

        self.current_filter = "all"
        self.filter_buttons = []
        self._init_filter_buttons()
        
        self.close_button_rect = pygame.Rect(width - 80, 15, 40, 40)

        try:
            self.close_image = load_image("close.png")
            self.close_image = pygame.transform.smoothscale(self.close_image, (40, 40))
        except Exception:
            self.close_image = None

        self.current_page = 0
        self.achievements_per_page = 10
        self.page_button_size = 40

    def _init_filter_buttons(self):
        button_width = 130
        button_height = 40
        start_x = self.width // 2 - (3 * button_width + 2 * 15) // 2
        start_y = 85
        self.filter_buttons = [
            {"rect": pygame.Rect(start_x, start_y, button_width, button_height), "text": "Todas", "filter": "all", "active": True},
            {"rect": pygame.Rect(start_x + button_width + 15, start_y, button_width, button_height), "text": "Desbloqueadas", "filter": "unlocked", "active": False},
            {"rect": pygame.Rect(start_x + 2 * (button_width + 15), start_y, button_width, button_height), "text": "Bloqueadas", "filter": "locked", "active": False}
        ]

    def update(self, tracker):
        self.achievements = tracker.achievements
        self.unlocked = tracker.unlocked
        self.tracker = tracker

    def draw(self):
        if not self.visible:
            return
        self.screen.fill(self.bg_color)
        title_text = "Conquistas"
        title_surf = self.title_font.render(title_text, True, self.text_color)
        title_rect = title_surf.get_rect(center=(self.width // 2, 35))
        self.screen.blit(title_surf, title_rect)
        self._draw_filter_buttons()
        show_hidden = False
        if self.config_menu and hasattr(self.config_menu, 'settings_menu'):
            show_hidden = self.config_menu.settings_menu.get_option("Mostrar descrição de conquistas bloqueadas")
        filtered = self._get_filtered_achievements()
        total_pages = max(1, (len(filtered) + self.achievements_per_page - 1) // self.achievements_per_page)
        start_index = self.current_page * self.achievements_per_page
        end_index = min(start_index + self.achievements_per_page, len(filtered))
        current_page_achievements = filtered[start_index:end_index]
        card_width = 220
        card_height = 250
        spacing_x = 20
        spacing_y = 30
        max_cols = 5
        min_cols = 4
        total_width_for_5 = max_cols * card_width + (max_cols - 1) * spacing_x
        cols = max_cols if total_width_for_5 <= self.width - 40 else min_cols
        start_y = 150
        total_grid_width = cols * card_width + (cols - 1) * spacing_x
        start_x = (self.width - total_grid_width) // 2
        for i, ach in enumerate(current_page_achievements):
            row = i // cols
            col = i % cols
            x = start_x + col * (card_width + spacing_x)
            y = start_y + row * (card_height + spacing_y)
            self._draw_achievement_card(ach, x, y, card_width, card_height, show_hidden)
        if total_pages > 1:
            self._draw_minimalist_navigation(total_pages)
        self._draw_close_button()

    def _draw_filter_buttons(self):
        for button in self.filter_buttons:
            bg_color = (52, 152, 219) if button["active"] else (255, 255, 255)
            text_color = (255, 255, 255) if button["active"] else (52, 152, 219)
            pygame.draw.rect(self.screen, bg_color, button["rect"], border_radius=22)
            pygame.draw.rect(self.screen, (52, 152, 219), button["rect"], 2, border_radius=22)
            text_surf = self.filter_font.render(button["text"], True, text_color)
            self.screen.blit(text_surf, (button["rect"].centerx - text_surf.get_width() // 2,
                                         button["rect"].centery - text_surf.get_height() // 2))

    _PROGRESS_MAP = {
        "first_click":    (lambda t: getattr(t.game, 'score', 0) if t.game else 0,    1,          (52,  152, 219)),
        "hundred_points": (lambda t: getattr(t.game, 'score', 0) if t.game else 0,    100,        (52,  152, 219)),
        "thousand_points":(lambda t: getattr(t.game, 'score', 0) if t.game else 0,    1000,       (52,  152, 219)),
        "million_points": (lambda t: getattr(t.game, 'score', 0) if t.game else 0,    1000000,    (52,  152, 219)),
        "billion_points": (lambda t: getattr(t.game, 'score', 0) if t.game else 0,    1000000000, (52,  152, 219)),
        "mini_event_1":   (lambda t: (getattr(t.game, 'mini_event1_session', 0) + getattr(t.game, 'mini_event2_session', 0)) if t.game else 0, 1,   (210, 100,  50)),
        "mini_event_10":  (lambda t: (getattr(t.game, 'mini_event1_session', 0) + getattr(t.game, 'mini_event2_session', 0)) if t.game else 0, 10,  (210, 100,  50)),
        "mini_event_100": (lambda t: (getattr(t.game, 'mini_event1_session', 0) + getattr(t.game, 'mini_event2_session', 0)) if t.game else 0, 100, (210, 100,  50)),
        "streak_3":       (lambda t: t.game.streak_data.get("current_streak", 0) if t.game else 0,   3,   (255, 160,  50)),
        "streak_10":      (lambda t: t.game.streak_data.get("current_streak", 0) if t.game else 0,   10,  (255, 160,  50)),
        "streak_30":      (lambda t: t.game.streak_data.get("current_streak", 0) if t.game else 0,   30,  (255, 160,  50)),
        "streak_100":     (lambda t: t.game.streak_data.get("current_streak", 0) if t.game else 0,   100, (255, 160,  50)),
    }

    def _draw_achievement_card(self, ach, x, y, width, height, show_hidden):
        if ach.unlocked:
            border_color = self.unlocked_color
            bg_color = (255, 255, 255)
            text_color = self.text_color
            desc_color = (68, 68, 68)
            date_color = (100, 100, 100)
            icon = "⭐"
            desc_text = ach.description
        else:
            border_color = self.locked_color
            bg_color = (240, 240, 240)
            text_color = (119, 119, 119)
            desc_color = (153, 153, 153)
            date_color = (153, 153, 153)
            icon = "🔒"
            desc_text = ach.description if show_hidden else ""
        shadow_surface = pygame.Surface((width + 8, height + 8), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, (0, 0, 0, 35), (4, 4, width, height), border_radius=self.radius)
        self.screen.blit(shadow_surface, (x - 2, y - 2))
        card_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, bg_color, card_rect, border_radius=self.radius)
        pygame.draw.rect(self.screen, border_color, card_rect, 2, border_radius=self.radius)
        icon_surf = self.icon_font.render(icon, True, border_color)
        self.screen.blit(icon_surf, (x + (width - icon_surf.get_width()) // 2, y + 5))
        self._draw_multiline_text(ach.name, self.item_font, text_color, x, y + 85, width)
        if ach.unlocked or show_hidden:
            self._draw_multiline_text(desc_text, self.desc_font, desc_color, x, y + 170, width)
        else:
            question_surf = self.question_font.render("???", True, desc_color)
            question_x = x + (width - question_surf.get_width()) // 2
            question_y = y + height - 65
            self.screen.blit(question_surf, (question_x, question_y))
        if ach.unlocked and ach.unlock_date:
            date_surf = self.date_font.render(ach.unlock_date, True, date_color)
            date_x = x + (width - date_surf.get_width()) // 2
            date_y = y + height - 25
            self.screen.blit(date_surf, (date_x, date_y))

        if not ach.unlocked and ach.id in self._PROGRESS_MAP and self.tracker:
            getter, threshold, bar_color = self._PROGRESS_MAP[ach.id]
            current   = getter(self.tracker)
            progress  = min(1.0, current / threshold) if threshold > 0 else 0.0
            remaining = max(0, threshold - current)

            PADDING = 14
            BAR_W   = width - PADDING * 2
            BAR_H   = 8
            bar_x   = x + PADDING
            bar_y   = y + height - 20

            pygame.draw.rect(self.screen, (200, 185, 195), (bar_x, bar_y, BAR_W, BAR_H), border_radius=4)
            fill_w = int(BAR_W * progress)
            if fill_w > 0:
                pygame.draw.rect(self.screen, bar_color, (bar_x, bar_y, fill_w, BAR_H), border_radius=4)
            pygame.draw.rect(self.screen, (160, 140, 155), (bar_x, bar_y, BAR_W, BAR_H), 1, border_radius=4)

    def _draw_multiline_text(self, text, font, color, x, y, max_width):
        words = text.split()
        lines = []
        current_line = ""
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            if font.size(test_line)[0] <= max_width - 20:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        line_height = font.get_height() + 1
        for i, line in enumerate(lines):
            line_surf = font.render(line, True, color)
            line_x = x + (max_width - line_surf.get_width()) // 2
            self.screen.blit(line_surf, (line_x, y + i * line_height))

    def _draw_minimalist_navigation(self, total_pages):
        nav_y = self.height - 70
        self.prev_button_rect = pygame.Rect(self.width // 2 - 80, nav_y, self.page_button_size, self.page_button_size)
        self.next_button_rect = pygame.Rect(self.width // 2 + 40, nav_y, self.page_button_size, self.page_button_size)
        page_text = f"{self.current_page + 1}/{total_pages}"
        page_surf = self.small_font.render(page_text, True, (100, 100, 100))
        page_rect = page_surf.get_rect(center=(self.width // 2, nav_y + self.page_button_size // 2))
        self.screen.blit(page_surf, page_rect)
        prev_color = (52, 152, 219) if self.current_page > 0 else (200, 200, 200)
        pygame.draw.circle(self.screen, prev_color, self.prev_button_rect.center, self.page_button_size // 2)
        pygame.draw.circle(self.screen, (30, 100, 180) if self.current_page > 0 else (150, 150, 150),
                          self.prev_button_rect.center, self.page_button_size // 2, 2)
        arrow_color = (255, 255, 255) if self.current_page > 0 else (220, 220, 220)
        arrow_points = [
            (self.prev_button_rect.centerx + 4, self.prev_button_rect.centery - 6),
            (self.prev_button_rect.centerx - 4, self.prev_button_rect.centery),
            (self.prev_button_rect.centerx + 4, self.prev_button_rect.centery + 6)
        ]
        pygame.draw.polygon(self.screen, arrow_color, arrow_points)
        next_color = (52, 152, 219) if self.current_page < total_pages - 1 else (200, 200, 200)
        pygame.draw.circle(self.screen, next_color, self.next_button_rect.center, self.page_button_size // 2)
        pygame.draw.circle(self.screen, (30, 100, 180) if self.current_page < total_pages - 1 else (150, 150, 150),
                          self.next_button_rect.center, self.page_button_size // 2, 2)
        arrow_points = [
            (self.next_button_rect.centerx - 4, self.next_button_rect.centery - 6),
            (self.next_button_rect.centerx + 4, self.next_button_rect.centery),
            (self.next_button_rect.centerx - 4, self.next_button_rect.centery + 6)
        ]
        pygame.draw.polygon(self.screen, arrow_color, arrow_points)

    def _draw_close_button(self):
        if self.close_image:
            image_rect = self.close_image.get_rect(center=self.close_button_rect.center)
            self.screen.blit(self.close_image, image_rect)
        else:
            pygame.draw.rect(self.screen, (255, 100, 100), self.close_button_rect, border_radius=6)
            center_x, center_y = self.close_button_rect.center
            line_length = 15
            pygame.draw.line(self.screen, (255, 255, 255), (center_x - line_length, center_y - line_length),
                            (center_x + line_length, center_y + line_length), 2)
            pygame.draw.line(self.screen, (255, 255, 255), (center_x - line_length, center_y + line_length),
                            (center_x + line_length, center_y - line_length), 2)

    def handle_event(self, event):
        if not self.visible:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.visible = False
                return True
            elif event.key == pygame.K_TAB:
                current_index = next((i for i, btn in enumerate(self.filter_buttons) if btn["active"]), 0)
                next_index = (current_index + 1) % len(self.filter_buttons)
                for i, btn in enumerate(self.filter_buttons):
                    btn["active"] = (i == next_index)
                self.current_filter = self.filter_buttons[next_index]["filter"]
                self.current_page = 0
                return True
            elif event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                filtered = self._get_filtered_achievements()
                total_pages = max(1, (len(filtered) + self.achievements_per_page - 1) // self.achievements_per_page)
                if event.key == pygame.K_LEFT and self.current_page > 0:
                    self.current_page -= 1
                    return True
                elif event.key == pygame.K_RIGHT and self.current_page < total_pages - 1:
                    self.current_page += 1
                    return True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button != 1:
                return True
            mouse_pos = pygame.mouse.get_pos()
            if self.close_button_rect.collidepoint(mouse_pos):
                self.visible = False
                return True
            for button in self.filter_buttons:
                if button["rect"].collidepoint(mouse_pos):
                    for btn in self.filter_buttons:
                        btn["active"] = (btn == button)
                    self.current_filter = button["filter"]
                    self.current_page = 0
                    return True
            filtered = self._get_filtered_achievements()
            total_pages = max(1, (len(filtered) + self.achievements_per_page - 1) // self.achievements_per_page)
            prev_distance = ((mouse_pos[0] - self.prev_button_rect.centerx) ** 2 +
                           (mouse_pos[1] - self.prev_button_rect.centery) ** 2) ** 0.5
            next_distance = ((mouse_pos[0] - self.next_button_rect.centerx) ** 2 +
                           (mouse_pos[1] - self.next_button_rect.centery) ** 2) ** 0.5
            if prev_distance <= self.page_button_size // 2 and self.current_page > 0:
                self.current_page -= 1
                return True
            if next_distance <= self.page_button_size // 2 and self.current_page < total_pages - 1:
                self.current_page += 1
                return True
            return True
        return True

    def _get_filtered_achievements(self):
        filtered = []
        for ach in self.achievements:
            if self.current_filter == "all":
                filtered.append(ach)
            elif self.current_filter == "unlocked" and ach.unlocked:
                filtered.append(ach)
            elif self.current_filter == "locked" and not ach.unlocked:
                filtered.append(ach)
        return filtered