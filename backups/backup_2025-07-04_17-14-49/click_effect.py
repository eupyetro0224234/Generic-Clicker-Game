import pygame

class ClickEffect:
    def __init__(self, x, y, text="+1", color=(255, 255, 0), lifespan=40):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.lifespan = lifespan
        self.age = 0
        self.font = pygame.font.SysFont(None, 32)
        self.alpha = 255

    def update(self):
        self.y -= 1  # move para cima
        self.age += 1
        self.alpha = max(0, 255 - int((self.age / self.lifespan) * 255))

    def draw(self, surface):
        if self.age < self.lifespan:
            text_surf = self.font.render(self.text, True, self.color)
            text_surf.set_alpha(self.alpha)
            rect = text_surf.get_rect(center=(self.x, self.y))
            surface.blit(text_surf, rect)

    def is_expired(self):
        return self.age >= self.lifespan
