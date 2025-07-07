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
    pasta_do_projeto = os.path.dirname(os.path.abspath(__file__))
    pasta_de_backups = os.path.join(pasta_do_projeto, "backups")
    fazer_backup(pasta_do_projeto, pasta_de_backups)

    # --- Pygame init ---
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Just Another Generic Clicker Game, But With References")
    clock = pygame.time.Clock()

    # --- Loading screen ---
    loading_screen = LoadingScreen(screen, WIDTH, HEIGHT)
    for msg, pct in [
        ("Carregando imagens...", 50),
        ("Inicializando menus...", 80),
        ("Quase lá...", 95),
        ("Concluído! Iniciando o jogo", 100),
    ]:
        loading_screen.draw(pct, msg)
        pygame.time.delay(700)

    # --- Fontes e cores ---
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

    # --- ConfigMenu e visibilidade dos controles ---
    config_menu = ConfigMenu(screen, WIDTH, HEIGHT, loading_callback=loading_screen.draw)
    config_menu.controls_menu.visible = controls_visible

    # --- AchievementTracker e conquistas carregadas ---
    tracker = AchievementTracker(screen)
    tracker.load_unlocked(saved_achievements)

    # Sincroniza conquistas no menu
    config_menu.achievements_menu.tracker = tracker
    config_menu.achievements_menu.achievements = tracker.achievements
    config_menu.achievements_menu.unlocked = tracker.unlocked

    click_effects = []

    running = True
    while running:
        # Fade-out de saída
        if config_menu.exit_handler.fading_out:
            if config_menu.exit_handler.update_fade_out():
                pygame.display.flip()
                clock.tick(60)
                continue

        for event in pygame.event.get():
            # Diálogo de saída
            if config_menu.exit_handler.active:
                config_menu.exit_handler.handle_event(event)
                continue

            # Submenus: Configurações, Controles, Conquistas
            if config_menu.settings_menu.visible and config_menu.settings_menu.handle_event(event):
                continue
            if config_menu.controls_menu.visible and config_menu.controls_menu.handle_event(event):
                continue
            if config_menu.achievements_menu.visible and config_menu.achievements_menu.handle_event(event):
                continue

            # Menu principal
            if config_menu.handle_event(event):
                continue

            # Fechar janela
            if event.type == pygame.QUIT:
                config_menu.exit_handler.start()
                continue

            # Clique no botão principal
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Verifica permissão de clique no config
                if config_menu.settings_menu.is_click_allowed(event.button):
                    # Só conta se nenhum submenu estiver aberto
                    if not (config_menu.settings_menu.visible or
                            config_menu.controls_menu.visible or
                            config_menu.achievements_menu.visible):
                        if button.is_clicked(event.pos):
                            button.click()
                            score += 1
                            click_effects.append(ClickEffect(event.pos[0], event.pos[1], "+1"))
                            tracker.check_unlock(score)

            # Reset de pontos
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                score = 0
                tracker.unlocked.clear()
                # também resetar o unlocked flag em cada Achievement
                for ach in tracker.achievements:
                    ach.unlocked = False

        # Desenha background e botão
        draw_background(screen)
        button.draw(screen)

        # Caixa de score
        bx, by, bw, bh = 20, 20, 220, 60
        score_manager.draw_score_box(screen, bx, by, bw, bh)
        score_surf = FONT.render(f"Pontos: {score}", True, TEXT_COLOR_SCORE)
        screen.blit(score_surf, score_surf.get_rect(center=(bx + bw//2, by + bh//2)))

        # Sincroniza conquistas no menu antes de desenhar
        config_menu.achievements_menu.tracker = tracker
        config_menu.achievements_menu.achievements = tracker.achievements
        config_menu.achievements_menu.unlocked = tracker.unlocked

        # Desenha menus
        config_menu.draw_icon()
        config_menu.draw()

        # Desenha popup de conquista desbloqueada
        tracker.draw_popup()

        # Desenha efeitos de clique
        for effect in click_effects[:]:
            effect.update()
            effect.draw(screen)
            if effect.finished:
                click_effects.remove(effect)

        pygame.display.flip()
        clock.tick(60)

    # Salvamento final
    score_manager.save_data(
        score,
        config_menu.controls_menu.visible,
        list(tracker.unlocked)
    )

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
