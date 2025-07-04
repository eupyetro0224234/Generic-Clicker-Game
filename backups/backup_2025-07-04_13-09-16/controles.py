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
        self.padding_x = 12
        self.padding_y = 5
        self.spacing = 10

        self.window_width = window_width
        self.window_height = window_height

        self.controls_list = [
            ("Clique Esquerdo", "Aumenta pontos"),
            ("Clique Direito", "Aumenta pontos"),
            ("Clique da rodinha do mouse", "Aumenta pontos"),
            ("Rolagem do botão mouse", "Aumenta pontos"),
            ("R", "Reseta pontos"),
            ("ESC", "Fecha menus"),
        ]

        self.visible = False

        # Definindo largura mínima e máxima da caixa das teclas
        self.min_key_box_width = 150
        self.max_key_box_width = 280

        # Altura da linha e altura total da caixa
        self.line_height = self.option_height + self.padding_y * 2
        self.height = len(self.controls_list) * self.line_height + self.padding_y * 2

        # Posição no canto inferior esquerdo, afastado da borda
        self.margin_x = 16
        self.margin_y = 24
        self.x = self.margin_x
        self.y = self.window_height - self.height - self.margin_y

        self.box_rect = pygame.Rect(self.x, self.y, 460, self.height)

    def draw(self):
        if not self.visible:
            return

        pygame.draw.rect(self.screen, self.bg_color, self.box_rect, border_radius=12)

        for i, (key, desc) in enumerate(self.controls_list):
            oy = self.y + self.padding_y + i * self.line_height

            # Ajusta largura da caixa da tecla com base no texto, dentro do limite
            key_text = self.font.render(key, True, self.text_color)
            key_box_width = key_text.get_width() + 24  # 12 px padding esquerda e direita
            key_box_width = max(self.min_key_box_width, min(key_box_width, self.max_key_box_width))

            key_rect = pygame.Rect(self.x + 12, oy, key_box_width, self.option_height)
            pygame.draw.rect(self.screen, self.option_color, key_rect, border_radius=self.option_radius)
            pygame.draw.rect(self.screen, self.option_border, key_rect, width=1, border_radius=self.option_radius)

            # Texto centralizado na caixa da tecla
            key_text_rect = key_text.get_rect(center=key_rect.center)
            self.screen.blit(key_text, key_text_rect)

            # Texto da descrição ao lado, com espaçamento seguro
            desc_text = self.font.render(desc, True, self.text_color)
            desc_text_rect = desc_text.get_rect(midleft=(key_rect.right + 20, key_rect.centery))
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
                # Comportamento: não fecha ao clicar fora
                return False
        return False
