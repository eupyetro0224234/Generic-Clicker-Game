import pygame

class LoadingScreen:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        self.bg_color = (20, 30, 60)
        self.bar_color = (100, 200, 255)
        self.bar_border = (255, 255, 255)
        self.text_color = (255, 255, 255)
        self.font = pygame.font.SysFont(None, 32)

    def draw(self, percent, message="Carregando..."):
        # Processa o loop de eventos para manter a janela responsiva
        pygame.event.pump()

        # Fundo
        self.screen.fill(self.bg_color)

        # Texto da mensagem
        text = self.font.render(message, True, self.text_color)
        text_rect = text.get_rect(center=(self.width // 2, self.height // 2 - 50))
        self.screen.blit(text, text_rect)

        # Barra de progresso
        bar_width = 400
        bar_height = 30
        bar_x = (self.width - bar_width) // 2
        bar_y = self.height // 2

        pygame.draw.rect(self.screen, self.bar_border,
                         (bar_x, bar_y, bar_width, bar_height), 2)
        inner_width = int((percent / 100) * (bar_width - 4))
        pygame.draw.rect(self.screen, self.bar_color,
                         (bar_x + 2, bar_y + 2, inner_width, bar_height - 4))

        # Percentual em texto
        percent_text = self.font.render(f"{int(percent)}%", True, self.text_color)
        percent_rect = percent_text.get_rect(center=(self.width // 2, bar_y + bar_height + 25))
        self.screen.blit(percent_text, percent_rect)

        pygame.display.update()
