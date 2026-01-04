import pygame

class Console:
    def __init__(self, screen, width, height, on_exit_callback=None, on_open_callback=None, tracker=None, config_menu=None, upgrade_manager=None, game=None):
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
        self.game = game

    def set_score_accessors(self, get_func, set_func):
        self.get_score = get_func
        self.set_score = set_func

    def open(self):
        self.visible = True
        self.lines = ["Console ativo."]
        self.input_text = ""
        if self.on_open_callback:
            self.on_open_callback()
        if self.tracker:
            self.tracker.unlock_secret("console")

    def close(self):
        self.visible = False
        if self.on_exit_callback:
            self.on_exit_callback()

    def minimize(self):
        self.visible = False

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
                self.minimize()
                return True

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
                "add points",
                "remove points",
                "reset",
                "trabalhador limit",
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
                    self.lines.append(f"Foram adicionados {n} pontos.")
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
                    self.lines.append(f"Foram removidos {n} pontos.")
                else:
                    self.lines.append("Erro: função de pontuação não configurada.")
            else:
                self.lines.append("Uso: remove points <n>")

        elif cmd == "reset upgrades":
            self.lines.append("Resetando upgrades...")
            if self.upgrade_manager:
                self.upgrade_manager.reset_upgrades()
                self.lines.append("Upgrades resetados.")
            else:
                self.lines.append("Erro: upgrade_manager não configurado.")

        elif cmd.startswith("reset"):
            parts = cmd.split()
            if len(parts) >= 2:
                reset_categories = parts[1:]
                reset_anything = False
                
                for category in reset_categories:
                    if category == "achievements":
                        if self.tracker:
                            total_normal_clicks = self.tracker.normal_clicks
                            total_mini_event_clicks = self.tracker.mini_event_clicks
                            
                            self.tracker.reset_achievements()
                            self.tracker.unlocked.clear()
                            
                            self.tracker.normal_clicks = total_normal_clicks
                            self.tracker.mini_event_clicks = total_mini_event_clicks
                            
                            if self.config_menu:
                                self.config_menu.achievements_menu.update(self.tracker)
                            
                            if self.game:
                                self.game.saved_achievements = {}
                                self.game.save_game_data()
                            
                            self.lines.append("Conquistas resetadas.")
                            reset_anything = True
                        else:
                            self.lines.append("Erro: tracker não configurado.")
                            
                    elif category == "points":
                        if self.set_score:
                            self.set_score(0)
                            self.lines.append("Pontos resetados.")
                            reset_anything = True
                        else:
                            self.lines.append("Erro: função de pontuação não configurada.")
                            
                    elif category == "upgrades":
                        if self.upgrade_manager:
                            self.upgrade_manager.reset_upgrades()
                            self.lines.append("Upgrades resetados.")
                            reset_anything = True
                        else:
                            self.lines.append("Erro: upgrade_manager não configurado.")
                            
                    elif category == "-a":
                        if self.set_score:
                            self.set_score(0)
                        
                        preserved_normal_clicks = 0
                        preserved_mini_clicks = 0
                        
                        if self.tracker:
                            preserved_normal_clicks = self.tracker.normal_clicks
                            preserved_mini_clicks = self.tracker.mini_event_clicks
                            
                            self.tracker.reset_achievements()
                            self.tracker.unlocked.clear()
                            
                            self.tracker.normal_clicks = preserved_normal_clicks
                            self.tracker.mini_event_clicks = preserved_mini_clicks
                        
                        if self.upgrade_manager:
                            self.upgrade_manager.reset_upgrades()
                        
                        if self.game:
                            self.game.mini_event1_session = 0
                            self.game.mini_event2_session = 0
                            self.game.total_score_earned = 0
                            self.game.max_score = 0
                        
                        if self.config_menu and self.tracker:
                            self.config_menu.achievements_menu.update(self.tracker)
                        
                        if self.game:
                            self.game.saved_achievements = {}
                            self.game.save_game_data()
                        
                        self.lines.append("Reset completo.")
                        reset_anything = True
                        break
                        
                    else:
                        self.lines.append(f"Categoria inválida: {category}")
                
                if not reset_anything and "-a" not in reset_categories:
                    self.lines.append("Nenhuma categoria válida foi resetada.")
                
                if self.config_menu and self.tracker and ("achievements" in reset_categories or "-a" in reset_categories):
                    self.config_menu.achievements_menu.update(self.tracker)
                    
                if reset_anything and self.game:
                    self.game.save_game_data()
                    
            else:
                self.lines.append("Uso: reset <categorias>")
                self.lines.append("Categorias: achievements, points, upgrades, -a (tudo)")

        elif cmd.startswith("trabalhador limit"):
            parts = cmd.split()
            if len(parts) == 3:
                if parts[2] == "on":
                    if self.upgrade_manager:
                        self.upgrade_manager.set_trabalhador_limit(True)
                        self.lines.append("O limite de 10 trabalhadores foi ativado.")
                    else:
                        self.lines.append("Erro: upgrade_manager não configurado.")
                elif parts[2] == "off":
                    if self.upgrade_manager:
                        self.upgrade_manager.set_trabalhador_limit(False)
                        self.lines.append("O limite de trabalhadores foi desativado.")
                    else:
                        self.lines.append("Erro: upgrade_manager não configurado.")
                else:
                    self.lines.append("Uso: trabalhador limit <on/off>")
            else:
                self.lines.append("Uso: trabalhador limit <on/off>")

        elif cmd == "exit":
            self.lines.append("Console fechado.")
            self.close()

        else:
            self.lines.append(f"Comando desconhecido: {cmd}.")

        if len(self.lines) > self.max_lines:
            self.lines = self.lines[-self.max_lines:]

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