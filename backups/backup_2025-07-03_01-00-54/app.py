import pygame
import sys
import os
from backup import fazer_backup
from background import draw_background, WIDTH, HEIGHT
from button import AnimatedButton
from score_manager import ScoreManager

def draw_score_box(screen, x, y, w, h):
    # Sombra
    shadow_color = (0, 0, 0, 50)
    shadow_surf = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(shadow_surf, shadow_color, (5, 5, w, h), border_radius=15)
    screen.blit(shadow_surf, (x, y))

    # Fundo pastel azul claro com cantos arredondados
    bg_color = (180, 210, 255)
    pygame.draw.rect(screen, bg_color, (x, y, w, h), border_radius=15)

    # Quadradinhos sutis (opcional)
    square_size = 12
    sq_surf = pygame.Surface((square_size, square_size), pygame.SRCALPHA)
    color1 = (200, 220, 255, 60)
    color2 = (170, 200, 250, 60)
    for i in range(0, w, square_size):
        for j in range(0, h, square_size):
            sq_surf.fill(color1 if (i//square_size + j//square_size) % 2 == 0 else color2)
            screen.blit(sq_surf, (x + i, y + j))

def main():
    pasta_do_projeto = os.path.dirname(os.path.abspath(__file__))
    pasta_de_backups = r"C:\Users\pyetr\OneDrive\Desktop\unitypy\backups"

    fazer_backup(pasta_do_projeto, pasta_de_backups)

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Just Another Generic Clicker Game, But With References")

    FONT = pygame.font.SysFont(None, 48)
    SMALL_FONT = pygame.font.SysFont(None, 32)
    TEXT_COLOR_SCORE = (40, 40, 60)
    TEXT_COLOR_INFO = (60, 60, 80)

    button = AnimatedButton(WIDTH // 2, HEIGHT // 2, 200, 200,
                            "https://minecraft.wiki/images/Enchanted_Book.gif?b21c4")

    score_manager = ScoreManager()
    score = score_manager.load_score()

    clock = pygame.time.Clock()

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
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
        draw_score_box(screen, box_x, box_y, box_w, box_h)

        score_text = FONT.render(f"Pontos: {score}", True, TEXT_COLOR_SCORE)
        screen.blit(score_text, (box_x + 15, box_y + 8))

        info_text = SMALL_FONT.render("Pressione R para resetar", True, TEXT_COLOR_INFO)
        screen.blit(info_text, (box_x + 15, box_y + 35))

        pygame.display.flip()
        clock.tick(60)

    score_manager.save_score(score)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
