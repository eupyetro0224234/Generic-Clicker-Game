import pygame
import sys
import os
from backup import fazer_backup
from background import draw_background, WIDTH, HEIGHT

def main():
    # Pastas do projeto e backup
    pasta_do_projeto = os.path.dirname(os.path.abspath(__file__))
    pasta_de_backups = r"C:\Users\pyetr\OneDrive\Desktop\unitypy\backups"  # ajuste seu caminho

    # Faz backup ao iniciar
    fazer_backup(pasta_do_projeto, pasta_de_backups)

    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Jogo Clicker Simples")

    FONT = pygame.font.SysFont(None, 48)
    TEXT_COLOR = (255, 255, 255)

    score = 0
    clock = pygame.time.Clock()

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()

        draw_background(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Note que o clique no botão animado agora vai ser tratado no seu arquivo button.py
            # Se quiser, pode importar e usar a classe AnimatedButton e tratar clique aqui
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    score = 0

        # Aqui só mostramos a pontuação e texto explicativo
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
