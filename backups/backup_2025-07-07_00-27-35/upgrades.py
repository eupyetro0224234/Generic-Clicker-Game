import pygame
import os
import urllib.request

class Upgrade:
    def __init__(self, id, name, cost, bonus):
        self.id = id
        self.name = name
        self.cost = cost
        self.bonus = bonus

class UpgradeMenu:
    def __init__(self, screen, x, y, width):
        self.screen = screen
        self.x, self.y = x, y
        self.width = width
        self.visible = False
        self.animation = 0.0
        self.speed = 0.1
        self.font = pygame.font.SysFont(None, 24)
        self.purchased = set()

        self.upgrades = [
            Upgrade("auto_click", "Auto Clique", 50, 1),
            Upgrade("double", "Pontos em dobro", 100, 2),
            Upgrade("mega", "Mega clique", 300, 5),
        ]

        self.icon_url = "https://i.postimg.cc/yxVZWpPk/image-removebg-preview-6.png"
        localappdata = os.getenv("LOCALAPPDATA")
        self.assets_path = os.path.join(localappdata, ".assests")
        os.makedirs(self.assets_path, exist_ok=True)
        self.icon_path = os.path.join(self.assets_path, "upg.png")
        if not os.path.exists(self.icon_path):
            urllib.request.urlretrieve(self.icon_url, self.icon_path)

        try:
            self.icon = pygame.image.load(self.icon_path).convert_alpha()
            self.icon = pygame.transform.smoothscale(self.icon, (50, 50))
        except:
            self.icon = None

        self.icon_rect = pygame.Rect(self.x + self.width + 10, self.y, 50, 50)

    def toggle(self):
        self.visible = not self.visible

    def draw(self, score):
        self.icon_rect.topleft = (self.x + self.width + 10, self.y)
        if self.icon:
            self.screen.blit(self.icon, self.icon_rect)
        else:
            pygame.draw.rect(self.screen, (150, 100, 100), self.icon_rect)

        if self.visible:
            self.animation = min(1.0, self.animation + self.speed)
        else:
            self.animation = max(0.0, self.animation - self.speed)

        if self.animation <= 0:
            return

        height = int(150 * self.animation)
        panel = pygame.Surface((200, height), pygame.SRCALPHA)
        pygame.draw.rect(panel, (240, 230, 255), (0, 0, 200, height), border_radius=12)

        for i, upg in enumerate(self.upgrades):
            y = 10 + i * 50
            color = (100, 200, 100) if upg.id in self.purchased else (200, 100, 100)
            pygame.draw.rect(panel, color, (10, y, 180, 40), border_radius=8)
            name = f"{upg.name} (${upg.cost})"
            text = self.font.render(name, True, (255, 255, 255))
            panel.blit(text, (20, y + 10))

        self.screen.blit(panel, (self.x, self.y + 60))

    def handle_event(self, event, score):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.icon_rect.collidepoint(event.pos):
                self.toggle()
                return score, self.purchased

            if self.visible:
                for i, upg in enumerate(self.upgrades):
                    upg_rect = pygame.Rect(self.x + 10, self.y + 70 + i * 50, 180, 40)
                    if upg_rect.collidepoint(event.pos) and score >= upg.cost:
                        self.purchased.add(upg.id)
                        score -= upg.cost
                        break
        return score, self.purchased

    def load_upgrades(self, upgrades: list[str]):
        self.purchased = set(upgrades)

    def get_bonus(self):
        bonus = 1
        for upg in self.upgrades:
            if upg.id in self.purchased:
                bonus += upg.bonus
        return bonus
