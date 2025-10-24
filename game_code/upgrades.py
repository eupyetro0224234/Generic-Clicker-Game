import pygame
import random
import os
import sys
from game_code.trabalhador import Trabalhador

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

        self.x = 15
        self.y = 15
        self.width = 400
        self.visible = False
        self.animation = 0.0
        self.speed = 0.12
        self.font = pygame.font.SysFont("None", 24)

        self.bg_color = (180, 210, 255)
        self.option_color = (255, 255, 255)
        self.purchased_color = (170, 250, 170)
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
            Upgrade("mini_event", "Trabalhador - Mini Evento", 15000, 1)
        ]

        self.icon = self._load_icon()
        self.icon_rect = pygame.Rect(self.x, self.y, 70, 70)

        self.purchased = {}
        self.trabalhadores = []
        self.max_trabalhadores = 10
        self.trabalhador_limit_enabled = True

    def _format_cost(self, cost):
        return f"{cost:,}".replace(",", ".")

    def _load_icon(self):
        try:
            if getattr(sys, 'frozen', False):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.abspath(".")
            icon_path = os.path.join(base_path, "game_assets", "upgrades.png")
            icon = pygame.image.load(icon_path).convert_alpha()
            return pygame.transform.smoothscale(icon, (60, 60))
        except Exception:
            return None

    def set_trabalhador_limit(self, enabled):
        self.trabalhador_limit_enabled = enabled
        
    def can_add_trabalhador(self):
        if not self.trabalhador_limit_enabled:
            return True
        return len(self.trabalhadores) < self.max_trabalhadores
        
    def get_trabalhador_limit_status(self):
        return self.trabalhador_limit_enabled

    def _get_trabalhador_text(self, upg):
        trabalhadores_ativos = len(self.trabalhadores)
        custo_formatado = self._format_cost(upg.cost)

        if not self.trabalhador_limit_enabled:
            return f"{upg.name} ({trabalhadores_ativos}) - {custo_formatado} pts"
        else:
            return f"{upg.name} ({trabalhadores_ativos}/{self.max_trabalhadores}) - {custo_formatado} pts"

    def toggle_visibility(self):
        self.visible = not self.visible

    def show_menu(self):
        self.visible = True

    def hide_menu(self):
        self.visible = False

    def draw_icon(self):
        if self.icon:
            icon_pos = (self.icon_rect.x + (self.icon_rect.width - self.icon.get_width()) // 2,
                        self.icon_rect.y + (self.icon_rect.height - self.icon.get_height()) // 2)
            self.screen.blit(self.icon, icon_pos)
        else:
            text = self.font.render("UPG", True, (255, 255, 255))
            text_rect = text.get_rect(center=self.icon_rect.center)
            self.screen.blit(text, text_rect)

    def draw(self, score=0):
        self.draw_icon()
        self.animation = min(1.0, self.animation + self.speed) if self.visible else max(0.0, self.animation - self.speed)
        if self.animation <= 0: 
            return

        upgrades_to_show = [
            upg for upg in self.upgrades 
            if not (
                (upg.id == "hold_click" and self.purchased.get("hold_click", 0) >= 1) or
                (upg.id == "mini_event" and self.purchased.get("mini_event", 0) >= 1)
            )
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
                trabalhadores_ativos = len(self.trabalhadores)

                if trabalhadores_ativos == 0:
                    color = self.option_color
                elif self.trabalhador_limit_enabled and trabalhadores_ativos >= self.max_trabalhadores:
                    color = (255, 150, 150)
                else:
                    color = self.purchased_color
            else:
                color = self.purchased_color if qtd > 0 else self.option_color
                
            pygame.draw.rect(panel, color, rect, border_radius=self.option_radius)
            pygame.draw.rect(panel, self.option_border, rect, width=2, border_radius=self.option_radius)
            
            if upg.id == "trabalhador":
                main_text = self._get_trabalhador_text(upg)
            elif upg.id == "hold_click":
                main_text = f"{upg.name} - {self._format_cost(upg.cost)} pts"
            elif upg.id == "mini_event":
                main_text = f"{upg.name} - {self._format_cost(upg.cost)} pts"
            else:
                main_text = f"{upg.name} x{qtd} - {self._format_cost(upg.cost)} pts"
                
            txt = self.font.render(main_text, True, self.text_color)
            text_rect = txt.get_rect(midleft=(rect.left + 10, rect.centery))
            panel.blit(txt, text_rect)

        self.screen.blit(panel, (self.x, self.y + 75))

    def handle_event(self, event, score):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.icon_rect.collidepoint(event.pos):
                self.toggle_visibility()
                return score, False

            if self.visible:
                upgrades_to_show = [
                    upg for upg in self.upgrades 
                    if not (
                        (upg.id == "hold_click" and self.purchased.get("hold_click", 0) >= 1) or
                        (upg.id == "mini_event" and self.purchased.get("mini_event", 0) >= 1)
                    )
                ]
                menu_height = len(upgrades_to_show) * (self.option_height + self.spacing) + 12
                menu_rect = pygame.Rect(self.x, self.y + 75, self.width, menu_height)
                if not menu_rect.collidepoint(event.pos):
                    self.visible = False
                    return score, False

                for i, upg in enumerate(upgrades_to_show):
                    upg_rect = pygame.Rect(self.x + self.padding_x, self.y + 81 + i * (self.option_height + self.spacing),
                                           self.width - 2 * self.padding_x, self.option_height)
                    if upg_rect.collidepoint(event.pos) and score >= upg.cost:
                        if upg.id == "trabalhador" and self.can_add_trabalhador():
                            novo_trabalhador = Trabalhador(self.screen, self.window_width, self.window_height)
                            self.trabalhadores.append(novo_trabalhador)
                            score -= upg.cost
                            
                            self.purchased[upg.id] = self.purchased.get(upg.id, 0) + 1
                            
                            if self.achievement_tracker:
                                if self.purchased[upg.id] == 1: 
                                    self.achievement_tracker.unlock_secret("worker")
                                elif self.purchased[upg.id] >= 5: 
                                    self.achievement_tracker.unlock_secret("worker_army")
                            return score, True
                        elif upg.id != "trabalhador":
                            self.purchased[upg.id] = self.purchased.get(upg.id, 0) + 1
                            score -= upg.cost
                            return score, False
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_u:
                self.toggle_visibility()
                return score, False
                
        return score, False

    def load_upgrades(self, upgrades: dict):
        self.purchased = upgrades if upgrades else {}
    
    def load_trabalhadores(self, trabalhadores_data):
        self.trabalhadores = []
        for trab_data in trabalhadores_data:
            from game_code.trabalhador import Trabalhador
            novo_trab = Trabalhador.from_state(
                screen=self.screen,
                width=self.window_width,
                height=self.window_height,
                state=trab_data
            )
            self.trabalhadores.append(novo_trab)

    def get_bonus(self):
        bonus = 1
        for upg in self.upgrades:
            qtd = self.purchased.get(upg.id, 0)
            if upg.id not in ["auto_click", "trabalhador", "mini_event"]:
                bonus += upg.bonus * qtd
        return bonus

    def auto_click_enabled(self):
        return self.purchased.get("auto_click", 0) > 0

    def get_auto_click_bonus(self):
        return self.purchased.get("auto_click", 0)

    def mini_event_enabled(self):
        return self.purchased.get("mini_event", 0) > 0

    def get_mini_event_bonus(self):
        return self.purchased.get("mini_event", 0)

    def get_trabalhador_pontos(self):
        return 1

    def get_trabalhador_intervalo(self):
        return 5000

    def reset_upgrades(self):
        self.purchased.clear()
        self.trabalhadores = []
        self.trabalhador_limit_enabled = True

    def purchase_random_upgrade(self):
        available_upgrades = [
            upg for upg in self.upgrades 
            if upg.id not in self.purchased or self.purchased.get(upg.id, 0) < 5
        ]
        if available_upgrades:
            upgrade = random.choice(available_upgrades)
            self.purchased[upgrade.id] = self.purchased.get(upgrade.id, 0) + 1
            if upgrade.id == "trabalhador" and self.can_add_trabalhador():
                self.trabalhadores.append(Trabalhador(self.screen, self.window_width, self.window_height))
            return True
        return False

    def get_upgrades_to_save(self):
        return self.purchased.copy()
    
    def update_trabalhadores(self, delta_time):
        pontos_gerados = 0
        
        for trabalhador in self.trabalhadores[:]:
            pontos = trabalhador.update(delta_time)
            if pontos:
                pontos_gerados += pontos
            
            if not trabalhador.active:
                self.trabalhadores.remove(trabalhador)
        
        return pontos_gerados

    def draw_trabalhadores(self):
        for trabalhador in self.trabalhadores:
            if hasattr(trabalhador, 'draw'):
                trabalhador.draw()

    def get_trabalhadores_ativos(self):
        return len(self.trabalhadores)

    def set_trabalhadores_ativos(self, qtd):
        pass