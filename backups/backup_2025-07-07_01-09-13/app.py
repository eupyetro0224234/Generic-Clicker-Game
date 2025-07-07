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

    # --- ConfigMenu e visibilidade inicial ---
    config_menu = ConfigMenu(screen, WIDTH, HEIGHT, loading_callback=loading.draw)
    config_menu.controls_menu.visible = controls_visible

    # --- AchievementTracker e conquistas carregadas ---
    tracker = AchievementTracker(screen)
    tracker.load_unlocked(saved_achievements)

    # --- UpgradeMenu posicionado no canto superior esquerdo ---
    upgrade_menu = UpgradeMenu(screen, 20, 90, 220)
    upgrade_menu.load_upgrades(saved_upgrades)

    click_effects = []

    running = True
    while running:
        # --- Fade-out de saída se ativo ---
        if config_menu.exit_handler.fading_out:
            if config_menu.exit_handler.update_fade_out():
                pygame.display.flip()
                clock.tick(60)
                continue

        for event in pygame.event.get():
            # 1) Se diálogo de saída ativo
            if config_menu.exit_handler.active:
                config_menu.exit_handler.handle_event(event)
                continue

            # 2) Fechar janela
            if event.type == pygame.QUIT:
                config_menu.exit_handler.start()
                continue

            # 3) ConfigMenu trata primeiro (ícone + submenus)
            if config_menu.handle_event(event):
                continue

            # 4) UpgradeMenu trata em seguida (ícone + compras)
            res = upgrade_menu.handle_event(event, score)
            if isinstance(res, tuple):
                score, _ = res
                continue
            elif res:
                continue

            # 5) Botão principal por último
            if button.handle_event(event):
                # sempre adicionar bônus e efeito de clique
                score += upgrade_menu.get_bonus()
                click_effects.append(ClickEffect(event.pos[0], event.pos[1], "+1"))
                tracker.check_unlock(score)
                continue

            # 6) Reset de pontos
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                score = 0
                for ach in tracker.achievements:
                    ach.unlocked = False
                tracker.unlocked.clear()
                upgrade_menu.purchased.clear()
                continue

        # --- Sincroniza conquistas para o ConfigMenu ---
        config_menu.achievements_menu.tracker = tracker
        config_menu.achievements_menu.achievements = tracker.achievements
        config_menu.achievements_menu.unlocked = tracker.unlocked

        # --- Desenho na tela ---
        draw_background(screen)
        button.draw(screen)

        # Caixa de pontuação
        bx, by, bw, bh = 20, 20, 220, 60
        score_manager.draw_score_box(screen, bx, by, bw, bh)
        score_surf = FONT.render(f"Pontos: {score}", True, TEXT_COLOR_SCORE)
        screen.blit(score_surf, score_surf.get_rect(center=(bx + bw//2, by + bh//2)))

        # Desenha upgrade menu e ícone de configurações
        upgrade_menu.draw(score)
        config_menu.draw_icon()
        config_menu.draw()

        # Popup de conquista
        tracker.draw_popup()

        # Efeitos de clique
        for eff in click_effects[:]:
            eff.update()
            eff.draw(screen)
            if eff.finished:
                click_effects.remove(eff)

        pygame.display.flip()
        clock.tick(60)

        # --- Salva progresso a cada frame ---
        score_manager.save_data(
            score,
            config_menu.controls_menu.visible,
            list(tracker.unlocked),
            upgrade_menu.purchased
        )

    # --- Salvamento final ---
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
