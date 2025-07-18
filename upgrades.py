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
        self.amount = 0

class UpgradeMenu:
    def __init__(self, screen, window_width, window_height, achievement_tracker=None):
        self.screen = screen
        self.window_width = window_width
        self.window_height = window_height
        self.achievement_tracker = achievement_tracker

        self.x = 10
        self.y = 10
        self.width = 280
        self.visible = False
        self.animation = 0.0
        self.speed = 0.12
        self.font = pygame.font.SysFont("None", 24)

        self.bg_color = (180, 210, 255)
        self.option_color = (255, 255, 255)
        self.purchased_color = (170, 250, 170)
        self.active_color = (170, 250, 170)
        self.option_border = (100, 149, 237)
        self.text_color = (40, 40, 60)

        self.option_height = 38
        self.option_radius = 10
        self.padding_x = 14
        self.spacing = 8

        self.upgrades = [
            Upgrade("hold_click", "Clique ao Segurar", 2500, 1),
            Upgrade("auto_click", "Auto Clique", 5000, 1),
            Upgrade("double", "Pontos em Dobro", 20000, 1),
            Upgrade("mega", "Mega Clique", 75000, 4),
            Upgrade("trabalhador", "Contratar Trabalhador", 1000, 0),
        ]

        self.icon = self._load_icon()
        self.icon_rect = pygame.Rect(self.x, self.y, 50, 50)

        self.purchased = {}
        self.trabalhadores_ativos = 0

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

    def is_trabalhador_comprado(self):
        return self.purchased.get("trabalhador", 0) > 0

    def get_trabalhador_quantidade(self):
        return self.trabalhadores_ativos

    def set_trabalhadores_ativos(self, quantidade):
        self.trabalhadores_ativos = quantidade

    def get_icon_rect(self):
        return self.icon_rect

    def toggle_visibility(self):
        self.visible = not self.visible

    def is_visible(self):
        return self.visible

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

            # Ajuste de cor para trabalhadores: se não tiver ativos, mostra como se nunca comprado
            if upg.id == "trabalhador" and self.trabalhadores_ativos == 0:
                color = self.option_color
            else:
                color = self.purchased_color if qtd > 0 else self.option_color

            pygame.draw.rect(panel, color, rect, border_radius=self.option_radius)
            pygame.draw.rect(panel, self.option_border, rect, width=2, border_radius=self.option_radius)

            # Texto também ajustado
            if upg.id == "trabalhador":
                if self.trabalhadores_ativos == 0:
                    main_text = f"{upg.name} (${upg.cost})"
                else:
                    main_text = f"{upg.name} x{self.trabalhadores_ativos}"
            else:
                main_text = f"{upg.name} (${upg.cost})" if qtd == 0 else f"{upg.name} x{qtd}"

            txt = self.font.render(main_text, True, self.text_color)
            text_rect = txt.get_rect(center=rect.center)
            panel.blit(txt, text_rect)

        self.screen.blit(panel, (self.x, self.y + 60))

    def handle_event(self, event, score):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.icon_rect.collidepoint(event.pos):
                self.toggle()
                return score, False

            if self.visible:
                upgrades_to_show = [
                    upg for upg in self.upgrades
                    if not (upg.id == "hold_click" and self.purchased.get("hold_click", 0) >= 1)
                ]
                menu_height = len(upgrades_to_show) * (self.option_height + self.spacing) + 12
                menu_rect = pygame.Rect(self.x, self.y + 60, self.width, menu_height)

                if not menu_rect.collidepoint(event.pos):
                    self.visible = False
                    return score, False

                for i, upg in enumerate(upgrades_to_show):
                    upg_rect = pygame.Rect(
                        self.x + self.padding_x,
                        self.y + 66 + i * (self.option_height + self.spacing),
                        self.width - 2 * self.padding_x,
                        self.option_height
                    )
                    if upg_rect.collidepoint(event.pos):
                        if score >= upg.cost:
                            if upg.id == "trabalhador":
                                self.purchased[upg.id] = self.purchased.get(upg.id, 0) + 1
                                self.trabalhadores_ativos += 1
                                score -= upg.cost
                                if self.achievement_tracker:
                                    if self.purchased[upg.id] == 1:
                                        self.achievement_tracker.unlock_secret("worker")
                                    elif self.purchased[upg.id] >= 5:
                                        self.achievement_tracker.unlock_secret("worker_army")
                                return score, True
                            else:
                                self.purchased[upg.id] = self.purchased.get(upg.id, 0) + 1
                                score -= upg.cost
                                return score, False
                        break

        return score, False

    def load_upgrades(self, upgrades: dict):
        self.purchased = upgrades if upgrades else {}
        self.trabalhadores_ativos = self.purchased.get("trabalhador", 0)

    def get_bonus(self):
        bonus = 1
        for upg in self.upgrades:
            qtd = self.purchased.get(upg.id, 0)
            if upg.id in ["auto_click", "trabalhador"]:
                continue
            bonus += upg.bonus * qtd
        return bonus

    def auto_click_enabled(self):
        return self.purchased.get("auto_click", 0) > 0

    def get_auto_click_bonus(self):
        return self.purchased.get("auto_click", 0)

    def get_trabalhador_pontos(self):
        return 1

    def get_trabalhador_intervalo(self):
        return 5000

    def reset_upgrades(self):
        self.purchased.clear()
        self.trabalhadores_ativos = 0

    def purchase_random_upgrade(self):
        available_upgrades = [
            upg for upg in self.upgrades
            if upg.id not in self.purchased or (isinstance(self.purchased.get(upg.id, 0), int) and self.purchased[upg.id] < 5)
        ]
        if available_upgrades:
            upgrade = random.choice(available_upgrades)
            self.purchased[upgrade.id] = self.purchased.get(upgrade.id, 0) + 1
            if upgrade.id == "trabalhador":
                self.trabalhadores_ativos += 1
            return True
        return False

    def get_upgrades_to_save(self):
        return self.purchased.copy()
