import os
import pygame
import random
import json
import sys
from background import draw_background, WIDTH, HEIGHT
from button import AnimatedButton
from score_manager import ScoreManager
from menu import ConfigMenu
from loading import LoadingScreen, download_assets
from click_effect import ClickEffect
from conquistas import AchievementTracker
from upgrades import UpgradeMenu
from console import Console
from exit_handler import ExitHandler
import updates
from mini_event import MiniEvent

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Just Another Generic Clicker Game, But With References")
    clock = pygame.time.Clock()

    loading = LoadingScreen(screen, WIDTH, HEIGHT)
    download_assets(screen, WIDTH, HEIGHT)

    FONT = pygame.font.SysFont(None, 64)
    TEXT_COLOR_SCORE = (40, 40, 60)
    fonte_update = pygame.font.SysFont(None, 48)
    fonte_aviso = pygame.font.SysFont(None, 28)

    button = AnimatedButton(
        WIDTH // 2, HEIGHT // 2, 200, 200,
        os.path.join(os.getenv("LOCALAPPDATA") or ".", ".assets", "button.gif")
    )

    score_manager = ScoreManager()
    score, controls_visible, saved_achievements, saved_upgrades, last_mini_event_click_time = score_manager.load_data()

    config_menu = ConfigMenu(screen, WIDTH, HEIGHT, loading_callback=loading.draw)
    config_menu.controls_menu.visible = controls_visible

    tracker = AchievementTracker(screen)
    tracker.load_unlocked(saved_achievements)

    upgrade_menu = UpgradeMenu(screen, WIDTH, HEIGHT)
    upgrade_menu.load_upgrades(saved_upgrades)

    click_effects = []
    auto_click_counter = 0

    # Inicialize o Console corretamente, passando o upgrade_manager
    console = Console(
        screen, 
        WIDTH, 
        HEIGHT, 
        on_exit_callback=config_menu.disable_console, 
        tracker=tracker, 
        config_menu=config_menu, 
        upgrade_manager=upgrade_menu
    )
    console.visible = False

    exit_handler = ExitHandler(screen, WIDTH, HEIGHT)
    config_menu.exit_handler = exit_handler

    mini_event = None
    last_mini_event_time = pygame.time.get_ticks()  # Tempo do último mini evento
    mini_event_cooldown = 30000  # 30 segundos entre eventos

    # Chance de 50% de spawn no início do jogo
    if random.random() < 0.1:
        mini_event = MiniEvent(screen, WIDTH, HEIGHT)
        last_mini_event_time = pygame.time.get_ticks()
        print("Mini evento spawnado no início do jogo!")
    else:
        print("Não spawnou mini evento no início")

    def get_score():
        return score

    def set_score(new_score):
        nonlocal score
        score = new_score

    console.set_score_accessors(get_score, set_score)
    config_menu.set_score_accessors(get_score, set_score)
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

    last_save_time = pygame.time.get_ticks()  # Variável para controlar o tempo de salvamento
    running = True
    while running:
        if exit_handler.fading_out:
            if exit_handler.update_fade_out():
                pygame.display.flip()
                clock.tick(60)
                continue

        for event in pygame.event.get():
            if exit_handler.active:
                if exit_handler.handle_event(event):
                    if exit_handler.detected_console:
                        config_menu.enable_console()
                        tracker.unlock_secret("console")
                        exit_handler.detected_console = False
                        exit_handler.active = False
                    continue

            if event.type == pygame.QUIT:
                if not exit_handler.active and not exit_handler.fading_out:
                    exit_handler.start()
                continue

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and not console.visible:
                    # Resetando o jogo
                    score = 0
                    tracker.unlocked.clear()
                    for ach in tracker.achievements:
                        ach.unlocked = False
                    upgrade_menu.reset_upgrades()
                    continue

                if event.key == pygame.K_u and not console.visible:
                    # Resetando os upgrades
                    print("Resetando upgrades...")
                    upgrade_menu.purchased.clear()
                    score_manager.save_data(
                        score,
                        config_menu.controls_menu.visible,
                        list(tracker.unlocked),
                        upgrade_menu.purchased,
                        last_mini_event_click_time
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
                prev_vis = upgrade_menu.visible
                new_score, _ = upgrade_menu.handle_event(event, score)
                if new_score != score or upgrade_menu.visible != prev_vis:
                    score = new_score
                    continue

                button._update_rect()
                if not (
                    config_menu.settings_menu.visible
                    or config_menu.achievements_menu.visible
                    or console.visible
                    or exit_handler.active
                ):
                    if config_menu.settings_menu.is_click_allowed(event.button):
                        if button.is_clicked(event.pos):
                            button.click()
                            score += upgrade_menu.get_bonus()
                            tracker.check_unlock(score)
                            click_effects.append(
                                ClickEffect(event.pos[0], event.pos[1], f"+{upgrade_menu.get_bonus()}")
                            )
                            # Salvar dados após o clique no botão
                            score_manager.save_data(
                                score,
                                config_menu.controls_menu.visible,
                                list(tracker.unlocked),
                                upgrade_menu.purchased,
                                last_mini_event_click_time
                            )
                            continue

                if mini_event and mini_event.visible:
                    score, upgrade = mini_event.handle_click(event.pos, score, upgrade_menu)
                    if upgrade:
                        tracker.check_unlock(score)
                        click_effects.append(
                            ClickEffect(event.pos[0], event.pos[1], "Upgrade Obtido!"))
                
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

        # Lógica de spawn do mini evento
        current_time = pygame.time.get_ticks()
        
        # Verifica se passou o cooldown e se não há evento ativo
        if (current_time - last_mini_event_time > mini_event_cooldown and 
            not mini_event and 
            random.random() < 0.1):  # 50% de chance de spawnar
            
            mini_event = MiniEvent(screen, WIDTH, HEIGHT)
            last_mini_event_time = current_time
            print("Novo mini evento spawnado!")

        if mini_event:
            mini_event.update()
            
            # Se o evento expirou, limpa a referência
            if not mini_event.visible:
                mini_event = None
                print("Mini evento expirado!")

        draw_background(screen)
        button.draw(screen)

        # Desenha o mini evento ANTES de outros elementos de UI
        if mini_event and mini_event.visible:
            print("Desenhando mini evento...")
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

        exit_handler.draw()
        tracker.draw_popup()

        for eff in click_effects[:]:
            eff.update()
            eff.draw(screen)
            if eff.finished:
                click_effects.remove(eff)

        pygame.display.flip()
        clock.tick(60)

        # Salvamento automático a cada 5 segundos
        current_time = pygame.time.get_ticks()
        if current_time - last_save_time >= 5000:  # 5000 ms = 5 segundos
            score_manager.save_data(
                score,
                config_menu.controls_menu.visible,
                list(tracker.unlocked),
                upgrade_menu.purchased,
                last_mini_event_click_time
            )
            last_save_time = current_time

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()