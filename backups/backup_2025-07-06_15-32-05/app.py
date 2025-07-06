import pygame
import sys
import os
import time
from backup import fazer_backup
from background import draw_background, WIDTH, HEIGHT
from button import AnimatedButton
from score_manager import ScoreManager
from menu import ConfigMenu
from loading import LoadingScreen
from click_effect import ClickEffect
from conquistas import AchievementsMenu

def main():
    # --- Backup inicial ---
    pasta_do_projeto = os.path.dirname(os.path.abspath(__file__))
    pasta_de_backups = os.path.join(pasta_do_projeto, "backups")
    fazer_backup(pasta_do_projeto, pasta_de_backups)

    # --- Inicialização Pygame ---
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Just Another Generic Clicker Game, But With References")
    clock = pygame.time.Clock()

    # --- Loading Screen ---
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
    TEXT_COLOR_SCORE = (120, 0, 60)

    # --- Botão principal ---
    button = AnimatedButton(
        WIDTH // 2, HEIGHT // 2, 200, 200,
        "https://minecraft.wiki/images/Enchanted_Book.gif?b21c4"
    )

    # --- ScoreManager: carrega score, controles e conquistas ---
    score_manager = ScoreManager()
    score, controls_visible, loaded_achievements = score_manager.load_data()

    # --- Configuração dos menus ---
    def loading_cb(p, m):
        loading.draw(p, m)

    config_menu = ConfigMenu(screen, WIDTH, HEIGHT, loading_callback=loading_cb)
    config_menu.controls_menu.visible = controls_visible

    achievements_menu = AchievementsMenu(screen, WIDTH, HEIGHT)
    achievements_menu.achievements = loaded_achievements[:]  # aplica conquistas carregadas
    config_menu.achievements_menu = achievements_menu

    click_effects = []

    # Ao desbloquear algo, salvamos imediatamente
    def try_unlock(id, display_name):
        if id not in achievements_menu.achievements:
            achievements_menu.add_achievement(display_name)
            score_manager.save_data(
                score,
                config_menu.controls_menu.visible,
                achievements_menu.achievements
            )

    running = True
    while running:
        # Se fade-out de saída está ativo, executa e continua
        if config_menu.exit_handler.fading_out:
            if config_menu.exit_handler.update_fade_out():
                pygame.display.flip()
                clock.tick(60)
                continue

        for event in pygame.event.get():
            # Se diálogo sair estiver ativo, deleto eventos para ele
            if config_menu.exit_handler.active:
                config_menu.exit_handler.handle_event(event)
                continue

            # Submenus primeiro
            if config_menu.settings_menu.visible and config_menu.settings_menu.handle_event(event):
                continue
            if config_menu.controls_menu.visible and config_menu.controls_menu.handle_event(event):
                continue
            if achievements_menu.visible and achievements_menu.handle_event(event):
                continue

            # Menu principal
            if config_menu.handle_event(event):
                continue

            # Se clicar no X da janela
            if event.type == pygame.QUIT:
                # salva antes de iniciar fade
                score_manager.save_data(
                    score,
                    config_menu.controls_menu.visible,
                    achievements_menu.achievements
                )
                config_menu.exit_handler.start()
                continue

            # Clique no botão do jogo
            if event.type == pygame.MOUSEBUTTONDOWN:
                if config_menu.settings_menu.is_click_allowed(event.button):
                    if button.is_clicked(event.pos):
                        button.click()
                        score += 1
                        click_effects.append(ClickEffect(event.pos[0], event.pos[1], "+1"))
                        # desbloqueios de exemplo
                        if score == 1:
                            try_unlock("first_click", "Primeiro Clique")
                        if score == 10:
                            try_unlock("ten_clicks", "10 Cliques")

            # Resetar pontuação
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                score = 0
                try_unlock("reset_score", "Recomeço")

        # --- Desenho da tela principal ---
        draw_background(screen)
        button.draw(screen)

        # Caixa de score rosa claro
        bx, by, bw, bh = 20, 20, 260, 60
        score_manager.draw_score_box(screen, bx, by, bw, bh)
        txt = FONT.render(f"Pontos: {score}", True, TEXT_COLOR_SCORE)
        r = txt.get_rect(center=(bx + bw//2, by + bh//2))
        screen.blit(txt, r)

        # Desenha menus
        config_menu.draw_icon()
        config_menu.draw()

        # Desenha menu de conquistas (se aberto) e alerta
        achievements_menu.draw()

        # Desenha efeitos de clique
        for eff in click_effects[:]:
            eff.update()
            eff.draw(screen)
            if eff.finished:
                click_effects.remove(eff)

        pygame.display.flip()
        clock.tick(60)

    # --- Salvamento final (caso chegue ao fim do loop) ---
    score_manager.save_data(
        score,
        config_menu.controls_menu.visible,
        achievements_menu.achievements
    )
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
