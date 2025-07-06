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

def main():
    # --- Backup inicial ---
    pasta = os.path.dirname(os.path.abspath(__file__))
    fazer_backup(pasta, os.path.join(pasta, "backups"))

    # --- Pygame init ---
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Just Another Generic Clicker Game, But With References")
    clock = pygame.time.Clock()

    # --- Loading screen ---
    loading = LoadingScreen(screen, WIDTH, HEIGHT)
    for msg, pct in [
        ("Carregando imagens...", 50),
        ("Inicializando menus...", 80),
        ("Quase lá...", 95),
        ("Concluído! Iniciando o jogo", 100),
    ]:
        loading.draw(pct, msg)
        pygame.time.delay(700)

    FONT = pygame.font.SysFont(None, 48)
    TEXT_COLOR_SCORE = (40, 40, 60)

    # --- Botão principal ---
    button = AnimatedButton(
        WIDTH // 2, HEIGHT // 2, 200, 200,
        "https://minecraft.wiki/images/Enchanted_Book.gif?b21c4"
    )

    # --- ScoreManager e dados iniciais ---
    score_manager = ScoreManager()
    score, controls_visible, saved_achievements = score_manager.load_data()

    # --- ConfigMenu e sincronização de controles ---
    config_menu = ConfigMenu(screen, WIDTH, HEIGHT, loading_callback=loading.draw)
    config_menu.controls_menu.visible = controls_visible

    # --- AchievementTracker e conquistas carregadas ---
    tracker = AchievementTracker(screen)
    tracker.load_unlocked(saved_achievements)

    click_effects = []

    running = True
    while running:
        # fade-out de saída
        if config_menu.exit_handler.fading_out:
            if config_menu.exit_handler.update_fade_out():
                pygame.display.flip()
                clock.tick(60)
                continue

        for event in pygame.event.get():
            # diálogo de saída
            if config_menu.exit_handler.active:
                config_menu.exit_handler.handle_event(event)
                continue

            # submenus
            if config_menu.settings_menu.visible and config_menu.settings_menu.handle_event(event):
                continue
            if config_menu.controls_menu.visible and config_menu.controls_menu.handle_event(event):
                continue
            if config_menu.achievements_menu.visible and config_menu.achievements_menu.handle_event(event):
                continue

            # menu principal
            if config_menu.handle_event(event):
                continue

            # sair
            if event.type == pygame.QUIT:
                config_menu.exit_handler.start()
                continue

            # clique do mouse
            if event.type == pygame.MOUSEBUTTONDOWN:
                # verifica permissão no config antes de contar clique
                if config_menu.settings_menu.is_click_allowed(event.button):
                    # só conta se nenhum submenu estiver aberto
                    if (not config_menu.settings_menu.visible and
                        not config_menu.controls_menu.visible and
                        not config_menu.achievements_menu.visible):
                        if button.is_clicked(event.pos):
                            button.click()
                            score += 1
                            click_effects.append(ClickEffect(event.pos[0], event.pos[1], "+1"))
                            tracker.check_unlock(score)

            # reset de pontos
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                score = 0

        # desenho da cena
        draw_background(screen)
        button.draw(screen)

        # caixa de score
        bx, by, bw, bh = 20, 20, 220, 60
        score_manager.draw_score_box(screen, bx, by, bw, bh)
        txt = FONT.render(f"Pontos: {score}", True, TEXT_COLOR_SCORE)
        screen.blit(txt, txt.get_rect(center=(bx + bw//2, by + bh//2)))

        # desenha menus
        config_menu.draw_icon()
        config_menu.draw()

        # notificação de conquistas
        tracker.draw_popup()

        # efeitos de clique
        for eff in click_effects[:]:
            eff.update()
            eff.draw(screen)
            if eff.finished:
                click_effects.remove(eff)

        # sincroniza conquistas no menu para a contagem aparecer
        config_menu.achievements_menu.tracker = tracker

        pygame.display.flip()
        clock.tick(60)

    # salvamento final
    score_manager.save_data(score,
                            config_menu.controls_menu.visible,
                            list(tracker.unlocked))

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
