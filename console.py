import pygame

class Console:
    def __init__(self, screen, width, height, on_exit_callback=None, tracker=None, config_menu=None, upgrade_manager=None):
        self.screen = screen
        self.width = width
        self.height = height
        self.font = pygame.font.SysFont("Consolas", 24)
        self.visible = False
        self.input_text = ""
        
        # Aumentando o número de linhas visíveis
        self.max_lines = 20  # Aumentado para suportar mais linhas de texto
        self.lines = []
        
        # Funções para get/set pontuação (devem ser configuradas por set_score_accessors)
        self.get_score = None
        self.set_score = None

        # Callback para notificar ConfigMenu que o console foi fechado com 'exit'
        self.on_exit_callback = on_exit_callback
        self.tracker = tracker  # Armazenando o tracker
        self.config_menu = config_menu  # Armazenando o config_menu
        self.upgrade_manager = upgrade_manager  # Agora estamos armazenando o upgrade_manager

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
        cmd = command.strip().lower()
        self.lines = []  # Limpa as linhas anteriores

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
                    new_score = self.get_score() - n
                    self.set_score(new_score)
                    self.lines.append(f"Removido {n} pontos. Pontos: {new_score}")
                else:
                    self.lines.append("Erro: função de pontuação não configurada.")
            else:
                self.lines.append("Uso: remove points <n>")

        elif cmd == "reset achievements":
            self.reset_achievements()

        elif cmd == "reset points":
            self.set_score(0)
            self.lines.append("Pontos resetados.")

        elif cmd == "reset upgrades":
            self.reset_upgrades()

        elif cmd == "reset -a":
            self.set_score(0)
            self.reset_achievements()
            self.reset_upgrades()
            self.lines.append("Tudo resetado!")

        elif cmd == "exit":
            self.visible = False
            if self.on_exit_callback:
                self.on_exit_callback()

        else:
            self.lines.append("Comando não reconhecido. Use 'help' para listar comandos.")

    def reset_upgrades(self):
        """Reseta os upgrades no UpgradeMenu."""
        if self.upgrade_manager:
            self.upgrade_manager.reset_upgrades()  # Chama a função no UpgradeMenu
            self.lines.append("Upgrades resetados com sucesso!")

    def reset_achievements(self):
        """Reseta as conquistas no AchievementTracker."""
        if self.tracker:
            self.tracker.unlocked.clear()
            self.tracker.check_unlock(self.get_score())
            self.lines.append("Conquistas resetadas com sucesso!")

    def draw(self):
        if self.visible:
            # Exibe as linhas do console na tela
            y_offset = 10
            for line in self.lines:
                text = self.font.render(line, True, (255, 255, 255))
                self.screen.blit(text, (10, y_offset))
                y_offset += self.font.get_height()
            input_text = self.font.render(f"> {self.input_text}", True, (255, 255, 255))
            self.screen.blit(input_text, (10, y_offset))
