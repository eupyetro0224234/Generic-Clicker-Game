import pygame
import sys

class ExitHandler:
    def __init__(self, screen, width, height, font=None):
        self.screen = screen
        self.width = width
        self.height = height
        self.active = False
        self.input_text = ""
        self.font = font or pygame.font.SysFont(None, 36)
        self.bg_color = (40, 40, 60)
        self.text_color = (255, 255, 255)
        self.prompt_text = "Deseja sair? Digite 'sim' para confirmar ou 'não' para cancelar:"
        self.finished_fade = False
        self.fade_alpha = 0
        self.fade_speed = 8  # quanto maior, mais rápido

    def start(self):
        self.active = True
        self.input_text = ""
        self.finished_fade = False
        self.fade_alpha = 0

    def handle_event(self, event):
        if not self.active:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            elif event.key == pygame.K_RETURN:
                resposta = self.input_text.strip().lower()
                if resposta == "sim":
                    # inicia fade out
                    self.finished_fade = False
                elif resposta == "não" or resposta == "nao":
                    # cancelar saída
                    self.active = False
                    self.input_text = ""
            else:
                # Limita a entrada a letras e espaço
                if event.unicode.isalpha() or event.unicode == " ":
                    self.input_text += event.unicode
            return True
        return False

    def update(self):
        if not self.active:
            return False

        if self.finished_fade is False and self.input_text.strip().lower() == "sim":
            # faz o fade out
            self.fade_alpha += self.fade_speed
            if self.fade_alpha >= 255:
                self.fade_alpha = 255
                pygame.display.flip()
                pygame.time.delay(200)
                pygame.quit()
                sys.exit()
            return True
        return False

    def draw(self):
        if not self.active:
            return
        # Tela escura semi-transparente atrás
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(180)
        overlay.fill(self.bg_color)
        self.screen.blit(overlay, (0, 0))

        # Desenha prompt
        prompt_surf = self.font.render(self.prompt_text, True, self.text_color)
        prompt_rect = prompt_surf.get_rect(center=(self.width//2, self.height//2 - 30))
        self.screen.blit(prompt_surf, prompt_rect)

        # Desenha input_text
        input_display = self.input_text if self.input_text else "_"
        input_surf = self.font.render(input_display, True, self.text_color)
        input_rect = input_surf.get_rect(center=(self.width//2, self.height//2 + 20))
        self.screen.blit(input_surf, input_rect)

        # Desenha fade out
        if self.fade_alpha > 0:
            fade_surface = pygame.Surface((self.width, self.height))
            fade_surface.fill((0, 0, 0))
            fade_surface.set_alpha(self.fade_alpha)
            self.screen.blit(fade_surface, (0, 0))
