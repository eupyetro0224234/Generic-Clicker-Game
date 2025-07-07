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
from upgrades import UpgradeMenu

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
    FONT_POINTS = pygame.font.SysFont(None, 40)
    TEXT_COLOR_SCORE = (40, 40, 60)

    button = AnimatedButton(WIDTH // 2, HEIGHT // 2, 200, 200,
                            "https://minecraft.wiki/images/Enchanted_Book.gif?b21c4")

    score_manager = ScoreManager()
    score, controls_visible, saved_achievements, saved_upgrades = score_manager.load_data()

    def loading_callback(percent, message):
        loading_screen.draw(percent, message)

    config_menu = ConfigMenu(screen, WIDTH, HEIGHT, loading_callback=loading_callback)
    config_menu.controls_menu.visible = controls_visible

    tracker = AchievementTracker(screen)
    tracker.load_unlocked(saved_achievements)

    upgrade_menu = UpgradeMenu(screen, WIDTH, HEIGHT)
    upgrade_menu.load_upgrades(saved_upgrades)

    # Adiciona ícone extra para o menu principal (ícone upgrades)
    config_menu.add_extra_icon(upgrade_menu.get_icon_rect(), upgrade_menu.toggle_visibility)

    click_effects = []

    clock = pygame.time.Clock()
    running = True

    while running:
        mouse_pos = pygame.mouse.get_pos()

        # Fade out do exit_handler
        if config_menu.exit_handler.fading_out:
            if config_menu.exit_handler.update_fade_out():
                pygame.display.flip()
                clock.tick(60)
                continue

        for event in pygame.event.get():
            # Diálogo sair
            if config_menu.exit_handler.active:
                config_menu.exit_handler.handle_event(event)
                continue

            # Submenus configuração
            if config_menu.settings_menu.visible:
                if config_menu.settings_menu.handle_event(event):
                    continue

            if config_menu.controls_menu.visible:
                if config_menu.controls_menu.handle_event(event):
                    continue

            if config_menu.achievements_menu.visible:
                if config_menu.achievements_menu.handle_event(event):
                    continue

            # Submenu upgrades
            score, purchased = upgrade_menu.handle_event(event, score)
            upgrade_menu.purchased = purchased

            # Menu principal trata evento
            if config_menu.handle_event(event):
                continue

            # Eventos principais
            if event.type == pygame.QUIT:
                config_menu.exit_handler.start()
                continue

            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Só permite clicar no botão se menus Config e Conquistas estiverem fechados e upgrades também
                if not (config_menu.settings_menu.visible or config_menu.achievements_menu.visible or upgrade_menu.visible):
                    if config_menu.settings_menu.is_click_allowed(event.button):
                        if button.is_clicked(event.pos):
                            button.click()
                            score += upgrade_menu.get_bonus()  # Aplica bônus upgrades
                            click_effects.append(ClickEffect(event.pos[0], event.pos[1], f"+{upgrade_menu.get_bonus()}"))
                            tracker.check_unlock(score)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    score = 0
                    upgrade_menu.reset_upgrades()
                    tracker.unlocked.clear()

                elif event.key == pygame.K_ESCAPE:
                    # ESC fecha menus abertos incluindo upgrades
                    if config_menu.exit_handler.active:
                        config_menu.exit_handler.active = False
                    elif config_menu.settings_menu.visible:
                        config_menu.settings_menu.visible = False
                    elif config_menu.controls_menu.visible:
                        config_menu.controls_menu.visible = False
                    elif config_menu.achievements_menu.visible:
                        config_menu.achievements_menu.visible = False
                    elif upgrade_menu.visible:
                        upgrade_menu.visible = False
                    elif config_menu.is_open:
                        config_menu.is_open = False

        # Desenha fundo
        draw_background(screen)

        # Desenha quantidade de pontos acima do botão (centralizado horizontalmente)
        points_text = FONT_POINTS.render(str(score), True, TEXT_COLOR_SCORE)
        points_rect = points_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 130))
        screen.blit(points_text, points_rect)

        # Desenha botão de click
        button.draw(screen)

        # Caixa de score à esquerda inferior (pode manter se quiser)
        # box_x, box_y = 20, HEIGHT - 80
        # box_w, box_h = 220, 60
        # score_manager.draw_score_box(screen, box_x, box_y, box_w, box_h)
        # score_text = FONT.render(f"Pontos: {score}", True, TEXT_COLOR_SCORE)
        # score_rect = score_text.get_rect(center=(box_x + box_w // 2, box_y + box_h // 2))
        # screen.blit(score_text, score_rect)

        # Desenha menu upgrades (ícone + painel)
        upgrade_menu.draw(score)

        # Desenha ícone e menus abertos do menu principal
        config_menu.draw_icon()
        config_menu.draw()

        # Desenha notificação de conquistas
        tracker.draw_popup()

        # Atualiza e desenha efeitos de clique
        for effect in click_effects[:]:
            effect.update()
            effect.draw(screen)
            if effect.finished:
                click_effects.remove(effect)

        # Atualiza conquistas no menu
        config_menu.achievements_menu.unlocked = tracker.unlocked
        config_menu.achievements_menu.achievements = tracker.achievements

        pygame.display.flip()
        clock.tick(60)

    # Salva dados ao sair
    score_manager.save_data(score, config_menu.controls_menu.visible, list(tracker.unlocked), list(upgrade_menu.purchased))

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
