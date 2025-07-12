import pygame

class ClickEffect:
    def __init__(self, x, y, text="+1"):
        self.x = x
        self.y = y
        self.text = text
        self.alpha = 255
        self.dy = -1
        self.font = pygame.font.SysFont(None, 32)
        self.finished = False

    def update(self):
        self.y += self.dy
        self.alpha -= 5
        if self.alpha <= 0:
            self.alpha = 0
            self.finished = True

    def draw(self, screen):
        if self.alpha > 0:
            text_surface = self.font.render(self.text, True, (255, 100, 100))
            text_surface.set_alpha(self.alpha)
            screen.blit(text_surface, (self.x, self.y))
