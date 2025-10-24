import pygame
import json
import os

class FullSettingsMenu:
    def __init__(self, screen, window_width, window_height):
        self.screen = screen
        self.width = window_width
        self.height = window_height

        self.bg_color = (255, 182, 193)  # Rosa claro
        self.text_color = (47, 24, 63)
        self.option_height = 60
        self.option_radius = 15
        self.padding_x = 20
        self.padding_y = 20
        self.spacing_x = 20
        self.spacing_y = 20
        self.options_per_row = 2

        appdata_roaming = os.getenv("APPDATA")
        self.game_folder = os.path.join(appdata_roaming, "genericclickergame")
        os.makedirs(self.game_folder, exist_ok=True)
        self.config_path = os.path.join(self.game_folder, "config.json")

        self.default_config = {
            "Clique Esquerdo": True,
            "Clique Direito": True,
            "Clique Botão do Meio": False,
            "Rolagem do Mouse": False,
            "Ativar Mods": False,
            "Verificar atualizações": True,
            "Mostrar descrição de conquistas bloqueadas": False,
            "Menu vertical": False
        }

        self.visible = False
        self.options = {}
        self.load_config()

        self.valor_original_update = self.options.get("Verificar atualizações", True)
        self.precisa_reiniciar = False

        self.title_font = pygame.font.SysFont(None, 42)
        self.font = pygame.font.SysFont(None, 32)

        self.hovered_option = None
        self.button_rects = []
        
        self.console_ativo = False
        
        # Botão X para fechar
        self.close_button_rect = pygame.Rect(self.width - 65, 25, 40, 40)

    def is_click_allowed(self, button):
        """Verifica se um tipo de clique do mouse está permitido pelas configurações"""
        if button == 1:  # Botão esquerdo
            return self.options.get("Clique Esquerdo", True)
        elif button == 2:  # Botão do meio
            return self.options.get("Clique Botão do Meio", False)
        elif button == 3:  # Botão direito
            return self.options.get("Clique Direito", True)
        elif button in (4, 5):  # Rolagem do mouse
            return self.options.get("Rolagem do Mouse", False)
        return False

    def load_config(self):
        """Carrega as configurações do arquivo JSON"""
        try:
            if os.path.isfile(self.config_path):
                with open(self.config_path, "r", encoding="utf-8") as f:
                    loaded_options = json.load(f)
                    # Mescla as configurações carregadas com as padrão
                    self.options = {**self.default_config}
                    for key in loaded_options:
                        if key in self.default_config or key == "Manter console aberto":
                            self.options[key] = loaded_options[key]
            else:
                # Se o arquivo não existe, usa as configurações padrão
                self.options = self.default_config.copy()
                self.save_config()
        except Exception as e:
            print(f"Erro ao carregar configurações: {e}")
            # Em caso de erro, usa as configurações padrão
            self.options = self.default_config.copy()

    def save_config(self):
        """Salva as configurações no arquivo JSON"""
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.options, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar configurações: {e}")

    def get_option(self, key):
        """Obtém o valor de uma opção específica"""
        return self.options.get(key, False)

    def set_option(self, key, value):
        """Define o valor de uma opção específica e salva"""
        self.options[key] = bool(value)
        self.save_config()

    def add_console_option(self):
        """Adiciona a opção do console ao menu"""
        if not self.console_ativo:
            self.console_ativo = True
            if "Manter console aberto" not in self.options:
                self.options["Manter console aberto"] = False
                self.save_config()

    def remove_console_option(self):
        """Remove a opção do console do menu"""
        if self.console_ativo:
            self.console_ativo = False
            if "Manter console aberto" in self.options:
                del self.options["Manter console aberto"]
                self.save_config()

    def draw_section_title(self, title, x, y):
        """Desenha o título de uma seção do menu"""
        box_width = self.width - 2 * x
        box_height = self.option_height
        box_rect = pygame.Rect(x, y, box_width, box_height)

        # Cor azul claro para os títulos das seções
        azul_claro = (200, 190, 255, 230)
        pygame.draw.rect(self.screen, azul_claro, box_rect, border_radius=self.option_radius)
        pygame.draw.rect(self.screen, (150, 150, 150), box_rect, width=2, border_radius=self.option_radius)

        title_surf = self.title_font.render(title, True, self.text_color)
        title_rect = title_surf.get_rect(center=box_rect.center)
        self.screen.blit(title_surf, title_rect)

        return y + box_height + self.spacing_y

    def draw_options(self, keys, x, y):
        """Desenha as opções do menu em grid"""
        mouse_pos = pygame.mouse.get_pos()
        button_width = (self.width - 2 * x - (self.options_per_row - 1) * self.spacing_x) // self.options_per_row

        for i, key in enumerate(keys):
            val = self.options.get(key, False)
            row = i // self.options_per_row
            col = i % self.options_per_row

            option_x = x + col * (button_width + self.spacing_x)
            option_y = y + row * (self.option_height + self.spacing_y)

            option_rect = pygame.Rect(option_x, option_y, button_width, self.option_height)
            self.button_rects.append((option_rect, key))

            # Sombra suave
            shadow_surface = pygame.Surface((button_width + 6, self.option_height + 6), pygame.SRCALPHA)
            pygame.draw.rect(shadow_surface, (0, 0, 0, 20), (0, 0, button_width + 6, self.option_height + 6), border_radius=15)
            self.screen.blit(shadow_surface, (option_x - 3, option_y - 3))

            # Cor do botão (muda no hover)
            color = (220, 235, 255) if option_rect.collidepoint(mouse_pos) else (255, 255, 255)

            pygame.draw.rect(self.screen, color, option_rect, border_radius=self.option_radius)
            pygame.draw.rect(self.screen, (150, 150, 150), option_rect, width=2, border_radius=self.option_radius)

            # Texto da opção
            text_surf = self.font.render(key, True, self.text_color)
            text_rect = text_surf.get_rect(midleft=(option_x + 20, option_rect.centery))
            self.screen.blit(text_surf, text_rect)

            # Texto do status (Ativado/Desativado)
            val_text = "Ativado" if val else "Desativado"
            val_surf = self.font.render(val_text, True, self.text_color)
            val_rect = val_surf.get_rect(midright=(option_x + button_width - 20, option_rect.centery))
            self.screen.blit(val_surf, val_rect)

        # Calcula a altura total usada pelas opções
        total_rows = (len(keys) + self.options_per_row - 1) // self.options_per_row
        return y + total_rows * (self.option_height + self.spacing_y)

    def draw(self):
        """Desenha o menu de configurações completo"""
        if not self.visible:
            return

        self.button_rects = []

        # Fundo rosa claro
        self.screen.fill(self.bg_color)

        x = self.padding_x
        y = self.padding_y

        # Título principal
        title_font = pygame.font.SysFont(None, 48)
        title_surf = title_font.render("Configurações", True, self.text_color)
        title_rect = title_surf.get_rect(center=(self.width // 2, 35))
        self.screen.blit(title_surf, title_rect)

        # Botão X para fechar
        pygame.draw.rect(self.screen, (255, 120, 120), self.close_button_rect, border_radius=20)
        pygame.draw.rect(self.screen, (180, 60, 60), self.close_button_rect, 2, border_radius=20)
        center_x, center_y = self.close_button_rect.center
        line_length = 12
        pygame.draw.line(self.screen, (255, 255, 255), (center_x - line_length, center_y - line_length),
                         (center_x + line_length, center_y + line_length), 4)
        pygame.draw.line(self.screen, (255, 255, 255), (center_x - line_length, center_y + line_length),
                         (center_x + line_length, center_y - line_length), 4)

        y = 90  # Posição inicial do conteúdo

        # Seção de Controles
        y = self.draw_section_title("Controles", x, y)
        controles_keys = [
            "Clique Esquerdo",
            "Clique Direito",
            "Clique Botão do Meio",
            "Rolagem do Mouse"
        ]
        y = self.draw_options(controles_keys, x, y)

        y += 40  # Espaço entre seções

        # Seção Outros
        y = self.draw_section_title("Outros", x, y)
        outros_keys = [
            "Ativar Mods",
            "Verificar atualizações",
            "Mostrar descrição de conquistas bloqueadas",
            "Menu vertical"
        ]

        # Adiciona opção do console se estiver ativo
        if self.console_ativo and "Manter console aberto" in self.options:
            if "Manter console aberto" in outros_keys:
                outros_keys.remove("Manter console aberto")
            outros_keys.append("Manter console aberto")

        self.draw_options(outros_keys, x, y)

        # Mensagem de reinicialização se necessário
        if self.precisa_reiniciar:
            restart_font = pygame.font.SysFont(None, 28)
            restart_text = restart_font.render("Reinicie o jogo para aplicar as mudanças de atualização", True, (200, 0, 0))
            restart_rect = restart_text.get_rect(center=(self.width // 2, self.height - 40))
            self.screen.blit(restart_text, restart_rect)

    def handle_event(self, event):
        """Processa eventos do menu de configurações"""
        if not self.visible:
            return False  # Retorna False se o menu não está ativo

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Fecha apenas o menu de configurações, sem afetar o resto
                self.visible = False
                return True  # indica que o evento foi consumido, mas não afeta outros menus
            return True

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            
            # Verificar clique no botão X para fechar
            if self.close_button_rect.collidepoint(mouse_pos):
                self.visible = False
                return True

            # Verificar clique nas opções
            for rect, key in self.button_rects:
                if rect.collidepoint(mouse_pos):
                    self.options[key] = not self.options[key]
                    self.save_config()

                    # Verificar se precisa reiniciar para atualizações
                    if key == "Verificar atualizações":
                        if self.options[key] != self.valor_original_update:
                            self.precisa_reiniciar = True
                        else:
                            self.precisa_reiniciar = False
                    return True

            return True

        return False  # <- ESSA LINHA é importante! Evita que ESC afete outros menus

    def show(self):
        """Mostra o menu de configurações"""
        self.visible = True
        self.valor_original_update = self.options.get("Verificar atualizações", True)
        self.precisa_reiniciar = False

    def hide(self):
        """Esconde o menu de configurações"""
        self.visible = False

    def toggle(self):
        """Alterna a visibilidade do menu"""
        if self.visible:
            self.hide()
        else:
            self.show()

    def get_click_settings(self):
        """Retorna um dicionário com as configurações de clique atuais"""
        return {
            "left_click": self.options.get("Clique Esquerdo", True),
            "right_click": self.options.get("Clique Direito", True),
            "middle_click": self.options.get("Clique Botão do Meio", False),
            "mouse_scroll": self.options.get("Rolagem do Mouse", False)
        }