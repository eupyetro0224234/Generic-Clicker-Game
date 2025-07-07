import pygame

class Console:
    def __init__(self, screen, width, height, get_score_callback, set_score_callback):
        self.screen = screen
        self.width = width
        self.height = height
        self.font = pygame.font.SysFont("Consolas", 24)
        self.lines = ["Console ativado! Digite 'help' para comandos."]
        self.visible = True  # Sempre visível
        self.input_text = ""
        self.max_lines = 6

        self.get_score = get_score_callback
        self.set_score = set_score_callback

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
        parts = command.split()

        if command == "help":
            self.lines.append("Comandos disponíveis:")
            self.lines.append("  add points X    -> adiciona X pontos")
            self.lines.append("  remove points X -> remove X pontos")
            self.lines.append("  help            -> mostra comandos")
        elif len(parts) == 3 and parts[0] == "add" and parts[1] == "points":
            try:
                amount = int(parts[2])
                current = self.get_score()
                self.set_score(current + amount)
                self.lines.append(f"Pontos aumentados em {amount}. Total: {self.get_score()}")
            except:
                self.lines.append("Uso incorreto. Exemplo: add points 10")
        elif len(parts) == 3 and parts[0] == "remove" and parts[1] == "points":
            try:
                amount = int(parts[2])
                current = self.get_score()
                new_score = max(0, current - amount)
                self.set_score(new_score)
                self.lines.append(f"Pontos diminuídos em {amount}. Total: {self.get_score()}")
            except:
                self.lines.append("Uso incorreto. Exemplo: remove points 5")
        else:
            self.lines.append(f"Comando desconhecido: {command}")

        if len(self.lines) > self.max_lines:
            self.lines = self.lines[-self.max_lines:]

    def draw(self):
        if not self.visible:
            return

        console_rect = pygame.Rect(20, self.height - 200, self.width - 40, 180)
        pygame.draw.rect(self.screen, (20, 20, 40), console_rect, border_radius=10)
        pygame.draw.rect(self.screen, (100, 100, 200), console_rect, 2, border_radius=10)

        for i, line in enumerate(self.lines):
            text = self.font.render(line, True, (200, 200, 255))
            self.screen.blit(text, (console_rect.x + 10, console_rect.y + 10 + i * 30))

        input_surface = self.font.render("> " + self.input_text, True, (200, 255, 200))
        self.screen.blit(input_surface, (console_rect.x + 10, console_rect.y + 10 + len(self.lines) * 30))


console_instance = None

def open_console(screen, width, height, get_score_callback, set_score_callback):
    global console_instance
    if console_instance is None:
        console_instance = Console(screen, width, height, get_score_callback, set_score_callback)
    console_instance.visible = True
    return console_instance
