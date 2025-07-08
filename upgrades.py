import pygame
import os

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
        self.width = 280
        self.visible = False
        self.animation = 0.0
        self.speed = 0.12
        self.font = pygame.font.SysFont(None, 24)
        self.purchased = {}  # {id: quantidade}
        self.auto_click_timer = 0

        self.upgrades = [
            Upgrade("auto_click", "Auto Clique", 5000, 1),  # bonus 1 ponto por tick
            Upgrade("double", "Pontos em Dobro", 20000, 1),
            Upgrade("mega", "Mega Clique", 75000, 4),
        ]

        self.bg_color = (180, 210, 255)
        self.option_color = (255, 255, 255)
        self.option_border = (100, 149, 237)
        self.text_color = (40, 40, 60)

        self.option_height = 38
        self.option_radius = 10
        self.padding_x = 14
        self.spacing = 8

        # Caminho para a imagem local, sem baixar automaticamente
        localappdata = os.getenv("LOCALAPPDATA")
        self.assets_path = os.path.join(localappdata, ".assets")
        os.makedirs(self.assets_path, exist_ok=True)
        self.icon_path = os.path.join(self.assets_path, "upgrades.png")

        try:
            self.icon = pygame.image.load(self.icon_path).convert_alpha()
            self.icon = pygame.transform.smoothscale(self.icon, (42, 42))
        except Exception:
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
        self.draw_icon()

        if self.visible:
            self.animation = min(1.0, self.animation + self.speed)
        else:
            self.animation = max(0.0, self.animation - self.speed)

        if self.animation <= 0:
            return

        full_h = len(self.upgrades) * (self.option_height + self.spacing) - self.spacing + 12
        height = int(full_h * self.animation)

        panel = pygame.Surface((self.width, height), pygame.SRCALPHA)
        pygame.draw.rect(panel, self.bg_color, (0, 0, self.width, height), border_radius=12)

        for i, upg in enumerate(self.upgrades):
            oy = 6 + i * (self.option_height + self.spacing)
            if oy + self.option_height > height:
                break
            rect = pygame.Rect(self.padding_x, oy, self.width - 2 * self.padding_x, self.option_height)

            qtd = self.purchased.get(upg.id, 0)
            color = (170, 250, 170) if qtd > 0 else self.option_color
            pygame.draw.rect(panel, color, rect, border_radius=self.option_radius)
            pygame.draw.rect(panel, self.option_border, rect, width=2, border_radius=self.option_radius)

            txt = self.font.render(
                f"{upg.name} (${upg.cost}) x{qtd}", True, self.text_color)
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
                    if upg_rect.collidepoint(event.pos):
                        qtd = self.purchased.get(upg.id, 0)
                        if score >= upg.cost:
                            self.purchased[upg.id] = qtd + 1
                            score -= upg.cost
                        break
        return score, self.purchased

    def load_upgrades(self, upgrades: dict):
        if not upgrades:
            self.purchased = {}
        else:
            self.purchased = upgrades

    def get_bonus(self):
        bonus = 1  # clique normal sempre dá 1 ponto base
        for upg in self.upgrades:
            qtd = self.purchased.get(upg.id, 0)
            if upg.id == "auto_click":
                continue  # auto click não soma no clique manual
            bonus += upg.bonus * qtd
        return bonus

    def auto_click_enabled(self):
        return self.purchased.get("auto_click", 0) > 0

    def get_auto_click_bonus(self):
        return self.purchased.get("auto_click", 0)

    def reset_upgrades(self):
        """Reseta os upgrades comprados e retorna o bônus a 0"""
        self.purchased.clear()
        print("Upgrades resetados com sucesso!")  # Mensagem de confirmação
