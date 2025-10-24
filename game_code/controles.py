import pygame

class ControlsMenu:
    def __init__(self, screen, window_width, window_height, settings_menu):
        self.screen = screen
        self.settings_menu = settings_menu  # Referência ao menu de configurações
        self.font = pygame.font.SysFont(None, 22)
        self.bg_color = (180, 210, 255) 
        self.option_color = (255, 255, 255)
        self.option_border = (200, 220, 250)
        self.text_color = (40, 40, 60)

        self.option_height = 32
        self.option_radius = 10
        self.padding_x = 12
        self.padding_y = 8
        self.spacing = 6

        self.window_width = window_width
        self.window_height = window_height

        # Lista base de controles (todos os possíveis)
        self.all_controls = [
            ("Clique Esquerdo", "Aumenta pontos", "Clique Esquerdo"),
            ("Clique Direito", "Aumenta pontos", "Clique Direito"),
            ("Clique da rodinha do mouse", "Aumenta pontos", "Clique Botão do Meio"),
            ("Rolagem do botão mouse", "Aumenta pontos", "Rolagem do Mouse"),
            ("R", "Reseta pontos", None),  # Sempre visível
            ("ESC", "Fecha menus", None),  # Sempre visível
        ]

        self.visible = False
        self.controls_list = []  # Será preenchida com controles ativos
        self.last_config_state = None  # Para verificar mudanças nas configurações

        self.key_box_width = 220
        self.colon_space = 6
        self.text_space = 6

        # Atualizar a lista de controles baseado nas configurações
        self.update_controls_list()

    def update_controls_list(self):
        """Atualiza a lista de controles mostrados baseado nas configurações ativas"""
        # Verifica se as configurações mudaram
        current_config = self.get_current_config_state()
        if current_config == self.last_config_state:
            return  # Não atualiza se nada mudou
            
        self.last_config_state = current_config
        
        self.controls_list = []
        
        for key, desc, config_key in self.all_controls:
            # Se não tem config_key (como R e ESC), sempre mostra
            if config_key is None:
                self.controls_list.append((key, desc))
            # Se tem config_key, verifica se está ativo nas configurações
            elif self.settings_menu.get_option(config_key):
                self.controls_list.append((key, desc))
        
        # Recalcular dimensões do menu baseado nos controles ativos
        self._recalculate_dimensions()

    def get_current_config_state(self):
        """Obtém o estado atual das configurações relevantes para comparação"""
        if not hasattr(self.settings_menu, 'get_option'):
            return None
            
        return tuple(
            self.settings_menu.get_option(config_key) 
            for key, desc, config_key in self.all_controls 
            if config_key is not None
        )

    def _recalculate_dimensions(self):
        """Recalcula as dimensões do menu baseado nos controles ativos"""
        if not self.controls_list:
            self.width = 0
            self.height = 0
            return

        max_desc_width = 0
        for _, desc in self.controls_list:
            desc_width = self.font.size(desc)[0]
            if desc_width > max_desc_width:
                max_desc_width = desc_width

        self.width = (self.padding_x * 2 +
                      self.key_box_width +
                      self.colon_space + self.font.size(":")[0] +
                      self.text_space +
                      max_desc_width)

        total_options_height = len(self.controls_list) * self.option_height
        total_spacing_height = (len(self.controls_list) - 1) * self.spacing
        self.height = total_options_height + total_spacing_height + 2 * self.padding_y

        self.margin_x = 16
        self.margin_y = 24
        self.x = self.margin_x
        self.y = self.window_height - self.height - self.margin_y

        self.box_rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self):
        if not self.visible:
            return

        # Atualiza a lista de controles apenas se as configurações mudaram
        self.update_controls_list()

        # Se não há controles para mostrar, não desenha nada
        if not self.controls_list:
            return

        pygame.draw.rect(self.screen, self.bg_color, self.box_rect, border_radius=12)

        for i, (key, desc) in enumerate(self.controls_list):
            oy = self.y + self.padding_y + i * (self.option_height + self.spacing)

            key_rect = pygame.Rect(self.x + self.padding_x, oy, self.key_box_width, self.option_height)
            pygame.draw.rect(self.screen, self.option_color, key_rect, border_radius=self.option_radius)
            pygame.draw.rect(self.screen, self.option_border, key_rect, width=1, border_radius=self.option_radius)

            key_text = self.font.render(key, True, self.text_color)
            key_text_rect = key_text.get_rect(center=key_rect.center)
            self.screen.blit(key_text, key_text_rect)

            colon_text = self.font.render(":", True, self.text_color)
            colon_x = key_rect.right + self.colon_space + colon_text.get_width() // 2
            colon_y = key_rect.centery
            colon_rect = colon_text.get_rect(center=(colon_x, colon_y))
            self.screen.blit(colon_text, colon_rect)

            desc_text = self.font.render(desc, True, self.text_color)
            desc_x = colon_rect.right + self.text_space
            desc_text_rect = desc_text.get_rect(midleft=(desc_x, key_rect.centery))
            self.screen.blit(desc_text, desc_text_rect)

    def handle_event(self, event):
        if not self.visible:
            return False

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.visible = False
            return True

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if not self.box_rect.collidepoint(event.pos):
                return False

        return False

    def show(self):
        """Mostra o menu de controles, atualizando a lista primeiro"""
        self.update_controls_list()
        self.visible = True

    def hide(self):
        """Esconde o menu de controles"""
        self.visible = False

    def refresh(self):
        """Força uma atualização da lista de controles"""
        self.last_config_state = None  # Reseta o estado para forçar atualização
        self.update_controls_list()