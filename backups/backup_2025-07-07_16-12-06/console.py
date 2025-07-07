import pygame

class Console:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        self.font = pygame.font.SysFont("Consolas", 24)
        self.lines = ["Console ativado!", "Digite comandos..."]
        self.visible = True
        self.input_text = ""
        self.max_lines = 6
        self.get_score = None
        self.set_score = None

    def set_score_accessors(self, get_func, set_func):
        self.get_score = get_func
        self.set_score = set_func

    def handle_event(self, event):
        if not self.visible:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            elif event.key == pygame.K_RETURN:
                self.execute_command(self.input_text)
                self.input_text = ""
            else:
                if len(event.unicode) == 1 and event.unicode.isprintable():
                    self.input_text += event.unicode
            return True
        return False

    def execute_command(self, command):
        command = command.strip()
        parts = command.lower().split()
        if not parts:
            return

        cmd = parts[0]

        if cmd == "exit":
            self.visible = False
            self.lines.append("Console fechado.")
        elif cmd == "help":
            self.lines.append("Comandos disponíveis: add <num>, remove <num>, help, exit")
        elif cmd == "add":
            if len(parts) == 2 and parts[1].isdigit():
                if self.get_score and self.set_score:
                    current = self.get_score()
                    new_score = current + int(parts[1])
                    self.set_score(new_score)
                    self.lines.append(f"Adicionado {parts[1]} pontos. Total: {new_score}")
                else:
                    self.lines.append("Funções de pontuação não configuradas.")
            else:
                self.lines.append("Uso correto: add <número>")
        elif cmd == "remove":
            if len(parts) == 2 and parts[1].isdigit():
                if self.get_score and self.set_score:
                    current = self.get_score()
                    new_score = max(0, current - int(parts[1]))
                    self.set_score(new_score)
                    self.lines.append(f"Removido {parts[1]} pontos. Total: {new_score}")
                else:
                    self.lines.append("Funções de pontuação não configuradas.")
            else:
                self.lines.append("Uso correto: remove <número>")
        else:
            self.lines.append(f"Comando desconhecido: {command}")

        # Mantém apenas as últimas max_lines linhas
        if len(self.lines) > self.max_lines:
            self.lines = self.lines[-self.max_lines:]

    def draw(self):
        if not self.visible:
            return

        console_rect = pygame.Rect(20, self.height - 200, self.width - 40, 180)
        pygame.draw.rect(self.screen, (20, 20, 40), console_rect, border_radius=10)
        pygame.draw.rect(self.screen, (100, 100, 200), console_rect, 2, border_radius=10)

        # Desenha linhas anteriores
        for i, line in enumerate(self.lines):
            text = self.font.render(line, True, (200, 200, 255))
            self.screen.blit(text, (console_rect.x + 10, console_rect.y + 10 + i * 30))

        # Desenha linha atual de input (sempre visível)
        input_surface = self.font.render("> " + self.input_text, True, (200, 255, 200))
        self.screen.blit(input_surface, (console_rect.x + 10, console_rect.y + 10 + len(self.lines) * 30))
