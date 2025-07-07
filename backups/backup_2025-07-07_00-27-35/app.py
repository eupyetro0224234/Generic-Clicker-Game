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
    upgrade_menu = UpgradeMenu(screen, 20, 90, 200)
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

        for event in pygame.event.get():
            # diálogo de saída
            if config_menu.exit_handler.active:
                config_menu.exit_handler.handle_event(event)
                continue

            # submenus: Configurações, Controles, Conquistas
            if config_menu.settings_menu.visible and config_menu.settings_menu.handle_event(event):
                continue
            if config_menu.controls_menu.visible and config_menu.controls_menu.handle_event(event):
                continue
            if config_menu.achievements_menu.visible and config_menu.achievements_menu.handle_event(event):
                continue

            # upgrade menu trata clique no seu ícone (passando o score)
            if upgrade_menu.handle_event(event, score):
                continue

            # menu principal
            if config_menu.handle_event(event):
                continue

            # fechar janela
            if event.type == pygame.QUIT:
                config_menu.exit_handler.start()
                continue

            # clique no botão principal
            if event.type == pygame.MOUSEBUTTONDOWN:
                # só processa clique se:
                # - o tipo de clique está permitido em Configurações
                # - e NÃO há menu de Configurações ou Conquistas abertos
                if (config_menu.settings_menu.is_click_allowed(event.button)
                    and not (config_menu.settings_menu.visible or
                             config_menu.achievements_menu.visible)):
                    if button.is_clicked(event.pos):
                        button.click()
                        # soma pontos considerando bônus dos upgrades
                        score += upgrade_menu.get_bonus()
                        click_effects.append(ClickEffect(event.pos[0], event.pos[1], f"+{upgrade_menu.get_bonus()}"))
                        tracker.check_unlock(score)

            # reset de pontos
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                score = 0
                for ach in tracker.achievements:
                    ach.unlocked = False
                tracker.unlocked.clear()
                upgrade_menu.reset_upgrades()

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

        # desenha upgrade menu (ícone e painel, se visível)
        upgrade_menu.draw()

        # desenha menus
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
