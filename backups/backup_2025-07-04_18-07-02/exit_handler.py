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

        self.bg_color = (180, 210, 255)  # azul parecido com outras caixas
        self.box_color = (180, 210, 255)  # mesma cor da caixa principal
        self.border_color = (100, 100, 100)
        self.text_color = (40, 40, 60)
        self.input_box_color = (210, 230, 255)  # azul clarinho para input
        self.input_border_color = (120, 120, 120)

        self.fade_alpha = 0
        self.fade_speed = 12
        self.fading_out = False

        self.box_width = 400
        self.box_height = 160
        self.box_rect = pygame.Rect(
            (self.width - self.box_width) // 2,
            (self.height - self.box_height) // 2,
            self.box_width,
            self.box_height
        )

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
                if len(self.input_text) < 10 and event.unicode.isalpha():
                    self.input_text += event.unicode.lower()
            return True

        return False

    def check_input(self):
        if self.input_text.strip() == "sim":
            self.fading_out = True
        elif self.input_text.strip() in ("não", "nao"):
            self.active = False
            self.input_text = ""

    def update_fade_out(self):
        if self.fading_out:
            self.fade_alpha += self.fade_speed
            if self.fade_alpha >= 255:
                pygame.display.flip()
                pygame.time.delay(200)
                pygame.quit()
                sys.exit()
            return True
        return False

    def draw(self):
        if not self.active:
            return

        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        self.screen.blit(overlay, (0, 0))

        pygame.draw.rect(self.screen, self.box_color, self.box_rect, border_radius=14)
        pygame.draw.rect(self.screen, self.border_color, self.box_rect, width=2, border_radius=14)

        title_text = self.title_font.render("Tem certeza que deseja sair?", True, self.text_color)
        title_rect = title_text.get_rect(center=(self.box_rect.centerx, self.box_rect.y + 40))
        self.screen.blit(title_text, title_rect)

        instr_text = self.font.render("Digite 'sim' para sair ou 'não' para cancelar:", True, self.text_color)
        instr_rect = instr_text.get_rect(center=(self.box_rect.centerx, self.box_rect.y + 75))
        self.screen.blit(instr_text, instr_rect)

        # Caixa input azul clara
        pygame.draw.rect(self.screen, self.input_box_color, self.input_rect, border_radius=6)
        pygame.draw.rect(self.screen, self.input_border_color, self.input_rect, width=2, border_radius=6)

        # Renderizar texto digitado e controlar overflow para não sair da caixa
        input_surface = self.font.render(self.input_text, True, self.text_color)
        max_width = self.input_rect.width - 20  # margem interna 10px dos dois lados

        # Se o texto for maior que a caixa, só mostra o final (rolagem para esquerda)
        if input_surface.get_width() > max_width:
            offset = input_surface.get_width() - max_width
            clip_rect = pygame.Rect(offset, 0, max_width, input_surface.get_height())
            self.screen.set_clip(self.input_rect)
            self.screen.blit(input_surface, (self.input_rect.x + 10 - offset, self.input_rect.y + (self.input_rect.height - input_surface.get_height()) // 2), clip_rect)
            self.screen.set_clip(None)
        else:
            self.screen.blit(input_surface, (self.input_rect.x + 10, self.input_rect.y + (self.input_rect.height - input_surface.get_height()) // 2))

        if self.fading_out:
            fade_surface = pygame.Surface((self.width, self.height))
            fade_surface.set_alpha(self.fade_alpha)
            fade_surface.fill((0, 0, 0))
            self.screen.blit(fade_surface, (0, 0))
