import pygame
import sys
import os
from backup import fazer_backup
from background import draw_background, WIDTH, HEIGHT
from button import AnimatedButton

def main():
    pasta_do_projeto = os.path.dirname(os.path.abspath(__file__))
    pasta_de_backups = r"C:\Users\pyetr\OneDrive\Desktop\unitypy\backups"  # ajuste seu caminho

    # Faz backup ANTES de iniciar o pygame
    fazer_backup(pasta_do_projeto, pasta_de_backups)

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Jogo Clicker com botão animado")

    FONT = pygame.font.SysFont(None, 48)
    TEXT_COLOR = (255, 255, 255)

    # Botão centralizado e maior (200x200)
    button = AnimatedButton(WIDTH // 2, HEIGHT // 2, 200, 200,
                            "https://minecraft.wiki/images/Enchanted_Book.gif?b21c4")

    score = 0
    clock = pygame.time.Clock()

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button.is_clicked(event.pos):
                    button.click()  # animação ao clicar
                    score += 1
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    score = 0

        draw_background(screen)
        button.draw(screen)

        score_surf = FONT.render(f"Pontos: {score}", True, TEXT_COLOR)
        screen.blit(score_surf, (20, 20))

        info_surf = pygame.font.SysFont(None, 24).render("Pressione R para resetar", True, TEXT_COLOR)
        screen.blit(info_surf, (20, HEIGHT - 30))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
