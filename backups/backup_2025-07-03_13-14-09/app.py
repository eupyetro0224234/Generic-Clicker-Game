import pygame
import sys
import os
from backup import fazer_backup
from background import draw_background, WIDTH, HEIGHT
from button import AnimatedButton
from score_manager import ScoreManager
from menu import ConfigMenu  # menu principal (ícone + opções + controle do controles)
# controles.py contém ControlsMenu

def main():
    pasta_do_projeto = os.path.dirname(os.path.abspath(__file__))
    pasta_de_backups = r"C:\Users\pyetr\OneDrive\Desktop\unitypy\backups"

    fazer_backup(pasta_do_projeto, pasta_de_backups)

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Just Another Generic Clicker Game, But With References")

    FONT = pygame.font.SysFont(None, 48)
    TEXT_COLOR_SCORE = (40, 40, 60)

    button = AnimatedButton(WIDTH // 2, HEIGHT // 2, 200, 200,
                            "https://minecraft.wiki/images/Enchanted_Book.gif?b21c4")

    score_manager = ScoreManager()
    score = score_manager.load_score()

    config_menu = ConfigMenu(screen, WIDTH, HEIGHT)

    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            # Prioridade para menus (controle de eventos)
            if config_menu.handle_event(event):
                continue

            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button.is_clicked(event.pos):
                    button.click()
                    score += 1
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    score = 0

        draw_background(screen)
        button.draw(screen)

        box_x, box_y = 20, 20
        box_w, box_h = 220, 60
        score_manager.draw_score_box(screen, box_x, box_y, box_w, box_h)

        score_text = FONT.render(f"Pontos: {score}", True, TEXT_COLOR_SCORE)
        score_rect = score_text.get_rect(center=(box_x + box_w // 2, box_y + box_h // 2))
        screen.blit(score_text, score_rect)

        # Desenha o ícone do menu, o menu pequeno e o menu controles (se visível)
        config_menu.draw_icon()
        config_menu.draw_menu()
        config_menu.controls_menu.draw()

        pygame.display.flip()
        clock.tick(60)

    score_manager.save_score(score)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
