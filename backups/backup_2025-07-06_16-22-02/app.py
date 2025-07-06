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
from conquistas import AchievementTracker

def main():
    # Pastas e backup
    pasta_do_projeto = os.path.dirname(os.path.abspath(__file__))
    pasta_de_backups = os.path.join(pasta_do_projeto, "backups")
    fazer_backup(pasta_do_projeto, pasta_de_backups)

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Just Another Generic Clicker Game, But With References")

    loading_screen = LoadingScreen(screen, WIDTH, HEIGHT)

    # Tela de loading com mensagens
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

    # Botão com GIF
    button = AnimatedButton(WIDTH // 2, HEIGHT // 2, 200, 200,
                            "https://minecraft.wiki/images/Enchanted_Book.gif?b21c4")

    # Gerenciador de score e carregamento inicial
    score_manager = ScoreManager()
    score, controls_visible, saved_achievements = score_manager.load_data()

    def loading_callback(percent, message):
        loading_screen.draw(percent, message)

    # Menus e tracker
    config_menu = ConfigMenu(screen, WIDTH, HEIGHT, loading_callback=loading_callback)
    config_menu.controls_menu.visible = controls_visible

    tracker = AchievementTracker(screen)
    tracker.load_unlocked(saved_achievements)

    click_effects = []

    clock = pygame.time.Clock()
    running = True

    while running:
        mouse_pos = pygame.mouse.get_pos()

        # Fade out do exit_handler para saída suave
        if config_menu.exit_handler.fading_out:
            if config_menu.exit_handler.update_fade_out():
                pygame.display.flip()
                clock.tick(60)
                continue

        for event in pygame.event.get():
            # Se diálogo de sair ativo, deixa ele tratar eventos primeiro
            if config_menu.exit_handler.active:
                config_menu.exit_handler.handle_event(event)
                continue

            # Menus abertos tratam eventos primeiro
            if config_menu.settings_menu.visible:
                if config_menu.settings_menu.handle_event(event):
                    continue

            if config_menu.controls_menu.visible:
                if config_menu.controls_menu.handle_event(event):
                    continue

            if config_menu.achievements_menu.visible:
                if config_menu.achievements_menu.handle_event(event):
                    continue

            # Se menu principal tratar evento, pula
            if config_menu.handle_event(event):
                continue

            # Eventos gerais
            if event.type == pygame.QUIT:
                config_menu.exit_handler.start()
                continue

            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Só permite clicar para subir pontos se menus Configurações e Conquistas fechados
                if not (config_menu.settings_menu.visible or config_menu.achievements_menu.visible):
                    # Removido uso de config_menu.settings_menu.is_click_allowed porque não existe
                    # Permitir clique normal
                    if button.is_clicked(event.pos) and event.button == 1:
                        button.click()
                        score += 1
                        click_effects.append(ClickEffect(event.pos[0], event.pos[1], "+1"))
                        tracker.check_unlock(score)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    score = 0

        # Desenha tela principal
        draw_background(screen)
        button.draw(screen)

        # Caixa de pontuação
        box_x, box_y = 20, 20
        box_w, box_h = 220, 60
        score_manager.draw_score_box(screen, box_x, box_y, box_w, box_h)

        score_text = FONT.render(f"Pontos: {score}", True, TEXT_COLOR_SCORE)
        score_rect = score_text.get_rect(center=(box_x + box_w // 2, box_y + box_h // 2))
        screen.blit(score_text, score_rect)

        # Se tiver upgrades, desenhe o ícone e menu (ajuste para seu código)
        if hasattr(config_menu, "upgrades_menu") and config_menu.upgrades_menu:
            config_menu.upgrades_menu.draw_icon()
            config_menu.upgrades_menu.draw()

        # Desenha ícone do menu e menus abertos
        config_menu.draw_icon()
        config_menu.draw()

        # Desenha popup de conquista
        tracker.draw_popup()

        # Atualiza e desenha efeitos de clique
        for effect in click_effects[:]:
            effect.update()
            effect.draw(screen)
            if effect.finished:
                click_effects.remove(effect)

        # Sincroniza conquistas desbloqueadas no menu
        config_menu.achievements_menu.unlocked = tracker.unlocked
        config_menu.achievements_menu.achievements = tracker.achievements

        pygame.display.flip()
        clock.tick(60)

    # Salva dados ao fechar o jogo
    score_manager.save_data(score, config_menu.controls_menu.visible, list(tracker.unlocked))

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
