import pygame
import os

class Console:
    def __init__(self, screen, width, height, on_exit_callback=None, on_open_callback=None, tracker=None, config_menu=None, upgrade_manager=None):
        self.screen = screen
        self.width = width
        self.height = height
        self.font = pygame.font.SysFont("Consolas", 24)
        self.visible = False
        self.input_text = ""
        self.max_lines = 20
        self.lines = []

        self.get_score = None
        self.set_score = None

        self.on_exit_callback = on_exit_callback
        self.on_open_callback = on_open_callback

        self.tracker = tracker
        self.config_menu = config_menu
        self.upgrade_manager = upgrade_manager

    def set_score_accessors(self, get_func, set_func):
        self.get_score = get_func
        self.set_score = set_func

    def open(self):
        self.visible = True
        self.lines = ["Console ativado!", "Digite comandos..."]
        self.input_text = ""
        if self.on_open_callback:
            self.on_open_callback()
        if self.tracker:
            self.tracker.unlock_secret("console")

    def close(self):
        self.visible = False
        if self.on_exit_callback:
            self.on_exit_callback()

    def handle_event(self, event):
        if not self.visible:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]

            elif event.key == pygame.K_RETURN:
                self.execute_command(self.input_text)
                self.input_text = ""

            elif event.key == pygame.K_ESCAPE:
                self.close()

            else:
                if len(event.unicode) == 1 and event.unicode.isprintable():
                    self.input_text += event.unicode

            return True

        return False

    def execute_command(self, command):
        cmd = command.strip().lower()
        self.lines = []

        if cmd == "help":
            self.lines.extend([
                "Comandos disponíveis:",
                "add points <n>",
                "remove points <n>",
                "reset achievements",
                "reset points",
                "reset upgrades",
                "reset -a",
                "help",
                "exit"
            ])

        elif cmd.startswith("add points"):
            parts = cmd.split()
            if len(parts) == 3 and parts[2].isdigit():
                n = int(parts[2])
                if self.get_score and self.set_score:
                    new_score = self.get_score() + n
                    self.set_score(new_score)
                    self.lines.append(f"Adicionado {n} pontos. Pontos: {new_score}")
                else:
                    self.lines.append("Erro: função de pontuação não configurada.")
            else:
                self.lines.append("Uso: add points <n>")

        elif cmd.startswith("remove points"):
            parts = cmd.split()
            if len(parts) == 3 and parts[2].isdigit():
                n = int(parts[2])
                if self.get_score and self.set_score:
                    new_score = max(0, self.get_score() - n)
                    self.set_score(new_score)
                    self.lines.append(f"Removido {n} pontos. Pontos: {new_score}")
                else:
                    self.lines.append("Erro: função de pontuação não configurada.")
            else:
                self.lines.append("Uso: remove points <n>")

        elif cmd == "reset upgrades":
            self.lines.append("Resetando upgrades...")
            if self.upgrade_manager:
                self.upgrade_manager.reset_upgrades()
                self.lines.append("Upgrades resetados com sucesso!")
            else:
                self.lines.append("Erro: upgrade_manager não configurado.")

        elif cmd.startswith("reset"):
            parts = cmd.split()
            if len(parts) == 2:
                if parts[1] == "achievements":
                    self.lines.append("Conquistas resetadas.")
                    self.reset_achievements()
                    if self.config_menu and self.tracker:
                        self.config_menu.achievements_menu.update(self.tracker)
                elif parts[1] == "points":
                    self.set_score(0)
                    self.lines.append("Pontos resetados.")
                elif parts[1] == "-a":
                    self.set_score(0)
                    self.lines.append("Tudo resetado (pontos, conquistas, upgrades).")
                    self.reset_achievements()
                    if self.upgrade_manager:
                        self.upgrade_manager.reset_upgrades()
                else:
                    self.lines.append("Comando inválido. Uso: reset <categoria>")
            else:
                self.lines.append("Uso: reset <categoria> (achievements, points, upgrades, -a)")

        elif cmd == "exit":
            self.lines.append("Console fechado.")
            self.close()

        else:
            self.lines.append(f"Comando desconhecido: {cmd}")

        if len(self.lines) > self.max_lines:
            self.lines = self.lines[-self.max_lines:]

    def reset_achievements(self):
        if self.tracker:
            self.tracker.unlocked.clear()
            for ach in self.tracker.achievements:
                ach.unlocked = False

    def draw(self):
        if not self.visible:
            return

        console_rect = pygame.Rect(20, self.height // 2, self.width - 40, self.height // 2 - 20)
        pygame.draw.rect(self.screen, (20, 20, 40), console_rect, border_radius=10)
        pygame.draw.rect(self.screen, (100, 100, 200), console_rect, 2, border_radius=10)

        for i, line in enumerate(self.lines):
            text = self.font.render(line, True, (200, 200, 255))
            self.screen.blit(text, (console_rect.x + 10, console_rect.y + 10 + i * 25))

        input_surface = self.font.render("> " + self.input_text, True, (200, 255, 200))
        self.screen.blit(input_surface, (console_rect.x + 10, console_rect.y + 10 + len(self.lines) * 25))
