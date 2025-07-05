import pygame
import sys
import os
import time
from backup import fazer_backup
from background import draw_background, WIDTH, HEIGHT
from button import AnimatedButton
from score_manager import ScoreManager
from menu import ConfigMenu
from loading import LoadingScreen
from click_effect import ClickEffect
from conquistas import AchievementsMenu

def main():
    # --- Setup inicial e backup ---
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
    steps = [
        ("Carregando imagens...", 50),
        ("Inicializando menus...", 80),
        ("Quase lá...", 95),
        ("Concluído! Iniciando o jogo", 100)
    ]
    for msg, pct in steps:
        loading_screen.draw(pct, msg)
        pygame.time.delay(700)

    # --- Fontes e cores ---
    FONT = pygame.font.SysFont(None, 48)
    TEXT_COLOR_SCORE = (120, 0, 60)  # rosa escuro

    # --- Botão principal ---
    button = AnimatedButton(
        WIDTH // 2, HEIGHT // 2, 200, 200,
        "https://minecraft.wiki/images/Enchanted_Book.gif?b21c4"
    )

    # --- ScoreManager carrega dados (score, controle, conquistas) ---
    score_manager = ScoreManager()
    score, controls_visible, loaded_achievements = score_manager.load_data()

    # --- Menus ---
    def loading_callback(pct, msg):
        loading_screen.draw(pct, msg)

    config_menu = ConfigMenu(screen, WIDTH, HEIGHT, loading_callback=loading_callback)
    config_menu.controls_menu.visible = controls_visible

    # Menu de conquistas
    achievements_menu = AchievementsMenu(screen, WIDTH, HEIGHT)
    achievements_menu.achievements = loaded_achievements[:]  # carrega conquistas
    config_menu.achievements_menu = achievements_menu

    click_effects = []

    running = True
    while running:
        for event in pygame.event.get():
            # diálogo de saída
            if config_menu.exit_handler.active:
                config_menu.exit_handler.handle_event(event)
                continue

            # submenus
            if config_menu.settings_menu.visible:
                if config_menu.settings_menu.handle_event(event):
                    continue
            if config_menu.controls_menu.visible:
                if config_menu.controls_menu.handle_event(event):
                    continue
            if achievements_menu.visible:
                if achievements_menu.handle_event(event):
                    continue

            # menu principal
            if config_menu.handle_event(event):
                continue

            # quit
            if event.type == pygame.QUIT:
                config_menu.exit_handler.start()
                continue

            # clique no botão
            if event.type == pygame.MOUSEBUTTONDOWN:
                if config_menu.settings_menu.is_click_allowed(event.button):
                    if button.is_clicked(event.pos):
                        button.click()
                        score += 1
                        click_effects.append(ClickEffect(event.pos[0], event.pos[1], "+1"))

                        # exemplo: conquista primeiro clique
                        if score == 1:
                            achievements_menu.add_achievement("Primeiro Clique")
                        # exemplo: conquista 10 cliques
                        if score == 10:
                            achievements_menu.add_achievement("10 Cliques")

            # resetar
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    score = 0
                    achievements_menu.add_achievement("Recomeço")

        # --- Desenho ---
        draw_background(screen)
        button.draw(screen)

        # caixa score rosa claro
        box_x, box_y, box_w, box_h = 20, 20, 260, 60
        score_manager.draw_score_box(screen, box_x, box_y, box_w, box_h)
        score_surf = FONT.render(f"Pontos: {score}", True, TEXT_COLOR_SCORE)
        score_rect = score_surf.get_rect(center=(box_x + box_w//2, box_y + box_h//2))
        screen.blit(score_surf, score_rect)

        # menus
        config_menu.draw_icon()
        config_menu.draw()
        achievements_menu.draw()        # desenha menu completo se aberto

        # notificações de conquista
        achievements_menu.draw()        # menu e
        # aviso temporário:
        achievements_menu.draw()        # nota: draw() já inclui alerta

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
        achievements_menu.achievements
    )
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
