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
from conquistas import AchievementTracker, AchievementsMenu

def main():
    # Backup
    pasta = os.path.dirname(os.path.abspath(__file__))
    fazer_backup(pasta, os.path.join(pasta, "backups"))

    # Pygame init
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Just Another Generic Clicker Game, But With References")
    clock = pygame.time.Clock()

    # Loading
    loading = LoadingScreen(screen, WIDTH, HEIGHT)
    for msg, pct in [
        ("Carregando imagens...", 50),
        ("Inicializando menus...", 80),
        ("Quase lá...", 95),
        ("Concluído! Iniciando o jogo", 100),
    ]:
        loading.draw(pct, msg)
        pygame.time.delay(700)

    FONT = pygame.font.SysFont(None, 48)
    TEXT_COLOR_SCORE = (40, 40, 60)

    button = AnimatedButton(WIDTH//2, HEIGHT//2, 200, 200,
                            "https://minecraft.wiki/images/Enchanted_Book.gif?b21c4")

    # ScoreManager
    mgr = ScoreManager()
    score, controls_vis, saved_achs = mgr.load_data()

    # Achievements
    tracker = AchievementTracker()
    tracker.load_unlocked(saved_achs)
    ach_menu = AchievementsMenu(screen, WIDTH, HEIGHT)
    ach_menu.unlocked = tracker.unlocked

    # Menus
    def cb(p,m): loading.draw(p,m)
    cfg = ConfigMenu(screen, WIDTH, HEIGHT, loading_callback=cb)
    cfg.controls_menu.visible = controls_vis
    cfg.achievements_menu = ach_menu

    effects = []

    while True:
        # fade-out
        if cfg.exit_handler.fading_out:
            if cfg.exit_handler.update_fade_out():
                pygame.display.flip()
                clock.tick(60)
                continue

        for e in pygame.event.get():
            if cfg.exit_handler.active:
                cfg.exit_handler.handle_event(e); continue

            if cfg.settings_menu.visible and cfg.settings_menu.handle_event(e):
                continue
            if cfg.controls_menu.visible and cfg.controls_menu.handle_event(e):
                continue
            if ach_menu.visible and ach_menu.handle_event(e):
                continue

            if cfg.handle_event(e):
                continue

            if e.type == pygame.QUIT:
                mgr.save_data(score, cfg.controls_menu.visible, list(tracker.unlocked))
                cfg.exit_handler.start()
                continue

            if e.type == pygame.MOUSEBUTTONDOWN:
                # impede clique se menus abertos
                if not (cfg.settings_menu.visible or ach_menu.visible):
                    if button.is_clicked(e.pos):
                        button.click()
                        score += 1
                        effects.append(ClickEffect(e.pos[0], e.pos[1], "+1"))
                        tracker.check_unlock(score)
                        ach_menu.unlocked = tracker.unlocked

            if e.type == pygame.KEYDOWN and e.key == pygame.K_r:
                score = 0
                tracker.unlocked.clear()
                ach_menu.unlocked = tracker.unlocked

        # Draw
        draw_background(screen)
        button.draw(screen)

        bx, by, bw, bh = 20, 20, 260, 60
        mgr.draw_score_box(screen, bx, by, bw, bh)
        txt = FONT.render(f"Pontos: {score}", True, TEXT_COLOR_SCORE)
        screen.blit(txt, txt.get_rect(center=(bx + bw//2, by + bh//2)))

        cfg.draw_icon()
        cfg.draw()
        ach_menu.draw()
        tracker.draw_popup(screen)

        for eff in effects[:]:
            eff.update(); eff.draw(screen)
            if eff.finished: effects.remove(eff)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
