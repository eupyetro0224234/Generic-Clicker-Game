import os
import pygame
import urllib.request

class UpgradeMenu:
    def __init__(self, screen, x, y):
        self.screen = screen
        self.visible = False
        self.x = x
        self.y = y
        self.width = 64
        self.height = 64

        localappdata = os.getenv("LOCALAPPDATA")
        self.assets_path = os.path.join(localappdata, ".assests")
        os.makedirs(self.assets_path, exist_ok=True)

        self.icon_url = "https://i.postimg.cc/yxVZWpPk/image-removebg-preview-6.png"
        self.icon_path = os.path.join(self.assets_path, "upgrade_icon.png")

        if not os.path.isfile(self.icon_path):
            try:
                urllib.request.urlretrieve(self.icon_url, self.icon_path)
            except Exception as e:
                print("Erro ao baixar imagem de upgrade:", e)

        try:
            self.icon_image = pygame.image.load(self.icon_path).convert_alpha()
            self.icon_image = pygame.transform.smoothscale(self.icon_image, (self.width, self.height))
        except Exception as e:
            print("Erro ao carregar imagem de upgrade:", e)
            self.icon_image = None

        self.icon_rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self):
        if self.icon_image:
            self.screen.blit(self.icon_image, self.icon_rect)
        else:
            pygame.draw.rect(self.screen, (100, 100, 100), self.icon_rect)

        if self.visible:
            pygame.draw.rect(self.screen, (240, 240, 250), (self.x, self.y + self.height + 10, 200, 100), border_radius=10)
            font = pygame.font.SysFont(None, 20)
            txt = font.render("Upgrades aqui!", True, (30, 30, 30))
            self.screen.blit(txt, (self.x + 10, self.y + self.height + 20))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.icon_rect.collidepoint(event.pos):
                self.visible = not self.visible
                return True
        return False
