import pygame
import random
import os
import sys
import time
import math
from game_code.background import draw_background, WIDTH, HEIGHT
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
from game_code.trabalhador import Trabalhador

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
        self.load_game_data()
        
        self.config_menu = ConfigMenu(screen, WIDTH, HEIGHT, score_manager=self.score_manager)
        self.setup_fonts()
        self.setup_game_components()
        self.setup_console()
        self.setup_event_handling()
        
        self.verificar_update()
        self.last_save_time = pygame.time.get_ticks()
        self.last_backup_save_time = pygame.time.get_ticks()
        self.last_scroll_time = 0
        
    def load_game_data(self):
        try:
            (self.score, self.controls_visible, saved_achievements, 
             saved_upgrades, mini_event_click_count, trabalhadores_data, trabalhador_limit_enabled) = self.score_manager.load_data()
            
            self.saved_trabalhadores_data = trabalhadores_data
            self.saved_trabalhador_limit_enabled = trabalhador_limit_enabled
                
        except Exception as e:
            restore_backup = self.show_confirmation_dialog(
                "Erro ao carregar os dados do jogo.\nDeseja restaurar o backup antigo?"
            )

            if restore_backup:
                backup_data = self.score_manager.load_backup()
                if backup_data:
                    (self.score, self.controls_visible, saved_achievements, 
                     saved_upgrades, mini_event_click_count, trabalhadores_data, trabalhador_limit_enabled) = backup_data
                    self.score_manager.save_data(
                        self.score, self.controls_visible, saved_achievements, 
                        saved_upgrades, mini_event_click_count, trabalhador_limit_enabled
                    )
                    
                    self.saved_trabalhadores_data = trabalhadores_data
                    self.saved_trabalhador_limit_enabled = trabalhador_limit_enabled
                else:
                    (self.score, self.controls_visible, saved_achievements, 
                     saved_upgrades, mini_event_click_count) = 0, False, [], {}, 0
                    self.saved_trabalhadores_data = []
                    self.saved_trabalhador_limit_enabled = True
            else:
                (self.score, self.controls_visible, saved_achievements, 
                 saved_upgrades, mini_event_click_count) = 0, False, [], {}, 0
                self.saved_trabalhadores_data = []
                self.saved_trabalhador_limit_enabled = True

        self.saved_achievements = saved_achievements
        self.saved_upgrades = saved_upgrades
        self.mini_event_click_count = mini_event_click_count

    def setup_fonts(self):
        self.FONT = pygame.font.SysFont(None, 64)
        self.TEXT_COLOR_SCORE = (40, 40, 60)
        self.fonte_update = pygame.font.SysFont(None, 48)
        self.fonte_aviso = pygame.font.SysFont(None, 28)

    def setup_game_components(self):
        button_path = resource_path(os.path.join("game_assets", "button.gif"))
        self.button = AnimatedButton(
            WIDTH // 2, HEIGHT // 2, 200, 200,
            button_path
        )

        self.config_menu.controls_menu.visible = self.controls_visible

        self.tracker = AchievementTracker(self.screen)
        self.tracker.load_unlocked(self.saved_achievements)
        self.tracker.load_sound()
        self.tracker.mini_event_clicks = self.mini_event_click_count

        self.upgrade_menu = UpgradeMenu(self.screen, WIDTH, HEIGHT, achievement_tracker=self.tracker)
        self.upgrade_menu.load_upgrades(self.saved_upgrades)
        self.upgrade_menu.set_trabalhador_limit(self.saved_trabalhador_limit_enabled)

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

        # Eventos unificados
        self.mini_event = None
        self.last_mini_event_time = pygame.time.get_ticks()
        self.mini_event_cooldown = 30000  # 30 segundos

        self.mini_event2 = None
        self.last_mini_event2_time = pygame.time.get_ticks()
        self.mini_event2_cooldown = 120000  # 2 minutos (reduzido para teste)

        # Spawn inicial para teste
        if random.random() < 0.3:
            self.mini_event = MiniEvent(self.screen, WIDTH, HEIGHT, "normal")
            self.last_mini_event_time = pygame.time.get_ticks()

        if random.random() < 0.2:
            self.mini_event2 = MiniEvent(self.screen, WIDTH, HEIGHT, "rare")
            self.last_mini_event2_time = pygame.time.get_ticks()

        self.config_menu.achievements_menu.tracker = self.tracker

        self.aviso_update = False
        self.texto_update = ""

    def resetar_trabalhadores(self):
        self.upgrade_menu.trabalhadores = []

    def adicionar_trabalhador(self):
        pass

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
                    continue

            if event.type == pygame.QUIT:
                if not self.exit_handler.active:
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
            if self.console.visible:
                self.console.minimize()
                return True
            if self.exit_handler.active:
                self.exit_handler.fading_cancel = True
                return True
            if self.upgrade_menu.visible:
                self.upgrade_menu.visible = False
                return True
            if self.config_menu.is_open:
                self.config_menu.is_open = False
                return True
            return True

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
                self.score_manager.save_data(
                    self.score,
                    self.config_menu.controls_menu.visible,
                    list(self.tracker.unlocked),
                    self.upgrade_menu.purchased,
                    self.tracker.mini_event_clicks,
                    self.upgrade_menu.get_trabalhador_limit_status()
                )
            return True

        if event.key == pygame.K_t and pygame.key.get_mods() & pygame.KMOD_CTRL:
            self.resetar_trabalhadores()
            return True

        if event.key == pygame.K_u and not self.console.visible:
            self.upgrade_menu.toggle_visibility()
            return True

        return False

    def handle_mousebuttondown(self, event):
        if event.button in (4, 5):
            current_time = pygame.time.get_ticks()
            if current_time - self.last_scroll_time < 60:
                return
            self.last_scroll_time = current_time
        
        menus_ativos = (
            self.console.visible or 
            self.exit_handler.active or
            self.config_menu.settings_menu.visible or
            self.config_menu.achievements_menu.visible or
            self.config_menu.is_open or
            self.upgrade_menu.visible
        )
        
        # Clique no MiniEvent normal
        if self.mini_event and self.mini_event.visible and not menus_ativos:
            prev_score = self.score
            new_score, upgrade, pontos_ganhos = self.mini_event.handle_click(event.pos, self.score, self.upgrade_menu)
            
            if upgrade or new_score != prev_score:
                self.tracker.add_mini_event_click()
                self.tracker.check_unlock(new_score)
                self.score = new_score

                if upgrade:
                    self.click_effects.append(
                        ClickEffect(event.pos[0], event.pos[1], "Upgrade Obtido!"))
                else:
                    self.click_effects.append(
                        ClickEffect(event.pos[0], event.pos[1], f"+{pontos_ganhos}"))
                
                self.score_manager.save_data(
                    self.score,
                    self.config_menu.controls_menu.visible,
                    list(self.tracker.unlocked),
                    self.upgrade_menu.purchased,
                    self.tracker.mini_event_clicks,
                    self.upgrade_menu.get_trabalhador_limit_status()
                )
                return

        # Clique no MiniEvent raro (MiniEvent2)
        if self.mini_event2 and self.mini_event2.visible and not menus_ativos:
            prev_score = self.score
            new_score, upgrade, pontos_ganhos = self.mini_event2.handle_click(event.pos, self.score, self.upgrade_menu)
            
            if upgrade or new_score != prev_score:
                self.tracker.add_mini_event_click()
                self.tracker.check_unlock(new_score)
                self.score = new_score

                if upgrade:
                    self.click_effects.append(
                        ClickEffect(event.pos[0], event.pos[1], "Upgrade Raro!", color=(0, 255, 100)))
                else:
                    self.click_effects.append(
                        ClickEffect(event.pos[0], event.pos[1], f"+{pontos_ganhos}!"))
                
                self.score_manager.save_data(
                    self.score,
                    self.config_menu.controls_menu.visible,
                    list(self.tracker.unlocked),
                    self.upgrade_menu.purchased,
                    self.tracker.mini_event_clicks,
                    self.upgrade_menu.get_trabalhador_limit_status()
                )
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
                    self.score += self.upgrade_menu.get_bonus()
                    self.tracker.check_unlock(self.score)
                    self.click_effects.append(
                        ClickEffect(event.pos[0], event.pos[1], f"+{self.upgrade_menu.get_bonus()}"))
                    
                    self.score_manager.save_data(
                        self.score,
                        self.config_menu.controls_menu.visible,
                        list(self.tracker.unlocked),
                        self.upgrade_menu.purchased,
                        self.tracker.mini_event_clicks,
                        self.upgrade_menu.get_trabalhador_limit_status()
                    )
                    return

        if self.console.visible:
            self.console.handle_event(event)

    def update(self):
        self.config_menu.achievements_menu.achievements = self.tracker.achievements
        self.config_menu.achievements_menu.unlocked = self.tracker.unlocked

        current_time = pygame.time.get_ticks()

        if self.upgrade_menu.auto_click_enabled():
            self.auto_click_counter += 1
            if self.auto_click_counter >= 40:
                self.auto_click_counter = 0
                bonus_auto = self.upgrade_menu.get_auto_click_bonus()
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
                            self.score += hold_click_qtd
                            self.tracker.check_unlock(self.score)
                            self.click_effects.append(
                                ClickEffect(WIDTH // 2, HEIGHT // 2, f"+{hold_click_qtd} (Hold)"))

        pontos_trabalhadores = self.upgrade_menu.update_trabalhadores(current_time)
        if pontos_trabalhadores > 0:
            self.score += pontos_trabalhadores
            self.tracker.check_unlock(self.score)

        # Trabalhadores interagem com MiniEvent normal
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
                            self.score += pontos_ganhos
                            self.tracker.check_unlock(self.score)
                            self.click_effects.append(
                                ClickEffect(
                                    self.mini_event.x + 25, 
                                    self.mini_event.y + 25, 
                                    f"+{pontos_ganhos}! (Trabalhador)"
                                )
                            )
                            self.mini_event.visible = False
                            break

        # Trabalhadores interagem com MiniEvent raro
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
                            self.score += pontos_ganhos
                            self.tracker.check_unlock(self.score)
                            self.click_effects.append(
                                ClickEffect(
                                    self.mini_event2.x + 30, 
                                    self.mini_event2.y + 30, 
                                    f"+{pontos_ganhos}! (Trabalhador)"
                                )
                            )
                            self.mini_event2.visible = False
                            break

        # Spawn do MiniEvent normal
        if (current_time - self.last_mini_event_time > self.mini_event_cooldown and
                not self.mini_event and
                random.random() < 0.3):
            self.mini_event = MiniEvent(self.screen, WIDTH, HEIGHT, "normal")
            self.last_mini_event_time = current_time

        # Spawn do MiniEvent raro
        if (current_time - self.last_mini_event2_time > self.mini_event2_cooldown and
                not self.mini_event2 and
                random.random() < 0.2):
            self.mini_event2 = MiniEvent(self.screen, WIDTH, HEIGHT, "rare")
            self.last_mini_event2_time = current_time

        # Atualização dos eventos
        if self.mini_event:
            self.mini_event.update()
            if not self.mini_event.visible:
                self.mini_event = None

        if self.mini_event2:
            self.mini_event2.update()
            if not self.mini_event2.visible:
                self.mini_event2 = None

        # Atualização dos efeitos de clique
        for eff in self.click_effects[:]:
            eff.update()
            if eff.finished:
                self.click_effects.remove(eff)

        # Salvamento automático
        if current_time - self.last_save_time >= 1000:
            self.score_manager.save_data(
                self.score,
                self.config_menu.controls_menu.visible,
                list(self.tracker.unlocked),
                self.upgrade_menu.purchased,
                self.tracker.mini_event_clicks,
                self.upgrade_menu.get_trabalhador_limit_status()
            )
            self.last_save_time = current_time

        if self.aviso_update and (current_time - self.last_backup_save_time >= 1000):
            self.score_manager.save_backup(
                self.score,
                self.config_menu.controls_menu.visible,
                list(self.tracker.unlocked),
                self.upgrade_menu.purchased,
                self.tracker.mini_event_clicks,
                self.upgrade_menu.get_trabalhador_limit_status()
            )
            self.last_backup_save_time = current_time

    def draw(self):
        draw_background(self.screen)
        
        self.upgrade_menu.draw_trabalhadores()
        
        self.button.draw(self.screen)

        self.tracker.draw_popup()
        for eff in self.click_effects:
            eff.draw(self.screen)

        # Desenha eventos
        if self.mini_event and self.mini_event.visible:
            self.mini_event.draw()

        if self.mini_event2 and self.mini_event2.visible:
            self.mini_event2.draw()

        # Score
        score_surf = self.FONT.render(str(self.score), True, self.TEXT_COLOR_SCORE)
        score_rect = score_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 180))
        self.screen.blit(score_surf, score_rect)

        # Aviso de update
        if self.aviso_update:
            text_surf = self.fonte_update.render(self.texto_update, True, (255, 50, 50))
            text_rect = text_surf.get_rect(center=(WIDTH // 2, 100))
            self.screen.blit(text_surf, text_rect)

        # Aviso de reinício
        if hasattr(self.config_menu.settings_menu, "precisa_reiniciar") and self.config_menu.settings_menu.precisa_reiniciar:
            aviso = self.fonte_aviso.render("Reinicie o jogo para aplicar mudanças", True, (200, 0, 0))
            aviso_rect = aviso.get_rect(center=(WIDTH // 2, HEIGHT - 30))
            self.screen.blit(aviso, aviso_rect)

        # Menus
        self.upgrade_menu.draw(self.score)
        self.config_menu.draw_icon()
        self.config_menu.draw()
        
        self.config_menu.achievements_menu.draw()
        
        if self.console.visible:
            self.console.draw()

        self.exit_handler.draw()

    def run(self):
        while self.running:
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