import pygame
import random
import os

class Upgrade:
    def __init__(self, id, name, cost, bonus):
        self.id = id
        self.name = name
        self.cost = cost
        self.bonus = bonus

class UpgradeMenu:
    def __init__(self, screen, window_width, window_height, achievement_tracker=None):
        self.screen = screen
        self.window_width = window_width
        self.window_height = window_height
        self.achievement_tracker = achievement_tracker  # novo parâmetro para conquistas

        self.x = 10
        self.y = 10
        self.width = 280
        self.visible = False
        self.animation = 0.0
        self.speed = 0.12
        self.font = pygame.font.SysFont(None, 24)
        self.purchased = {}
        self.auto_click_timer = 0

        self.upgrades = [
            Upgrade("hold_click", "Clique ao Segurar", 2500, 1),  # upgrade que desbloqueia conquista
            Upgrade("auto_click", "Auto Clique", 5000, 1),
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

        # Filtra upgrades para mostrar, excluindo hold_click se já comprado
        upgrades_to_show = [
            upg for upg in self.upgrades
            if not (upg.id == "hold_click" and self.purchased.get("hold_click", 0) >= 1)
        ]

        full_h = len(upgrades_to_show) * (self.option_height + self.spacing) - self.spacing + 12
        height = int(full_h * self.animation)

        panel = pygame.Surface((self.width, height), pygame.SRCALPHA)
        pygame.draw.rect(panel, self.bg_color, (0, 0, self.width, height), border_radius=12)

        for i, upg in enumerate(upgrades_to_show):
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
                # Filtra upgrades para clique, excluindo hold_click se comprado
                upgrades_to_click = [
                    upg for upg in self.upgrades
                    if not (upg.id == "hold_click" and self.purchased.get("hold_click", 0) >= 1)
                ]

                for i, upg in enumerate(upgrades_to_click):
                    upg_rect = pygame.Rect(
                        self.x + self.padding_x,
                        self.y + 66 + i * (self.option_height + self.spacing),
                        self.width - 2 * self.padding_x,
                        self.option_height
                    )
                    if upg_rect.collidepoint(event.pos):
                        qtd = self.purchased.get(upg.id, 0)
                        # Só permite comprar hold_click se ainda não comprado
                        if score >= upg.cost and (upg.id != "hold_click" or qtd == 0):
                            self.purchased[upg.id] = qtd + 1
                            score -= upg.cost

                            # Desbloqueia conquista ao comprar hold_click
                            if upg.id == "hold_click" and self.achievement_tracker:
                                self.achievement_tracker.unlock_secret("manual_phase")
                        break
        return score, self.purchased

    def load_upgrades(self, upgrades: dict):
        """Carrega os upgrades salvos."""
        if not upgrades:
            self.purchased = {}
        else:
            self.purchased = upgrades

    def get_bonus(self):
        bonus = 1 
        for upg in self.upgrades:
            qtd = self.purchased.get(upg.id, 0)
            if upg.id == "auto_click":
                continue
            bonus += upg.bonus * qtd
        return bonus

    def auto_click_enabled(self):
        return self.purchased.get("auto_click", 0) > 0

    def get_auto_click_bonus(self):
        return self.purchased.get("auto_click", 0)

    def reset_upgrades(self):
        """Reseta os upgrades comprados e retorna o bônus a 0"""
        self.purchased.clear()
        self.auto_click_timer = 0

    def purchase_random_upgrade(self):
        """Compra um upgrade aleatório (usado no mini evento)."""
        available_upgrades = [upg for upg in self.upgrades if upg.id not in self.purchased or self.purchased[upg.id] < 5]  # Exemplo: limite de 5 compras
        if available_upgrades:
            upgrade = random.choice(available_upgrades)
            self.purchased[upgrade.id] = self.purchased.get(upgrade.id, 0) + 1
            return True
        return False
