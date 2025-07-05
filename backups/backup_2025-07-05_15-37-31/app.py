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
from conquistas import AchievementsMenu

def main():
    # Backup
    pasta_do_projeto = os.path.dirname(os.path.abspath(__file__))
    pasta_de_backups = os.path.join(pasta_do_projeto, "backups")
    fazer_backup(pasta_do_projeto, pasta_de_backups)

    # Inicialização Pygame
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Just Another Generic Clicker Game, But With References")
    clock = pygame.time.Clock()

    # Tela de loading
    loading_screen = LoadingScreen(screen, WIDTH, HEIGHT)
    for msg, pct in [
        ("Carregando imagens...", 50),
        ("Inicializando menus...", 80),
        ("Quase lá...", 95),
        ("Concluído! Iniciando o jogo", 100)
    ]:
        loading_screen.draw(pct, msg)
        pygame.time.delay(700)

    # Fontes e cores
    FONT = pygame.font.SysFont(None, 48)
    TEXT_COLOR_SCORE = (120, 0, 60)

    # Botão principal
    button = AnimatedButton(
        WIDTH // 2, HEIGHT // 2, 200, 200,
        "https://minecraft.wiki/images/Enchanted_Book.gif?b21c4"
    )

    # Carrega score, controles e conquistas
    score_manager = ScoreManager()
    score, controls_visible, loaded_achievements = score_manager.load_data()

    # Menus
    def loading_callback(pct, msg):
        loading_screen.draw(pct, msg)

    config_menu = ConfigMenu(screen, WIDTH, HEIGHT, loading_callback=loading_callback)
    config_menu.controls_menu.visible = controls_visible

    achievements_menu = AchievementsMenu(screen, WIDTH, HEIGHT)
    achievements_menu.achievements = loaded_achievements[:]
    config_menu.achievements_menu = achievements_menu

    click_effects = []

    running = True
    while running:
        # Primeiro, se fade-out ativo, atualiza e continua
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

            # Submenus abertos tratam evento
            if config_menu.settings_menu.visible:
                if config_menu.settings_menu.handle_event(event):
                    continue
            if config_menu.controls_menu.visible:
                if config_menu.controls_menu.handle_event(event):
                    continue
            if achievements_menu.visible:
                if achievements_menu.handle_event(event):
                    continue

            # Menu principal
            if config_menu.handle_event(event):
                continue

            # Quit
            if event.type == pygame.QUIT:
                config_menu.exit_handler.start()
                continue

            # Clique no botão
            if event.type == pygame.MOUSEBUTTONDOWN:
                if config_menu.settings_menu.is_click_allowed(event.button):
                    if button.is_clicked(event.pos):
                        button.click()
                        score += 1
                        click_effects.append(ClickEffect(event.pos[0], event.pos[1], "+1"))
                        # Conquistas de exemplo
                        if score == 1:
                            achievements_menu.add_achievement("Primeiro Clique")
                        if score == 10:
                            achievements_menu.add_achievement("10 Cliques")

            # Reset
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    score = 0
                    achievements_menu.add_achievement("Recomeço")

        # Desenho da tela
        draw_background(screen)
        button.draw(screen)

        # Caixa do score
        box_x, box_y, box_w, box_h = 20, 20, 260, 60
        score_manager.draw_score_box(screen, box_x, box_y, box_w, box_h)
        score_surf = FONT.render(f"Pontos: {score}", True, TEXT_COLOR_SCORE)
        score_rect = score_surf.get_rect(center=(box_x + box_w//2, box_y + box_h//2))
        screen.blit(score_surf, score_rect)

        # Desenha ícone e menus
        config_menu.draw_icon()
        config_menu.draw()
        achievements_menu.draw()

        # Desenha notificações temporárias de conquista
        achievements_menu.draw()

        # Efeitos de clique
        for eff in click_effects[:]:
            eff.update()
            eff.draw(screen)
            if eff.finished:
                click_effects.remove(eff)

        pygame.display.flip()
        clock.tick(60)

    # Salva dados ao sair
    score_manager.save_data(
        score,
        config_menu.controls_menu.visible,
        achievements_menu.achievements
    )
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
