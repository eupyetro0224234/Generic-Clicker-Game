import pygame

class ClickEffect:
    def __init__(self, x, y, text="+1", color=None):
        """
        Inicializa o efeito de clique
        :param x: Posição X inicial
        :param y: Posição Y inicial
        :param text: Texto a ser exibido (padrão: "+1")
        :param color: Cor do texto no formato RGB (padrão: vermelho claro)
        """
        self.x = x
        self.y = y
        self.text = text
        self.color = color if color is not None else (255, 100, 100)
        self.alpha = 255
        self.dy = -1
        self.font = pygame.font.SysFont(None, 32)
        self.finished = False
        self.lifetime = 60

    def update(self):
        """Atualiza o estado do efeito a cada frame"""
        self.y += self.dy
        self.alpha -= 5
        if self.alpha <= 0:
            self.alpha = 0
            self.finished = True

    def draw(self, screen):
        """Desenha o efeito na tela"""
        if self.alpha > 0:
            text_surface = self.font.render(self.text, True, self.color)
            text_surface.set_alpha(self.alpha)
            
            text_rect = text_surface.get_rect(center=(self.x, self.y))
            screen.blit(text_surface, text_rect)