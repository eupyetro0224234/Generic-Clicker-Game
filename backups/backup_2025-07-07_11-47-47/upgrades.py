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
    def __init__(self, screen, window_width, window_height):
        self.screen = screen
        self.window_width = window_width
        self.window_height = window_height

        self.x = 10
        self.y = 10
        self.width = 220  # Largura do painel aumentada para caber melhor os textos
        self.visible = False
        self.animation = 0.0
        self.speed = 0.12
        self.font = pygame.font.SysFont(None, 24)
        self.purchased = set()
        self.auto_click_timer = 0

        self.upgrades = [
            Upgrade("auto_click", "Auto Clique", 5000, 0),  # preço maior
            Upgrade("double", "Pontos em Dobro", 20000, 1),
            Upgrade("mega", "Mega Clique", 75000, 4),
        ]

        # Cores para o fundo e opções, inspirado no menu principal
        self.bg_color = (180, 210, 255)
        self.option_color = (255, 255, 255)
        self.option_border = (100, 149, 237)  # cornflower blue para borda
        self.text_color = (40, 40, 60)

        self.option_height = 38
        self.option_radius = 10
        self.padding_x = 10
        self.spacing = 8

        self.icon_url = "https://i.postimg.cc/yxVZWpPk/image-removebg-preview-6.png"
        localappdata = os.getenv("LOCALAPPDATA")
        self.assets_path = os.path.join(localappdata, ".assets")
        os.makedirs(self.assets_path, exist_ok=True)
        self.icon_path = os.path.join(self.assets_path, "upg.png")

        if not os.path.exists(self.icon_path):
            urllib.request.urlretrieve(self.icon_url, self.icon_path)

        try:
            self.icon = pygame.image.load(self.icon_path).convert_alpha()
            self.icon = pygame.transform.smoothscale(self.icon, (42, 42))
        except:
            self.icon = None

        self.icon_rect = pygame.Rect(self.x, self.y, 50, 50)

    def get_icon_rect(self):
        return self.icon_rect

    def toggle_visibility(self):
        self.visible = not self.visible

    def toggle(self):
        self.toggle_visibility()

    def draw_icon(self):
        if self.icon:
            self.screen.blit(self.icon, self.icon_rect)
        else:
            pygame.draw.rect(self.screen, (150, 100, 100), self.icon_rect)

    def draw(self, score=0):
        # Desenha o ícone sempre
        self.draw_icon()

        # Animação para aparecer/desaparecer
        if self.visible:
            self.animation = min(1.0, self.animation + self.speed)
        else:
            self.animation = max(0.0, self.animation - self.speed)

        if self.animation <= 0:
            return

        display = [f"{u.name} (${u.cost})" for u in self.upgrades]
        full_h = len(display) * (self.option_height + self.spacing) - self.spacing + 12
        height = int(full_h * self.animation)
        panel = pygame.Surface((self.width, height), pygame.SRCALPHA)
        pygame.draw.rect(panel, self.bg_color, (0, 0, self.width, height), border_radius=12)

        for i, upg in enumerate(self.upgrades):
            oy = 6 + i * (self.option_height + self.spacing)
            if oy + self.option_height > height:
                break
            rect = pygame.Rect(self.padding_x, oy, self.width - 2 * self.padding_x, self.option_height)
            color = (170, 250, 170) if upg.id in self.purchased else self.option_color
            pygame.draw.rect(panel, color, rect, border_radius=self.option_radius)
            pygame.draw.rect(panel, self.option_border, rect, width=2, border_radius=self.option_radius)
            txt = self.font.render(f"{upg.name} (${upg.cost})", True, self.text_color)
            panel.blit(txt, txt.get_rect(center=rect.center))

        self.screen.blit(panel, (self.x, self.y + 60))

    def handle_event(self, event, score):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.icon_rect.collidepoint(event.pos):
                self.toggle()
                return score, self.purchased

            if self.visible:
                for i, upg in enumerate(self.upgrades):
                    upg_rect = pygame.Rect(
                        self.x + self.padding_x,
                        self.y + 66 + i * (self.option_height + self.spacing),
                        self.width - 2 * self.padding_x,
                        self.option_height
                    )
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
            if upg.id in self.purchased and upg.id != "auto_click":
                bonus += upg.bonus
        return bonus

    def auto_click_enabled(self):
        return "auto_click" in self.purchased

    def reset_upgrades(self):
        self.purchased.clear()
