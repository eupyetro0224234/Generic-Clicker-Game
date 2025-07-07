import pygame
import sys
import os
from backup import fazer_backup
from background import draw_background, WIDTH, HEIGHT
from button import AnimatedButton
from score_manager import ScoreManager
from menu import ConfigMenu

class ClickEffect:
    def __init__(self, x, y, text="+1 pontos"):
        self.x = x
        self.y = y
        self.text = text
        self.alpha = 255
        self.dy = -0.5  # movimento vertical para cima mais suave e lento
        self.font = pygame.font.SysFont(None, 32)
        self.finished = False
        # Pré-renderiza o texto para evitar recriação todo frame
        self.text_surface = self.font.render(self.text, True, (255, 100, 100))

    def update(self):
        self.y += self.dy
        self.alpha -= 3  # decaimento mais lento para maior fluidez
        if self.alpha <= 0:
            self.alpha = 0
            self.finished = True

    def draw(self, screen):
        if self.alpha > 0:
            # Usa uma cópia para ajustar alpha sem recriar toda hora
            surface = self.text_surface.copy()
            surface.set_alpha(self.alpha)
            screen.blit(surface, (self.x, self.y))

def main():
    pasta_do_projeto = os.path.dirname(os.path.abspath(__file__))
    pasta_de_backups = os.path.join(pasta_do_projeto, "backups")
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

    config_menu = ConfigMenu(screen, WIDTH, HEIGHT)
    config_menu.controls_menu.visible = controls_visible

    click_effects = []

    clock = pygame.time.Clock()
    running = True
    while running:
        dt = clock.tick(60) / 1000  # delta time em segundos (não obrigatório mas útil p/ futuros ajustes)
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if config_menu.handle_event(event):
                continue  # evento consumido pelo menu, ignora o resto
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if config_menu.settings_menu.is_click_allowed(event.button):
                    if button.is_clicked(event.pos):
                        button.click()
                        score += 1
                        effect = ClickEffect(event.pos[0], event.pos[1], text="+1 pontos")
                        click_effects.append(effect)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    score = 0

        draw_background(screen)
        button.draw(screen)

        # Atualiza e desenha os efeitos de clique
        for effect in click_effects[:]:
            effect.update()
            effect.draw(screen)
            if effect.finished:
                click_effects.remove(effect)

        box_x, box_y = 20, 20
        box_w, box_h = 220, 60
        score_manager.draw_score_box(screen, box_x, box_y, box_w, box_h)

        score_text = FONT.render(f"ponto: {score}", True, TEXT_COLOR_SCORE)
        score_rect = score_text.get_rect(center=(box_x + box_w // 2, box_y + box_h // 2))
        screen.blit(score_text, score_rect)

        config_menu.draw_icon()
        config_menu.draw()

        pygame.display.flip()

    score_manager.save_data(score, config_menu.controls_menu.visible)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
