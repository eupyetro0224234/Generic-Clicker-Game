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
        ("Concluído! Iniciando o jogo", 100)
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

    click_effects = []

    clock = pygame.time.Clock()
    running = True

    while running:
        mouse_pos = pygame.mouse.get_pos()

        # Atualiza fade out do exit_handler (fecha o jogo com fade)
        if config_menu.exit_handler.fading_out:
            if config_menu.exit_handler.update_fade_out():
                pygame.display.flip()
                clock.tick(60)
                continue

        for event in pygame.event.get():
            # Se o diálogo de sair estiver ativo, deixa ele tratar os eventos
            if config_menu.exit_handler.active:
                config_menu.exit_handler.handle_event(event)
                continue

            # Se qualquer submenu (Configurações, Controles, Conquistas) estiver aberto, deixa ele tratar
            if config_menu.settings_menu.visible:
                if config_menu.settings_menu.handle_event(event):
                    continue

            if config_menu.controls_menu.visible:
                if config_menu.controls_menu.handle_event(event):
                    continue

            if hasattr(config_menu, "achievements_menu") and config_menu.achievements_menu.visible:
                if config_menu.achievements_menu.handle_event(event):
                    continue

            # Se o menu principal tratar o evento, pula para próximo evento
            if config_menu.handle_event(event):
                continue

            # Eventos principais
            if event.type == pygame.QUIT:
                config_menu.exit_handler.start()
                continue

            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Verifica se clique está permitido e se clicou no botão principal
                if config_menu.settings_menu.is_click_allowed(event.button):
                    if button.is_clicked(event.pos):
                        button.click()
                        score += 1
                        click_effects.append(ClickEffect(event.pos[0], event.pos[1], "+1"))

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    score = 0

        # Desenho da tela principal
        draw_background(screen)
        button.draw(screen)

        # Caixa do score
        box_x, box_y = 20, 20
        box_w, box_h = 220, 60
        score_manager.draw_score_box(screen, box_x, box_y, box_w, box_h)

        score_text = FONT.render(f"Pontos: {score}", True, TEXT_COLOR_SCORE)
        score_rect = score_text.get_rect(center=(box_x + box_w // 2, box_y + box_h // 2))
        screen.blit(score_text, score_rect)

        # Desenha o ícone do menu e menus abertos
        config_menu.draw_icon()
        config_menu.draw()

        # Atualiza e desenha efeitos de clique
        for effect in click_effects[:]:
            effect.update()
            effect.draw(screen)
            if effect.finished:
                click_effects.remove(effect)

        pygame.display.flip()
        clock.tick(60)

    # Salva score e estado do menu controles ao sair
    score_manager.save_data(score, config_menu.controls_menu.visible)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
