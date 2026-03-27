import pygame

class ClickEffect:
    def __init__(self, x, y, text="+1", color=None, alpha_decay=5):
        self.x = x
        self.y = y
        self.text = text
        self.color = color if color is not None else (255, 100, 100)
        self.alpha = 255
        self.dy = -1
        self.font = pygame.font.SysFont(None, 32)
        self.finished = False
        self.lifetime = 60
        self.alpha_decay = alpha_decay

    def update(self):
        self.y += self.dy
        self.alpha -= self.alpha_decay
        if self.alpha <= 0:
            self.alpha = 0
            self.finished = True

    def draw(self, screen):
        if self.alpha > 0:
            text_surface = self.font.render(self.text, True, self.color)
            text_surface.set_alpha(self.alpha)
            text_rect = text_surface.get_rect(center=(self.x, self.y))
            screen.blit(text_surface, text_rect)