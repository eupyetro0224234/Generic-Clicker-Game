import pygame
import sys
import os
from backup import fazer_backup
from background import draw_background, WIDTH, HEIGHT
from button import AnimatedButton
from score_manager import ScoreManager
from menu import ConfigMenu
from loading import LoadingScreen
from click_effect import ClickEffect
from conquistas import AchievementTracker
from upgrades import UpgradeMenu

def main():
    pasta = os.path.dirname(os.path.abspath(__file__))
    fazer_backup(pasta, os.path.join(pasta, "backups"))

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Just Another Generic Clicker Game, But With References")
    clock = pygame.time.Clock()

    loading = LoadingScreen(screen, WIDTH, HEIGHT)
    for msg, pct in [
        ("Carregando imagens...", 50),
        ("Inicializando menus...", 80),
        ("Quase lá...", 95),
        ("Concluído! Iniciando o jogo", 100),
    ]:
        loading.draw(pct, msg)
        pygame.time.delay(700)

    FONT = pygame.font.SysFont(None, 64)
    TEXT_COLOR_SCORE = (40, 40, 60)

    button = AnimatedButton(
        WIDTH // 2, HEIGHT // 2, 200, 200,
        "https://minecraft.wiki/images/Enchanted_Book.gif?b21c4"
    )

    score_manager = ScoreManager()
    score, controls_visible, saved_achievements, saved_upgrades = score_manager.load_data()

    config_menu = ConfigMenu(screen, WIDTH, HEIGHT, loading_callback=loading.draw)
    config_menu.controls_menu.visible = controls_visible

    tracker = AchievementTracker(screen)
    tracker.load_unlocked(saved_achievements)

    upgrade_menu = UpgradeMenu(screen, WIDTH, HEIGHT)
    upgrade_menu.load_upgrades(saved_upgrades)

    # Adiciona o botão de upgrade ao lado do botão de configurações
    config_menu.add_extra_icon(upgrade_menu.get_icon_rect(), upgrade_menu.toggle_visibility)

    click_effects = []
    running = True

    while running:
        if config_menu.exit_handler.fading_out:
            if config_menu.exit_handler.update_fade_out():
                pygame.display.flip()
                clock.tick(60)
                continue

        for event in pygame.event.get():
            if config_menu.exit_handler.active:
                config_menu.exit_handler.handle_event(event)
                continue

            if event.type == pygame.QUIT:
                config_menu.exit_handler.start()
                continue

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    score = 0
                    tracker.unlocked.clear()
                    for ach in tracker.achievements:
                        ach.unlocked = False
                    upgrade_menu.reset_upgrades()
                    continue

                if event.key == pygame.K_ESCAPE:
                    if config_menu.exit_handler.active:
                        config_menu.exit_handler.active = False
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

            if config_menu.handle_event(event):
                continue

            if event.type == pygame.MOUSEBUTTONDOWN:
                button._update_rect()
                if config_menu.settings_menu.is_click_allowed(event.button):
                    if button.is_clicked(event.pos):
                        button.click()
                        score += upgrade_menu.get_bonus()
                        click_effects.append(ClickEffect(event.pos[0], event.pos[1], "+1"))
                        tracker.check_unlock(score)
                        continue

                res = upgrade_menu.handle_event(event, score)
                if isinstance(res, tuple):
                    score, _ = res
                    continue
                elif res:
                    continue

        config_menu.achievements_menu.tracker = tracker
        config_menu.achievements_menu.achievements = tracker.achievements
        config_menu.achievements_menu.unlocked = tracker.unlocked

        draw_background(screen)
        button.draw(screen)

        # Pontuação centralizada acima do botão
        score_surf = FONT.render(str(score), True, TEXT_COLOR_SCORE)
        score_rect = score_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 130))
        screen.blit(score_surf, score_rect)

        # Auto clique automático a cada 1 segundo
        if upgrade_menu.auto_click_enabled():
            upgrade_menu.auto_click_timer += clock.get_time()
            if upgrade_menu.auto_click_timer >= 1000:
                score += 1
                upgrade_menu.auto_click_timer = 0

        upgrade_menu.draw(score)
        config_menu.draw_icon()
        config_menu.draw()
        tracker.draw_popup()

        for eff in click_effects[:]:
            eff.update()
            eff.draw(screen)
            if eff.finished:
                click_effects.remove(eff)

        pygame.display.flip()
        clock.tick(60)

        # Salvar progresso em cada loop (você pode mover isso para somente ao sair, se quiser)
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
