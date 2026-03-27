import pygame, random
from game_code.trabalhador import Trabalhador

class Upgrade:
    def __init__(self, id, name, cost, bonus, price_increase=0, bonus_increment=0, requires=None, requires_amount=0):
        self.id = id
        self.name = name
        self.base_cost = cost
        self.cost = cost
        self.bonus = bonus
        self.bonus_increment = bonus_increment
        self.amount = 0
        self.price_increase = price_increase
        self.requires = requires
        self.requires_amount = requires_amount

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
        self.locked_color = (180, 180, 180, 160)
        self.option_border = (150, 180, 230, 160)
        self.text_color = (40, 40, 60)
        self.locked_text_color = (120, 120, 140)
        self.glass_highlight = (255, 255, 255, 60)

        self.option_height = 40
        self.option_radius = 16
        self.padding_x = 10
        self.spacing = 6

        self.upgrades = [
            Upgrade("double", "Clique Aprimorado", 2000, 1, price_increase=100, bonus_increment=0.5),
            Upgrade("pequeno_auto_click", "Pequeno Auto Click", 2500, 0, price_increase=150,
                    requires="double", requires_amount=6),
            Upgrade("clique_potente", "Clique Potente", 6000, 2, price_increase=200, bonus_increment=1.5,
                    requires="pequeno_auto_click", requires_amount=24),
            Upgrade("auto_click_medio", "Auto Clicker Médio", 7000, 0, price_increase=300,
                    requires="clique_potente", requires_amount=6),
            Upgrade("mega", "Mega Click", 10000, 4, price_increase=4000, bonus_increment=5,
                    requires="auto_click_medio", requires_amount=11),
            Upgrade("trabalhador", "Contratar Trabalhador", 1000, 0,
        	    requires="mega", requires_amount=1),
            Upgrade("hold_click", "Click ao Segurar", 2500, 1,
                    requires="trabalhador", requires_amount=10),
            Upgrade("auto_click", "Auto Click", 5000, 1, price_increase=250,
                    requires="hold_click", requires_amount=1),
            Upgrade("auto_compra_trabalhador", "Auto Compra: Trabalhador", 3500, 0,
                    requires="auto_click", requires_amount=5),
            Upgrade("ganhos_offline", "Ganhos Offline", 12000, 0,
                    requires="auto_compra_trabalhador", requires_amount=1),
            Upgrade("mini_event", "Trabalhador: Mini Evento", 15000, 1,
                    requires="ganhos_offline", requires_amount=1),
            Upgrade("tempo_aprimorado", "Tempo Aprimorado", 20000, 0,
                    requires="mini_event", requires_amount=1),
        ]

        self.icon = self._load_icon()
        self.icon_rect = pygame.Rect(self.x, self.y, 70, 70)

        self.purchased = {}
        self.trabalhadores = []
        self.max_trabalhadores = 10
        self.trabalhador_limit_enabled = True
        self.trabalhador_time_enabled = True

        self.purchase_quantity = 1
        self.hovered_option = None
        
        self.offline_time_bank = 0
        self.max_offline_time = float('inf')
        
        self.auto_compra_timer = 0
        self.auto_compra_intervalo = 1500
        self.clock = pygame.time.Clock()
        self.menu_clock = pygame.time.Clock()
        
        self.auto_compra_ativa = True
        
        self.option_surface_cache = {}
        self.panel_cache = {}
        self.text_cache = {}
        self.upgrades_dirty = True
        self.cached_upgrades_to_show = []

        self.visible_upgrade_count = 1
        self.reveal_timer = 0
        self.reveal_interval = 15000

        self.holding_upgrade = None
        self.holding_upgrade_index = None
        self.hold_start_time = 0
        self.auto_buy_active = False
        self.auto_buy_last_time = 0
        self.auto_buy_interval = 200
        self.hold_duration = 1000

    def is_unlocked(self, upg):
        if upg.requires:
            return self.purchased.get(upg.requires, 0) >= upg.requires_amount
        return True

    def _get_lock_text(self, upg):
        req_upg = next((u for u in self.upgrades if u.id == upg.requires), None)
        req_name = req_upg.name if req_upg else upg.requires
        return f"🔒 {req_name} x{upg.requires_amount}"

    def _load_icon(self):
        try:
            from game_assets.game_assets_packed import load_image
            icon = load_image("upgrades.png")
            return pygame.transform.smoothscale(icon, (60, 60))
        except Exception:
            return None

    def export_trabalhadores(self):
        trabalhadores_data = []
        for trabalhador in self.trabalhadores:
            if hasattr(trabalhador, 'get_state'):
                trabalhadores_data.append(trabalhador.get_state())
            else:
                trabalhadores_data.append({
                    'active': getattr(trabalhador, 'active', True),
                    'visible': getattr(trabalhador, 'visible', True),
                    'x': getattr(trabalhador, 'x', 0),
                    'y': getattr(trabalhador, 'y', 0),
                    'speed_x': getattr(trabalhador, 'speed_x', 0),
                    'speed_y': getattr(trabalhador, 'speed_y', 0)
                })
        return trabalhadores_data

    @property
    def auto_compra_enabled(self):
        return self.auto_compra_ativa

    def update_trabalhadores(self, current_time, delta_time, score):
        pontos_gerados = 0
        
        trabalhadores_ativos = [t for t in self.trabalhadores if t.active]
        
        for trabalhador in trabalhadores_ativos:
            pontos = trabalhador.update(current_time)
            if pontos:
                pontos_gerados += pontos

        self.trabalhadores = [t for t in self.trabalhadores if t.active]

        if self.purchased.get("auto_compra_trabalhador", 0) > 0 and self.auto_compra_ativa:
            delta_seguro = min(delta_time, 200)
            
            self.auto_compra_timer += delta_seguro
            
            if self.auto_compra_timer >= self.auto_compra_intervalo:
                self.auto_compra_timer = 0
                
                trabalhador_upgrade = next((upg for upg in self.upgrades if upg.id == "trabalhador"), None)
                
                if trabalhador_upgrade and score >= trabalhador_upgrade.cost:
                    if self.can_add_trabalhador():
                        novo_trabalhador = Trabalhador(self.screen, self.window_width, self.window_height)
                        if not self.trabalhador_time_enabled:
                            novo_trabalhador.lifetime = None
                        self.trabalhadores.append(novo_trabalhador)
                        score -= trabalhador_upgrade.cost
                        self.purchased["trabalhador"] = self.purchased.get("trabalhador", 0) + 1
                        
                        if self.achievement_tracker:
                            if self.purchased["trabalhador"] == 1:
                                self.achievement_tracker.unlock_secret("worker")
                            elif self.purchased["trabalhador"] >= 5:
                                self.achievement_tracker.unlock_secret("worker_army")
                            self.achievement_tracker.check_all_upgrades_purchased(self)
    
        return pontos_gerados, score

    def draw_trabalhadores(self):
        if not self.trabalhadores:
            return
        
        for trabalhador in self.trabalhadores:
            if trabalhador.visible and hasattr(trabalhador, 'draw'):
                trabalhador.draw()

    def load_trabalhadores(self, trabalhadores_data):
        if not trabalhadores_data:
            self.trabalhadores = []
            return
        
        self.trabalhadores = [
            Trabalhador.from_state(
                screen=self.screen,
                width=self.window_width,
                height=self.window_height,
                state=trab_data
            )
            for trab_data in trabalhadores_data
        ]

    def cleanup(self):
        Trabalhador.clear_cache()
        self.trabalhadores.clear()
        self.option_surface_cache.clear()
        self.panel_cache.clear()
        self.text_cache.clear()

    def get_option_surface(self, width, height, color):
        key = (width, height, color)
        if key not in self.option_surface_cache:
            self.option_surface_cache[key] = self._create_glass_option(width, height, color)
        return self.option_surface_cache[key]

    def get_panel_surface(self, width, height):
        key = (width, height)
        if key not in self.panel_cache:
            self.panel_cache[key] = self._create_glass_effect(width, height)
        return self.panel_cache[key]

    def get_text(self, text, color=None):
        cache_key = (text, color)
        if cache_key not in self.text_cache:
            render_color = color if color else self.text_color
            self.text_cache[cache_key] = self.font.render(text, True, render_color)
        return self.text_cache[cache_key]

    def _update_reveal(self, delta_ms):
        total_upgrades = len(self.upgrades)
        if self.visible_upgrade_count >= total_upgrades:
            return

        self.reveal_timer += delta_ms
        while self.reveal_timer >= self.reveal_interval and self.visible_upgrade_count < total_upgrades:
            self.reveal_timer -= self.reveal_interval
            self.visible_upgrade_count += 1
            self.upgrades_dirty = True

    def update_upgrades_cache(self):
        ONE_TIME = {"hold_click", "mini_event", "auto_compra_trabalhador", "ganhos_offline", "tempo_aprimorado"}

        revealed = []
        for upg in self.upgrades:
            if upg.id in ONE_TIME and self.purchased.get(upg.id, 0) >= 1:
                continue
            if upg.requires:
                if self.is_unlocked(upg):
                    revealed.append(upg)
            else:
                revealed.append(upg)

        self.cached_upgrades_to_show = revealed
        self.upgrades_dirty = False

    def toggle_auto_compra(self):
        if self.purchased.get("auto_compra_trabalhador", 0) <= 0:
            return self.auto_compra_ativa
        self.auto_compra_ativa = not self.auto_compra_ativa
        return self.auto_compra_ativa

    def add_offline_time(self, seconds=30):
        if self.ganhos_offline_enabled():
            self.offline_time_bank += seconds

    def get_offline_time_formatted(self):
        hours = self.offline_time_bank // 3600
        minutes = (self.offline_time_bank % 3600) // 60
        seconds = self.offline_time_bank % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def _format_cost(self, cost):
        return f"{cost:,}".replace(",", ".")

    def auto_comprar_trabalhador(self, score):
        trabalhador_upgrade = next((upg for upg in self.upgrades if upg.id == "trabalhador"), None)
        
        if (self.auto_compra_ativa and
            self.purchased.get("auto_compra_trabalhador", 0) > 0 and 
            trabalhador_upgrade and 
            score >= trabalhador_upgrade.cost):
            
            if self.can_add_trabalhador():
                novo_trabalhador = Trabalhador(self.screen, self.window_width, self.window_height)
                if not self.trabalhador_time_enabled:
                    novo_trabalhador.lifetime = None
                self.trabalhadores.append(novo_trabalhador)
                score -= trabalhador_upgrade.cost
                self.purchased["trabalhador"] = self.purchased.get("trabalhador", 0) + 1
                
                if self.achievement_tracker:
                    if self.purchased["trabalhador"] == 1:
                        self.achievement_tracker.unlock_secret("worker")
                    elif self.purchased["trabalhador"] >= 5:
                        self.achievement_tracker.unlock_secret("worker_army")
                    self.achievement_tracker.check_all_upgrades_purchased(self)
        
        return score

    def set_trabalhador_limit(self, enabled):
        self.trabalhador_limit_enabled = enabled

    def set_trabalhador_time(self, enabled):
        self.trabalhador_time_enabled = enabled
        for t in self.trabalhadores:
            if enabled:
                t.lifetime = 30000
                t.creation_time = pygame.time.get_ticks()
            else:
                t.lifetime = None
        
    def can_add_trabalhador(self):
        if not self.trabalhador_limit_enabled:
            return True
        return self.get_trabalhadores_ativos() < self.max_trabalhadores
        
    def get_trabalhador_limit_status(self):
        return self.trabalhador_limit_enabled

    def _get_trabalhador_text(self, upg):
        trabalhadores_ativos = self.get_trabalhadores_ativos()
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
        pygame.draw.rect(border_surface, self.option_border, (0, 0, width, height), width=2, border_radius=20)
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
        pygame.draw.rect(border_surface, self.option_border, (0, 0, width, height), width=1, border_radius=14)
        option_surface.blit(border_surface, (0, 0))
        return option_surface

    def draw(self, score=0):
        delta_ms = self.menu_clock.tick(30)

        self._update_reveal(delta_ms)

        self.draw_icon()
        self.animation = min(1.0, self.animation + self.speed) if self.visible else max(0.0, self.animation - self.speed)
        if self.animation <= 0: 
            return

        mouse_pos = pygame.mouse.get_pos()
        self.hovered_option = None

        if self.upgrades_dirty:
            self.update_upgrades_cache()

        upgrades_to_show = self.cached_upgrades_to_show
        
        vertical_padding = 12
        full_h = len(upgrades_to_show) * (self.option_height + self.spacing) - self.spacing + 2 * vertical_padding
        height = int(full_h * self.animation)

        panel = self.get_panel_surface(self.width, height).copy()

        ONE_TIME_DISPLAY = {"hold_click", "mini_event", "auto_compra_trabalhador", "ganhos_offline", "tempo_aprimorado"}

        for i, upg in enumerate(upgrades_to_show):
            oy = vertical_padding + i * (self.option_height + self.spacing)
            if oy + self.option_height > height: 
                break
                
            rect_width = self.width - 2 * self.padding_x
            option_rect = pygame.Rect(self.x + self.padding_x, self.y + 75 + oy, rect_width, self.option_height)
            
            unlocked = self.is_unlocked(upg)

            is_hovered = option_rect.collidepoint(mouse_pos) and unlocked
            if is_hovered:
                self.hovered_option = upg.id

            if not unlocked:
                base_color = self.locked_color
            elif upg.id == "trabalhador":
                trabalhadores_ativos = self.get_trabalhadores_ativos()
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
            
            option_surface = self.get_option_surface(rect_width, self.option_height, base_color)
            panel.blit(option_surface, (self.padding_x, oy))
            
            if not unlocked:
                main_text = self._get_lock_text(upg)
                txt = self.get_text(main_text, self.locked_text_color)
            elif upg.id == "trabalhador":
                main_text = self._get_trabalhador_text(upg)
                txt = self.get_text(main_text)
            elif upg.id in ONE_TIME_DISPLAY:
                main_text = f"{upg.name} - {self._format_cost(upg.cost)} pts"
                txt = self.get_text(main_text)
            else:
                main_text = f"{upg.name} x{self.purchased.get(upg.id, 0)} - {self._format_cost(upg.cost)} pts"
                txt = self.get_text(main_text)

            text_rect = txt.get_rect(midleft=(self.padding_x + 10, oy + self.option_height // 2))
            panel.blit(txt, text_rect)
            
            if (unlocked and
                    upg.id not in ONE_TIME_DISPLAY and
                    upg.id != "trabalhador" and
                    self.purchase_quantity > 1):
                qtd_text = self.font.render(f"  +{self.purchase_quantity}", True, (60, 80, 120))
                qtd_text_rect = qtd_text.get_rect(midleft=(self.padding_x + 10 + txt.get_width(), oy + self.option_height // 2))
                panel.blit(qtd_text, qtd_text_rect)

        self.screen.blit(panel, (self.x, self.y + 75))

    def _attempt_purchase(self, upg, score):
        ONE_TIME_BUY = {"hold_click", "mini_event", "auto_compra_trabalhador", "ganhos_offline", "tempo_aprimorado"}

        if score < upg.cost:
            return score, False

        if upg.id == "trabalhador":
            ativos = self.get_trabalhadores_ativos()
            max_slots = (self.max_trabalhadores - ativos) if self.trabalhador_limit_enabled else self.purchase_quantity
            compras = min(self.purchase_quantity, max_slots)
            max_afford = score // upg.cost if upg.cost > 0 else compras
            compras = int(min(compras, max_afford))
            total_custo = upg.cost * compras
            if score >= total_custo and compras > 0:
                for _ in range(compras):
                    novo_trabalhador = Trabalhador(self.screen, self.window_width, self.window_height)
                    if not self.trabalhador_time_enabled:
                        novo_trabalhador.lifetime = None
                    self.trabalhadores.append(novo_trabalhador)
                score -= total_custo
                self.purchased[upg.id] = self.purchased.get(upg.id, 0) + compras
                if self.achievement_tracker:
                    if self.purchased[upg.id] == 1:
                        self.achievement_tracker.unlock_secret("worker")
                    elif self.purchased[upg.id] >= 5:
                        self.achievement_tracker.unlock_secret("worker_army")
                    self.achievement_tracker.check_all_upgrades_purchased(self)
                self.upgrades_dirty = True
                self.text_cache.clear()
                return score, True
            return score, False

        elif upg.id not in ONE_TIME_BUY:
            compras = self.purchase_quantity
            total_custo = upg.cost * compras
            if score >= total_custo:
                self.purchased[upg.id] = self.purchased.get(upg.id, 0) + compras
                score -= total_custo
                if upg.price_increase > 0:
                    upg.cost += upg.price_increase * compras
                if self.achievement_tracker:
                    self.achievement_tracker.check_all_upgrades_purchased(self)
                self.upgrades_dirty = True
                self.text_cache.clear()
                return score, True
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
            self.upgrades_dirty = True
            self.text_cache.clear()
            return score, True

    def handle_event(self, event, score):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.icon_rect.collidepoint(event.pos):
                self.toggle_visibility()
                return score, False

            if self.visible:
                if self.upgrades_dirty:
                    self.update_upgrades_cache()
                
                upgrades_to_show = self.cached_upgrades_to_show
                
                vertical_padding = 12
                menu_height = len(upgrades_to_show) * (self.option_height + self.spacing) - self.spacing + 2 * vertical_padding
                menu_rect = pygame.Rect(self.x, self.y + 75, self.width, menu_height)
                if not menu_rect.collidepoint(event.pos):
                    self.visible = False
                    return score, False

                for i, upg in enumerate(upgrades_to_show):
                    upg_rect = pygame.Rect(self.x + self.padding_x, self.y + 75 + vertical_padding + i * (self.option_height + self.spacing),
                                           self.width - 2 * self.padding_x, self.option_height)
                    if upg_rect.collidepoint(event.pos):
                        if not self.is_unlocked(upg):
                            return score, False

                        self.holding_upgrade = upg
                        self.holding_upgrade_index = i
                        self.hold_start_time = pygame.time.get_ticks()
                        self.auto_buy_active = False

                        score, comprou = self._attempt_purchase(upg, score)
                        if comprou:
                            if upg.id in {"hold_click", "mini_event", "auto_compra_trabalhador", "ganhos_offline", "tempo_aprimorado"}:
                                self.holding_upgrade = None
                                self.auto_buy_active = False
                            if upg.id == "trabalhador":
                                ativos = self.get_trabalhadores_ativos()
                                if (self.trabalhador_limit_enabled and ativos >= self.max_trabalhadores) or (not self.trabalhador_limit_enabled and ativos >= 1000):
                                    self.holding_upgrade = None
                                    self.auto_buy_active = False
                            return score, True
                        else:
                            self.holding_upgrade = None
                            self.auto_buy_active = False
                            return score, False

        elif event.type == pygame.MOUSEBUTTONUP:
            self.holding_upgrade = None
            self.auto_buy_active = False

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

    def update_auto_buy(self, score):
        if self.holding_upgrade is None:
            return score, False

        if not pygame.mouse.get_pressed()[0]:
            self.holding_upgrade = None
            self.auto_buy_active = False
            return score, False

        if self.holding_upgrade_index is not None:
            vertical_padding = 12
            upg_rect = pygame.Rect(
                self.x + self.padding_x,
                self.y + 75 + vertical_padding + self.holding_upgrade_index * (self.option_height + self.spacing),
                self.width - 2 * self.padding_x,
                self.option_height
            )
            if not upg_rect.collidepoint(pygame.mouse.get_pos()):
                self.holding_upgrade = None
                self.auto_buy_active = False
                return score, False

        current_time = pygame.time.get_ticks()

        if not self.auto_buy_active:
            if current_time - self.hold_start_time >= self.hold_duration:
                self.auto_buy_active = True
                self.auto_buy_last_time = current_time
            return score, False

        if current_time - self.auto_buy_last_time >= self.auto_buy_interval:
            upg = self.holding_upgrade
            if not self.is_unlocked(upg):
                self.holding_upgrade = None
                self.auto_buy_active = False
                return score, False

            score, comprou = self._attempt_purchase(upg, score)
            if comprou:
                self.auto_buy_last_time = current_time
                if upg.id in {"hold_click", "mini_event", "auto_compra_trabalhador", "ganhos_offline", "tempo_aprimorado"}:
                    self.holding_upgrade = None
                    self.auto_buy_active = False
                if upg.id == "trabalhador":
                    ativos = self.get_trabalhadores_ativos()
                    if (self.trabalhador_limit_enabled and ativos >= self.max_trabalhadores) or (not self.trabalhador_limit_enabled and ativos >= 1000):
                        self.holding_upgrade = None
                        self.auto_buy_active = False
            else:
                self.holding_upgrade = None
                self.auto_buy_active = False
            return score, comprou

        return score, False

    def update(self, score):
        score, comprou = self.update_auto_buy(score)
        return score, comprou

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
        
        self.upgrades_dirty = True

    def get_bonus(self):
        bonus = 1.0
        for upg in self.upgrades:
            qtd = self.purchased.get(upg.id, 0)
            if upg.id not in ["auto_click", "pequeno_auto_click", "auto_click_medio", "trabalhador", "mini_event", "auto_compra_trabalhador", "ganhos_offline"]:
                if qtd > 0:
                    if upg.bonus_increment > 0:
                        bonus += upg.bonus + (upg.bonus_increment * (qtd - 1))
                    else:
                        bonus += upg.bonus * qtd
        return bonus

    def auto_click_enabled(self):
        return (self.purchased.get("auto_click", 0) > 0 or
                self.purchased.get("pequeno_auto_click", 0) > 0 or
                self.purchased.get("auto_click_medio", 0) > 0)

    def get_auto_click_bonus(self):
        base = self.purchased.get("auto_click", 0)
        pequeno = self.purchased.get("pequeno_auto_click", 0) * 0.5
        medio = self.purchased.get("auto_click_medio", 0) * 0.75
        return base + pequeno + medio

    def mini_event_enabled(self):
        return self.purchased.get("mini_event", 0) > 0

    def get_mini_event_bonus(self):
        return self.purchased.get("mini_event", 0)

    def tempo_aprimorado_enabled(self):
        return self.purchased.get("tempo_aprimorado", 0) > 0

    def ganhos_offline_enabled(self):
        return self.purchased.get("ganhos_offline", 0) > 0

    def get_trabalhador_pontos(self):
        return 1

    def get_trabalhador_intervalo(self):
        return 5000

    def reset_upgrades(self):
        for upg in self.upgrades:
            upg.cost = upg.base_cost
        
        self.purchased.clear()
        self.trabalhadores = []
        self.trabalhador_limit_enabled = True
        self.trabalhador_time_enabled = True
        self.purchase_quantity = 1
        self.offline_time_bank = 0
        self.auto_compra_timer = 0
        self.auto_compra_ativa = True
        self.visible_upgrade_count = 1
        self.reveal_timer = 0
        self.upgrades_dirty = True
        self.text_cache.clear()

    def purchase_random_upgrade(self):
        if self.upgrades_dirty:
            self.update_upgrades_cache()

        available_upgrades = [
            upg for upg in self.cached_upgrades_to_show
            if (upg.id not in self.purchased or self.purchased.get(upg.id, 0) < 5)
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
                novo_trabalhador = Trabalhador(self.screen, self.window_width, self.window_height)
                if not self.trabalhador_time_enabled:
                    novo_trabalhador.lifetime = None
                self.trabalhadores.append(novo_trabalhador)
            
            if self.achievement_tracker:
                self.achievement_tracker.check_all_upgrades_purchased(self)
            
            self.upgrades_dirty = True
            self.text_cache.clear()
            return True
        return False

    def get_upgrades_to_save(self):
        return self.purchased.copy()

    def get_trabalhadores_ativos(self):
        return sum(1 for t in self.trabalhadores if t.active)

    def set_trabalhadores_ativos(self, qtd):
        pass