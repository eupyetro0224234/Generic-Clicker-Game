import pygame
import os
import json
from datetime import datetime

class Console:
    def __init__(self, screen, width, height, on_exit_callback=None, on_open_callback=None, tracker=None, config_menu=None, upgrade_manager=None, game=None):
        self.screen = screen
        self.width = width
        self.height = height
        self.font = pygame.font.SysFont("Consolas", 24)
        self.emoji_font = pygame.font.SysFont("segoeuiemoji", 24)
        self.visible = False
        self.input_text = ""
        self.max_lines = 20
        self.lines = []

        self.get_score = None
        self.set_score = None

        # Histórico persistente
        self.history = []          # lista de dicionários: {"cmd": str, "time": str, "output": [str]}
        self.history_index = -1
        self.saved_lines = []      # backup da saída antes de começar a navegação
        self.edited_commands = {}  # dicionário: index -> {"input": str, "lines": [str]}
        self.cursor_pos = 0
        self.cursor_moved_at = 0

        # Caminho do arquivo de histórico
        appdata = os.environ.get('APPDATA', os.path.expanduser("~"))
        self.history_dir = os.path.join(appdata, "genericclickergame")
        self.history_path = os.path.join(self.history_dir, ".history")
        self._load_history()

        self.scroll_offset = 0

        self.on_exit_callback = on_exit_callback
        self.on_open_callback = on_open_callback

        self.tracker = tracker
        self.config_menu = config_menu
        self.upgrade_manager = upgrade_manager
        self.game = game

    def _load_history(self):
        if not os.path.exists(self.history_path):
            return
        try:
            with open(self.history_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                        if "cmd" in entry and "output" in entry:
                            self.history.append(entry)
                        else:
                            self.history.append({"cmd": line, "time": "", "output": []})
                    except json.JSONDecodeError:
                        self.history.append({"cmd": line, "time": "", "output": []})
        except Exception as e:
            print(f"Erro ao carregar histórico: {e}")

    def _save_history(self):
        try:
            os.makedirs(self.history_dir, exist_ok=True)
            with open(self.history_path, 'w', encoding='utf-8') as f:
                for entry in self.history:
                    f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        except Exception as e:
            print(f"Erro ao salvar histórico: {e}")

    def _save_current_state(self, index):
        """Salva o estado atual (input e lines) no cache, associado ao índice."""
        if index >= 0:
            self.edited_commands[index] = {
                "input": self.input_text,
                "lines": self.lines[:]
            }
        else:
            # índice -1 = estado original da sessão
            self.saved_lines = self.lines[:]  # já mantemos, mas podemos sobrescrever se quiser
            # Não salvamos input vazio para índice -1

    def _load_state(self, index):
        """Carrega um estado salvo (editado) ou do histórico original."""
        if index in self.edited_commands:
            # Usa a versão editada
            state = self.edited_commands[index]
            self.input_text = state["input"]
            self.lines = state["lines"][:]
        elif index >= 0 and index < len(self.history):
            # Carrega do histórico original
            entry = self.history[index]
            self.input_text = entry["cmd"]
            self.lines = entry["output"][:]
        else:
            # Fora do histórico: restaura a sessão
            self.input_text = ""
            self.lines = self.saved_lines[:] if self.saved_lines else []

    def set_score_accessors(self, get_func, set_func):
        self.get_score = get_func
        self.set_score = set_func

    def open(self):
        self.visible = True
        if not self.lines:
            self.lines = ["Console ativo."]
        self.input_text = ""
        self.cursor_pos = 0
        self.cursor_moved_at = 0
        self.scroll_offset = 0
        pygame.key.set_repeat(400, 40)
        if self.on_open_callback:
            self.on_open_callback()
        if self.tracker:
            self.tracker.unlock_secret("console")

    def close(self):
        self.visible = False
        pygame.key.set_repeat(0)
        if self.on_exit_callback:
            self.on_exit_callback()

    def minimize(self):
        self.visible = False
        pygame.key.set_repeat(0)

    def _max_scroll(self, visible_lines):
        return max(0, len(self.lines) - visible_lines)

    def handle_event(self, event):
        if not self.visible:
            return False

        if event.type == pygame.MOUSEWHEEL:
            console_rect = pygame.Rect(20, self.height // 2, self.width - 40, self.height // 2 - 20)
            visible_lines = max(1, (console_rect.height - 50) // 25)
            self.scroll_offset += event.y
            self.scroll_offset = max(0, min(self.scroll_offset, self._max_scroll(visible_lines)))
            return True

        if event.type == pygame.KEYDOWN:
            self.cursor_moved_at = pygame.time.get_ticks()

            if event.key == pygame.K_BACKSPACE:
                if self.cursor_pos > 0:
                    self.input_text = self.input_text[:self.cursor_pos - 1] + self.input_text[self.cursor_pos:]
                    self.cursor_pos -= 1

            elif event.key == pygame.K_RETURN:
                if not self.input_text.strip():
                    return True
                # Executa o comando
                command = self.input_text
                self.execute_command(command)
                # Após executar, self.lines contém a saída gerada
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                entry = {
                    "cmd": command,
                    "time": timestamp,
                    "output": self.lines[:]
                }
                self.history.append(entry)
                self._save_history()
                # Limpa cache de edições porque o histórico mudou
                self.edited_commands.clear()
                self.history_index = -1
                self.saved_lines = []
                self.input_text = ""
                self.cursor_pos = 0

            elif event.key == pygame.K_UP:
                if self.history:
                    # Salva estado atual antes de mudar
                    if self.history_index != -1:
                        self._save_current_state(self.history_index)
                    elif self.history_index == -1:
                        # Estava na sessão normal, guarda como base
                        self.saved_lines = self.lines[:]

                    if self.history_index == -1:
                        self.history_index = len(self.history) - 1
                    elif self.history_index > 0:
                        self.history_index -= 1

                    # Carrega o estado do novo índice
                    self._load_state(self.history_index)
                    self.cursor_pos = len(self.input_text)

            elif event.key == pygame.K_DOWN:
                if self.history and self.history_index != -1:
                    # Salva estado atual
                    self._save_current_state(self.history_index)

                    if self.history_index < len(self.history) - 1:
                        self.history_index += 1
                        self._load_state(self.history_index)
                    else:
                        # Sai do histórico
                        self.history_index = -1
                        self.input_text = ""
                        self.lines = self.saved_lines[:] if self.saved_lines else []
                    self.cursor_pos = len(self.input_text)

            elif event.key == pygame.K_LEFT:
                if self.cursor_pos > 0:
                    self.cursor_pos -= 1

            elif event.key == pygame.K_RIGHT:
                if self.cursor_pos < len(self.input_text):
                    self.cursor_pos += 1

            elif event.key == pygame.K_HOME:
                self.cursor_pos = 0

            elif event.key == pygame.K_END:
                self.cursor_pos = len(self.input_text)

            elif event.key == pygame.K_ESCAPE:
                self.minimize()
                return True

            else:
                if len(event.unicode) == 1 and event.unicode.isprintable():
                    self.input_text = self.input_text[:self.cursor_pos] + event.unicode + self.input_text[self.cursor_pos:]
                    self.cursor_pos += 1

            return True

        return False

    def execute_command(self, command):
        # (mesma implementação original)
        cmd = command.strip().lower()
        self.lines = []
        self.scroll_offset = 0

        if cmd == "help":
            self.lines.extend([
                "Comandos disponíveis:",
                "add points",
                "remove points",
                "reset",
                "trabalhador limit",
                "trabalhador time",
                "list achievements",
                "unlock achievement <id>",
                "lock achievement <id>",
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

        elif cmd.startswith("unlock achievement"):
            parts = cmd.split()
            if len(parts) == 3:
                ach_id = parts[2]
                if self.tracker:
                    ach = next((a for a in self.tracker.achievements if a.id == ach_id), None)
                    if ach:
                        if ach.unlocked:
                            self.lines.append(f"Conquista '{ach_id}' já está desbloqueada.")
                        else:
                            self.tracker.unlock_secret(ach_id)
                            self.lines.append(f"Conquista '{ach_id}' desbloqueada.")
                            if self.game:
                                self.game.save_game_data()
                    else:
                        self.lines.append(f"Conquista '{ach_id}' não encontrada.")
                else:
                    self.lines.append("Erro: tracker não configurado.")
            else:
                self.lines.append("Uso: unlock achievement <id>")

        elif cmd.startswith("lock achievement"):
            parts = cmd.split()
            if len(parts) == 3:
                ach_id = parts[2]
                if self.tracker:
                    ach = next((a for a in self.tracker.achievements if a.id == ach_id), None)
                    if ach:
                        if not ach.unlocked:
                            self.lines.append(f"Conquista '{ach_id}' já está bloqueada.")
                        else:
                            ach.unlocked = False
                            ach.unlock_date = None
                            self.tracker.unlocked.discard(ach_id)
                            if self.config_menu:
                                self.config_menu.achievements_menu.update(self.tracker)
                            if self.game:
                                self.game.save_game_data()
                            self.lines.append(f"Conquista '{ach_id}' bloqueada.")
                    else:
                        self.lines.append(f"Conquista '{ach_id}' não encontrada.")
                else:
                    self.lines.append("Erro: tracker não configurado.")
            else:
                self.lines.append("Uso: lock achievement <id>")

        elif cmd == "list achievements":
            if self.tracker:
                self.max_lines = max(200, len(self.tracker.achievements) + 5)
                for i, ach in enumerate(self.tracker.achievements, start=1):
                    status = "✓" if ach.unlocked else "✗"
                    self.lines.append(f"{i}: {ach.id}: {ach.name} - {ach.description} [{status}]")
                self.lines.append(f"— {len(self.tracker.achievements)} conquistas no total —")
                self.scroll_offset = len(self.lines)
            else:
                self.lines.append("Erro: tracker não configurado.")

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

        elif cmd.startswith("trabalhador time"):
            parts = cmd.split()
            if len(parts) == 3:
                if parts[2] == "on":
                    if self.upgrade_manager:
                        self.upgrade_manager.set_trabalhador_time(True)
                        self.lines.append("Tempo de vida dos trabalhadores ativado.")
                    else:
                        self.lines.append("Erro: upgrade_manager não configurado.")
                elif parts[2] == "off":
                    if self.upgrade_manager:
                        self.upgrade_manager.set_trabalhador_time(False)
                        self.lines.append("Tempo de vida dos trabalhadores desativado.")
                    else:
                        self.lines.append("Erro: upgrade_manager não configurado.")
                else:
                    self.lines.append("Uso: trabalhador time <on/off>")
            else:
                self.lines.append("Uso: trabalhador time <on/off>")

        elif cmd == "exit":
            self.lines.append("Console fechado.")
            self.close()

        else:
            self.lines.append(f"Comando desconhecido: {cmd}.")

        if cmd != "list achievements":
            self.max_lines = 20
            if len(self.lines) > self.max_lines:
                self.lines = self.lines[-self.max_lines:]

    def draw(self):
        # (mesma implementação original)
        if not self.visible:
            return

        console_rect = pygame.Rect(20, self.height // 2, self.width - 40, self.height // 2 - 20)
        pygame.draw.rect(self.screen, (20, 20, 40), console_rect, border_radius=10)
        pygame.draw.rect(self.screen, (100, 100, 200), console_rect, 2, border_radius=10)

        input_y = console_rect.y + console_rect.height - 30
        visible_lines = max(1, (input_y - console_rect.y - 10) // 25)

        max_scroll = max(0, len(self.lines) - visible_lines)
        self.scroll_offset = max(0, min(self.scroll_offset, max_scroll))

        end = len(self.lines) - self.scroll_offset
        start = max(0, end - visible_lines)
        visible = self.lines[start:end]

        for i, line in enumerate(visible):
            y_pos = input_y - (len(visible) - i) * 25
            if line.endswith("[✓]") or line.endswith("[✗]"):
                main_part  = line[:-3]
                emoji_part = line[-3:]
                main_surf  = self.font.render(main_part, True, (200, 200, 255))
                self.screen.blit(main_surf, (console_rect.x + 10, y_pos))
                emoji_surf = self.emoji_font.render(emoji_part, True, (200, 200, 255))
                self.screen.blit(emoji_surf, (console_rect.x + 10 + main_surf.get_width(), y_pos))
            else:
                text = self.font.render(line, True, (200, 200, 255))
                self.screen.blit(text, (console_rect.x + 10, y_pos))

        input_y = console_rect.y + console_rect.height - 30
        before_cursor = "> " + self.input_text[:self.cursor_pos]
        after_cursor = self.input_text[self.cursor_pos:]
        before_surf = self.font.render(before_cursor, True, (200, 255, 200))
        after_surf = self.font.render(after_cursor, True, (200, 255, 200))
        self.screen.blit(before_surf, (console_rect.x + 10, input_y))
        cursor_x = console_rect.x + 10 + before_surf.get_width()
        ticks = pygame.time.get_ticks()
        cursor_visible = (ticks - self.cursor_moved_at < 500) or (ticks // 500) % 2 == 0
        if cursor_visible:
            pygame.draw.line(self.screen, (200, 255, 200), (cursor_x, input_y + 2), (cursor_x, input_y + self.font.get_height() - 2), 2)
        self.screen.blit(after_surf, (cursor_x, input_y))