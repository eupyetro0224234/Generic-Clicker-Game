import pygame
import random
import os
from trabalhador import Trabalhador

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
        self.achievement_tracker = achievement_tracker

        # Position and appearance
        self.x = 10
        self.y = 10
        self.width = 280
        self.visible = False
        self.animation = 0.0
        self.speed = 0.12
        self.font = pygame.font.SysFont(None, 24)
        
        # Colors
        self.bg_color = (180, 210, 255)
        self.option_color = (255, 255, 255)
        self.purchased_color = (170, 250, 170)
        self.active_color = (170, 250, 170)
        self.option_border = (100, 149, 237)
        self.text_color = (40, 40, 60)

        # Layout
        self.option_height = 38
        self.option_radius = 10
        self.padding_x = 14
        self.spacing = 8

        # Upgrades
        self.upgrades = [
            Upgrade("hold_click", "Clique ao Segurar", 2500, 1),
            Upgrade("auto_click", "Auto Clique", 5000, 1),
            Upgrade("double", "Pontos em Dobro", 20000, 1),
            Upgrade("mega", "Mega Clique", 75000, 4),
            Upgrade("trabalhador", "Trabalhador", 1000, 0),
        ]

        # Icon
        self.icon = self._load_icon()
        self.icon_rect = pygame.Rect(self.x, self.y, 50, 50)
        
        # State
        self.purchased = {}
        self.auto_click_timer = 0
        self.trabalhador_instancia = None

    def _load_icon(self):
        localappdata = os.getenv("LOCALAPPDATA")
        assets_path = os.path.join(localappdata, ".assets")
        os.makedirs(assets_path, exist_ok=True)
        icon_path = os.path.join(assets_path, "upgrades.png")
        
        try:
            icon = pygame.image.load(icon_path).convert_alpha()
            return pygame.transform.smoothscale(icon, (42, 42))
        except Exception:
            return None

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
            
            if upg.id == "trabalhador":
                if self.trabalhador_instancia and self.trabalhador_instancia.active:
                    color = self.active_color
                elif qtd > 0:
                    color = self.option_color
                else:
                    color = self.option_color
            else:
                color = self.purchased_color if qtd > 0 else self.option_color
            
            pygame.draw.rect(panel, color, rect, border_radius=self.option_radius)
            pygame.draw.rect(panel, self.option_border, rect, width=2, border_radius=self.option_radius)

            txt = self.font.render(f"{upg.name} (${upg.cost}) x{qtd}", True, self.text_color)
            panel.blit(txt, txt.get_rect(center=rect.center))

        self.screen.blit(panel, (self.x, self.y + 60))

    def handle_event(self, event, score):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.icon_rect.collidepoint(event.pos):
                self.toggle()
                return score, self.purchased

            if self.visible:
                upgrades_to_show = [
                    upg for upg in self.upgrades
                    if not (upg.id == "hold_click" and self.purchased.get("hold_click", 0) >= 1)
                ]
                menu_height = len(upgrades_to_show) * (self.option_height + self.spacing) + 12
                menu_rect = pygame.Rect(self.x, self.y + 60, self.width, menu_height)

                if not menu_rect.collidepoint(event.pos):
                    self.visible = False
                    return score, self.purchased

                for i, upg in enumerate(upgrades_to_show):
                    upg_rect = pygame.Rect(
                        self.x + self.padding_x,
                        self.y + 66 + i * (self.option_height + self.spacing),
                        self.width - 2 * self.padding_x,
                        self.option_height
                    )
                    if upg_rect.collidepoint(event.pos):
                        qtd = self.purchased.get(upg.id, 0)
                        if score >= upg.cost:
                            if upg.id == "trabalhador":
                                if not self.trabalhador_instancia or not self.trabalhador_instancia.active:
                                    self.purchased[upg.id] = 1
                                    score -= upg.cost
                                    now = pygame.time.get_ticks()
                                    if self.trabalhador_instancia:
                                        self.trabalhador_instancia.start(now)
                                    else:
                                        self.trabalhador_instancia = Trabalhador(self.screen, self.window_width, self.window_height)
                                        self.trabalhador_instancia.start(now)
                            elif upg.id != "hold_click" or qtd == 0:
                                self.purchased[upg.id] = qtd + 1
                                score -= upg.cost
                                if upg.id == "hold_click" and self.achievement_tracker:
                                    self.achievement_tracker.unlock_secret("manual_phase")
                        break
        return score, self.purchased

    def load_upgrades(self, upgrades: dict):
        self.purchased = upgrades if upgrades else {}
        if "trabalhador" in self.purchased:
            self.trabalhador_instancia = Trabalhador(self.screen, self.window_width, self.window_height)

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
        """Completely resets all upgrades including worker instance"""
        self.purchased.clear()
        self.auto_click_timer = 0
        if self.trabalhador_instancia:
            self.trabalhador_instancia.active = False
            self.trabalhador_instancia = None  # Remove worker completely

    def purchase_random_upgrade(self):
        available_upgrades = [
            upg for upg in self.upgrades
            if upg.id not in self.purchased or self.purchased[upg.id] < 5
        ]
        if available_upgrades:
            upgrade = random.choice(available_upgrades)
            self.purchased[upgrade.id] = self.purchased.get(upgrade.id, 0) + 1
            return True
        return False

    def set_trabalhador(self, trabalhador):
        self.trabalhador_instancia = trabalhador