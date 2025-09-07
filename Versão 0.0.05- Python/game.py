import pygame
import random
import os
import sys
import time
import math
import webbrowser
import json
from datetime import datetime
from background import draw_background, WIDTH, HEIGHT
from button import AnimatedButton
from score_manager import ScoreManager
from menu import ConfigMenu
from loading import LoadingScreen, download_assets
from click_effect import ClickEffect
from conquistas import AchievementTracker, AchievementsMenu
from upgrades import UpgradeMenu
from console import Console
from exit_handler import ExitHandler
import updates
from mini_event import MiniEvent
from trabalhador import Trabalhador
import urllib.request
from image_viewer import ImageViewer

class EventManager:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        self.events = []
        self.active_events = []
        self.event_bonus = 1
        self.visible = True
        self.EVENTS_JSON_URL = "https://raw.githubusercontent.com/eupyetro0224234/Generic-Clicker-Game/main/eventos.json"
        self.last_check = 0
        self.check_interval = 300  # 5 minutes
        self.load_events()

    def load_events(self):
        try:
            with urllib.request.urlopen(self.EVENTS_JSON_URL, timeout=5) as response:
                data = response.read().decode('utf-8')
                self.events = json.loads(data)
        except (urllib.error.URLError, json.JSONDecodeError) as e:
            print(f"Error loading events from GitHub: {e}")
            self.events = []

    def check_events(self):
        now = time.time()
        if now - self.last_check < self.check_interval:
            return
            
        self.last_check = now
        self.load_events()
        
        now = datetime.now()
        current_date_str = now.strftime("%Y-%m-%d")
        current_time_str = now.strftime("%H:%M")
        
        self.active_events = []
        self.event_bonus = 1
        
        for event in self.events:
            if not event.get("active", False):
                continue
                
            start_date = event.get("start_date")
            end_date = event.get("end_date")
            start_time = event.get("start_time", "00:00")
            end_time = event.get("end_time", "23:59")
            
            if start_date <= current_date_str <= end_date:
                if current_date_str == start_date and current_time_str < start_time:
                    continue
                if current_date_str == end_date and current_time_str > end_time:
                    continue
                    
                self.active_events.append(event)
                self.event_bonus *= event.get("bonus", 1)

    def get_current_bonus(self):
        return self.event_bonus

    def has_active_events(self):
        return len(self.active_events) > 0

    def draw(self):
        if not self.has_active_events() or not self.visible:
            return
            
        font = pygame.font.SysFont(None, 24)
        text = font.render("Evento ativo", True, (255, 255, 255))
        text_rect = text.get_rect(bottomright=(self.width - 20, self.height - 20))
        
        bg_rect = text_rect.inflate(20, 10)
        s = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        s.fill((0, 0, 0, 150))
        pygame.draw.rect(s, (0, 0, 0, 200), (0, 0, bg_rect.width, bg_rect.height), border_radius=4)
        
        self.screen.blit(s, bg_rect)
        self.screen.blit(text, text_rect)

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        pygame.mixer.init()

        self.score_manager = ScoreManager()
        self.load_game_data()
        
        self.config_menu = ConfigMenu(screen, WIDTH, HEIGHT, score_manager=self.score_manager)
        self.event_manager = EventManager(screen, WIDTH, HEIGHT)
        self.image_viewer = ImageViewer(screen, WIDTH, HEIGHT)  # Inicializa e já mostra a imagem
        self.setup_loading()
        self.setup_fonts()
        self.setup_game_components()
        self.setup_console()
        self.setup_event_handling()
        
        self.fonte_update_notification = pygame.font.SysFont(None, 28)
        self.mensagem_update = None
        self.rect_update = None
        self.verificar_update()
        
        self.last_save_time = pygame.time.get_ticks()
        self.last_backup_save_time = pygame.time.get_ticks()

    def load_game_data(self):
        try:
            (self.score, self.controls_visible, saved_achievements, 
             saved_upgrades, mini_event_click_count, trabalhadores_data) = self.score_manager.load_data()
            
            self.trabalhadores = []
            for trab_data in trabalhadores_data:
                novo_trab = Trabalhador.from_state(
                    screen=self.screen,
                    width=WIDTH,
                    height=HEIGHT,
                    state=trab_data
                )
                self.trabalhadores.append(novo_trab)
                
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
            restore_backup = self.show_confirmation_dialog(
                "Erro ao carregar os dados do jogo.\nDeseja restaurar o backup antigo?"
            )

            if restore_backup:
                backup_data = self.score_manager.load_backup()
                if backup_data:
                    (self.score, self.controls_visible, saved_achievements, 
                     saved_upgrades, mini_event_click_count, trabalhadores_data) = backup_data
                    self.score_manager.save_data(
                        self.score, self.controls_visible, saved_achievements, 
                        saved_upgrades, mini_event_click_count, trabalhadores_data
                    )
                    
                    self.trabalhadores = []
                    for trab_data in trabalhadores_data:
                        novo_trab = Trabalhador.from_state(
                            screen=self.screen,
                            width=WIDTH,
                            height=HEIGHT,
                            state=trab_data
                        )
                        self.trabalhadores.append(novo_trab)
                else:
                    (self.score, self.controls_visible, saved_achievements, 
                     saved_upgrades, mini_event_click_count) = 0, False, [], {}, 0
                    self.trabalhadores = []
            else:
                (self.score, self.controls_visible, saved_achievements, 
                 saved_upgrades, mini_event_click_count) = 0, False, [], {}, 0
                self.trabalhadores = []

        self.saved_achievements = saved_achievements
        self.saved_upgrades = saved_upgrades
        self.mini_event_click_count = mini_event_click_count

    def setup_loading(self):
        pular_loading = False
        if hasattr(self.config_menu, "settings_menu") and self.config_menu.settings_menu:
            pular_loading = self.config_menu.settings_menu.get_option("Pular o loading")

        download_assets(self.screen, WIDTH, HEIGHT, skip_loading=pular_loading)

    def setup_fonts(self):
        self.FONT = pygame.font.SysFont(None, 64)
        self.TEXT_COLOR_SCORE = (40, 40, 60)
        self.fonte_update = pygame.font.SysFont(None, 48)
        self.fonte_aviso = pygame.font.SysFont(None, 28)
        self.event_font_large = pygame.font.SysFont(None, 36)
        self.event_font_small = pygame.font.SysFont(None, 24)

    def setup_game_components(self):
        self.button = AnimatedButton(
            WIDTH // 2, HEIGHT // 2, 200, 200,
            os.path.join(os.getenv("LOCALAPPDATA") or ".", ".assets", "button.gif")
        )

        self.config_menu.controls_menu.visible = self.controls_visible

        self.tracker = AchievementTracker(self.screen)
        self.tracker.load_unlocked(self.saved_achievements)
        self.tracker.load_sound()
        self.tracker.mini_event_clicks = self.mini_event_click_count

        self.upgrade_menu = UpgradeMenu(self.screen, WIDTH, HEIGHT, achievement_tracker=self.tracker)
        self.upgrade_menu.load_upgrades(self.saved_upgrades)

        if not hasattr(self, 'trabalhadores'):
            self.trabalhadores = []
            trabalhador_count = self.upgrade_menu.get_trabalhador_quantidade()
            for _ in range(trabalhador_count):
                self.adicionar_trabalhador()

        self.click_effects = []
        self.auto_click_counter = 0
        self.hold_click_start_time = None
        self.hold_click_accumulator = 0

        self.exit_handler = ExitHandler(self.screen, WIDTH, HEIGHT)
        self.config_menu.exit_handler = self.exit_handler

        self.config_menu.achievements_menu = AchievementsMenu(self.screen, WIDTH, HEIGHT, self.config_menu)
        self.config_menu.achievements_menu.achievements = self.tracker.achievements
        self.config_menu.achievements_menu.unlocked = self.tracker.unlocked

        self.mini_event = None
        self.last_mini_event_time = pygame.time.get_ticks()
        self.mini_event_cooldown = 30000

        if random.random() < 0.1:
            self.mini_event = MiniEvent(self.screen, WIDTH, HEIGHT)
            self.last_mini_event_time = pygame.time.get_ticks()

        self.config_menu.achievements_menu.tracker = self.tracker

        self.aviso_update = False
        self.texto_update = ""

    def verificar_update(self):
        if self.config_menu.settings_menu.get_option("Verificar atualizações"):
            tem_update, versao_nova = updates.checar_atualizacao()
            if tem_update and versao_nova:
                self.mensagem_update = f"Atualização disponível: v{versao_nova}"
                texto_renderizado = self.fonte_update_notification.render(self.mensagem_update, True, (255, 0, 0))
                self.rect_update = texto_renderizado.get_rect(bottomleft=(20, HEIGHT - 30))
                self.aviso_update = True
                self.texto_update = f"Nova versão disponível: {versao_nova}!"
            else:
                self.mensagem_update = None
                self.rect_update = None
                self.aviso_update = False
                self.texto_update = ""
        else:
            self.mensagem_update = None
            self.rect_update = None
            self.aviso_update = False
            self.texto_update = ""

    def resetar_trabalhadores(self):
        self.trabalhadores = []
        self.upgrade_menu.set_trabalhadores_ativos(0)

    def adicionar_trabalhador(self):
        novo_trabalhador = Trabalhador(
            screen=self.screen,
            width=WIDTH,
            height=HEIGHT
        )
        self.trabalhadores.append(novo_trabalhador)

    def setup_console(self):
        def get_score():
            return self.score

        def set_score(new_score):
            if isinstance(new_score, float) and new_score.is_integer():
                self.score = int(new_score)
            else:
                self.score = new_score

        def on_console_open():
            self.config_menu.enable_console(add_option=True)

        def on_console_close():
            self.config_menu.disable_console(remove_option=True)

        self.console = Console(
            self.screen,
            WIDTH,
            HEIGHT,
            on_exit_callback=on_console_close,
            on_open_callback=on_console_open,
            tracker=self.tracker,
            config_menu=self.config_menu,
            upgrade_manager=self.upgrade_menu
        )
        self.console.set_score_accessors(get_score, set_score)
        self.config_menu.set_score_accessors(get_score, set_score)

        if self.config_menu.settings_menu.get_option("Manter console aberto"):
            self.config_menu.enable_console(add_option=True)
            if self.config_menu.console_instance:
                self.config_menu.console_instance.open()

        self.config_menu.console_instance = self.console

    def setup_event_handling(self):
        self.running = True

    def show_confirmation_dialog(self, message):
        class ConfirmationDialog:
            def __init__(self, screen, width, height, message):
                self.screen = screen
                self.width = width
                self.height = height
                self.message = message
                self.font = pygame.font.SysFont(None, 32)
                self.prompt_font = pygame.font.SysFont(None, 28)
                self.text_color = (40, 40, 60)
                self.bg_box_color = (180, 210, 255)
                self.box_color = (255, 255, 255)
                self.bg_rect = pygame.Rect(width // 2 - 250, height // 2 - 100, 500, 200)
                btn_width = 120
                btn_height = 45
                self.yes_btn = pygame.Rect(width // 2 - 140, height // 2 + 30, btn_width, btn_height)
                self.no_btn = pygame.Rect(width // 2 + 20, height // 2 + 30, btn_width, btn_height)
                self.result = None

            def handle_event(self, event):
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.result = True
                        return True
                    elif event.key == pygame.K_ESCAPE:
                        self.result = False
                        return True

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.yes_btn.collidepoint(event.pos):
                        self.result = True
                        return True
                    elif self.no_btn.collidepoint(event.pos):
                        self.result = False
                        return True

                return False

            def draw(self):
                pygame.draw.rect(self.screen, self.bg_box_color, self.bg_rect, border_radius=16)
                lines = [self.message[i:i + 50] for i in range(0, len(self.message), 50)]
                for i, line in enumerate(lines):
                    prompt_surf = self.prompt_font.render(line, True, self.text_color)
                    prompt_rect = prompt_surf.get_rect(center=(self.width // 2, self.bg_rect.y + 60 + i * 30))
                    self.screen.blit(prompt_surf, prompt_rect)
                pygame.draw.rect(self.screen, (70, 180, 70), self.yes_btn, border_radius=8)
                pygame.draw.rect(self.screen, (200, 70, 70), self.no_btn, border_radius=8)
                yes_text = self.font.render("Sim (R)", True, (255, 255, 255))
                no_text = self.font.render("Não (ESC)", True, (255, 255, 255))
                self.screen.blit(yes_text, (self.yes_btn.centerx - yes_text.get_width() // 2,
                                            self.yes_btn.centery - yes_text.get_height() // 2))
                self.screen.blit(no_text, (self.no_btn.centerx - no_text.get_width() // 2,
                                           self.no_btn.centery - no_text.get_height() // 2))

        dialog = ConfirmationDialog(self.screen, WIDTH, HEIGHT, message)
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 150))
        self.screen.blit(s, (0, 0))
        waiting = True
        while waiting:
            dialog.draw()
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if dialog.handle_event(event):
                    waiting = False
            pygame.time.delay(10)
        return dialog.result

    def handle_events(self):
        for event in pygame.event.get():
            if self.exit_handler.fading_out:
                if self.exit_handler.update_fade_out():
                    pygame.display.flip()
                    self.clock.tick(60)
                    continue

            if self.exit_handler.active:
                result = self.exit_handler.handle_event(event)

                if self.exit_handler.detected_console:
                    self.config_menu.enable_console(add_option=True)
                    self.tracker.unlock_secret("console")
                    self.exit_handler.active = False
                    self.exit_handler.user_text = ""
                    self.exit_handler.detected_console = False
                    continue

                if result:
                    continue

            if event.type == pygame.QUIT:
                if not self.exit_handler.active and not self.exit_handler.fading_out:
                    self.exit_handler.start()
                continue

            if event.type == pygame.KEYDOWN:
                self.handle_keydown(event)

            if event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mousebuttondown(event)

            if self.image_viewer.handle_event(event):
                continue

            if self.config_menu.handle_event(event):
                continue

            if (event.type == pygame.MOUSEBUTTONDOWN and 
                self.config_menu.achievements_menu.visible and
                self.config_menu.achievements_menu.close_button_rect and
                self.config_menu.achievements_menu.close_button_rect.collidepoint(event.pos)):
                self.config_menu.achievements_menu.visible = False

            if (event.type == pygame.MOUSEBUTTONDOWN and 
                event.button == 1 and
                self.rect_update and 
                self.rect_update.collidepoint(event.pos)):
                webbrowser.open("https://github.com/eupyetro0224234/Generic-Clicker-Game/releases")

    def handle_keydown(self, event):
        if event.key == pygame.K_r and not self.console.visible:
            confirmed = self.show_confirmation_dialog(
                "Deseja realmente resetar TODOS os dados do jogo?"
            )
            if confirmed:
                self.score = 0
                self.tracker.unlocked.clear()
                self.tracker.normal_clicks = 0
                self.tracker.mini_event_clicks = 0
                for ach in self.tracker.achievements:
                    ach.unlocked = False
                self.upgrade_menu.reset_upgrades()
                self.trabalhadores = []
                trabalhadores_data = []
                self.score_manager.save_data(
                    self.score,
                    self.config_menu.controls_menu.visible,
                    list(self.tracker.unlocked),
                    self.upgrade_menu.purchased,
                    self.tracker.mini_event_clicks,
                    trabalhadores_data
                )
            return

        if event.key == pygame.K_t and pygame.key.get_mods() & pygame.KMOD_CTRL:
            self.resetar_trabalhadores()
            return

        if event.key == pygame.K_u and not self.console.visible:
            self.upgrade_menu.purchased.clear()
            self.trabalhadores = []
            trabalhadores_data = []
            self.score_manager.save_data(
                self.score,
                self.config_menu.controls_menu.visible,
                list(self.tracker.unlocked),
                self.upgrade_menu.purchased,
                self.tracker.mini_event_clicks,
                trabalhadores_data
            )
            return

        if event.key == pygame.K_ESCAPE:
            if self.console.visible:
                self.console.visible = False
                return
            if self.exit_handler.active:
                self.exit_handler.active = False
                return
            if self.config_menu.settings_menu.visible:
                self.config_menu.settings_menu.visible = False
                return
            if self.config_menu.controls_menu.visible:
                self.config_menu.controls_menu.visible = False
                return
            if self.config_menu.achievements_menu.visible:
                self.config_menu.achievements_menu.visible = False
                return
            if self.upgrade_menu.visible:
                self.upgrade_menu.visible = False
                return
            if self.config_menu.is_open:
                self.config_menu.is_open = False
                return
            
            self.event_manager.visible = not self.event_manager.visible

    def handle_mousebuttondown(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button in (1, 2, 3, 4, 5):
            button_clicked = self.button.is_clicked(event.pos)
            
            if button_clicked and not (self.console.visible or self.exit_handler.active or self.image_viewer.visible):
                self.tracker.add_normal_click()
                total_bonus = self.upgrade_menu.get_bonus() * self.event_manager.get_current_bonus()
                self.score += total_bonus
                self.tracker.check_unlock(self.score)
                self.click_effects.append(
                    ClickEffect(event.pos[0], event.pos[1], f"+{total_bonus}"))
                
                trabalhadores_data = [trab.get_state() for trab in self.trabalhadores]
                self.score_manager.save_data(
                    self.score,
                    self.config_menu.controls_menu.visible,
                    list(self.tracker.unlocked),
                    self.upgrade_menu.purchased,
                    self.tracker.mini_event_clicks,
                    trabalhadores_data
                )
                return
            
            if self.mini_event and self.mini_event.visible:
                prev_score = self.score
                mini_event_score, upgrade = self.mini_event.handle_click(event.pos, self.score, self.upgrade_menu)
                if upgrade or mini_event_score != prev_score:
                    if mini_event_score != prev_score:
                        mini_event_score = prev_score + (mini_event_score - prev_score) * self.event_manager.get_current_bonus()
                    self.score = mini_event_score
                    self.tracker.add_mini_event_click()
                    if upgrade:
                        self.click_effects.append(
                            ClickEffect(event.pos[0], event.pos[1], "Upgrade Obtido!"))
                    else:
                        self.click_effects.append(
                            ClickEffect(event.pos[0], event.pos[1], "+Pontos!"))
                    
                    trabalhadores_data = [trab.get_state() for trab in self.trabalhadores]
                    self.score_manager.save_data(
                        self.score,
                        self.config_menu.controls_menu.visible,
                        list(self.tracker.unlocked),
                        self.upgrade_menu.purchased,
                        self.tracker.mini_event_clicks,
                        trabalhadores_data
                    )
                    return

            prev_vis = self.upgrade_menu.visible
            new_score, trabalhador_comprado = self.upgrade_menu.handle_event(event, self.score)
            
            if new_score != self.score and "auto_click" in self.upgrade_menu.purchased:
                self.tracker.unlock_secret("automatico")
            
            self.tracker.check_all_achievements_completed()
            
            if trabalhador_comprado:
                self.adicionar_trabalhador()
                
            if new_score != self.score or self.upgrade_menu.visible != prev_vis:
                self.score = new_score
                return

            self.button._update_rect()

    def update(self):
        self.event_manager.check_events()
        
        self.config_menu.achievements_menu.achievements = self.tracker.achievements
        self.config_menu.achievements_menu.unlocked = self.tracker.unlocked

        current_time = pygame.time.get_ticks()

        if self.upgrade_menu.auto_click_enabled():
            self.auto_click_counter += 1
            if self.auto_click_counter >= 40:
                self.auto_click_counter = 0
                bonus_auto = self.upgrade_menu.get_auto_click_bonus() * self.event_manager.get_current_bonus()
                self.score += bonus_auto
                self.tracker.check_unlock(self.score)
                self.click_effects.append(
                    ClickEffect(WIDTH // 2, HEIGHT // 2, f"+{bonus_auto} (Auto)"))

        mouse_buttons = pygame.mouse.get_pressed()

        if mouse_buttons[0]:
            hold_click_qtd = self.upgrade_menu.purchased.get("hold_click", 0)
            if hold_click_qtd > 0:
                if self.hold_click_start_time is None:
                    self.hold_click_start_time = current_time
                    self.hold_click_accumulator = 0
                    self.tracker.unlock_secret("manual_phase")
                else:
                    elapsed = current_time - self.hold_click_start_time
                    if elapsed >= 3000:
                        self.hold_click_accumulator += self.clock.get_time()
                        if self.hold_click_accumulator >= 500:
                            self.hold_click_accumulator = 0
                            hold_bonus = hold_click_qtd * self.event_manager.get_current_bonus()
                            self.score += hold_bonus
                            self.tracker.check_unlock(self.score)
                            self.click_effects.append(
                                ClickEffect(WIDTH // 2, HEIGHT // 2, f"+{hold_bonus} (Hold)"))

        if (self.mini_event and self.mini_event.visible and 
            self.upgrade_menu.purchased.get("auto_mini_event", 0) > 0):
            prev_score = self.score
            mini_event_score, upgrade = self.mini_event.handle_click(
                (self.mini_event.x + 25, self.mini_event.y + 25),
                self.score,
                self.upgrade_menu
            )
            if upgrade or mini_event_score != prev_score:
                if mini_event_score != prev_score:
                    mini_event_score = prev_score + (mini_event_score - prev_score) * self.event_manager.get_current_bonus()
                self.score = mini_event_score
                self.tracker.add_mini_event_click()
                if upgrade:
                    self.click_effects.append(
                        ClickEffect(
                            self.mini_event.x + 25, 
                            self.mini_event.y + 25, 
                            "Upgrade Obtido! (Auto)"
                        )
                    )
                else:
                    self.click_effects.append(
                        ClickEffect(
                            self.mini_event.x + 25, 
                            self.mini_event.y + 25, 
                            "+Pontos! (Auto)"
                        )
                    )
                
                trabalhadores_data = [trab.get_state() for trab in self.trabalhadores]
                self.score_manager.save_data(
                    self.score,
                    self.config_menu.controls_menu.visible,
                    list(self.tracker.unlocked),
                    self.upgrade_menu.purchased,
                    self.tracker.mini_event_clicks,
                    trabalhadores_data
                )

        pontos_acumulados = 0
        trabalhadores_remover = []
        
        for trabalhador in self.trabalhadores[:]:
            resultado = trabalhador.update(current_time)

            if isinstance(resultado, tuple) and resultado[0] == "expired":
                pontos_acumulados += resultado[1] * self.event_manager.get_current_bonus()
                trabalhadores_remover.append(trabalhador)
            elif isinstance(resultado, int):
                pontos_acumulados += resultado * self.event_manager.get_current_bonus()
        
        if pontos_acumulados > 0:
            self.score += pontos_acumulados
            self.tracker.check_unlock(self.score)
            
            if len(self.trabalhadores) > 0:
                posicao_media = (
                    sum(t.pos[0] for t in self.trabalhadores)/len(self.trabalhadores),
                    sum(t.pos[1] for t in self.trabalhadores)/len(self.trabalhadores)
                )
                self.click_effects.append(
                    ClickEffect(
                        posicao_media[0], 
                        posicao_media[1], 
                        f"+{pontos_acumulados} (Trab.)", 
                        color=(100, 100, 255)
                    )
                )
        
        for trab in trabalhadores_remover:
            if trab in self.trabalhadores:
                self.trabalhadores.remove(trab)
                self.upgrade_menu.set_trabalhadores_ativos(len(self.trabalhadores))
                self.click_effects.append(
                    ClickEffect(
                        trab.pos[0], 
                        trab.pos[1], 
                        f"+{pontos_acumulados} (Trab. Final)", 
                        color=(100, 100, 255)
                    )
                )

        if (current_time - self.last_mini_event_time > self.mini_event_cooldown and
                not self.mini_event and
                random.random() < 0.1):
            self.mini_event = MiniEvent(self.screen, WIDTH, HEIGHT)
            self.last_mini_event_time = current_time

        if self.mini_event:
            self.mini_event.update()
            if not self.mini_event.visible:
                self.mini_event = None

        for eff in self.click_effects[:]:
            eff.update()
            if eff.finished:
                self.click_effects.remove(eff)

        if current_time - self.last_save_time >= 1000:
            trabalhadores_data = [trab.get_state() for trab in self.trabalhadores]
            self.score_manager.save_data(
                self.score,
                self.config_menu.controls_menu.visible,
                list(self.tracker.unlocked),
                self.upgrade_menu.purchased,
                self.tracker.mini_event_clicks,
                trabalhadores_data
            )
            self.last_save_time = current_time

        if self.aviso_update and (current_time - self.last_backup_save_time >= 1000):
            trabalhadores_data = [trab.get_state() for trab in self.trabalhadores]
            self.score_manager.save_backup(
                self.score,
                self.config_menu.controls_menu.visible,
                list(self.tracker.unlocked),
                self.upgrade_menu.purchased,
                self.tracker.mini_event_clicks,
                trabalhadores_data
            )
            self.last_backup_save_time = current_time

    def draw(self):
        draw_background(self.screen)
        
        for trabalhador in self.trabalhadores:
            trabalhador.draw()

        self.button.draw(self.screen)

        for eff in self.click_effects:
            eff.draw(self.screen)

        if self.mini_event and self.mini_event.visible:
            self.mini_event.draw()

        score_surf = self.FONT.render(str(self.score), True, self.TEXT_COLOR_SCORE)
        score_rect = score_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 140))
        self.screen.blit(score_surf, score_rect)

        self.event_manager.draw()

        self.upgrade_menu.draw(self.score)

        self.config_menu.draw_icon()

        self.config_menu.draw()

        if self.console.visible:
            self.console.draw()

        self.exit_handler.draw()

        self.tracker.update_and_draw()

        if self.mensagem_update and self.rect_update:
            self.screen.blit(self.fonte_update_notification.render(self.mensagem_update, True, (255, 0, 0)), self.rect_update)

        if hasattr(self.config_menu.settings_menu, "precisa_reiniciar") and self.config_menu.settings_menu.precisa_reiniciar:
            aviso = self.fonte_aviso.render("Reinicie o jogo para aplicar mudanças", True, (200, 0, 0))
            aviso_rect = aviso.get_rect(center=(WIDTH // 2, HEIGHT - 30))
            self.screen.blit(aviso, aviso_rect)

        # Desenha o visualizador de imagens por último (por cima de tudo)
        self.image_viewer.draw()

    def run(self):
        while self.running:
            if self.exit_handler.fading_out:
                if self.exit_handler.update_fade_out():
                    pygame.display.flip()
                    self.clock.tick(60)
                    continue

            self.handle_events()
            self.update()
            self.draw()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Generic Clicker Game")
    game = Game(screen)
    game.run()