import pygame

class ControlsMenu:
    def __init__(self, screen, window_width, window_height, settings_menu, upgrade_menu):
        self.screen = screen
        self.window_width = window_width
        self.window_height = window_height
        self.settings_menu = settings_menu
        self.upgrade_menu = upgrade_menu
        self.font = pygame.font.SysFont(None, 22)
        self.bg_color = (180, 210, 255, 180)
        self.option_color = (255, 255, 255, 220)
        self.option_border = (150, 180, 230, 160)
        self.text_color = (40, 40, 60)
        self.glass_highlight = (255, 255, 255, 60)
        self.option_height = 32
        self.option_radius = 10
        self.padding_x = 12
        self.padding_y = 8
        self.spacing = 6

        # Lista completa de controles (key, desc, config_key)
        # config_key pode ser None (sempre exibe) ou uma chave para condicionar a exibição
        self.all_controls = [
            ("Clique Esquerdo", "Aumenta pontos", "Clique Esquerdo"),
            ("Clique Direito", "Aumenta pontos", "Clique Direito"),
            ("Clique da rodinha do mouse", "Aumenta pontos", "Clique Botão do Meio"),
            ("Rolagem do botão mouse", "Aumenta pontos", "Rolagem do Mouse"),
            ("P", "Ativar / Desativar auto compra", "AUTO_COMPRA_TRABALHADOR"),
            ("C", "Mostrar / Ocultar controles", None),
            ("ESC", "Fecha menus", None),
            # As entradas "U" e "I" foram removidas conforme solicitado
        ]

        self.visible = False
        self.controls_list = []      # lista final de (key, desc) a ser desenhada
        self.last_config_state = None  # estado para detectar mudanças

        self.key_box_width = 220
        self.colon_space = 6
        self.text_space = 6

        self.update_controls_list()

    def update_controls_list(self):
        """Atualiza self.controls_list com base nas configurações atuais."""
        current_state = self.get_current_config_state()
        if current_state == self.last_config_state:
            # Nada mudou, não precisa reconstruir a lista
            return

        self.last_config_state = current_state
        self.controls_list = []

        for key, desc, config_key in self.all_controls:
            if config_key is None:
                # Controle sempre visível
                self.controls_list.append((key, desc))
                continue

            if config_key == "AUTO_COMPRA_TRABALHADOR":
                # Só exibe se o upgrade foi comprado
                if self.upgrade_menu.purchased.get("auto_compra_trabalhador", 0) > 0:
                    # Descrição dinâmica baseada no estado atual da auto-compra
                    if self.upgrade_menu.auto_compra_enabled:
                        real_desc = "Desativar auto-compra"
                    else:
                        real_desc = "Ativar auto-compra"
                    self.controls_list.append(("P", real_desc))
                continue

            # Controles condicionais baseados nas configurações do settings_menu
            if self.settings_menu.get_option(config_key):
                self.controls_list.append((key, desc))

        self._recalculate_dimensions()

    def get_current_config_state(self):
        """Retorna uma tupla com os estados que influenciam a lista de controles."""
        state = []

        for key, desc, config_key in self.all_controls:
            if config_key is None:
                continue

            if config_key == "AUTO_COMPRA_TRABALHADOR":
                # Estado importante: se o upgrade foi comprado e se está ativo
                purchased = self.upgrade_menu.purchased.get("auto_compra_trabalhador", 0) > 0
                enabled = self.upgrade_menu.auto_compra_enabled if purchased else False
                state.append((purchased, enabled))
            else:
                state.append(self.settings_menu.get_option(config_key))

        return tuple(state)

    def _recalculate_dimensions(self):
        """Recalcula as dimensões do menu com base no conteúdo atual."""
        if not self.controls_list:
            self.width = 0
            self.height = 0
            return

        max_desc_width = 0
        for _, desc in self.controls_list:
            desc_width = self.font.size(desc)[0]
            if desc_width > max_desc_width:
                max_desc_width = desc_width

        self.width = (self.padding_x * 2 + self.key_box_width +
                      self.colon_space + self.font.size(":")[0] +
                      self.text_space + max_desc_width)

        total_options_height = len(self.controls_list) * self.option_height
        total_spacing_height = (len(self.controls_list) - 1) * self.spacing
        self.height = total_options_height + total_spacing_height + 2 * self.padding_y

        self.margin_x = 16
        self.margin_y = 24
        self.x = self.margin_x
        self.y = self.window_height - self.height - self.margin_y
        self.box_rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def _draw_rounded_rect_aa(self, surface, color, rect, radius):
        """Desenha um retângulo arredondado com suavização."""
        temp_surface = pygame.Surface((rect[2] + 4, rect[3] + 4), pygame.SRCALPHA)
        temp_surface.fill((0, 0, 0, 0))

        temp_rect = pygame.Rect(2, 2, rect[2], rect[3])
        pygame.draw.rect(temp_surface, color, temp_rect, border_radius=radius)

        surface.blit(temp_surface, (rect[0] - 2, rect[1] - 2))

    def _create_glass_effect(self, width, height):
        """Cria o painel principal com efeito vidro."""
        glass_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        glass_surface.fill((0, 0, 0, 0))

        self._draw_rounded_rect_aa(glass_surface, self.bg_color, (0, 0, width, height), 20)

        highlight = pygame.Surface((width, height), pygame.SRCALPHA)
        highlight.fill((0, 0, 0, 0))
        for i in range(height):
            alpha = int(50 * (1 - i / height * 0.6))
            pygame.draw.line(highlight, (255, 255, 255, alpha), (0, i), (width, i))

        mask = pygame.Surface((width, height), pygame.SRCALPHA)
        mask.fill((0, 0, 0, 0))
        self._draw_rounded_rect_aa(mask, (255, 255, 255, 255), (0, 0, width, height), 20)

        highlight.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        glass_surface.blit(highlight, (0, 0))

        border_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        border_surface.fill((0, 0, 0, 0))
        self._draw_rounded_rect_aa(border_surface, (0, 0, 0, 0), (0, 0, width, height), 20)
        pygame.draw.rect(border_surface, self.option_border, (0, 0, width, height),
                         width=2, border_radius=20)
        glass_surface.blit(border_surface, (0, 0))

        return glass_surface

    def _create_glass_option(self, width, height, color):
        """Cria um item de opção com efeito vidro."""
        option_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        option_surface.fill((0, 0, 0, 0))

        self._draw_rounded_rect_aa(option_surface, color, (0, 0, width, height), 14)

        highlight = pygame.Surface((width, height), pygame.SRCALPHA)
        highlight.fill((0, 0, 0, 0))
        for i in range(height):
            alpha = int(40 * (1 - i / height * 0.7))
            pygame.draw.line(highlight, (255, 255, 255, alpha), (0, i), (width, i))

        mask = pygame.Surface((width, height), pygame.SRCALPHA)
        mask.fill((0, 0, 0, 0))
        self._draw_rounded_rect_aa(mask, (255, 255, 255, 255), (0, 0, width, height), 14)

        highlight.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        option_surface.blit(highlight, (0, 0))

        border_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        border_surface.fill((0, 0, 0, 0))
        self._draw_rounded_rect_aa(border_surface, (0, 0, 0, 0), (0, 0, width, height), 14)
        pygame.draw.rect(border_surface, self.option_border, (0, 0, width, height),
                         width=1, border_radius=14)
        option_surface.blit(border_surface, (0, 0))

        return option_surface

    def draw(self):
        """Desenha o menu na tela se estiver visível."""
        if not self.visible:
            return

        self.update_controls_list()  # Atualiza caso haja mudanças

        if not self.controls_list:
            return

        panel = self._create_glass_effect(self.width, self.height)

        for i, (key, desc) in enumerate(self.controls_list):
            oy = self.padding_y + i * (self.option_height + self.spacing)

            key_width = self.key_box_width
            option_surface = self._create_glass_option(key_width, self.option_height, self.option_color)
            panel.blit(option_surface, (self.padding_x, oy))

            key_text = self.font.render(key, True, self.text_color)
            key_text_rect = key_text.get_rect(center=(self.padding_x + key_width // 2, oy + self.option_height // 2))
            panel.blit(key_text, key_text_rect)

            colon_text = self.font.render(":", True, self.text_color)
            colon_x = self.padding_x + key_width + self.colon_space + colon_text.get_width() // 2
            colon_y = oy + self.option_height // 2
            colon_rect = colon_text.get_rect(center=(colon_x, colon_y))
            panel.blit(colon_text, colon_rect)

            desc_text = self.font.render(desc, True, self.text_color)
            desc_x = colon_rect.right + self.text_space
            desc_text_rect = desc_text.get_rect(midleft=(desc_x, oy + self.option_height // 2))
            panel.blit(desc_text, desc_text_rect)

        self.screen.blit(panel, (self.x, self.y))

    def handle_event(self, event):
        """Processa eventos do menu (teclas, mouse)."""
        if not self.visible:
            return False

        # REMOVER esse bloco:
        # if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
        #     self.visible = False
        #     return True

        if event.type == pygame.MOUSEBUTTONDOWN:
            if not self.box_rect.collidepoint(event.pos):
                return False

        return False

    def toggle(self):
        """Alterna a visibilidade do menu de controles."""
        self.visible = not self.visible
        if self.visible:
            self.update_controls_list()

    def show(self):
        """Exibe o menu."""
        self.update_controls_list()
        self.visible = True

    def hide(self):
        """Esconde o menu."""
        self.visible = False

    def refresh(self):
        """Força a atualização do menu."""
        self.last_config_state = None
        self.update_controls_list()