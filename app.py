import os
import pygame
import random
import json
import sys
import time
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

def carregar_icone():
    icon_path = os.path.join(os.getenv("LOCALAPPDATA") or ".", ".assets", "icone.ico")
    if os.path.exists(icon_path):
        try:
            try:
                from PIL import Image
                img = Image.open(icon_path)
                icon = pygame.image.fromstring(img.tobytes(), img.size, img.mode)
                pygame.display.set_icon(icon)
            except ImportError:
                icon = pygame.image.load(icon_path)
                pygame.display.set_icon(icon)

            if sys.platform == 'win32':
                import ctypes
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("GenericClickerGame.1.0")
        except Exception:
            pass

def show_confirmation_dialog(screen, width, height, message):
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

    dialog = ConfirmationDialog(screen, width, height, message)
    s = pygame.Surface((width, height), pygame.SRCALPHA)
    s.fill((0, 0, 0, 150))
    screen.blit(s, (0, 0))
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

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Just Another Generic Clicker Game, But With References")

    carregar_icone()
    clock = pygame.time.Clock()
    pygame.mixer.init()

    score_manager = ScoreManager()

    try:
        score, controls_visible, saved_achievements, saved_upgrades, mini_event_click_count = score_manager.load_data()
    except Exception:
        restore_backup = show_confirmation_dialog(
            screen, WIDTH, HEIGHT,
            "Erro ao carregar os dados do jogo.\nDeseja restaurar o backup antigo?"
        )

        if restore_backup:
            backup_data = score_manager.load_backup()
            if backup_data:
                score, controls_visible, saved_achievements, saved_upgrades, mini_event_click_count = backup_data
                score_manager.save_data(
                    score, controls_visible, saved_achievements, saved_upgrades, mini_event_click_count
                )
            else:
                score, controls_visible, saved_achievements, saved_upgrades, mini_event_click_count = 0, False, [], {}, 0
        else:
            score, controls_visible, saved_achievements, saved_upgrades, mini_event_click_count = 0, False, [], {}, 0

    config_menu = ConfigMenu(screen, WIDTH, HEIGHT, score_manager=score_manager)

    pular_loading = False
    if hasattr(config_menu, "settings_menu") and config_menu.settings_menu:
        pular_loading = config_menu.settings_menu.get_option("Pular o loading")

    download_assets(screen, WIDTH, HEIGHT, skip_loading=pular_loading)

    FONT = pygame.font.SysFont(None, 64)
    TEXT_COLOR_SCORE = (40, 40, 60)
    fonte_update = pygame.font.SysFont(None, 48)
    fonte_aviso = pygame.font.SysFont(None, 28)

    button = AnimatedButton(
        WIDTH // 2, HEIGHT // 2, 200, 200,
        os.path.join(os.getenv("LOCALAPPDATA") or ".", ".assets", "button.gif")
    )

    config_menu.controls_menu.visible = controls_visible

    tracker = AchievementTracker(screen)
    tracker.load_unlocked(saved_achievements)
    tracker.load_sound()
    tracker.mini_event_clicks = mini_event_click_count

    upgrade_menu = UpgradeMenu(screen, WIDTH, HEIGHT, achievement_tracker=tracker)
    upgrade_menu.load_upgrades(saved_upgrades)

    trabalhador = upgrade_menu.trabalhador_instancia
    if trabalhador and trabalhador.active:
        trabalhador.start(pygame.time.get_ticks())

    click_effects = []
    auto_click_counter = 0

    hold_click_start_time = None
    hold_click_accumulator = 0

    def get_score():
        return score

    def set_score(new_score):
        nonlocal score
        if isinstance(new_score, float) and new_score.is_integer():
            score = int(new_score)
        else:
            score = new_score

    def on_console_open():
        config_menu.enable_console(add_option=True)

    def on_console_close():
        config_menu.disable_console(remove_option=True)

    console = Console(
        screen,
        WIDTH,
        HEIGHT,
        on_exit_callback=on_console_close,
        on_open_callback=on_console_open,
        tracker=tracker,
        config_menu=config_menu,
        upgrade_manager=upgrade_menu
    )
    console.set_score_accessors(get_score, set_score)
    config_menu.set_score_accessors(get_score, set_score)

    if config_menu.settings_menu.get_option("Manter console aberto"):
        config_menu.enable_console(add_option=True)
        if config_menu.console_instance:
            config_menu.console_instance.open()

    exit_handler = ExitHandler(screen, WIDTH, HEIGHT)
    config_menu.exit_handler = exit_handler

    config_menu.achievements_menu = AchievementsMenu(screen, WIDTH, HEIGHT, config_menu)
    config_menu.achievements_menu.achievements = tracker.achievements
    config_menu.achievements_menu.unlocked = tracker.unlocked

    mini_event = None
    last_mini_event_time = pygame.time.get_ticks()
    mini_event_cooldown = 30000

    if random.random() < 0.1:
        mini_event = MiniEvent(screen, WIDTH, HEIGHT)
        last_mini_event_time = pygame.time.get_ticks()

    config_menu.achievements_menu.tracker = tracker
    config_menu.console_instance = console

    aviso_update = False
    texto_update = ""

    def verificar_update():
        nonlocal aviso_update, texto_update
        if config_menu.settings_menu.get_option("Verificar atualizações"):
            atualizou, versao_online = updates.checar_atualizacao()
            if atualizou:
                aviso_update = True
                texto_update = f"Nova versão disponível: {versao_online}!"
            else:
                aviso_update = False
                texto_update = ""
        else:
            aviso_update = False
            texto_update = ""

    verificar_update()

    last_save_time = pygame.time.get_ticks()
    last_backup_save_time = pygame.time.get_ticks()

    running = True
    while running:
        if exit_handler.fading_out:
            if exit_handler.update_fade_out():
                pygame.display.flip()
                clock.tick(60)
                continue

        for event in pygame.event.get():
            if exit_handler.active:
                result = exit_handler.handle_event(event)

                if exit_handler.detected_console:
                    config_menu.enable_console(add_option=True)
                    tracker.unlock_secret("console")
                    exit_handler.active = False
                    exit_handler.user_text = ""
                    exit_handler.detected_console = False
                    continue

                if result:
                    continue

            if event.type == pygame.QUIT:
                if not exit_handler.active and not exit_handler.fading_out:
                    exit_handler.start()
                continue

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and not console.visible:
                    confirmed = show_confirmation_dialog(
                        screen, WIDTH, HEIGHT,
                        "Deseja realmente resetar TODOS os dados do jogo?"
                    )
                    if confirmed:
                        score = 0
                        tracker.unlocked.clear()
                        tracker.normal_clicks = 0
                        tracker.mini_event_clicks = 0
                        for ach in tracker.achievements:
                            ach.unlocked = False
                        upgrade_menu.reset_upgrades()
                        trabalhador.active = False
                        score_manager.save_data(
                            score,
                            config_menu.controls_menu.visible,
                            list(tracker.unlocked),
                            upgrade_menu.purchased,
                            tracker.mini_event_clicks
                        )
                    continue

                if event.key == pygame.K_u and not console.visible:
                    upgrade_menu.purchased.clear()
                    trabalhador.active = False
                    score_manager.save_data(
                        score,
                        config_menu.controls_menu.visible,
                        list(tracker.unlocked),
                        upgrade_menu.purchased,
                        tracker.mini_event_clicks
                    )
                    continue

                if event.key == pygame.K_ESCAPE:
                    if console.visible:
                        console.visible = False
                        continue
                    if exit_handler.active:
                        exit_handler.active = False
                        continue
                    if config_menu.settings_menu.visible:
                        config_menu.settings_menu.visible = False
                        continue
                    if config_menu.controls_menu.visible:
                        config_menu.controls_menu.visible = False
                        continue
                    if config_menu.achievements_menu.visible:
                        config_menu.achievements_menu.visible = False
                        continue
                    if upgrade_menu.visible:
                        upgrade_menu.visible = False
                        continue
                    if config_menu.is_open:
                        config_menu.is_open = False
                        continue

            if event.type == pygame.MOUSEBUTTONDOWN:
                if mini_event and mini_event.visible:
                    prev_score = score
                    score, upgrade = mini_event.handle_click(event.pos, score, upgrade_menu)
                    if upgrade or score != prev_score:
                        tracker.add_mini_event_click()
                        if upgrade:
                            click_effects.append(
                                ClickEffect(event.pos[0], event.pos[1], "Upgrade Obtido!"))
                        else:
                            click_effects.append(
                                ClickEffect(event.pos[0], event.pos[1], "+Pontos!"))
                        score_manager.save_data(
                            score,
                            config_menu.controls_menu.visible,
                            list(tracker.unlocked),
                            upgrade_menu.purchased,
                            tracker.mini_event_clicks
                        )
                        continue

                prev_vis = upgrade_menu.visible
                new_score, _ = upgrade_menu.handle_event(event, score)
                if new_score != score or upgrade_menu.visible != prev_vis:
                    score = new_score
                    continue

                button._update_rect()

                if not (config_menu.settings_menu.visible or
                        config_menu.achievements_menu.visible or
                        console.visible or
                        exit_handler.active):
                    if config_menu.settings_menu.is_click_allowed(event.button):
                        if button.is_clicked(event.pos):
                            button.click()
                            score += upgrade_menu.get_bonus()
                            tracker.add_normal_click()
                            tracker.check_unlock(score)
                            click_effects.append(
                                ClickEffect(event.pos[0], event.pos[1], f"+{upgrade_menu.get_bonus()}"))
                            score_manager.save_data(
                                score,
                                config_menu.controls_menu.visible,
                                list(tracker.unlocked),
                                upgrade_menu.purchased,
                                tracker.mini_event_clicks
                            )
                            continue

                if console.visible:
                    console.handle_event(event)

            if config_menu.handle_event(event):
                continue

        config_menu.achievements_menu.achievements = tracker.achievements
        config_menu.achievements_menu.unlocked = tracker.unlocked

        if upgrade_menu.auto_click_enabled():
            auto_click_counter += 1
            if auto_click_counter >= 40:
                auto_click_counter = 0
                bonus_auto = upgrade_menu.get_auto_click_bonus()
                score += bonus_auto
                tracker.check_unlock(score)
                click_effects.append(
                    ClickEffect(WIDTH // 2, HEIGHT // 2, f"+{bonus_auto} (Auto)"))

        mouse_buttons = pygame.mouse.get_pressed()

        if mouse_buttons[0]:
            hold_click_qtd = upgrade_menu.purchased.get("hold_click", 0)
            if hold_click_qtd > 0:
                if hold_click_start_time is None:
                    hold_click_start_time = pygame.time.get_ticks()
                    hold_click_accumulator = 0
                else:
                    elapsed = pygame.time.get_ticks() - hold_click_start_time
                    if elapsed >= 3000:
                        hold_click_accumulator += clock.get_time()
                        if hold_click_accumulator >= 500:
                            hold_click_accumulator = 0
                            score += hold_click_qtd
                            tracker.add_normal_click()
                            tracker.check_unlock(score)
                            click_effects.append(
                                ClickEffect(WIDTH // 2, HEIGHT // 2, f"+{hold_click_qtd} (Hold)"))
        else:
            hold_click_start_time = None
            hold_click_accumulator = 0

        current_time = pygame.time.get_ticks()
        if (current_time - last_mini_event_time > mini_event_cooldown and
                not mini_event and
                random.random() < 0.1):
            mini_event = MiniEvent(screen, WIDTH, HEIGHT)
            last_mini_event_time = current_time

        if mini_event:
            mini_event.update()
            if not mini_event.visible:
                mini_event = None

        # Update worker if active
        if trabalhador and trabalhador.active:
            pontos = trabalhador.update(current_time)
            if pontos > 0:
                score += pontos

        draw_background(screen)
        button.draw(screen)

        if mini_event and mini_event.visible:
            mini_event.draw()

        score_surf = FONT.render(str(score), True, TEXT_COLOR_SCORE)
        score_rect = score_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 140))
        screen.blit(score_surf, score_rect)

        if aviso_update:
            text_surf = fonte_update.render(texto_update, True, (255, 50, 50))
            text_rect = text_surf.get_rect(center=(WIDTH // 2, 100))
            screen.blit(text_surf, text_rect)

        if hasattr(config_menu.settings_menu, "precisa_reiniciar") and config_menu.settings_menu.precisa_reiniciar:
            aviso = fonte_aviso.render("Reinicie o jogo para aplicar mudanças", True, (200, 0, 0))
            aviso_rect = aviso.get_rect(center=(WIDTH // 2, HEIGHT - 30))
            screen.blit(aviso, aviso_rect)

        upgrade_menu.draw(score)
        config_menu.draw_icon()
        config_menu.draw()
        if console.visible:
            console.draw()

        # Draw worker
        if trabalhador:
            trabalhador.draw()

        exit_handler.draw()
        tracker.draw_popup()

        for eff in click_effects[:]:
            eff.update()
            eff.draw(screen)
            if eff.finished:
                click_effects.remove(eff)

        pygame.display.flip()
        clock.tick(60)

        if current_time - last_save_time >= 1000:
            score_manager.save_data(
                score,
                config_menu.controls_menu.visible,
                list(tracker.unlocked),
                upgrade_menu.purchased,
                tracker.mini_event_clicks
            )
            last_save_time = current_time

        if aviso_update and (current_time - last_backup_save_time >= 1000):
            score_manager.save_backup(
                score,
                config_menu.controls_menu.visible,
                list(tracker.unlocked),
                upgrade_menu.purchased,
                tracker.mini_event_clicks
            )
            last_backup_save_time = current_time

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()