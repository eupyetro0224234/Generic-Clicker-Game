import pygame, random, os, sys
from game_code.trabalhador import Trabalhador

class Upgrade:
    def __init__(self, id, name, cost, bonus, price_increase=0, bonus_increment=0):
        self.id = id
        self.name = name
        self.base_cost = cost
        self.cost = cost
        self.bonus = bonus
        self.bonus_increment = bonus_increment
        self.amount = 0
        self.price_increase = price_increase

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
        self.font = pygame.font.SysFont("None", 26)

        self.bg_color = (180, 210, 255, 180)
        self.option_color = (255, 255, 255, 220)
        self.option_hover_color = (200, 220, 255, 240)
        self.purchased_color = (170, 250, 170, 180)
        self.purchased_hover_color = (170, 250, 170, 255)
        self.option_border = (150, 180, 230, 160)
        self.text_color = (40, 40, 60)
        self.glass_highlight = (255, 255, 255, 60)

        self.option_height = 40
        self.option_radius = 16
        self.padding_x = 10
        self.spacing = 6

        self.upgrades = [
            Upgrade("hold_click", "Click ao Segurar", 2500, 1),
            Upgrade("auto_click", "Auto Click", 5000, 1, price_increase=250),
            Upgrade("double", "Clique Aprimorado", 2000, 1, price_increase=100, bonus_increment=0.2),
            Upgrade("clique_potente", "Clique Potente", 6000, 2, price_increase=200, bonus_increment=1),
            Upgrade("mega", "Mega Click", 10000, 4, price_increase=4000, bonus_increment=2),
            Upgrade("trabalhador", "Contratar Trabalhador", 1000, 0),
            Upgrade("mini_event", "Trabalhador: Mini Evento", 15000, 1),
            Upgrade("auto_compra_trabalhador", "Auto Compra: Trabalhador", 3500, 0),
            Upgrade("ganhos_offline", "Ganhos Offline", 12000, 0)
        ]

        self.icon = self._load_icon()
        self.icon_rect = pygame.Rect(self.x, self.y, 70, 70)

        self.purchased = {}
        self.trabalhadores = []
        self.max_trabalhadores = 10
        self.trabalhador_limit_enabled = True

        self.purchase_quantity = 1
        self.hovered_option = None
        
        self.offline_time_bank = 0
        self.max_offline_time = 7200

    def add_offline_time(self, seconds=30):
        if self.ganhos_offline_enabled():
            self.offline_time_bank = min(self.offline_time_bank + seconds, self.max_offline_time)

    def get_offline_time_formatted(self):
        hours = self.offline_time_bank // 3600
        minutes = (self.offline_time_bank % 3600) // 60
        seconds = self.offline_time_bank % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

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

    def auto_comprar_trabalhador(self, score):
        if (self.purchased.get("auto_compra_trabalhador", 0) > 0 and 
            self.can_add_trabalhador() and score >= 950):
            
            novo_trabalhador = Trabalhador(self.screen, self.window_width, self.window_height)
            self.trabalhadores.append(novo_trabalhador)
            score -= 100
            self.purchased["trabalhador"] = self.purchased.get("trabalhador", 0) + 1
        return score

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

    def _draw_rounded_rect_aa(self, surface, color, rect, radius):
        temp_surface = pygame.Surface((rect[2] + 4, rect[3] + 4), pygame.SRCALPHA)
        temp_surface.fill((0, 0, 0, 0))
        
        temp_rect = pygame.Rect(2, 2, rect[2], rect[3])
        pygame.draw.rect(temp_surface, color, temp_rect, border_radius=radius)
        
        surface.blit(temp_surface, (rect[0] - 2, rect[1] - 2))

    def _create_glass_effect(self, width, height):
        glass_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        glass_surface.fill((0, 0, 0, 0))
        
        self._draw_rounded_rect_aa(glass_surface, self.bg_color, (0, 0, width, height), 20)
        
        highlight = pygame.Surface((width, height), pygame.SRCALPHA)
        highlight.fill((0, 0, 0, 0))
        for i in range(height):
            alpha = int(50 * (1 - i / height * 0.6))
            pygame.draw.line(highlight, (255, 255, 255, alpha), (0, i), (width, i))
        
        mask = pygame.Surface((width, height), pygame.SRCALPHA)
        mask.fill((0, 0, 0, 0))
        self._draw_rounded_rect_aa(mask, (255, 255, 255, 255), (0, 0, width, height), 20)
        
        highlight.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        glass_surface.blit(highlight, (0, 0))
        
        border_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        border_surface.fill((0, 0, 0, 0))
        self._draw_rounded_rect_aa(border_surface, (0, 0, 0, 0), (0, 0, width, height), 20)
        pygame.draw.rect(border_surface, self.option_border, (0, 0, width, height), 
                        width=2, border_radius=20)
        glass_surface.blit(border_surface, (0, 0))
        
        return glass_surface

    def _create_glass_option(self, width, height, color):
        option_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        option_surface.fill((0, 0, 0, 0))
        
        self._draw_rounded_rect_aa(option_surface, color, (0, 0, width, height), 14)
        
        highlight = pygame.Surface((width, height), pygame.SRCALPHA)
        highlight.fill((0, 0, 0, 0))
        for i in range(height):
            alpha = int(40 * (1 - i / height * 0.7))
            pygame.draw.line(highlight, (255, 255, 255, alpha), (0, i), (width, i))
        
        mask = pygame.Surface((width, height), pygame.SRCALPHA)
        mask.fill((0, 0, 0, 0))
        self._draw_rounded_rect_aa(mask, (255, 255, 255, 255), (0, 0, width, height), 14)
        
        highlight.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        option_surface.blit(highlight, (0, 0))
        
        border_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        border_surface.fill((0, 0, 0, 0))
        self._draw_rounded_rect_aa(border_surface, (0, 0, 0, 0), (0, 0, width, height), 14)
        pygame.draw.rect(border_surface, self.option_border, (0, 0, width, height), 
                        width=1, border_radius=14)
        option_surface.blit(border_surface, (0, 0))
        
        return option_surface

    def draw(self, score=0):
        self.draw_icon()
        self.animation = min(1.0, self.animation + self.speed) if self.visible else max(0.0, self.animation - self.speed)
        if self.animation <= 0: 
            return

        mouse_pos = pygame.mouse.get_pos()
        self.hovered_option = None

        upgrades_to_show = [
            upg for upg in self.upgrades 
            if not (
                (upg.id == "hold_click" and self.purchased.get("hold_click", 0) >= 1) or
                (upg.id == "mini_event" and self.purchased.get("mini_event", 0) >= 1) or
                (upg.id == "auto_compra_trabalhador" and self.purchased.get("auto_compra_trabalhador", 0) >= 1) or
                (upg.id == "ganhos_offline" and self.purchased.get("ganhos_offline", 0) >= 1)
            )
        ]
        
        vertical_padding = 12
        full_h = len(upgrades_to_show) * (self.option_height + self.spacing) - self.spacing + 2 * vertical_padding
        height = int(full_h * self.animation)

        panel = self._create_glass_effect(self.width, height)

        for i, upg in enumerate(upgrades_to_show):
            oy = vertical_padding + i * (self.option_height + self.spacing)
            if oy + self.option_height > height: 
                break
                
            rect_width = self.width - 2 * self.padding_x
            option_rect = pygame.Rect(self.x + self.padding_x, self.y + 75 + oy, rect_width, self.option_height)
            
            is_hovered = option_rect.collidepoint(mouse_pos)
            if is_hovered:
                self.hovered_option = upg.id

            if upg.id == "trabalhador":
                trabalhadores_ativos = len(self.trabalhadores)
                if trabalhadores_ativos == 0:
                    base_color = self.option_hover_color if is_hovered else self.option_color
                elif self.trabalhador_limit_enabled and trabalhadores_ativos >= self.max_trabalhadores:
                    base_color = (255, 150, 150, 220)
                else:
                    base_color = self.purchased_hover_color if is_hovered else self.purchased_color
            else:
                if self.purchased.get(upg.id, 0) > 0:
                    base_color = self.purchased_hover_color if is_hovered else self.purchased_color
                else:
                    base_color = self.option_hover_color if is_hovered else self.option_color
            
            option_surface = self._create_glass_option(rect_width, self.option_height, base_color)
            panel.blit(option_surface, (self.padding_x, oy))
            
            if upg.id == "trabalhador":
                main_text = self._get_trabalhador_text(upg)
            elif upg.id in ["hold_click", "mini_event", "auto_compra_trabalhador", "ganhos_offline"]:
                main_text = f"{upg.name} - {self._format_cost(upg.cost)} pts"
            else:
                main_text = f"{upg.name} x{self.purchased.get(upg.id, 0)} - {self._format_cost(upg.cost)} pts"
                
            txt = self.font.render(main_text, True, self.text_color)
            text_rect = txt.get_rect(midleft=(self.padding_x + 10, oy + self.option_height // 2))
            panel.blit(txt, text_rect)
            
            if upg.id not in ["hold_click", "mini_event", "auto_compra_trabalhador", "ganhos_offline"] and self.purchase_quantity > 1:
                qtd_text = self.font.render(f"+{self.purchase_quantity}", True, (60, 80, 120))
                qtd_text_rect = qtd_text.get_rect(midright=(self.width - self.padding_x - 10, oy + self.option_height // 2))
                panel.blit(qtd_text, qtd_text_rect)

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
                        (upg.id == "mini_event" and self.purchased.get("mini_event", 0) >= 1) or
                        (upg.id == "auto_compra_trabalhador" and self.purchased.get("auto_compra_trabalhador", 0) >= 1) or
                        (upg.id == "ganhos_offline" and self.purchased.get("ganhos_offline", 0) >= 1)
                    )
                ]
                vertical_padding = 12
                menu_height = len(upgrades_to_show) * (self.option_height + self.spacing) - self.spacing + 2 * vertical_padding
                menu_rect = pygame.Rect(self.x, self.y + 75, self.width, menu_height)
                if not menu_rect.collidepoint(event.pos):
                    self.visible = False
                    return score, False

                for i, upg in enumerate(upgrades_to_show):
                    upg_rect = pygame.Rect(self.x + self.padding_x, self.y + 75 + vertical_padding + i * (self.option_height + self.spacing),
                                           self.width - 2 * self.padding_x, self.option_height)
                    if upg_rect.collidepoint(event.pos) and score >= upg.cost:
                        if upg.id == "trabalhador":
                            compras = min(self.purchase_quantity, self.max_trabalhadores - len(self.trabalhadores)) \
                                      if self.trabalhador_limit_enabled else self.purchase_quantity
                            total_custo = upg.cost * compras
                            if score >= total_custo and compras > 0:
                                for _ in range(compras):
                                    novo_trabalhador = Trabalhador(self.screen, self.window_width, self.window_height)
                                    self.trabalhadores.append(novo_trabalhador)
                                score -= total_custo
                                self.purchased[upg.id] = self.purchased.get(upg.id, 0) + compras
                                if self.achievement_tracker:
                                    if self.purchased[upg.id] == 1: 
                                        self.achievement_tracker.unlock_secret("worker")
                                    elif self.purchased[upg.id] >= 5: 
                                        self.achievement_tracker.unlock_secret("worker_army")
                                    self.achievement_tracker.check_all_upgrades_purchased(self)
                                return score, True
                        elif upg.id not in ["hold_click", "mini_event", "auto_compra_trabalhador", "ganhos_offline"]:
                            compras = self.purchase_quantity
                            total_custo = upg.cost * compras
                            if score >= total_custo:
                                self.purchased[upg.id] = self.purchased.get(upg.id, 0) + compras
                                score -= total_custo
                                
                                if upg.price_increase > 0:
                                    upg.cost += upg.price_increase * compras
                                
                                if self.achievement_tracker:
                                    self.achievement_tracker.check_all_upgrades_purchased(self)
                                return score, False
                        else:
                            self.purchased[upg.id] = 1
                            score -= upg.cost
                            if self.achievement_tracker:
                                if upg.id == "hold_click":
                                    self.achievement_tracker.unlock_secret("manual_phase")
                                elif upg.id == "auto_click":
                                    self.achievement_tracker.unlock_secret("automatico")
                                elif upg.id == "ganhos_offline":
                                    self.achievement_tracker.unlock_secret("offline_earnings")
                                self.achievement_tracker.check_all_upgrades_purchased(self)
                            return score, False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_u:
                self.toggle_visibility()
                return score, False
            elif event.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
                self.purchase_quantity += 1
                if self.trabalhador_limit_enabled:
                    self.purchase_quantity = min(self.purchase_quantity, 10)
            elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                self.purchase_quantity = max(1, self.purchase_quantity - 1)

        return score, False

    def load_upgrades(self, upgrades: dict):
        self.purchased = upgrades if upgrades else {}
        
        for upg in self.upgrades:
            upg.cost = upg.base_cost
            if upg.price_increase > 0 and upg.id in self.purchased:
                upg.cost += upg.price_increase * self.purchased[upg.id]
        
        if self.achievement_tracker and self.purchased.get("auto_click", 0) > 0:
            self.achievement_tracker.unlock_secret("automatico")
        if self.achievement_tracker:
            self.achievement_tracker.check_all_upgrades_purchased(self)

    def load_trabalhadores(self, trabalhadores_data):
        self.trabalhadores = []
        for trab_data in trabalhadores_data:
            novo_trab = Trabalhador.from_state(
                screen=self.screen,
                width=self.window_width,
                height=self.window_height,
                state=trab_data
            )
            self.trabalhadores.append(novo_trab)

    def get_bonus(self):
        bonus = 1.0
        for upg in self.upgrades:
            qtd = self.purchased.get(upg.id, 0)
            if upg.id not in ["auto_click", "trabalhador", "mini_event", "auto_compra_trabalhador", "ganhos_offline"]:
                if qtd > 0:
                    if upg.bonus_increment > 0:
                        bonus += upg.bonus + (upg.bonus_increment * (qtd - 1))
                    else:
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

    def ganhos_offline_enabled(self):
        return self.purchased.get("ganhos_offline", 0) > 0

    def get_trabalhador_pontos(self):
        return 1

    def get_trabalhador_intervalo(self):
        return 5000

    def update_trabalhadores(self, delta_time, score):
        pontos_gerados = 0
        trabalhadores_removidos = 0
        
        for trabalhador in self.trabalhadores[:]:
            pontos = trabalhador.update(delta_time)
            if pontos:
                pontos_gerados += pontos
            
            if not trabalhador.active:
                self.trabalhadores.remove(trabalhador)
                trabalhadores_removidos += 1
        
        if trabalhadores_removidos > 0 and self.purchased.get("auto_compra_trabalhador", 0) > 0:
            score = self.auto_comprar_trabalhador(score)
        
        return pontos_gerados, score

    def reset_upgrades(self):
        for upg in self.upgrades:
            upg.cost = upg.base_cost
        
        self.purchased.clear()
        self.trabalhadores = []
        self.trabalhador_limit_enabled = True
        self.purchase_quantity = 1
        self.offline_time_bank = 0

    def purchase_random_upgrade(self):
        available_upgrades = [
            upg for upg in self.upgrades 
            if upg.id not in self.purchased or self.purchased.get(upg.id, 0) < 5
        ]
        if available_upgrades:
            upgrade = random.choice(available_upgrades)
            self.purchased[upgrade.id] = self.purchased.get(upgrade.id, 0) + 1
            
            if upgrade.price_increase > 0:
                upgrade.cost += upgrade.price_increase
            
            if upgrade.id == "auto_click" and self.purchased[upgrade.id] == 1:
                if self.achievement_tracker:
                    self.achievement_tracker.unlock_secret("automatico")
                    
            if upgrade.id == "trabalhador" and self.can_add_trabalhador():
                self.trabalhadores.append(Trabalhador(self.screen, self.window_width, self.window_height))
            
            if self.achievement_tracker:
                self.achievement_tracker.check_all_upgrades_purchased(self)
                
            return True
        return False

    def get_upgrades_to_save(self):
        return self.purchased.copy()

    def draw_trabalhadores(self):
        for trabalhador in self.trabalhadores:
            if hasattr(trabalhador, 'draw'):
                trabalhador.draw()

    def get_trabalhadores_ativos(self):
        return len(self.trabalhadores)

    def set_trabalhadores_ativos(self, qtd):
        pass