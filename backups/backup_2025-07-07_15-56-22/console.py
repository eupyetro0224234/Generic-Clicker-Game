import pygame

console_instance = None

def open_console(screen, width, height):
    global console_instance
    if console_instance is None:
        console_instance = Console(screen, width, height)
    console_instance.visible = True
    return console_instance

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
        command = command.strip().lower()
        if command == "exit":
            self.visible = False
            self.lines.append("Console fechado.")
        elif command == "help":
            self.lines.append("Comandos: help, exit")
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

        # Desenha linha atual de input
        input_surface = self.font.render("> " + self.input_text, True, (200, 255, 200))
        self.screen.blit(input_surface, (console_rect.x + 10, console_rect.y + 10 + len(self.lines) * 30))
