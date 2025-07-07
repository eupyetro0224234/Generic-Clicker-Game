import pygame

class AchievementsMenu:
    def __init__(self, screen, window_width, window_height):
        self.screen = screen
        self.width = window_width
        self.height = window_height
        self.visible = False

        self.bg_color = (180, 210, 255)
        self.text_color = (40, 40, 60)
        self.font_title = pygame.font.SysFont(None, 36)
        self.font_item = pygame.font.SysFont(None, 28)

        # Lista de conquistas exemplo (pode expandir ou carregar de arquivo)
        self.achievements = [
            {"title": "Primeiro Clique", "description": "Faça seu primeiro clique.", "completed": True},
            {"title": "Centena de Cliques", "description": "Clique 100 vezes.", "completed": False},
            {"title": "Modo Mod", "description": "Ative o modo mods nas configurações.", "completed": False},
            # Adicione mais aqui...
        ]

        self.padding = 20
        self.line_height = 40
        self.spacing = 10

    def draw(self):
        if not self.visible:
            return

        self.screen.fill(self.bg_color)

        # Título centralizado
        title_surf = self.font_title.render("Conquistas", True, self.text_color)
        title_rect = title_surf.get_rect(center=(self.width // 2, self.padding + title_surf.get_height() // 2))
        self.screen.blit(title_surf, title_rect)

        # Lista de conquistas
        y = title_rect.bottom + self.spacing * 2
        for ach in self.achievements:
            color = (0, 150, 0) if ach["completed"] else (150, 0, 0)
            title_text = self.font_item.render(ach["title"], True, color)
            desc_text = self.font_item.render(ach["description"], True, self.text_color)

            self.screen.blit(title_text, (self.padding, y))
            y += self.line_height // 2
            self.screen.blit(desc_text, (self.padding + 10, y))
            y += self.line_height + self.spacing

    def handle_event(self, event):
        if not self.visible:
            return False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.visible = False
            return True
        return False
