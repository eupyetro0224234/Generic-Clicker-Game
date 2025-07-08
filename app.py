import pygame
import sys
import os
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
import updates  # seu módulo updates.py

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
    fonte_aviso = pygame.font.SysFont(None, 28)  # Fonte para aviso reinício

    button = AnimatedButton(
        WIDTH // 2, HEIGHT // 2, 200, 200,
        os.path.join(os.getenv("LOCALAPPDATA") or ".", ".assets", "button.gif")
    )

    score_manager = ScoreManager()
    score, controls_visible, saved_achievements, saved_upgrades = score_manager.load_data()

    config_menu = ConfigMenu(screen, WIDTH, HEIGHT, loading_callback=loading.draw)
    config_menu.controls_menu.visible = controls_visible

    tracker = AchievementTracker(screen)
    tracker.load_unlocked(saved_achievements)

    upgrade_menu = UpgradeMenu(screen, WIDTH, HEIGHT)
    upgrade_menu.load_upgrades(saved_upgrades)

    click_effects = []
    auto_click_counter = 0

    console = Console(screen, WIDTH, HEIGHT, on_exit_callback=config_menu.disable_console)
    console.visible = False

    exit_handler = ExitHandler(screen, WIDTH, HEIGHT)
    config_menu.exit_handler = exit_handler

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

    # === NOVO: Verifica atualização APENAS UMA VEZ no início ===
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

    while True:
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
                    score = 0
                    tracker.unlocked.clear()
                    for ach in tracker.achievements:
                        ach.unlocked = False
                    upgrade_menu.reset_upgrades()
                    config_menu.enable_console()
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

            if config_menu.settings_menu.visible and config_menu.settings_menu.handle_event(event):
                continue
            if config_menu.controls_menu.visible and config_menu.controls_menu.handle_event(event):
                continue
            if config_menu.achievements_menu.visible and config_menu.achievements_menu.handle_event(event):
                continue
            if console.visible and console.handle_event(event):
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
                            continue

            if config_menu.handle_event(event):
                continue

        config_menu.achievements_menu.achievements = tracker.achievements
        config_menu.achievements_menu.unlocked = tracker.unlocked

        draw_background(screen)
        button.draw(screen)

        if upgrade_menu.auto_click_enabled():
            auto_click_counter += 1
            if auto_click_counter >= 40:
                auto_click_counter = 0
                bonus_auto = upgrade_menu.get_auto_click_bonus()
                score += bonus_auto
                tracker.check_unlock(score)
                click_effects.append(
                    ClickEffect(WIDTH // 2, HEIGHT // 2, f"+{bonus_auto} (Auto)")
                )

        score_surf = FONT.render(str(score), True, TEXT_COLOR_SCORE)
        score_rect = score_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 140))
        screen.blit(score_surf, score_rect)

        if aviso_update:
            text_surf = fonte_update.render(texto_update, True, (255, 50, 50))
            text_rect = text_surf.get_rect(center=(WIDTH // 2, 100))
            screen.blit(text_surf, text_rect)

        # Exibe aviso para reiniciar se a opção "Verificar atualizações" foi alterada
        if config_menu.settings_menu.precisa_reiniciar:
            aviso_reiniciar_texto = "Para aplicar a mudança em 'Verificar atualizações', reinicie o jogo."
            aviso_surf = fonte_aviso.render(aviso_reiniciar_texto, True, (255, 165, 0))
            aviso_rect = aviso_surf.get_rect(center=(WIDTH // 2, HEIGHT - 50))
            screen.blit(aviso_surf, aviso_rect)

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

        score_manager.save_data(
            score,
            config_menu.controls_menu.visible,
            list(tracker.unlocked),
            upgrade_menu.purchased
        )

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
