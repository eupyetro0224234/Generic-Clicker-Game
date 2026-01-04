import os, pygame, pytz, random, sys, webbrowser, time
from datetime import datetime
from game_code.background import draw_background, WIDTH, HEIGHT, set_game_reference
from game_code.button import AnimatedButton
from game_code.score_manager import ScoreManager
from game_code.menu import ConfigMenu
from game_code.click_effect import ClickEffect
from game_code.conquistas import AchievementTracker, AchievementsMenu
from game_code.upgrades import UpgradeMenu
from game_code.console import Console
from game_code.exit_handler import ExitHandler
from game_code import updates
from game_code.mini_event import MiniEvent
from game_code.eventos import GerenciadorEventos, EventosMenu
from game_code.image_viewer import ImageViewer
from game_code.estatisticas import StatisticsMenu
from game_code.mod_manager import load_mod
from game_code import background

mod = load_mod()
if mod:
    background.set_mod(mod)

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        pygame.mixer.init()

        self.score_manager = ScoreManager()
        
        self.inicializar_dados_zerados()
        
        self.pontos_acumulados = 0.0
        
        self.load_game_data()
        
        self.config_menu = ConfigMenu(screen, WIDTH, HEIGHT, score_manager=self.score_manager)
        self.image_viewer = ImageViewer(screen, WIDTH, HEIGHT)
        self.setup_fonts()
        self.setup_game_components()
        self.setup_console()
        self.setup_event_handling()
        
        self.game_start_time = pygame.time.get_ticks()
        self.last_session_time = self.saved_total_time
        self.session_start_time = self.game_start_time
        self.is_paused = False
        self.last_scroll_time = 0
        
        self.achievement_sound_volume = 1.0
        self.minigame_sound_volume = 1.0
        self.load_volume_settings()
        self.update_volumes()
        
        set_game_reference(self)
        
        self.calcular_ganhos_offline()
        self.verificar_update()
        self.last_save_time = pygame.time.get_ticks()
        
        self.statistics_menu = StatisticsMenu(screen, WIDTH, HEIGHT, self)
        self.config_menu.settings_menu.statistics_menu = self.statistics_menu
        
        self.update_daily_streak()

    def inicializar_dados_zerados(self):
        self.score = 0
        self.controls_visible = False
        self.saved_achievements = []
        self.saved_upgrades = {}
        self.mini_event_click_count = 0
        self.saved_trabalhadores_data = []
        self.saved_trabalhador_limit_enabled = True
        self.eventos_participados = {}
        self.saved_total_time = 0
        self.last_timestamp = None
        self.max_score = 0
        self.total_score_earned = 0
        self.mini_event1_total = 0
        self.mini_event2_total = 0
        self.mini_event1_session = 0
        self.mini_event2_session = 0
        self.saved_normal_clicks = 0
        self.offline_time_bank = 0
        
        tz_brasilia = pytz.timezone('America/Sao_Paulo')
        self.first_join_date = datetime.now(tz_brasilia).strftime("%d/%m/%Y - %H:%M")
        self.streak_data = {"current_streak": 0, "last_login_date": None, "max_streak": 0}

    def calcular_ganhos_offline(self):
        if not self.upgrade_menu.ganhos_offline_enabled():
            return
    
        if not self.last_timestamp:
            return
    
        current_timestamp = int(time.time())
        tempo_offline = current_timestamp - self.last_timestamp
    
        tempo_offline = min(tempo_offline, self.upgrade_menu.offline_time_bank)
    
        if tempo_offline <= 0:
            return
    
        pontos_offline = 0
        
        if self.upgrade_menu.auto_click_enabled():
            ciclos_auto_click = tempo_offline // (40 / 60)
            bonus_auto = self.upgrade_menu.get_auto_click_bonus()
            pontos_offline += int(ciclos_auto_click * bonus_auto)
        
        for trabalhador in self.upgrade_menu.trabalhadores:
            if hasattr(trabalhador, 'get_offline_production'):
                pontos_trabalhador = trabalhador.get_offline_production(tempo_offline)
                pontos_offline += pontos_trabalhador
        
        if pontos_offline > 0:
            self.adicionar_pontos(pontos_offline)
            self.tracker.check_unlock(self.score)
    
            self.click_effects.append(
                ClickEffect(
                    WIDTH // 2, 
                    HEIGHT // 2,
                    
                    f"+{pontos_offline} pts Offline! ({self.format_time(tempo_offline)})",
                    color=(100, 255, 100)
                )
            )
    
        self.upgrade_menu.offline_time_bank = max(0, self.upgrade_menu.offline_time_bank - tempo_offline)

    def adicionar_pontos(self, pontos):
        self.pontos_acumulados += pontos
        pontos_inteiros = int(self.pontos_acumulados)
        if pontos_inteiros > 0:
            self.score += pontos_inteiros
            self.pontos_acumulados -= pontos_inteiros
            self.total_score_earned += pontos_inteiros
            if self.score > self.max_score:
                self.max_score = self.score
        return pontos_inteiros
        
    def update_daily_streak(self):
        tz_brasilia = pytz.timezone('America/Sao_Paulo')
        today = datetime.now(tz_brasilia).strftime("%Y-%m-%d")
        
        if self.streak_data["last_login_date"] != today:
            if self.streak_data["last_login_date"]:
                last_login = datetime.strptime(self.streak_data["last_login_date"], "%Y-%m-%d")
                today_date = datetime.strptime(today, "%Y-%m-%d")
                days_diff = (today_date - last_login).days
                
                if days_diff == 1:
                    self.streak_data["current_streak"] += 1
                elif days_diff > 1:
                    self.streak_data["current_streak"] = 1
            else:
                self.streak_data["current_streak"] = 1
            
            self.streak_data["last_login_date"] = today
            
            if self.streak_data["current_streak"] > self.streak_data["max_streak"]:
                self.streak_data["max_streak"] = self.streak_data["current_streak"]
            
            self.save_game_data()

    def get_mini_events_session_total(self):
        return getattr(self, 'mini_event1_session', 0) + getattr(self, 'mini_event2_session', 0)

    def load_volume_settings(self):
        volume_settings = self.config_menu.settings_menu.get_volume_settings()
        self.achievement_sound_volume = volume_settings["achievement_volume"]
        self.minigame_sound_volume = volume_settings["minievent_volume"]

    def load_game_data(self):
        try:
            (self.score, self.controls_visible, saved_achievements, 
             saved_upgrades, mini_event_click_count, trabalhadores_data, 
             trabalhador_limit_enabled, self.eventos_participados, 
             self.saved_total_time, self.last_timestamp, self.max_score,
             self.total_score_earned, self.mini_event1_total, self.mini_event2_total,
             self.saved_normal_clicks, self.first_join_date, self.streak_data,
             self.mini_event1_session, self.mini_event2_session,
             self.offline_time_bank) = self.score_manager.load_data()
            
            self.score = max(0, int(self.score))
            self.max_score = max(self.score, int(self.max_score))
            self.total_score_earned = max(0, int(self.total_score_earned))
            self.mini_event1_total = max(0, int(self.mini_event1_total))
            self.mini_event2_total = max(0, int(self.mini_event2_total))
            self.mini_event1_session = max(0, int(self.mini_event1_session))
            self.mini_event2_session = max(0, int(self.mini_event2_session))
            
            self.saved_trabalhador_limit_enabled = trabalhador_limit_enabled
            self.saved_trabalhadores_data = trabalhadores_data
            self.saved_achievements = saved_achievements
            self.saved_upgrades = saved_upgrades
            self.mini_event_click_count = mini_event_click_count
            
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
            print("Iniciando com dados padrão...")
            self.inicializar_dados_zerados()

    def save_game_data(self):
        try:
            achievements_to_save = self.tracker.get_achievements_with_dates()
            
            self.score_manager.save_data(
                self.score,
                self.config_menu.controls_menu.visible,
                achievements_to_save,
                self.upgrade_menu.purchased,
                self.tracker.mini_event_clicks,
                self.upgrade_menu.get_trabalhador_limit_status(),
                self.eventos_participados,
                self.get_total_play_time(),
                int(time.time()),
                self.max_score,
                self.total_score_earned,
                self.mini_event1_total,
                self.mini_event2_total,
                self.tracker.normal_clicks,
                self.first_join_date,
                self.streak_data,
                False,
                self.mini_event1_session,
                self.mini_event2_session,
                self.upgrade_menu.offline_time_bank
            )
            return True
        except Exception as e:
            print(f"Erro ao salvar dados: {e}")
            return False

    def setup_fonts(self):
        self.FONT = pygame.font.SysFont(None, 64)
        self.TEXT_COLOR_SCORE = (40, 40, 60)
        self.fonte_update = pygame.font.SysFont(None, 24)
        self.fonte_aviso = pygame.font.SysFont(None, 28)
        self.fonte_evento = pygame.font.SysFont(None, 26)
        self.fonte_evento_pequena = pygame.font.SysFont(None, 20)
        self.fonte_tempo = pygame.font.SysFont(None, 22)
        self.fonte_streak = pygame.font.SysFont(None, 28)
        try:
            self.fonte_emoji = pygame.font.SysFont("seguiemj", 32)
        except:
            try:
                self.fonte_emoji = pygame.font.SysFont("apple color emoji", 32)
            except:
                try:
                    self.fonte_emoji = pygame.font.SysFont("noto color emoji", 32)
                except:
                    self.fonte_emoji = pygame.font.SysFont(None, 32)

    def setup_game_components(self):
        button_path = resource_path(os.path.join("game_assets", "button.gif"))
        self.button = AnimatedButton(
            WIDTH // 2, HEIGHT // 2, 200, 200,
            button_path
        )

        self.config_menu.controls_menu.visible = self.controls_visible

        self.tracker = AchievementTracker(self.screen, game=self)
        self.tracker.load_unlocked(self.saved_achievements)
        self.tracker.load_sound()
        self.tracker.mini_event_clicks = self.mini_event_click_count
        self.tracker.normal_clicks = self.saved_normal_clicks

        self.upgrade_menu = UpgradeMenu(self.screen, WIDTH, HEIGHT, achievement_tracker=self.tracker)
        self.upgrade_menu.load_upgrades(self.saved_upgrades)
        self.upgrade_menu.set_trabalhador_limit(self.saved_trabalhador_limit_enabled)
        self.upgrade_menu.offline_time_bank = self.offline_time_bank

        if hasattr(self, 'saved_trabalhadores_data'):
            self.upgrade_menu.load_trabalhadores(self.saved_trabalhadores_data)

        self.click_effects = []
        self.auto_click_counter = 0
        self.hold_click_start_time = None
        self.hold_click_accumulator = 0

        self.exit_handler = ExitHandler(self.screen, WIDTH, HEIGHT)
        self.config_menu.exit_handler = self.exit_handler

        self.config_menu.achievements_menu = AchievementsMenu(self.screen, WIDTH, HEIGHT, self.config_menu)
        self.config_menu.achievements_menu.achievements = self.tracker.achievements
        self.config_menu.achievements_menu.unlocked = self.tracker.unlocked

        self.gerenciador_eventos = GerenciadorEventos()
        self.gerenciador_eventos.carregar_eventos()

        self.config_menu.eventos_menu.set_gerenciador(self.gerenciador_eventos)

        self.mini_event = None
        self.last_mini_event_time = pygame.time.get_ticks()
        self.mini_event_cooldown = 30000

        self.mini_event2 = None
        self.last_mini_event2_time = pygame.time.get_ticks()
        self.mini_event2_cooldown = 120000

        if random.random() < 0.3:
            self.mini_event = MiniEvent(self.screen, WIDTH, HEIGHT, "normal")
            self.last_mini_event_time = pygame.time.get_ticks()

        if random.random() < 0.2:
            self.mini_event2 = MiniEvent(self.screen, WIDTH, HEIGHT, "rare")
            self.last_mini_event2_time = pygame.time.get_ticks()

        self.config_menu.achievements_menu.tracker = self.tracker

        self.aviso_update = False
        self.texto_update = ""
        self.update_rect = None

    def update_volumes(self):
        self.load_volume_settings()
        
        if hasattr(self.tracker, 'set_volume'):
            self.tracker.set_volume(self.achievement_sound_volume)
        
        if hasattr(self, 'mini_event') and self.mini_event and hasattr(self.mini_event, 'set_volume'):
            self.mini_event.set_volume(self.minigame_sound_volume)
        if hasattr(self, 'mini_event2') and self.mini_event2 and hasattr(self.mini_event2, 'set_volume'):
            self.mini_event2.set_volume(self.minigame_sound_volume)

    def get_total_play_time(self):
        if self.is_paused:
            return self.last_session_time
        
        current_time = pygame.time.get_ticks()
        current_session_time = (current_time - self.session_start_time) // 1000
        return self.last_session_time + current_session_time

    def format_time(self, total_seconds):
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def pause_timer(self):
        if not self.is_paused:
            self.is_paused = True
            current_time = pygame.time.get_ticks()
            current_session_time = (current_time - self.session_start_time) // 1000
            self.last_session_time += current_session_time

    def resume_timer(self):
        if self.is_paused:
            self.is_paused = False
            self.session_start_time = pygame.time.get_ticks()

    def resetar_trabalhadores(self):
        self.upgrade_menu.trabalhadores = []

    def adicionar_trabalhador(self):
        pass

    def increment_mini_event1_total(self):
        self.mini_event1_total += 1
        self.mini_event1_session += 1

    def increment_mini_event2_total(self):
        self.mini_event2_total += 1
        self.mini_event2_session += 1

    def add_to_total_score_earned(self, amount):
        amount_int = int(amount)
        self.total_score_earned += amount_int

    def setup_console(self):
        def get_score():
            return self.score

        def set_score(new_score):
            if isinstance(new_score, float) and new_score.is_integer():
                self.score = int(new_score)
            else:
                self.score = new_score

            unlocked_achievements = self.tracker.check_unlock(self.score)
            if unlocked_achievements:
                for achievement in unlocked_achievements:
                    pass

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
            upgrade_manager=self.upgrade_menu,
            game=self
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

    def verificar_update(self):
        if self.config_menu.settings_menu.get_option("Verificar atualizações"):
            atualizou, versao_online = updates.checar_atualizacao()
            if atualizou:
                self.aviso_update = True
                self.texto_update = f"Nova versão disponível: {versao_online}!"
            else:
                self.aviso_update = False
                self.texto_update = ""
        else:
            self.aviso_update = False
            self.texto_update = ""

    def registrar_participacao_evento(self, evento_id):
        if evento_id not in self.eventos_participados:
            self.eventos_participados[evento_id] = 1

    def handle_events(self):
        for event in pygame.event.get():
            if self.image_viewer.handle_event(event):
                continue

            if self.statistics_menu.visible:
                if self.statistics_menu.handle_event(event):
                    continue

            if self.config_menu.achievements_menu.visible:
                if self.config_menu.achievements_menu.handle_event(event):
                    continue

            if self.console.visible:
                if self.console.handle_event(event):
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

            if self.config_menu.settings_menu.visible:
                if self.config_menu.settings_menu.handle_event(event):
                    self.update_volumes()
                    continue

            if self.config_menu.eventos_menu.visible:
                if self.config_menu.eventos_menu.handle_event(event):
                    continue

            if event.type == pygame.QUIT:
                menus_abertos = (
                    self.config_menu.achievements_menu.visible or
                    self.config_menu.settings_menu.visible or
                    self.config_menu.eventos_menu.visible or
                    self.config_menu.is_open or
                    self.upgrade_menu.visible or
                    self.image_viewer.visible or
                    self.statistics_menu.visible
                )
                
                if not menus_abertos and not self.exit_handler.active:
                    self.exit_handler.start()
                continue

            if event.type == pygame.KEYDOWN:
                if self.handle_keydown(event):
                    continue

            if event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mousebuttondown(event)

            if self.config_menu.handle_event(event):
                continue

    def handle_keydown(self, event):
        if event.key == pygame.K_ESCAPE:
            if self.statistics_menu.visible:
                self.statistics_menu.visible = False
                return True
            if self.image_viewer.visible:
                self.image_viewer.visible = False
                return True
            if self.console.visible:
                self.console.minimize()
                return True
            if self.exit_handler.active:
                self.exit_handler.fading_cancel = True
                return True
            if self.upgrade_menu.visible:
                self.upgrade_menu.visible = False
                return True
            if self.config_menu.achievements_menu.visible:
                self.config_menu.achievements_menu.visible = False
                return True
            if self.config_menu.settings_menu.visible:
                self.config_menu.settings_menu.visible = False
                self.update_volumes()
                return True
            if self.config_menu.eventos_menu.visible:
                self.config_menu.eventos_menu.visible = False
                return True
            if self.config_menu.is_open:
                self.config_menu.is_open = False
                return True
            return True

        if event.key == pygame.K_t and pygame.key.get_mods() & pygame.KMOD_CTRL:
            self.resetar_trabalhadores()
            return True

        if event.key == pygame.K_u and not self.console.visible:
            self.upgrade_menu.toggle_visibility()
            return True

        if event.key == pygame.K_i and pygame.key.get_mods() & pygame.KMOD_CTRL:
            self.image_viewer.toggle_visibility()
            return True

        return False

    def handle_mousebuttondown(self, event):
        menus_ativos = (
            self.image_viewer.visible or
            self.console.visible or 
            self.exit_handler.active or
            self.config_menu.settings_menu.visible or
            self.config_menu.achievements_menu.visible or
            self.config_menu.eventos_menu.visible or
            self.config_menu.is_open or
            self.upgrade_menu.visible or
            self.statistics_menu.visible
        )
        
        if event.button in (4, 5):
            current_time = pygame.time.get_ticks()
            if current_time - self.last_scroll_time < 60:
                return
            self.last_scroll_time = current_time
        
        if self.aviso_update and self.update_rect and self.update_rect.collidepoint(event.pos):
            webbrowser.open("https://github.com/eupyetro0224234/Generic-Clicker-Game/releases")
            return
        
        if self.mini_event and self.mini_event.visible and not menus_ativos:
            prev_score = self.score
            new_score, upgrade, pontos_ganhos = self.mini_event.handle_click(event.pos, self.score, self.upgrade_menu)
            
            if upgrade or new_score != prev_score:
                self.tracker.add_mini_event_click()
                self.increment_mini_event1_total()
                self.tracker._check_click_achievements("mini_event")
                self.tracker.check_unlock(new_score)
                
                pontos_com_evento = self.gerenciador_eventos.aplicar_efeitos_pontos(pontos_ganhos)
                self.score = prev_score + pontos_com_evento

                if upgrade:
                    self.click_effects.append(
                        ClickEffect(event.pos[0], event.pos[1], "Upgrade Obtido!"))
                else:
                    self.click_effects.append(
                        ClickEffect(event.pos[0], event.pos[1], f"+{pontos_com_evento}"))
                
                self.save_game_data()
                return

        if self.mini_event2 and self.mini_event2.visible and not menus_ativos:
            prev_score = self.score
            new_score, upgrade, pontos_ganhos = self.mini_event2.handle_click(event.pos, self.score, self.upgrade_menu)
            
            if upgrade or new_score != prev_score:
                self.tracker.add_mini_event_click()
                self.increment_mini_event2_total()
                self.tracker._check_click_achievements("mini_event")
                self.tracker.check_unlock(new_score)
                
                pontos_com_evento = self.gerenciador_eventos.aplicar_efeitos_pontos(pontos_ganhos)
                self.score = prev_score + pontos_com_evento

                if upgrade:
                    self.click_effects.append(
                        ClickEffect(event.pos[0], event.pos[1], "Upgrade Raro!", color=(0, 255, 100)))
                else:
                    self.click_effects.append(
                        ClickEffect(event.pos[0], event.pos[1], f"+{pontos_com_evento}!"))
                
                self.save_game_data()
                return

        button_clicked = self.button.is_clicked(event.pos)
        
        if button_clicked and not menus_ativos:
            self.tracker.add_normal_click()

        prev_vis = self.upgrade_menu.visible
        new_score, trabalhador_comprado = self.upgrade_menu.handle_event(event, self.score)
        
        if new_score != self.score and "auto_click" in self.upgrade_menu.purchased:
            self.tracker.unlock_secret("automatico")
        
        self.tracker.check_all_achievements_completed()
        
        if new_score != self.score or self.upgrade_menu.visible != prev_vis:
            self.score = new_score
            return

        self.button._update_rect()

        if not menus_ativos:
            if self.config_menu.settings_menu.is_click_allowed(event.button):
                if button_clicked:
                    self.button.click()
                    self.upgrade_menu.add_offline_time(30)
                    
                    bonus_base = self.upgrade_menu.get_bonus()
                    bonus_com_evento = self.gerenciador_eventos.aplicar_efeitos_pontos(bonus_base)
                    
                    self.adicionar_pontos(bonus_com_evento)
                    
                    self.tracker.check_unlock(self.score)
                    
                    self.click_effects.append(
                        ClickEffect(event.pos[0], event.pos[1], f"+{int(bonus_com_evento)}"))
                    
                    self.save_game_data()
                    return

        if self.console.visible:
            self.console.handle_event(event)

    def update(self):
        if self.score > self.max_score:
            self.max_score = self.score

        self.config_menu.achievements_menu.achievements = self.tracker.achievements
        self.config_menu.achievements_menu.unlocked = self.tracker.unlocked

        current_time = pygame.time.get_ticks()

        eventos_ativos = self.gerenciador_eventos.atualizar_eventos()
        for evento in eventos_ativos:
            if evento.ativo and evento.id not in self.eventos_participados:
                self.registrar_participacao_evento(evento.id)

        if self.upgrade_menu.auto_click_enabled():
            self.auto_click_counter += 1
            if self.auto_click_counter >= 40:
                self.auto_click_counter = 0
                bonus_auto = self.upgrade_menu.get_auto_click_bonus()
                bonus_com_evento = self.gerenciador_eventos.aplicar_efeitos_pontos(bonus_auto)
                
                pontos_adicionados = self.adicionar_pontos(bonus_com_evento)
                
                if pontos_adicionados > 0:
                    self.tracker.check_unlock(self.score)
                
                self.click_effects.append(
                    ClickEffect(WIDTH // 2, HEIGHT // 2, f"+{int(bonus_com_evento)} (Auto)"))

        mouse_buttons = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()

        mouse_over_button = self.button.rect.collidepoint(mouse_pos)

        if mouse_buttons[0] and mouse_over_button:
            hold_click_qtd = self.upgrade_menu.purchased.get("hold_click", 0)
            if hold_click_qtd > 0:
                if self.hold_click_start_time is None:
                    self.hold_click_start_time = current_time
                    self.hold_click_accumulator = 0
                    self.tracker.unlock_secret("manual_phase")
                else:
                    elapsed = current_time - self.hold_click_start_time
                    if elapsed >= 1000:
                        self.hold_click_accumulator += self.clock.get_time()
                        if self.hold_click_accumulator >= 500:
                            self.hold_click_accumulator = 0
                            hold_com_evento = self.gerenciador_eventos.aplicar_efeitos_pontos(hold_click_qtd)
                            
                            pontos_adicionados = self.adicionar_pontos(hold_com_evento)
                            
                            if pontos_adicionados > 0:
                                self.tracker.check_unlock(self.score)
                            
                            self.click_effects.append(
                                ClickEffect(WIDTH // 2, HEIGHT // 2, f"+{int(hold_com_evento)}"))
        else:
            self.hold_click_start_time = None
            self.hold_click_accumulator = 0

        pontos_trabalhadores, self.score = self.upgrade_menu.update_trabalhadores(current_time, self.score)
        if pontos_trabalhadores > 0:
            pontos_com_evento = self.gerenciador_eventos.aplicar_efeitos_pontos(pontos_trabalhadores)
            
            pontos_adicionados = self.adicionar_pontos(pontos_com_evento)
            
            if pontos_adicionados > 0:
                self.tracker.check_unlock(self.score)

        if self.mini_event and self.mini_event.visible and self.upgrade_menu.mini_event_enabled():
            for trab in self.upgrade_menu.trabalhadores:
                if trab.active and trab.visible:
                    trab_rect = trab.rect
                    mini_rect = pygame.Rect(
                        self.mini_event.x, 
                        self.mini_event.y, 
                        self.mini_event.image.get_width() if hasattr(self.mini_event, 'image') else 50,
                        self.mini_event.image.get_height() if hasattr(self.mini_event, 'image') else 50
                    )
                    
                    if trab_rect.colliderect(mini_rect):
                        success = self.mini_event.handle_worker_click()
                        if success:
                            pontos_ganhos = random.randint(1, 1000)
                            pontos_com_evento = self.gerenciador_eventos.aplicar_efeitos_pontos(pontos_ganhos)
                            
                            pontos_adicionados = self.adicionar_pontos(pontos_com_evento)
                            
                            if pontos_adicionados > 0:
                                self.tracker.check_unlock(self.score)
                            
                            self.click_effects.append(
                                ClickEffect(
                                    self.mini_event.x + 25, 
                                    self.mini_event.y + 25, 
                                    f"+{int(pontos_com_evento)}! (Trabalhador)"
                                )
                            )
                            self.mini_event.visible = False
                            break

        if self.mini_event2 and self.mini_event2.visible and self.upgrade_menu.mini_event_enabled():
            for trab in self.upgrade_menu.trabalhadores:
                if trab.active and trab.visible:
                    trab_rect = trab.rect
                    mini_rect = pygame.Rect(
                        self.mini_event2.x, 
                        self.mini_event2.y, 
                        self.mini_event2.image.get_width() if hasattr(self.mini_event2, 'image') else 60,
                        self.mini_event2.image.get_height() if hasattr(self.mini_event2, 'image') else 60
                    )
                    
                    if trab_rect.colliderect(mini_rect):
                        success = self.mini_event2.handle_worker_click()
                        if success:
                            pontos_ganhos = random.randint(1, 1000) * 2
                            pontos_com_evento = self.gerenciador_eventos.aplicar_efeitos_pontos(pontos_ganhos)
                            
                            pontos_adicionados = self.adicionar_pontos(pontos_com_evento)
                            
                            if pontos_adicionados > 0:
                                self.tracker.check_unlock(self.score)
                            
                            self.click_effects.append(
                                ClickEffect(
                                    self.mini_event2.x + 30, 
                                    self.mini_event2.y + 30, 
                                    f"+{int(pontos_com_evento)}! (Trabalhador)"
                                )
                            )
                            self.mini_event2.visible = False
                            break

        if (current_time - self.last_mini_event_time > self.mini_event_cooldown and
                not self.mini_event and
                random.random() < 0.3):
            self.mini_event = MiniEvent(self.screen, WIDTH, HEIGHT, "normal")
            self.mini_event.set_volume(self.minigame_sound_volume)
            self.last_mini_event_time = current_time

        if (current_time - self.last_mini_event2_time > self.mini_event2_cooldown and
                not self.mini_event2 and
                random.random() < 0.2):
            self.mini_event2 = MiniEvent(self.screen, WIDTH, HEIGHT, "rare")
            self.mini_event2.set_volume(self.minigame_sound_volume)
            self.last_mini_event2_time = current_time

        if self.mini_event:
            self.mini_event.update()
            if not self.mini_event.visible:
                self.mini_event = None

        if self.mini_event2:
            self.mini_event2.update()
            if not self.mini_event2.visible:
                self.mini_event2 = None

        for eff in self.click_effects[:]:
            eff.update()
            if eff.finished:
                self.click_effects.remove(eff)

        if current_time - self.last_save_time >= 1000:
            self.save_game_data()
            self.last_save_time = current_time

    def draw(self):
        draw_background(self.screen)
        
        self.upgrade_menu.draw_trabalhadores()
        
        self.button.draw(self.screen)

        for eff in self.click_effects:
            eff.draw(self.screen)

        if self.mini_event and self.mini_event.visible:
            self.mini_event.draw()

        if self.mini_event2 and self.mini_event2.visible:
            self.mini_event2.draw()

        score_surf = self.FONT.render(str(self.score), True, self.TEXT_COLOR_SCORE)
        score_rect = score_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 180))
        self.screen.blit(score_surf, score_rect)

        mostrar_sequencia = self.config_menu.settings_menu.get_option("Mostrar sequência")
        if mostrar_sequencia and self.streak_data["current_streak"] > 0:
            self.fonte_emoji = pygame.font.SysFont("Segoe UI Emoji", 20)
            emoji_surf = self.fonte_emoji.render("🔥", True, (255, 100, 0))

            numero_surf = self.fonte_streak.render(str(self.streak_data['current_streak']), True, (40, 40, 60))
            
            margin = 20
            total_width = emoji_surf.get_width() + numero_surf.get_width() + 2
            total_height = max(emoji_surf.get_height(), numero_surf.get_height())
            
            x_pos = WIDTH - total_width - margin
            y_pos = HEIGHT - total_height - margin
            
            self.screen.blit(emoji_surf, (x_pos, y_pos))
            self.screen.blit(numero_surf, (x_pos + emoji_surf.get_width() + 2, y_pos))

        if self.upgrade_menu.ganhos_offline_enabled():
            tempo_offline_text = f"Offline: {self.upgrade_menu.get_offline_time_formatted()}"
            tempo_offline_surf = self.fonte_tempo.render(tempo_offline_text, True, (100, 150, 255))
            
            x_pos = (WIDTH - tempo_offline_surf.get_width()) // 2
            y_pos = 20
            
            bg_width = tempo_offline_surf.get_width() + 10
            bg_height = tempo_offline_surf.get_height() + 6
            bg_surface = pygame.Surface((bg_width, bg_height), pygame.SRCALPHA)
            pygame.draw.rect(bg_surface, (50, 50, 80, 180), (0, 0, bg_width, bg_height), border_radius=8)
            self.screen.blit(bg_surface, (x_pos - 5, y_pos - 3))
            
            self.screen.blit(tempo_offline_surf, (x_pos, y_pos))

        self.tracker.draw_popup()

        eventos_ativos = self.gerenciador_eventos.get_eventos_ativos()
        if eventos_ativos:
            for i, evento in enumerate(eventos_ativos):
                evento_ativo_surf = self.fonte_evento.render("EVENTO ATIVO: ", True, (255, 215, 0))
                nome_evento_surf = self.fonte_evento.render(f"{evento.nome}", True, (0, 0, 0))
                
                evento_ativo_rect = evento_ativo_surf.get_rect(center=(WIDTH // 2 - nome_evento_surf.get_width() // 2, HEIGHT - 50))
                nome_evento_rect = nome_evento_surf.get_rect(center=(WIDTH // 2 + evento_ativo_rect.width // 2, HEIGHT - 50))
                
                bg_width = evento_ativo_rect.width + nome_evento_rect.width + 20
                bg_height = max(evento_ativo_rect.height, nome_evento_rect.height) + 10
                bg_rect = pygame.Rect(
                    WIDTH // 2 - bg_width // 2,
                    HEIGHT - 50 - bg_height // 2,
                    bg_width,
                    bg_height
                )
                
                bg_surface = pygame.Surface((bg_width, bg_height), pygame.SRCALPHA)
                
                pygame.draw.rect(bg_surface, (100, 100, 100, 180), (0, 0, bg_width, bg_height), 
                               border_radius=8)
                
                pygame.draw.rect(bg_surface, (150, 150, 150), (0, 0, bg_width, bg_height), 
                               2, border_radius=8)
                
                self.screen.blit(bg_surface, bg_rect)
                
                self.screen.blit(evento_ativo_surf, evento_ativo_rect)
                self.screen.blit(nome_evento_surf, nome_evento_rect)

        if self.aviso_update:
            text_surf = self.fonte_update.render(self.texto_update, True, (255, 50, 50))
            text_rect = text_surf.get_rect(bottomleft=(10, HEIGHT - 10))
            self.screen.blit(text_surf, text_rect)
            self.update_rect = text_rect

        if hasattr(self.config_menu.settings_menu, "precisa_reiniciar") and self.config_menu.settings_menu.precisa_reiniciar:
            aviso = self.fonte_aviso.render("Reinicie o jogo para aplicar mudanças", True, (200, 0, 0))
            aviso_rect = aviso.get_rect(center=(WIDTH // 2, HEIGHT - 30))
            self.screen.blit(aviso, aviso_rect)

        self.upgrade_menu.draw(self.score)
        self.config_menu.draw_icon()
        self.config_menu.draw()
        
        self.config_menu.achievements_menu.draw()
        self.config_menu.eventos_menu.draw()
        
        self.statistics_menu.draw()

        if self.console.visible:
            self.console.draw()

        self.exit_handler.draw()

        self.image_viewer.draw()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)
            
            if pygame.time.get_ticks() % 30 == 0:
                self.update_volumes()

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Generic Clicker Game")
    game = Game(screen)
    game.run()