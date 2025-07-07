import pygame
import sys
import os
from backup import fazer_backup
from background import draw_background, WIDTH, HEIGHT
from button import AnimatedButton
from score_manager import ScoreManager
from menu import ConfigMenu
from loading import LoadingScreen, download_assets  # IMPORTANTE: download_assets para verificar/baixar assets
from click_effect import ClickEffect
from conquistas import AchievementTracker
from upgrades import UpgradeMenu
from console import Console
from exit_handler import ExitHandler

def main():
    pasta = os.path.dirname(os.path.abspath(__file__))
    fazer_backup(pasta, os.path.join(pasta, "backups"))

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Just Another Generic Clicker Game, But With References")
    clock = pygame.time.Clock()

    # Tela de loading com progresso real
    loading = LoadingScreen(screen, WIDTH, HEIGHT)

    # ** VERIFICA E BAIXA ASSETS ANTES DE CONTINUAR **
    download_assets(screen, WIDTH, HEIGHT)

    # Funções simulando carregamento real das etapas (substitua pelo carregamento real)
    def load_images():
        # Se precisar carregar imagens do AnimatedButton, faça aqui
        pass

    def init_menus():
        # Se tiver função real para carregar menus, coloque aqui
        pass

    def other_init():
        # Simule outra tarefa de inicialização, se quiser
        pass

    etapas = [
        ("Carregando imagens...", load_images),
        ("Inicializando menus...", init_menus),
        ("Quase lá...", other_init),
        ("Concluído! Iniciando o jogo", lambda: None),
    ]

    for i, (msg, func) in enumerate(etapas, start=1):
        func()  # executa a etapa real de carregamento
        pct = i / len(etapas) * 100
        loading.draw(pct, msg)
        # Processa eventos para janela não travar
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

    FONT = pygame.font.SysFont(None, 64)
    TEXT_COLOR_SCORE = (40, 40, 60)

    button = AnimatedButton(
        WIDTH // 2, HEIGHT // 2, 200, 200,
        "https://minecraft.wiki/images/Enchanted_Book.gif?b21c4"
    )

    score_manager = ScoreManager()
    score, controls_visible, saved_achievements, saved_upgrades = score_manager.load_data()

    config_menu = ConfigMenu(screen, WIDTH, HEIGHT, loading_callback=loading.draw)
    config_menu.controls_menu.visible = controls_visible

    tracker = AchievementTracker(screen)
    tracker.load_unlocked(saved_achievements)

    upgrade_menu = UpgradeMenu(screen, WIDTH, HEIGHT)
    upgrade_menu.load_upgrades(saved_upgrades)

    click_effects = []
    auto_click_counter = 0

    console = Console(screen, WIDTH, HEIGHT, on_exit_callback=config_menu.disable_console)
    console.visible = False

    exit_handler = ExitHandler(screen, WIDTH, HEIGHT)
    config_menu.exit_handler = exit_handler

    def get_score():
        return score
    def set_score(new_score):
        nonlocal score
        score = new_score

    console.set_score_accessors(get_score, set_score)
    config_menu.set_score_accessors(get_score, set_score)
    config_menu.achievements_menu.tracker = tracker
    config_menu.console_instance = console

    running = True
    while running:
        # Fade-out para sair
        if exit_handler.fading_out:
            if exit_handler.update_fade_out():
                pygame.display.flip()
                clock.tick(60)
                continue

        for event in pygame.event.get():
            # Prioridade: ExitHandler ativo
            if exit_handler.active:
                if exit_handler.handle_event(event):
                    if exit_handler.detected_console:
                        # Só ativa ao apertar Enter com texto == "console"
                        config_menu.enable_console()
                        tracker.unlock_secret("console")
                        exit_handler.detected_console = False
                        exit_handler.active = False
                    # Se texto inválido ou ESC, ExitHandler se torna inactive, sem abrir console
                continue

            # QUIT abre prompt de saída
            if event.type == pygame.QUIT:
                if not exit_handler.active and not exit_handler.fading_out:
                    exit_handler.start()
                continue

            # Teclas gerais
            if event.type == pygame.KEYDOWN:
                # R = reset completo (inclui upgrades)
                if event.key == pygame.K_r and not console.visible:
                    score = 0
                    tracker.unlocked.clear()
                    for ach in tracker.achievements:
                        ach.unlocked = False
                    upgrade_menu.reset_upgrades()
                    config_menu.enable_console()
                    continue

                # ESC fecha/minimiza console ou menus
                if event.key == pygame.K_ESCAPE:
                    if console.visible:
                        console.visible = False
                        continue
                    if exit_handler.active:
                        exit_handler.active = False
                        continue
                    if config_menu.settings_menu.visible:
                        config_menu.settings_menu.visible = False
                        continue
                    if config_menu.controls_menu.visible:
                        config_menu.controls_menu.visible = False
                        continue
                    if config_menu.achievements_menu.visible:
                        config_menu.achievements_menu.visible = False
                        continue
                    if upgrade_menu.visible:
                        upgrade_menu.visible = False
                        continue
                    if config_menu.is_open:
                        config_menu.is_open = False
                        continue

            # Eventos de submenus/configuração/console
            if config_menu.settings_menu.visible and config_menu.settings_menu.handle_event(event):
                continue
            if config_menu.controls_menu.visible and config_menu.controls_menu.handle_event(event):
                continue
            if config_menu.achievements_menu.visible and config_menu.achievements_menu.handle_event(event):
                continue
            if console.visible and console.handle_event(event):
                continue

            # Clique no upgrade icon ou opções
            if event.type == pygame.MOUSEBUTTONDOWN:
                prev_vis = upgrade_menu.visible
                new_score, _ = upgrade_menu.handle_event(event, score)
                if new_score != score or upgrade_menu.visible != prev_vis:
                    score = new_score
                    continue

                # Clique principal só se nenhum menu aberto
                button._update_rect()
                if not (
                    config_menu.settings_menu.visible
                    or config_menu.achievements_menu.visible
                    or console.visible
                    or exit_handler.active
                ):
                    if config_menu.settings_menu.is_click_allowed(event.button):
                        if button.is_clicked(event.pos):
                            button.click()
                            score += upgrade_menu.get_bonus()
                            tracker.check_unlock(score)
                            click_effects.append(
                                ClickEffect(event.pos[0], event.pos[1], f"+{upgrade_menu.get_bonus()}")
                            )
                            continue

            # Itens do ConfigMenu
            if config_menu.handle_event(event):
                continue

        # Atualiza conquistas
        config_menu.achievements_menu.achievements = tracker.achievements
        config_menu.achievements_menu.unlocked = tracker.unlocked

        # Desenho da tela
        draw_background(screen)
        button.draw(screen)

        # Auto-click múltiplo
        if upgrade_menu.auto_click_enabled():
            auto_click_counter += 1
            if auto_click_counter >= 40:
                auto_click_counter = 0
                bonus_auto = upgrade_menu.get_auto_click_bonus()
                score += bonus_auto
                tracker.check_unlock(score)
                click_effects.append(
                    ClickEffect(WIDTH // 2, HEIGHT // 2, f"+{bonus_auto} (Auto)")
                )

        # Desenha pontuação
        score_surf = FONT.render(str(score), True, TEXT_COLOR_SCORE)
        score_rect = score_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 140))
        screen.blit(score_surf, score_rect)

        # Desenha menus e efeitos
        upgrade_menu.draw(score)
        config_menu.draw_icon()
        config_menu.draw()
        if console.visible:
            console.draw()
        exit_handler.draw()
        tracker.draw_popup()

        for eff in click_effects[:]:
            eff.update()
            eff.draw(screen)
            if eff.finished:
                click_effects.remove(eff)

        pygame.display.flip()
        clock.tick(60)

        # Salva estado (upgrades agora é dict)
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
