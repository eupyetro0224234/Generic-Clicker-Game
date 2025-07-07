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
from console import Console
from exit_handler import ExitHandler

def main():
    pasta = os.path.dirname(os.path.abspath(__file__))
    fazer_backup(pasta, os.path.join(pasta, "backups"))

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Just Another Generic Clicker Game, But With References")
    clock = pygame.time.Clock()

    # Tela de loading
    loading = LoadingScreen(screen, WIDTH, HEIGHT)
    for msg, pct in [
        ("Carregando imagens...", 50),
        ("Inicializando menus...", 80),
        ("Quase lá...", 95),
        ("Concluído! Iniciando o jogo", 100),
    ]:
        loading.draw(pct, msg)
        pygame.time.delay(700)

    # Fonte e cores
    FONT = pygame.font.SysFont(None, 64)
    TEXT_COLOR_SCORE = (40, 40, 60)

    # Botão principal
    button = AnimatedButton(
        WIDTH // 2, HEIGHT // 2, 200, 200,
        "https://minecraft.wiki/images/Enchanted_Book.gif?b21c4"
    )

    # Carrega dados salvos
    score_manager = ScoreManager()
    score, controls_visible, saved_achievements, saved_upgrades = score_manager.load_data()

    # ConfigMenu (inclui exit_handler e, depois, console)
    config_menu = ConfigMenu(screen, WIDTH, HEIGHT, loading_callback=loading.draw)
    config_menu.controls_menu.visible = controls_visible

    # Tracker de conquistas
    tracker = AchievementTracker(screen)
    tracker.load_unlocked(saved_achievements)

    # Menu de upgrades
    upgrade_menu = UpgradeMenu(screen, WIDTH, HEIGHT)
    upgrade_menu.load_upgrades(saved_upgrades)

    # Efeitos de clique e contador auto-click
    click_effects = []
    auto_click_counter = 0

    # Console (inicialmente oculto)
    console = Console(screen, WIDTH, HEIGHT)
    console.visible = False

    # ExitHandler
    exit_handler = ExitHandler(screen, WIDTH, HEIGHT)
    config_menu.exit_handler = exit_handler

    # Score accessors
    def get_score():
        return score
    def set_score(new_score):
        nonlocal score
        score = new_score

    console.set_score_accessors(get_score, set_score)
    config_menu.set_score_accessors(get_score, set_score)
    config_menu.achievements_menu.tracker = tracker

    running = True
    while running:
        # Se estiver fazendo fade-out de saída
        if exit_handler.fading_out:
            if exit_handler.update_fade_out():
                pygame.display.flip()
                clock.tick(60)
                continue

        for event in pygame.event.get():
            # Se o exit_handler estiver ativo, ele “consome” o evento
            if exit_handler.active:
                if exit_handler.handle_event(event) and exit_handler.detected_console:
                    # desbloqueia console se digitou “console”
                    config_menu.enable_console()
                    tracker.unlock_secret("console")
                    exit_handler.detected_console = False
                    exit_handler.active = False
                continue

            # Quit (fecha com prompt)
            if event.type == pygame.QUIT:
                exit_handler.start()
                continue

            # Teclas
            if event.type == pygame.KEYDOWN:
                # R = reset completo
                if event.key == pygame.K_r and not console.visible:
                    score = 0
                    tracker.unlocked.clear()
                    for ach in tracker.achievements:
                        ach.unlocked = False
                    upgrade_menu.purchased.clear()
                    # reabilita console sem reiniciar
                    config_menu.enable_console()
                    continue

                # ESC fecha submenus/console
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

            # Eventos dos submenus
            if config_menu.settings_menu.visible and config_menu.settings_menu.handle_event(event):
                continue
            if config_menu.controls_menu.visible and config_menu.controls_menu.handle_event(event):
                continue
            if config_menu.achievements_menu.visible and config_menu.achievements_menu.handle_event(event):
                continue
            if console.visible and console.handle_event(event):
                continue

            # Clique no ícone de upgrades (abre/fecha sempre)
            if event.type == pygame.MOUSEBUTTONDOWN:
                prev_vis = upgrade_menu.visible
                new_score, _ = upgrade_menu.handle_event(event, score)
                if new_score != score or upgrade_menu.visible != prev_vis:
                    score = new_score
                    continue

                # Tratamento do clique no botão principal
                button._update_rect()
                if not (
                    config_menu.settings_menu.visible or
                    config_menu.achievements_menu.visible or
                    console.visible or
                    exit_handler.active
                ):
                    if config_menu.settings_menu.is_click_allowed(event.button):
                        if button.is_clicked(event.pos):
                            button.click()
                            score += upgrade_menu.get_bonus()
                            tracker.check_unlock(score)
                            click_effects.append(ClickEffect(event.pos[0], event.pos[1], "+1"))
                            continue

            # Clique nos itens do ConfigMenu (abertura/seleção)
            if config_menu.handle_event(event):
                continue

        # Atualiza dados do menu de conquistas
        config_menu.achievements_menu.achievements = tracker.achievements
        config_menu.achievements_menu.unlocked = tracker.unlocked

        # Desenho geral
        draw_background(screen)
        button.draw(screen)

        # Auto-click
        if upgrade_menu.auto_click_enabled():
            auto_click_counter += 1
            if auto_click_counter >= 40:
                auto_click_counter = 0
                score += upgrade_menu.get_bonus()
                tracker.check_unlock(score)
                click_effects.append(ClickEffect(WIDTH // 2, HEIGHT // 2, "+1 (Auto)"))

        # Pontuação
        score_surf = FONT.render(str(score), True, TEXT_COLOR_SCORE)
        score_rect = score_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 140))
        screen.blit(score_surf, score_rect)

        # Desenha menus
        upgrade_menu.draw(score)
        config_menu.draw_icon()
        config_menu.draw()
        if console.visible:
            console.draw()
        exit_handler.draw()
        tracker.draw_popup()

        # Efeitos
        for eff in click_effects[:]:
            eff.update()
            eff.draw(screen)
            if eff.finished:
                click_effects.remove(eff)

        pygame.display.flip()
        clock.tick(60)

        # Salva estado
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
