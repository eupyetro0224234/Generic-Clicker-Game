import pygame
import random
import os

class MiniEvent:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        
        localappdata = os.getenv("LOCALAPPDATA") or "."
        self.image_path = os.path.join(localappdata, ".assets", "mini-event.png")
        
        try:
            self.image = pygame.image.load(self.image_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (50, 50))
        except Exception as e:
            self.image = pygame.Surface((50, 50))
            self.image.fill((255, 0, 0))
            font = pygame.font.SysFont(None, 20)
            text = font.render("EVENTO", True, (255, 255, 255))
            self.image.blit(text, (10, 15))
            
        self.x = random.randint(0, self.width - 50)
        self.y = random.randint(0, self.height - 50)
        self.time_to_live = 10000
        self.spawn_time = pygame.time.get_ticks()
        self.visible = True
        self.font = pygame.font.SysFont("Arial", 20)
        self.rect = pygame.Rect(self.x, self.y, 50, 50)

    def update(self):
        if not self.visible:
            return
            
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - self.spawn_time
        
        if elapsed_time >= self.time_to_live:
            self.visible = False

    def draw(self):
        if self.visible:
            self.screen.blit(self.image, (self.x, self.y))
            
            elapsed_time = pygame.time.get_ticks() - self.spawn_time
            time_left = max(0, self.time_to_live - elapsed_time) // 1000
            time_text = self.font.render(f"{time_left}s", True, (255, 255, 255))
            self.screen.blit(time_text, (self.x + 5, self.y - 25))

    def handle_click(self, pos, score, upgrade_menu):
        if not self.visible:
            return score, False
            
        if self.rect.collidepoint(pos):
            self.visible = False
            
            if random.random() < 0.05:
                upgrade_menu.purchase_random_upgrade()
                return score, True
            else:
                points = random.randint(1, 1000)
                score += points
                return score, False
                
        return score, False