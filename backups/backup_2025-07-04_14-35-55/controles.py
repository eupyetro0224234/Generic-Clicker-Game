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

        # Caixa fixa para todas as teclas (largura fixa)
        self.key_box_width = 240

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

            # Caixa da tecla com largura fixa
            key_rect = pygame.Rect(self.x + 12, oy, self.key_box_width, self.option_height)
            pygame.draw.rect(self.screen, self.option_color, key_rect, border_radius=self.option_radius)
            pygame.draw.rect(self.screen, self.option_border, key_rect, width=1, border_radius=self.option_radius)

            # Texto centralizado dentro da caixa da tecla
            key_text = self.font.render(key, True, self.text_color)
            key_text_rect = key_text.get_rect(center=key_rect.center)
            self.screen.blit(key_text, key_text_rect)

            # Desenhar ":" logo após a caixinha, com pequeno espaçamento
            colon_text = self.font.render(":", True, self.text_color)
            colon_x = key_rect.right + 6
            colon_y = key_rect.centery
            colon_rect = colon_text.get_rect(center=(colon_x, colon_y))
            self.screen.blit(colon_text, colon_rect)

            # Texto da descrição à direita do ":"
            desc_text = self.font.render(desc, True, self.text_color)
            desc_text_rect = desc_text.get_rect(midleft=(colon_rect.right + 6, key_rect.centery))
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
                # Não fecha ao clicar fora
                return False
        return False
