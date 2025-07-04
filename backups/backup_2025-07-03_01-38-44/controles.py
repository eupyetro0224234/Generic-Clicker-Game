import pygame

class ControlsMenu:
    def __init__(self, screen, window_width, window_height):
        self.screen = screen
        self.font = pygame.font.SysFont(None, 24)
        self.bg_color = (180, 210, 255)
        self.option_color = (255, 255, 255)
        self.option_border = (200, 220, 250)
        self.text_color = (40, 40, 60)

        self.option_height = 38
        self.option_radius = 10
        self.padding_x = 8
        self.spacing = 10

        self.window_width = window_width
        self.window_height = window_height

        self.controls_list = [
            ("Clique Esquerdo", "Aumenta pontos"),
            ("R", "Reseta pontos"),
            ("Clique Direito", "Configurações"),
            ("ESC", "Fecha menus"),
        ]

        self.visible = False

        # Dimensões da caixa
        self.width = 340
        self.line_height = 38
        self.height = len(self.controls_list) * self.line_height + 20

        # Posição no canto inferior esquerdo, afastado da borda
        self.margin_x = 16
        self.margin_y = 24
        self.x = self.margin_x
        self.y = self.window_height - self.height - self.margin_y

        # Retângulo da caixa
        self.box_rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self):
        if not self.visible:
            return

        # Fundo da caixa com borda arredondada
        pygame.draw.rect(self.screen, self.bg_color, self.box_rect, border_radius=12)

        for i, (key, desc) in enumerate(self.controls_list):
            oy = self.y + 10 + i * self.line_height

            # Caixa para a tecla
            key_rect = pygame.Rect(self.x + 12, oy, 130, 28)
            pygame.draw.rect(self.screen, self.option_color, key_rect, border_radius=self.option_radius)
            pygame.draw.rect(self.screen, self.option_border, key_rect, width=1, border_radius=self.option_radius)

            key_text = self.font.render(key, True, self.text_color)
            key_text_rect = key_text.get_rect(center=key_rect.center)
            self.screen.blit(key_text, key_text_rect)

            # Texto da descrição
            desc_text = self.font.render(desc, True, self.text_color)
            desc_text_rect = desc_text.get_rect(midleft=(key_rect.right + 16, key_rect.centery))
            self.screen.blit(desc_text, desc_text_rect)

    def handle_event(self, event):
        if not self.visible:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.visible = False
                return True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if not self.box_rect.collidepoint(event.pos):
                self.visible = False
                return True
        return False
