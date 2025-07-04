import pygame
import sys

class ExitHandler:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        self.active = False
        self.input_text = ""
        self.font = pygame.font.SysFont(None, 28)
        self.title_font = pygame.font.SysFont(None, 36, bold=True)

        self.bg_color = (240, 240, 240)
        self.box_color = (255, 255, 255)
        self.border_color = (100, 100, 100)
        self.text_color = (40, 40, 60)
        self.input_box_color = (255, 255, 255)
        self.input_border_color = (120, 120, 120)

        self.fade_alpha = 0
        self.fade_speed = 12
        self.fading_out = False

        # Caixa centralizada e proporções do diálogo
        self.box_width = 400
        self.box_height = 160
        self.box_rect = pygame.Rect(
            (self.width - self.box_width) // 2,
            (self.height - self.box_height) // 2,
            self.box_width,
            self.box_height
        )

        # Caixa de input menor dentro da box principal
        self.input_rect = pygame.Rect(
            self.box_rect.x + 40,
            self.box_rect.y + 95,
            self.box_width - 80,
            36
        )

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
                self.check_input()
            else:
                # Permitir só letras e limitar tamanho
                if len(self.input_text) < 10 and event.unicode.isalpha():
                    self.input_text += event.unicode.lower()
            return True

        return False

    def check_input(self):
        # Se usuário digitar 'sim' fecha com fade out
        if self.input_text.strip() == "sim":
            self.fading_out = True
        elif self.input_text.strip() == "não" or self.input_text.strip() == "nao":
            self.active = False
            self.input_text = ""

    def update_fade_out(self):
        if self.fading_out:
            self.fade_alpha += self.fade_speed
            if self.fade_alpha >= 255:
                pygame.display.flip()
                pygame.time.delay(200)  # Pequena pausa para o fade ser notado
                pygame.quit()
                sys.exit()
            return True
        return False

    def draw(self):
        if not self.active:
            return

        # Fundo semitransparente
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        self.screen.blit(overlay, (0, 0))

        # Caixa principal
        pygame.draw.rect(self.screen, self.box_color, self.box_rect, border_radius=14)
        pygame.draw.rect(self.screen, self.border_color, self.box_rect, width=2, border_radius=14)

        # Título centralizado
        title_text = self.title_font.render("Tem certeza que deseja sair?", True, self.text_color)
        title_rect = title_text.get_rect(center=(self.box_rect.centerx, self.box_rect.y + 40))
        self.screen.blit(title_text, title_rect)

        # Texto instrução
        instr_text = self.font.render("Digite 'sim' para sair ou 'não' para cancelar:", True, self.text_color)
        instr_rect = instr_text.get_rect(center=(self.box_rect.centerx, self.box_rect.y + 75))
        self.screen.blit(instr_text, instr_rect)

        # Caixa de input
        pygame.draw.rect(self.screen, self.input_box_color, self.input_rect, border_radius=6)
        pygame.draw.rect(self.screen, self.input_border_color, self.input_rect, width=2, border_radius=6)

        # Texto digitado, alinhado com padding interno
        input_surface = self.font.render(self.input_text, True, self.text_color)
        input_pos = (self.input_rect.x + 10, self.input_rect.y + (self.input_rect.height - input_surface.get_height()) // 2)
        self.screen.blit(input_surface, input_pos)

        # Se estiver fazendo fade out, desenha um retângulo preto com alpha progressivo
        if self.fading_out:
            fade_surface = pygame.Surface((self.width, self.height))
            fade_surface.set_alpha(self.fade_alpha)
            fade_surface.fill((0, 0, 0))
            self.screen.blit(fade_surface, (0, 0))
