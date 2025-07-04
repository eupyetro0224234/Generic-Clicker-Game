import pygame
import sys
import os
from backup import fazer_backup
from background import draw_background, WIDTH, HEIGHT
from button import AnimatedButton
from score_manager import ScoreManager
from menu1 import MainMenu
from menu2 import SubMenus

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
    score, controls_visible = score_manager.load_data()

    options = ["Configurações", "Volume: [•••••]", "Tema: Claro", "Controles"]

    submenus = SubMenus(screen, WIDTH, HEIGHT)
    submenus.controls_menu.visible = controls_visible

    def on_option_select(selected):
        if selected == "Controles":
            submenus.toggle_menu("Controles")
        elif selected == "Configurações":
            submenus.toggle_menu("Configurações")
        # Pode adicionar lógica para Volume, Tema etc se quiser

    main_menu = MainMenu(screen, WIDTH, HEIGHT, options, on_option_select)

    clock = pygame.time.Clock()

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if submenus.handle_event(event):
                continue  # evento consumido pelos submenus
            if main_menu.handle_event(event):
                continue  # evento consumido pelo menu principal

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

        main_menu.draw()
        submenus.draw()

        pygame.display.flip()
        clock.tick(60)

    score_manager.save_data(score, submenus.controls_menu.visible)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
