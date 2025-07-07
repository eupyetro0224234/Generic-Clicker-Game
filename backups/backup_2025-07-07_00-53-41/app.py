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
from upgrades import UpgradeMenu  # importa o menu de upgrades

def main():
    # --- Backup inicial ---
    pasta = os.path.dirname(os.path.abspath(__file__))
    fazer_backup(pasta, os.path.join(pasta, "backups"))

    # --- Pygame init ---
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Just Another Generic Clicker Game, But With References")
    clock = pygame.time.Clock()

    # --- Loading screen ---
    loading = LoadingScreen(screen, WIDTH, HEIGHT)
    for msg, pct in [
        ("Carregando imagens...", 50),
        ("Inicializando menus...", 80),
        ("Quase lá...", 95),
        ("Concluído! Iniciando o jogo", 100),
    ]:
        loading.draw(pct, msg)
        pygame.time.delay(700)

    # --- Fontes e cores ---
    FONT = pygame.font.SysFont(None, 48)
    TEXT_COLOR_SCORE = (40, 40, 60)

    # --- Botão principal ---
    button = AnimatedButton(
        WIDTH // 2, HEIGHT // 2, 200, 200,
        "https://minecraft.wiki/images/Enchanted_Book.gif?b21c4"
    )

    # --- ScoreManager e dados iniciais ---
    score_manager = ScoreManager()
    score, controls_visible, saved_achievements, saved_upgrades = score_manager.load_data()

    # --- ConfigMenu e visibilidade dos controles ---
    config_menu = ConfigMenu(screen, WIDTH, HEIGHT, loading_callback=loading.draw)
    config_menu.controls_menu.visible = controls_visible

    # --- AchievementTracker e conquistas carregadas ---
    tracker = AchievementTracker(screen)
    tracker.load_unlocked(saved_achievements)

    # --- UpgradeMenu posicionado abaixo da pontuação ---
    upgrade_menu = UpgradeMenu(screen, 20, 90, 220)
    upgrade_menu.load_upgrades(saved_upgrades)

    click_effects = []

    running = True
    while running:
        # fade-out de saída
        if config_menu.exit_handler.fading_out:
            if config_menu.exit_handler.update_fade_out():
                pygame.display.flip()
                clock.tick(60)
                continue

        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            # diálogo de saída
            if config_menu.exit_handler.active:
                config_menu.exit_handler.handle_event(event)
                continue

            # fechar janela
            if event.type == pygame.QUIT:
                config_menu.exit_handler.start()
                continue
                
            # reset de pontos
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                score = 0
                for ach in tracker.achievements:
                    ach.unlocked = False
                tracker.unlocked.clear()
                upgrade_menu.purchased.clear()
                continue

            # Processa cliques apenas se não está em diálogo de saída
            if event.type == pygame.MOUSEBUTTONDOWN:
                event_handled = False

                # Verifica menus na ordem inversa de prioridade
                
                if config_menu.settings_menu.visible and config_menu.settings_menu.handle_event(event):
                    event_handled = True
                if config_menu.controls_menu.visible and config_menu.controls_menu.handle_event(event):
                    event_handled = True
                if config_menu.achievements_menu.visible and config_menu.achievements_menu.handle_event(event):
                    event_handled = True
                
                # Menu de upgrades
                # IMPORTANTE: handle_event retorna (score, purchased) ou False? Vamos adaptar para bool
                res = upgrade_menu.handle_event(event, score)
                if isinstance(res, tuple):
                    score, _ = res
                    event_handled = True
                elif res:
                    event_handled = True

                # Ícone de configurações
                if config_menu.handle_event(event):
                    event_handled = True

                # Se nenhum menu consumiu o clique, verifica o botão principal
                if not event_handled:
                    # Atualiza o rect do botão ANTES de verificar clique
                    button._update_rect()
                    # Debug (descomente se quiser):
                    # print(f"Botão área: {button.rect}, Clique em: {event.pos}")
                    if (config_menu.settings_menu.is_click_allowed(event.button)
                        and button.is_clicked(event.pos)):
                        button.click()
                        score += upgrade_menu.get_bonus()
                        click_effects.append(ClickEffect(event.pos[0], event.pos[1], "+1"))
                        tracker.check_unlock(score)

        # sincroniza conquistas no menu
        config_menu.achievements_menu.tracker = tracker
        config_menu.achievements_menu.achievements = tracker.achievements
        config_menu.achievements_menu.unlocked = tracker.unlocked

        # desenha background e botão
        draw_background(screen)
        button.draw(screen)

        # caixa de score
        bx, by, bw, bh = 20, 20, 220, 60
        score_manager.draw_score_box(screen, bx, by, bw, bh)
        score_surf = FONT.render(f"Pontos: {score}", True, TEXT_COLOR_SCORE)
        screen.blit(score_surf, score_surf.get_rect(center=(bx + bw//2, by + bh//2)))

        # posiciona o upgrade menu logo abaixo da pontuação
        upgrade_menu.x = bx
        upgrade_menu.y = by + bh + 10
        upgrade_menu.width = bw

        upgrade_menu.draw(score)

        # desenha menus e ícones
        config_menu.draw_icon()
        config_menu.draw()

        # popup de conquista
        tracker.draw_popup()

        # efeitos de clique
        for eff in click_effects[:]:
            eff.update()
            eff.draw(screen)
            if eff.finished:
                click_effects.remove(eff)

        pygame.display.flip()
        clock.tick(60)

        # salva dados a cada frame
        score_manager.save_data(
            score,
            config_menu.controls_menu.visible,
            list(tracker.unlocked),
            upgrade_menu.purchased
        )

    # salvamento final (opcional, já salva a cada frame)
    score_manager.save_data(
        score,
        config_menu.controls_menu.visible,
        list(tracker.unlocked),
        upgrade_menu.purchased
    )

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
