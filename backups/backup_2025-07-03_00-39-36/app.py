import pygame
import sys
import os
from backup import fazer_backup  # importa a função do backup.py
from background import draw_background, WIDTH, HEIGHT  # seu background

def main():
    # Define as pastas do projeto e backup
    pasta_do_projeto = os.path.dirname(os.path.abspath(__file__))
    pasta_de_backups = r"C:\Users\pyetr\OneDrive\Desktop\unitypy\backups"  # ajuste para dentro do seu repo!

    # Faz backup ao iniciar
    fazer_backup(pasta_do_projeto, pasta_de_backups)

    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Jogo Clicker Simples")

    FONT = pygame.font.SysFont(None, 48)
    BUTTON_COLOR = (70, 130, 180)
    BUTTON_HOVER_COLOR = (100, 160, 210)
    TEXT_COLOR = (255, 255, 255)

    def draw_button(screen, rect, text, mouse_pos):
        color = BUTTON_HOVER_COLOR if rect.collidepoint(mouse_pos) else BUTTON_COLOR
        pygame.draw.rect(screen, color, rect)
        txt_surf = FONT.render(text, True, TEXT_COLOR)
        txt_rect = txt_surf.get_rect(center=rect.center)
        screen.blit(txt_surf, txt_rect)

    score = 0
    clock = pygame.time.Clock()
    button_rect = pygame.Rect(WIDTH//2 - 75, HEIGHT//2 - 40, 150, 80)

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()

        draw_background(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    score += 1
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    score = 0

        draw_button(screen, button_rect, "Clique!", mouse_pos)

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
