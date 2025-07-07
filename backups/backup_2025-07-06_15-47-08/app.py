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
from conquistas import AchievementTracker, AchievementsMenu

def main():
    # --- Backup inicial ---
    pasta_do_projeto = os.path.dirname(os.path.abspath(__file__))
    pasta_de_backups = os.path.join(pasta_do_projeto, "backups")
    fazer_backup(pasta_do_projeto, pasta_de_backups)

    # --- Inicialização do Pygame ---
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Just Another Generic Clicker Game, But With References")
    clock = pygame.time.Clock()

    # --- Tela de loading ---
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

    # --- ScoreManager: carrega score, visibilidade dos controles e conquistas ---
    score_manager = ScoreManager()
    score, controls_visible, loaded_achievements = score_manager.load_data()

    # --- AchievementTracker e AchievementsMenu ---
    tracker = AchievementTracker(screen)
    tracker.unlocked = set(loaded_achievements)

    achievements_menu = AchievementsMenu(screen, WIDTH, HEIGHT)
    achievements_menu.tracker = tracker

    # --- Configuração dos menus ---
    def loading_cb(p, m):
        loading_screen.draw(p, m)

    config_menu = ConfigMenu(screen, WIDTH, HEIGHT, loading_callback=loading_cb)
    config_menu.controls_menu.visible = controls_visible
    config_menu.achievements_menu = achievements_menu

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

            # submenus tratam evento
            if config_menu.settings_menu.visible and config_menu.settings_menu.handle_event(event):
                continue
            if config_menu.controls_menu.visible and config_menu.controls_menu.handle_event(event):
                continue
            if achievements_menu.visible and achievements_menu.handle_event(event):
                continue

            # menu principal
            if config_menu.handle_event(event):
                continue

            # fechar janela
            if event.type == pygame.QUIT:
                # salva antes de iniciar fade
                score_manager.save_data(
                    score,
                    config_menu.controls_menu.visible,
                    list(tracker.unlocked)
                )
                config_menu.exit_handler.start()
                continue

            # clique no botão
            if event.type == pygame.MOUSEBUTTONDOWN:
                # desativa clique se Configurações ou Conquistas estiverem abertos
                if config_menu.settings_menu.visible or achievements_menu.visible:
                    continue
                if config_menu.settings_menu.is_click_allowed(event.button) and button.is_clicked(event.pos):
                    button.click()
                    score += 1
                    click_effects.append(ClickEffect(event.pos[0], event.pos[1], "+1"))
                    tracker.check(score)
                    # salva após mudança
                    score_manager.save_data(
                        score,
                        config_menu.controls_menu.visible,
                        list(tracker.unlocked)
                    )

            # resetar pontuação
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                score = 0
                tracker.unlocked.clear()
                score_manager.save_data(
                    score,
                    config_menu.controls_menu.visible,
                    list(tracker.unlocked)
                )

        # --- Desenho da tela principal ---
        draw_background(screen)
        button.draw(screen)

        # caixa de score
        bx, by, bw, bh = 20, 20, 260, 60
        score_manager.draw_score_box(screen, bx, by, bw, bh)
        score_surf = FONT.render(f"Pontos: {score}", True, TEXT_COLOR_SCORE)
        score_rect = score_surf.get_rect(center=(bx + bw // 2, by + bh // 2))
        screen.blit(score_surf, score_rect)

        # desenha menus
        config_menu.draw_icon()
        config_menu.draw()

        # desenha menu de conquistas (compacto ou detalhado)
        achievements_menu.draw()

        # desenha popup de novas conquistas
        tracker.draw_popup()

        # efeitos de clique
        for eff in click_effects[:]:
            eff.update()
            eff.draw(screen)
            if eff.finished:
                click_effects.remove(eff)

        pygame.display.flip()
        clock.tick(60)

    # --- Salvamento final ---
    score_manager.save_data(
        score,
        config_menu.controls_menu.visible,
        list(tracker.unlocked)
    )
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
