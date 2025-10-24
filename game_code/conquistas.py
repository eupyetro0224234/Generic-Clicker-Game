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
            Achievement("first_click", "Primeiro ponto", "Dê seu primeiro clique", 1),
            Achievement("hundred_points", "100 Pontos", "Chegue a cem pontos", 100),
            Achievement("thousand_points", "1.000 Pontos", "Chegue a mil pontos", 1000),
            Achievement("million_points", "1.000.000 Pontos", "Chegue a um milhão de pontos", 1000000),
            Achievement("billion_points", "1.000.000.000 Pontos", "Chegue a um bilhão de pontos (parabéns)", 1000000000),
            Achievement("console", "Ativar Console", "Você descobriu o console secreto!"),
            Achievement("mini_event_1", "Mini Evento: Primeiro Clique", "Clique pela primeira vez no mini evento", 1),
            Achievement("mini_event_10", "Mini Evento: 10 Cliques", "Clique 10 vezes no mini evento", 10),
            Achievement("mini_event_100", "Mini Evento: 100 Cliques", "Clique 100 vezes no mini evento", 100),
            Achievement("manual_phase", "Antes de Automação, vem a fase manual", "Compre o upgrade de clique manual (segurar botão)"),
            Achievement("triple_unlock", "Desbloqueio Triplo", "Desbloqueie 3 conquistas em 5 segundos"),
            Achievement("perfeicao_15", "Perfeição 1.5", "Complete todas as conquistas")
        ]
        self.unlocked = set()
        self.achievement_queue = []
        self.current_achievement = None
        self.font = pygame.font.SysFont("None", 100, bold=True)
        self.desc_font = pygame.font.SysFont("None", 100)
        self.icon_font = pygame.font.SysFont("Segoe UI Emoji", 30)
        self.sound = None
        self.animation_speed = 0.08
        self.popup_duration = 3.0
        self.normal_clicks = 0
        self.mini_event_clicks = 0
        
        # Variáveis para controle do Desbloqueio Triplo
        self.last_unlock_time = None
        self.unlock_count = 0
        self.triple_unlock_triggered = False
        
        self.load_sound()

    def reset_achievements(self):
        """Reseta completamente todas as conquistas e variáveis de controle"""
        self.unlocked.clear()
        for ach in self.achievements:
            ach.unlocked = False
        
        # RESETA AS VARIÁVEIS DE CONTROLE DO DESBLOQUEIO TRIPLO
        self.last_unlock_time = None
        self.unlock_count = 0
        self.triple_unlock_triggered = False
        
        # Reseta contadores de cliques
        self.normal_clicks = 0
        self.mini_event_clicks = 0
        
        # Limpa a fila de animações
        self.achievement_queue = []
        self.current_achievement = None

    def load_sound(self):
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(current_dir)
            sound_path = os.path.join(parent_dir, "game_assets", "complete-quest.ogg")

            if os.path.exists(sound_path):
                self.sound = pygame.mixer.Sound(sound_path)
            else:
                sound_path2 = os.path.join("..", "game_assets", "complete-quest.ogg")
                if os.path.exists(sound_path2):
                    self.sound = pygame.mixer.Sound(sound_path2)
        except Exception:
            self.sound = None

    def load_unlocked(self, saved_ids):
        for ach in self.achievements:
            if ach.id in saved_ids:
                ach.unlocked = True
                self.unlocked.add(ach.id)

    def _check_triple_unlock(self):
        """Verifica se o jogador desbloqueou 3 conquistas em 5 segundos"""
        if self.triple_unlock_triggered:
            return
            
        current_time = time.time()
        
        if self.last_unlock_time is None:
            self.last_unlock_time = current_time
            self.unlock_count = 1
            return
        
        # Se passaram mais de 5 segundos, reinicia a contagem
        if current_time - self.last_unlock_time > 5:
            self.last_unlock_time = current_time
            self.unlock_count = 1
            return
        
        # Ainda dentro da janela de 5 segundos
        self.unlock_count += 1
        self.last_unlock_time = current_time
        
        # Verifica se atingiu 3 conquistas
        if self.unlock_count >= 3:
            self._unlock_triple_achievement()

    def _unlock_triple_achievement(self):
        """Desbloqueia a conquista de Desbloqueio Triplo"""
        triple_ach = next((ach for ach in self.achievements if ach.id == "triple_unlock"), None)
        if triple_ach and not triple_ach.unlocked:
            triple_ach.unlocked = True
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
            for _ in new_achievements:
                self._check_triple_unlock()
            self.check_all_achievements_completed()

    def check_unlock(self, score):
        new_achievements = []
        for ach in self.achievements:
            if not ach.unlocked:
                if ach.id == "first_click" and score >= ach.threshold:
                    ach.unlocked = True
                elif ach.id == "hundred_points" and score >= ach.threshold:
                    ach.unlocked = True
                elif ach.id == "thousand_points" and score >= ach.threshold:
                    ach.unlocked = True
                elif ach.id == "million_points" and score >= ach.threshold:
                    ach.unlocked = True
                elif ach.id == "billion_points" and score >= ach.threshold:
                    ach.unlocked = True
                
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
                self.unlocked.add(ach.id)
                self.achievement_queue.append(ach)
                self._start_next_achievement()
                self._check_triple_unlock()
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
                try:
                    self.sound.play()
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
        self.tracker = None
        
        # CORES IGUAIS AO FullSettingsMenu
        self.bg_color = (255, 182, 193)  # Rosa claro igual ao FullSettingsMenu
        self.text_color = (47, 24, 63)   # Texto roxo escuro igual
        self.box_color = (255, 255, 255)
        self.border_color = (180, 190, 210)
        self.unlocked_color = (45, 160, 90)
        self.locked_color = (160, 160, 160)
        self.shadow_color = (0, 0, 0, 25)
        
        self.title_font = pygame.font.SysFont("None", 48, bold=True)
        self.item_font = pygame.font.SysFont("None", 32, bold=True)  # Aumentado de 26 para 32
        self.desc_font = pygame.font.SysFont("None", 26)  # Aumentado de 20 para 26
        self.icon_font = pygame.font.SysFont("Segoe UI Emoji", 80)
        self.filter_font = pygame.font.SysFont("None", 18, bold=True)
        self.instruction_font = pygame.font.SysFont("None", 22)
        self.radius = 25

        self.current_filter = "all"
        self.filter_buttons = []
        self._init_filter_buttons()
        self.close_button_rect = pygame.Rect(width - 65, 25, 40, 40)

    def _init_filter_buttons(self):
        button_width = 140
        button_height = 45
        start_x = self.width // 2 - (3 * button_width + 2 * 15) // 2
        start_y = 60
        self.filter_buttons = [
            {"rect": pygame.Rect(start_x, start_y, button_width, button_height), "text": "Todas", "filter": "all", "active": True},
            {"rect": pygame.Rect(start_x + button_width + 15, start_y, button_width, button_height), "text": "Desbloqueadas", "filter": "unlocked", "active": False},
            {"rect": pygame.Rect(start_x + 2 * (button_width + 15), start_y, button_width, button_height), "text": "Bloqueadas", "filter": "locked", "active": False}
        ]

    def update(self, tracker):
        self.achievements = tracker.achievements
        self.unlocked = tracker.unlocked

    def draw(self):
        if not self.visible:
            return

        # FUNDO ROSA CLARO IGUAL AO FullSettingsMenu - SEM OVERLAY ESCURO
        self.screen.fill(self.bg_color)

        # Título (apenas um)
        title_text = "Conquistas"
        title_surf = self.title_font.render(title_text, True, self.text_color)
        self.screen.blit(title_surf, (self.width // 2 - title_surf.get_width() // 2, 8))

        self._draw_filter_buttons()

        show_hidden = False
        if self.config_menu and hasattr(self.config_menu, 'settings_menu'):
            show_hidden = self.config_menu.settings_menu.get_option("Mostrar conquistas ocultas")

        filtered = []
        for ach in self.achievements:
            if self.current_filter == "all":
                filtered.append(ach)
            elif self.current_filter == "unlocked" and ach.unlocked:
                filtered.append(ach)
            elif self.current_filter == "locked" and not ach.unlocked:
                filtered.append(ach)

        card_width = 260
        card_height = 280
        spacing_x = 25
        spacing_y = 40
        max_cols = 5
        min_cols = 4

        total_width_for_5 = max_cols * card_width + (max_cols - 1) * spacing_x
        cols = max_cols if total_width_for_5 <= self.width - 60 else min_cols

        total_grid_width = cols * card_width + (cols - 1) * spacing_x
        start_x = (self.width - total_grid_width) // 2
        start_y = 130

        for i, ach in enumerate(filtered):
            row = i // cols
            col = i % cols
            x = start_x + col * (card_width + spacing_x)
            y = start_y + row * (card_height + spacing_y)
            self._draw_achievement_card(ach, x, y, card_width, card_height, show_hidden)

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

    def _draw_achievement_card(self, ach, x, y, width, height, show_hidden):
        if ach.unlocked:
            border_color = self.unlocked_color
            bg_color = (255, 255, 255)
            text_color = self.text_color
            desc_color = (68, 68, 68)
            icon = "⭐"
        else:
            border_color = self.locked_color
            bg_color = (240, 240, 240)
            text_color = (119, 119, 119)
            desc_color = (153, 153, 153)
            icon = "🔒"

        shadow_surface = pygame.Surface((width + 12, height + 12), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, (0, 0, 0, 35), (6, 6, width, height), border_radius=self.radius)
        self.screen.blit(shadow_surface, (x - 3, y - 3))

        card_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, bg_color, card_rect, border_radius=self.radius)
        pygame.draw.rect(self.screen, border_color, card_rect, 3, border_radius=self.radius)

        icon_surf = self.icon_font.render(icon, True, border_color)
        self.screen.blit(icon_surf, (x + (width - icon_surf.get_width()) // 2, y + 10))

        # Ajustado o posicionamento vertical para acomodar textos maiores
        self._draw_multiline_text(ach.name, self.item_font, text_color, x, y + 100, width)  # Ajustado de 110 para 100
        desc_text = ach.description if ach.unlocked or show_hidden else "???"
        self._draw_multiline_text(desc_text, self.desc_font, desc_color, x, y + 160, width)  # Ajustado de 175 para 160

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

        for i, line in enumerate(lines):
            line_surf = font.render(line, True, color)
            line_x = x + (max_width - line_surf.get_width()) // 2
            self.screen.blit(line_surf, (line_x, y + i * (font.get_height() + 2)))

    def _draw_close_button(self):
        pygame.draw.rect(self.screen, (255, 120, 120), self.close_button_rect, border_radius=20)
        pygame.draw.rect(self.screen, (180, 60, 60), self.close_button_rect, 2, border_radius=20)
        center_x, center_y = self.close_button_rect.center
        line_length = 12
        pygame.draw.line(self.screen, (255, 255, 255), (center_x - line_length, center_y - line_length),
                         (center_x + line_length, center_y + line_length), 4)
        pygame.draw.line(self.screen, (255, 255, 255), (center_x - line_length, center_y + line_length),
                         (center_x + line_length, center_y - line_length), 4)

    def handle_event(self, event):
        if not self.visible:
            return False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.visible = False
            return True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if self.close_button_rect.collidepoint(mouse_pos):
                self.visible = False
                return True
            for button in self.filter_buttons:
                if button["rect"].collidepoint(mouse_pos):
                    for btn in self.filter_buttons:
                        btn["active"] = (btn == button)
                    self.current_filter = button["filter"]
                    return True
            return True
        return True