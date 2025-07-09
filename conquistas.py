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
            Achievement("console", "Ativar Console", "Você descobriu o console secreto!"),
            Achievement("mini_event_1", "Mini Evento: Primeiro Clique", "Clique pela primeira vez no mini evento", 1),
            Achievement("mini_event_10", "Mini Evento: 10 Cliques", "Clique 10 vezes no mini evento", 10),
            Achievement("mini_event_100", "Mini Evento: 100 Cliques", "Clique 100 vezes no mini evento", 100)
        ]
        self.unlocked = set()
        self.achievement_queue = []
        self.current_achievement = None
        self.font = pygame.font.SysFont("Arial", 28, bold=True)
        self.desc_font = pygame.font.SysFont("Arial", 22)
        self.bg_color = (255, 215, 230)  # Rosa claro
        self.border_color = (220, 150, 180)  # Rosa mais escuro para borda
        self.text_color = (80, 0, 60)  # Roxo escuro para texto
        self.sound = None
        self.animation_speed = 0.08  # Mais rápido
        self.popup_duration = 3.5  # 3.5 segundos visível
        self.normal_clicks = 0
        self.mini_event_clicks = 0
        self.icon_font = pygame.font.SysFont("Segoe UI Emoji", 36)

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
        # Efeito de easing para suavizar a animação
        eased_progress = math.sin(ach.animation_progress * math.pi/2)
        alpha = int(eased_progress * 255)
        
        # Tamanho e posição do popup
        w, h = 380, 90
        x = (self.screen.get_width() - w) // 2
        y = int(40 + (1 - eased_progress) * 10)
        
        # Cria superfície com transparência
        popup_surface = pygame.Surface((w, h), pygame.SRCALPHA)
        
        # Desenha fundo com borda arredondada
        bg_with_alpha = (*self.bg_color, alpha)
        border_with_alpha = (*self.border_color, alpha)
        pygame.draw.rect(popup_surface, bg_with_alpha, (0, 0, w, h), border_radius=16)
        pygame.draw.rect(popup_surface, border_with_alpha, (0, 0, w, h), 3, border_radius=16)
        
        # Desenha ícone de troféu
        trophy = self.icon_font.render("🏆", True, (255, 215, 0, alpha))
        popup_surface.blit(trophy, (20, (h - trophy.get_height()) // 2))
        
        # Desenha textos
        text_color = (*self.text_color, alpha)
        title = self.font.render("Conquista Desbloqueada!", True, text_color)
        popup_surface.blit(title, (60, 15))
        
        name = self.desc_font.render(f"{ach.name}", True, text_color)
        popup_surface.blit(name, (60, 45))
        
        # Adiciona sombra sutil
        shadow_surface = pygame.Surface((w+4, h+4), pygame.SRCALPHA)
        shadow_surface.fill((0, 0, 0, alpha//4))
        self.screen.blit(shadow_surface, (x-2, y-2))
        
        # Desenha o popup na tela principal
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

        # Cores e estilos
        self.bg_color = (245, 225, 240, 220)
        self.box_color = (255, 245, 250)
        self.text_color = (60, 0, 60)
        self.border_color = (180, 150, 180)
        self.unlocked_color = (40, 180, 100)
        self.locked_color = (150, 150, 150)
        self.highlight_color = (255, 105, 180)

        # Fontes
        self.title_font = pygame.font.SysFont("Arial", 36, bold=True)
        self.item_font = pygame.font.SysFont("Arial", 26, bold=True)
        self.desc_font = pygame.font.SysFont("Arial", 20)
        self.icon_font = pygame.font.SysFont("Segoe UI Emoji", 28)

        # Layout
        self.padding = 20
        self.item_height = 70
        self.radius = 14

    def update(self, tracker):
        self.achievements = tracker.achievements
        self.unlocked = tracker.unlocked

    def draw(self):
        if not self.visible:
            return

        # Fundo semi-transparente
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill(self.bg_color)
        self.screen.blit(overlay, (0, 0))

        # Caixa principal
        box_width = min(600, self.width - 80)
        box_height = min(500, self.height - 80)
        box_rect = pygame.Rect((self.width - box_width) // 2, (self.height - box_height) // 2, box_width, box_height)

        pygame.draw.rect(self.screen, self.box_color, box_rect, border_radius=self.radius)
        pygame.draw.rect(self.screen, self.border_color, box_rect, 3, border_radius=self.radius)

        # Título
        title = self.title_font.render("Conquistas", True, self.text_color)
        self.screen.blit(title, (box_rect.centerx - title.get_width() // 2, box_rect.top + 25))

        # Verifica se deve mostrar conquistas ocultas
        show_hidden = False
        if self.config_menu and hasattr(self.config_menu, 'settings_menu'):
            show_hidden = self.config_menu.settings_menu.get_option("Mostrar conquistas ocultas")

        # Filtra conquistas
        filtered = [a for a in self.achievements if a.unlocked or show_hidden]

        # Lista de conquistas
        start_y = box_rect.top + 80
        scrollable_height = box_rect.height - 100
        end_y = box_rect.top + box_rect.height - 20

        for i, ach in enumerate(filtered):
            y = start_y + i * (self.item_height + 10)
            if y + self.item_height > end_y:
                break

            item_rect = pygame.Rect(box_rect.left + self.padding, y, box_width - 2 * self.padding, self.item_height)
            
            # Fundo do item
            pygame.draw.rect(self.screen, (250, 240, 248), item_rect, border_radius=self.radius)
            
            # Borda colorida
            border_color = self.unlocked_color if ach.unlocked else self.locked_color
            pygame.draw.rect(self.screen, border_color, item_rect, 2, border_radius=self.radius)

            # Ícone
            icon = "✓" if ach.unlocked else "?"
            icon_surf = self.icon_font.render(icon, True, border_color)
            self.screen.blit(icon_surf, (item_rect.left + 15, item_rect.centery - icon_surf.get_height() // 2))

            # Nome e descrição
            name_surf = self.item_font.render(ach.name, True, self.text_color if ach.unlocked else self.locked_color)
            desc_surf = self.desc_font.render(ach.description, True, (100, 80, 100) if ach.unlocked else (120, 120, 120))

            self.screen.blit(name_surf, (item_rect.left + 60, item_rect.top + 12))
            self.screen.blit(desc_surf, (item_rect.left + 60, item_rect.top + 38))

    def handle_event(self, event):
        if not self.visible:
            return False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.visible = False
            return True
        if event.type == pygame.MOUSEBUTTONDOWN:
            return True
        return False