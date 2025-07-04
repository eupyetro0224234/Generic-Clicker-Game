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

def main():
    pasta_do_projeto = os.path.dirname(os.path.abspath(__file__))
    pasta_de_backups = os.path.join(pasta_do_projeto, "backups")
    fazer_backup(pasta_do_projeto, pasta_de_backups)

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Just Another Generic Clicker Game, But With References")

    loading_screen = LoadingScreen(screen, WIDTH, HEIGHT)
    steps = [
        ("Carregando imagens...", 50),
        ("Inicializando menus...", 80),
        ("Quase lá...", 95),
        ("Concluído!", 100)
    ]
    for msg, percent in steps:
        loading_screen.draw(percent, msg)
        pygame.time.delay(700)

    FONT = pygame.font.SysFont(None, 48)
    TEXT_COLOR_SCORE = (40, 40, 60)

    button = AnimatedButton(WIDTH // 2, HEIGHT // 2, 200, 200,
                            "https://minecraft.wiki/images/Enchanted_Book.gif?b21c4")

    score_manager = ScoreManager()
    score, controls_visible = score_manager.load_data()

    def loading_callback(percent, message):
        loading_screen.draw(percent, message)

    config_menu = ConfigMenu(screen, WIDTH, HEIGHT, loading_callback=loading_callback)
    config_menu.controls_menu.visible = controls_visible

    clock = pygame.time.Clock()
    click_effects = []

    botoes_pressionados = set()
    pontuou_no_frame = False  # controle para só pontuar 1 vez por frame

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        pontuou_no_frame = False  # reseta a flag a cada frame

        for event in pygame.event.get():
            if config_menu.handle_event(event):
                continue
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                botoes_pressionados.add(event.button)

                # Só pontua e mostra efeito se o clique foi no botão animado e não pontuou ainda neste frame
                if not pontuou_no_frame and button.is_clicked(event.pos):
                    button.click()
                    pontos_para_adicionar = len(botoes_pressionados)
                    score += pontos_para_adicionar

                    # Exibe efeito visual com +N
                    effect = ClickEffect(event.pos[0], event.pos[1], text=f"+{pontos_para_adicionar}")
                    click_effects.append(effect)

                    pontuou_no_frame = True  # evita pontuar múltiplas vezes por frame

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button in botoes_pressionados:
                    botoes_pressionados.remove(event.button)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    score = 0

        draw_background(screen)
        button.draw(screen)

        # Caixa de pontuação
        box_x, box_y = 20, 20
        box_w, box_h = 220, 60
        score_manager.draw_score_box(screen, box_x, box_y, box_w, box_h)

        score_text = FONT.render(f"Pontos: {score}", True, TEXT_COLOR_SCORE)
        score_rect = score_text.get_rect(center=(box_x + box_w // 2, box_y + box_h // 2))
        screen.blit(score_text, score_rect)

        for effect in click_effects[:]:
            effect.update()
            effect.draw(screen)
            if effect.finished:
                click_effects.remove(effect)

        config_menu.draw_icon()
        config_menu.draw()

        if hasattr(config_menu, "exit_handler") and config_menu.exit_handler.update_fade_out():
            pygame.display.flip()
            continue

        pygame.display.flip()
        clock.tick(60)

    score_manager.save_data(score, config_menu.controls_menu.visible)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
