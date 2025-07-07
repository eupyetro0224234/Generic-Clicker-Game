import pygame

class Console:
    def __init__(self, screen, width, height, on_exit_callback=None):
        self.screen = screen
        self.width = width
        self.height = height
        self.font = pygame.font.SysFont("Consolas", 24)
        self.visible = False
        self.input_text = ""
        self.max_lines = 6
        self.lines = []

        # Funções para get/set pontuação (devem ser configuradas por set_score_accessors)
        self.get_score = None
        self.set_score = None

        # Callback para notificar ConfigMenu que console fechou com comando exit
        self.on_exit_callback = on_exit_callback

    def set_score_accessors(self, get_func, set_func):
        self.get_score = get_func
        self.set_score = set_func

    def open(self):
        """Abre o console limpando o histórico e iniciando com mensagens padrão."""
        self.visible = True
        self.lines = ["Console ativado!", "Digite comandos..."]
        self.input_text = ""

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
                # ESC minimiza (fecha) o console sem apagar histórico
                self.visible = False
            else:
                # Permite letras, números, símbolos imprimíveis
                if len(event.unicode) == 1 and event.unicode.isprintable():
                    self.input_text += event.unicode
            return True
        return False

    def execute_command(self, command):
        command = command.strip().lower()

        # Limpa linhas e adiciona resposta do comando atual
        self.lines = []

        if command == "help":
            self.lines.append("Comandos disponíveis:")
            self.lines.append("add points <n>")
            self.lines.append("remove points <n>")
            self.lines.append("help")
            self.lines.append("exit")
        elif command.startswith("add points"):
            parts = command.split()
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
        elif command.startswith("remove points"):
            parts = command.split()
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
        elif command == "exit":
            self.visible = False
            self.lines.append("Console fechado.")
            if self.on_exit_callback:
                self.on_exit_callback()
        else:
            self.lines.append(f"Comando desconhecido: {command}")

        # Mantém no máximo max_lines linhas (normalmente não ultrapassa)
        if len(self.lines) > self.max_lines:
            self.lines = self.lines[-self.max_lines:]

    def draw(self):
        if not self.visible:
            return

        console_rect = pygame.Rect(20, self.height - 200, self.width - 40, 180)
        pygame.draw.rect(self.screen, (20, 20, 40), console_rect, border_radius=10)
        pygame.draw.rect(self.screen, (100, 100, 200), console_rect, 2, border_radius=10)

        # Desenha linhas da última saída
        for i, line in enumerate(self.lines):
            text = self.font.render(line, True, (200, 200, 255))
            self.screen.blit(text, (console_rect.x + 10, console_rect.y + 10 + i * 30))

        # Desenha linha atual de input
        input_surface = self.font.render("> " + self.input_text, True, (200, 255, 200))
        self.screen.blit(input_surface, (console_rect.x + 10, console_rect.y + 10 + len(self.lines) * 30))
