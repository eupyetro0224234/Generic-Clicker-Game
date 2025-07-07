import pygame
import time

class Achievement:
    def __init__(self, id, name, description):
        self.id = id
        self.name = name
        self.description = description
        self.unlocked = False

class AchievementsMenu:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        self.font_title = pygame.font.SysFont(None, 30)
        self.font_desc = pygame.font.SysFont(None, 22)
        self.bg_color = (180, 210, 255)
        self.option_color = (255, 255, 255)
        self.option_border = (200, 220, 250)
        self.text_color = (40, 40, 60)
        self.option_height = 60
        self.option_radius = 10
        self.padding_x = 12
        self.spacing = 8
        self.visible = False

        # Lista de conquistas (exemplo)
        self.achievements = [
            Achievement("first_click", "Primeiro Clique", "Faça seu primeiro clique no botão."),
            Achievement("hundred_points", "100 Pontos", "Alcance 100 pontos."),
            Achievement("reset_score", "Zerou o Score", "Resete sua pontuação."),
            # Adicione mais conquistas aqui
        ]

        # Caixa para avisos de conquista desbloqueada
        self.alert_active = False
        self.alert_text = ""
        self.alert_start_time = 0
        self.alert_duration = 3.5  # segundos
        self.alert_bg_color = (255, 240, 200)
        self.alert_text_color = (20, 80, 40)
        self.alert_box_rect = pygame.Rect(0, 0, 400, 50)
        self.alert_box_rect.center = (self.width // 2, 80)

    def unlock(self, achievement_id):
        for ach in self.achievements:
            if ach.id == achievement_id and not ach.unlocked:
                ach.unlocked = True
                self.show_alert(f"Conquista desbloqueada: {ach.name}")
                return True
        return False

    def show_alert(self, text):
        self.alert_text = text
        self.alert_start_time = time.time()
        self.alert_active = True

    def update_alert(self):
        if self.alert_active:
            if time.time() - self.alert_start_time > self.alert_duration:
                self.alert_active = False

    def draw_alert(self):
        if self.alert_active:
            s = pygame.Surface((self.alert_box_rect.width, self.alert_box_rect.height), pygame.SRCALPHA)
            s.fill((*self.alert_bg_color, 230))
            self.screen.blit(s, self.alert_box_rect.topleft)

            text_surf = self.font_title.render(self.alert_text, True, self.alert_text_color)
            text_rect = text_surf.get_rect(center=self.alert_box_rect.center)
            self.screen.blit(text_surf, text_rect)

    def draw(self):
        if not self.visible:
            return

        margin = 20
        menu_width = self.width - 2 * margin
        menu_height = self.height - 2 * margin
        menu_rect = pygame.Rect(margin, margin, menu_width, menu_height)

        # Fundo geral
        pygame.draw.rect(self.screen, self.bg_color, menu_rect, border_radius=12)

        # Título
        title_surf = self.font_title.render("Conquistas", True, self.text_color)
        title_rect = title_surf.get_rect(midtop=(self.width // 2, margin + 10))
        self.screen.blit(title_surf, title_rect)

        # Lista de conquistas
        start_y = title_rect.bottom + 20
        for i, ach in enumerate(self.achievements):
            oy = start_y + i * (self.option_height + self.spacing)
            option_rect = pygame.Rect(margin + 10, oy, menu_width - 20, self.option_height)

            # Fundo e borda da caixa
            color_bg = (200, 255, 200) if ach.unlocked else self.option_color
            border_color = (100, 160, 100) if ach.unlocked else self.option_border

            pygame.draw.rect(self.screen, color_bg, option_rect, border_radius=self.option_radius)
            pygame.draw.rect(self.screen, border_color, option_rect, width=2, border_radius=self.option_radius)

            # Nome e descrição
            name_surf = self.font_title.render(ach.name, True, self.text_color)
            desc_surf = self.font_desc.render(ach.description, True, self.text_color)

            self.screen.blit(name_surf, (option_rect.x + 12, option_rect.y + 8))
            self.screen.blit(desc_surf, (option_rect.x + 12, option_rect.y + 34))

        # Desenha o alerta caso ativo
        self.draw_alert()

    def handle_event(self, event):
        # Fechar conquistas com ESC ou clique fora (opcional)
        if not self.visible:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.visible = False
                return True

        if event.type == pygame.MOUSEBUTTONDOWN:
            # Se clicar fora do menu, fecha (opcional)
            margin = 20
            menu_width = self.width - 2 * margin
            menu_height = self.height - 2 * margin
            menu_rect = pygame.Rect(margin, margin, menu_width, menu_height)

            if not menu_rect.collidepoint(event.pos):
                self.visible = False
                return True

        return False

    def load_achievements(self, unlocked_ids):
        """Recebe uma lista ou set com ids desbloqueados para atualizar o estado."""
        unlocked_set = set(unlocked_ids)
        for ach in self.achievements:
            ach.unlocked = ach.id in unlocked_set

    def get_unlocked_ids(self):
        """Retorna uma lista com os ids desbloqueados."""
        return [ach.id for ach in self.achievements if ach.unlocked]
