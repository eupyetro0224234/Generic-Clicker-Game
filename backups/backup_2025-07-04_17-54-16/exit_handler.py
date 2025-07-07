import pygame
import sys

class ExitHandler:
    def __init__(self, screen, window_width, window_height):
        self.screen = screen
        self.window_width = window_width
        self.window_height = window_height

        self.active = False
        self.fading_out = False

        self.fade_alpha = 0
        self.fade_speed = 8  # controle da velocidade do fade

        self.font = pygame.font.SysFont(None, 30)
        self.title_font = pygame.font.SysFont(None, 42, bold=True)

        self.input_text = ""
        self.input_active = False

        self.box_width = 350
        self.box_height = 140

        self.box_color = (180, 210, 255)
        self.border_color = (70, 130, 180)
        self.text_color = (40, 40, 60)
        self.input_bg_color = (255, 255, 255)
        self.input_border_color = (70, 130, 180)

        self.fade_surface = pygame.Surface((window_width, window_height))
        self.fade_surface.fill((0, 0, 0))
        self.fade_surface.set_alpha(self.fade_alpha)

        # Centraliza caixa
        self.box_rect = pygame.Rect(
            (window_width - self.box_width) // 2,
            (window_height - self.box_height) // 2,
            self.box_width,
            self.box_height
        )

        # Caixa de input dentro da box, com padding
        input_height = 36
        input_padding = 20
        self.input_rect = pygame.Rect(
            self.box_rect.x + input_padding,
            self.box_rect.y + self.box_height - input_height - input_padding,
            self.box_width - input_padding * 2,
            input_height
        )

    def open(self):
        self.active = True
        self.input_active = True
        self.input_text = ""
        self.fade_alpha = 0
        self.fading_out = False

    def close(self):
        self.active = False
        self.input_active = False
        self.input_text = ""
        self.fade_alpha = 0
        self.fading_out = False

    def handle_event(self, event):
        if not self.active:
            return False

        if event.type == pygame.KEYDOWN and self.input_active:
            if event.key == pygame.K_RETURN:
                # Resposta confirmada
                answer = self.input_text.strip().lower()
                if answer == "sim":
                    self.fading_out = True
                else:
                    self.close()
            elif event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            else:
                # Limitar tamanho do texto e aceitar apenas caracteres visíveis
                if len(self.input_text) < 10 and event.unicode.isprintable():
                    self.input_text += event.unicode
            return True

        return False

    def update_fade_out(self):
        if self.fading_out:
            self.fade_alpha += self.fade_speed
            if self.fade_alpha > 255:
                self.fade_alpha = 255
            self.fade_surface.set_alpha(self.fade_alpha)
            if self.fade_alpha >= 255:
                pygame.time.delay(200)
                pygame.quit()
                sys.exit()
            return True
        return False

    def draw(self):
        if not self.active:
            return

        # Fundo escurecido atrás da caixa
        overlay = pygame.Surface((self.window_width, self.window_height))
        overlay.set_alpha(120)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # Caixa principal
        pygame.draw.rect(self.screen, self.box_color, self.box_rect, border_radius=12)
        pygame.draw.rect(self.screen, self.border_color, self.box_rect, width=3, border_radius=12)

        # Texto principal
        title_surf = self.title_font.render("Deseja sair do jogo?", True, self.text_color)
        title_rect = title_surf.get_rect(center=(self.box_rect.centerx, self.box_rect.y + 40))
        self.screen.blit(title_surf, title_rect)

        # Texto da pergunta para digitar sim ou não
        prompt_text = "Digite 'sim' ou 'não' e pressione Enter:"
        prompt_surf = self.font.render(prompt_text, True, self.text_color)
        prompt_rect = prompt_surf.get_rect(midtop=(self.box_rect.centerx, title_rect.bottom + 12))
        self.screen.blit(prompt_surf, prompt_rect)

        # Caixa de input
        pygame.draw.rect(self.screen, self.input_bg_color, self.input_rect, border_radius=8)
        pygame.draw.rect(self.screen, self.input_border_color, self.input_rect, width=2, border_radius=8)

        # Texto do input
        input_surf = self.font.render(self.input_text, True, self.text_color)
        input_rect = input_surf.get_rect(midleft=(self.input_rect.x + 10, self.input_rect.centery))
        self.screen.blit(input_surf, input_rect)

        # Cursor piscante
        if self.input_active:
            if (pygame.time.get_ticks() // 500) % 2 == 0:
                cursor_x = input_rect.right + 3
                cursor_y = input_rect.top + 5
                cursor_height = input_rect.height - 10
                pygame.draw.rect(self.screen, self.text_color, (cursor_x, cursor_y, 3, cursor_height))

        # Desenha o fade em cima, se estiver em fade out
        if self.fading_out:
            self.screen.blit(self.fade_surface, (0, 0))
