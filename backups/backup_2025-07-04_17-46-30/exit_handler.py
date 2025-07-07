import pygame
import sys

class ExitHandler:
    def __init__(self, screen, window_width, window_height):
        self.screen = screen
        self.window_width = window_width
        self.window_height = window_height
        self.active = False
        self.input_text = ""
        self.font = pygame.font.SysFont(None, 28)
        self.title_font = pygame.font.SysFont(None, 36, bold=True)
        self.bg_color = (180, 210, 255)
        self.box_color = (255, 255, 255)
        self.box_border_color = (100, 140, 220)
        self.text_color = (40, 40, 60)
        self.fade_surface = pygame.Surface((window_width, window_height))
        self.fade_surface.fill((0, 0, 0))
        self.fade_alpha = 0
        self.fading_out = False
        self.fade_speed = 5

        # Caixa texto
        self.input_box_rect = pygame.Rect(window_width // 2 - 100, window_height // 2 + 40, 200, 36)

    def start(self):
        self.active = True
        self.input_text = ""
        self.fade_alpha = 0
        self.fading_out = False

    def handle_event(self, event):
        if not self.active:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            elif event.key == pygame.K_RETURN:
                self._process_input()
            else:
                # Limitar o input a caracteres visíveis simples
                if len(event.unicode) == 1 and event.unicode.isprintable():
                    self.input_text += event.unicode.lower()
            return True

        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Clicar fora da caixa fecha o menu? Não, só ignora.
            # Poderia implementar clique fora para cancelar, se quiser.
            return True

        return False

    def _process_input(self):
        text = self.input_text.strip().lower()
        if text == "sim":
            self.fading_out = True
        elif text == "não" or text == "nao":
            self.active = False
            self.input_text = ""
        else:
            # texto inválido, só limpa para tentar de novo
            self.input_text = ""

    def update_fade_out(self):
        if self.fading_out:
            self.fade_alpha += self.fade_speed
            if self.fade_alpha >= 255:
                self.fade_alpha = 255
                pygame.display.update()
                pygame.time.delay(200)
                pygame.quit()
                sys.exit()
            return True
        return False

    def draw(self):
        if not self.active:
            return

        # Fundo semitransparente
        overlay = pygame.Surface((self.window_width, self.window_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        self.screen.blit(overlay, (0, 0))

        # Caixa principal
        box_w, box_h = 360, 140
        box_x = self.window_width // 2 - box_w // 2
        box_y = self.window_height // 2 - box_h // 2

        pygame.draw.rect(self.screen, self.bg_color, (box_x, box_y, box_w, box_h), border_radius=14)
        pygame.draw.rect(self.screen, self.box_border_color, (box_x, box_y, box_w, box_h), width=2, border_radius=14)

        # Texto título
        title_surf = self.title_font.render("Tem certeza que deseja sair?", True, self.text_color)
        title_rect = title_surf.get_rect(center=(self.window_width // 2, box_y + 40))
        self.screen.blit(title_surf, title_rect)

        # Caixa de texto
        pygame.draw.rect(self.screen, self.box_color, self.input_box_rect, border_radius=8)
        pygame.draw.rect(self.screen, self.box_border_color, self.input_box_rect, width=2, border_radius=8)

        # Texto digitado
        input_surf = self.font.render(self.input_text, True, self.text_color)
        input_rect = input_surf.get_rect(midleft=(self.input_box_rect.x + 10, self.input_box_rect.centery))
        self.screen.blit(input_surf, input_rect)

        # Texto dica
        hint_surf = self.font.render("Digite 'sim' ou 'não' e pressione Enter", True, self.text_color)
        hint_rect = hint_surf.get_rect(center=(self.window_width // 2, box_y + box_h - 30))
        self.screen.blit(hint_surf, hint_rect)

        # Desenha fade out se estiver
        if self.fading_out:
            self.fade_surface.set_alpha(self.fade_alpha)
            self.screen.blit(self.fade_surface, (0, 0))
