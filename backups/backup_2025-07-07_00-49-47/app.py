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

    # Sobrescrevendo is_clicked para debug
    original_is_clicked = button.is_clicked
    def debug_is_clicked(mouse_pos):
        result = original_is_clicked(mouse_pos)
        print(f"is_clicked chamado: mouse_pos={mouse_pos}, resultado={result}, rect={button.rect}")
        return result
    button.is_clicked = debug_is_clicked

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
    upgrade_menu = UpgradeMenu(screen, 20, 90, 220)  # adiciona largura inicial (220)
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

            # Fechar menus com ESC — prioriza ControlsMenu
            if config_menu.controls_menu.visible:
                if config_menu.controls_menu.handle_event(event):
                    continue

            if config_menu.settings_menu.visible:
                if config_menu.settings_menu.handle_event(event):
                    continue

            if config_menu.achievements_menu.visible:
                if config_menu.achievements_menu.handle_event(event):
                    continue

            # fechar janela principal
            if event.type == pygame.QUIT:
                config_menu.exit_handler.start()
                continue
                
            # reset de pontos
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                score = 0
                for ach in tracker.achievements:
                    ach.unlocked = False
                tracker.unlocked.clear()
                # Corrigindo: UpgradeMenu não tinha reset_upgrades, vamos limpar purchased
                upgrade_menu.purchased.clear()
                continue

            # Processa cliques apenas se não está em diálogo de saída
            if event.type == pygame.MOUSEBUTTONDOWN:
                print(f"Clique detectado em {event.pos}, botão mouse: {event.button}")

                event_handled = False
                
                # Verifica menus na ordem inversa de prioridade (do mais "na frente" para o mais "atrás")
                if config_menu.settings_menu.visible and config_menu.settings_menu.handle_event(event):
                    event_handled = True
                if config_menu.controls_menu.visible and config_menu.controls_menu.handle_event(event):
                    event_handled = True
                if config_menu.achievements_menu.visible and config_menu.achievements_menu.handle_event(event):
                    event_handled = True
                
                # upgrade menu retorna True se o evento foi tratado e novo score (tuple)
                result = upgrade_menu.handle_event(event, score)
                if isinstance(result, tuple):
                    score, purchased = result
                    upgrade_menu.purchased = purchased
                    event_handled = True
                
                if config_menu.handle_event(event):
                    event_handled = True
                
                if not event_handled:
                    button._update_rect()  # garante que o rect está correto
                    print(f"Verificando clique no botão...")
                    if config_menu.settings_menu.is_click_allowed(event.button) and button.is_clicked(event.pos):
                        print("Clique no botão detectado!")
                        button.click()
                        bonus = upgrade_menu.get_bonus()
                        score += bonus
                        print(f"Score incrementado por {bonus}. Novo score: {score}")
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
        upgrade_menu.y = by + bh + 10  # margem de 10 px
        upgrade_menu.width = bw  # mesma largura da caixa

        upgrade_menu.draw(score)  # desenha o upgrade menu

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

        # salva dados em cada loop
        score_manager.save_data(
            score,
            config_menu.controls_menu.visible,
            list(tracker.unlocked),
            upgrade_menu.purchased  # salvo lista de upgrades comprados
        )

    # salvamento final
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
