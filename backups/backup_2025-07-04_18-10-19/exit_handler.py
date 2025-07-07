import pygame
import sys

class ExitHandler:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        self.active = False
        self.user_text = ""
        self.font = pygame.font.SysFont(None, 32)
        self.prompt_font = pygame.font.SysFont(None, 28)
        self.input_rect = pygame.Rect(width // 2 - 130, height // 2 + 10, 260, 40)  # Caixa maior e centralizada
        self.alpha = 0
        self.fading_out = False
        self.fade_speed = 8
        self.text_color = (255, 255, 255)
        self.box_color = (50, 100, 200)  # azul padrão como solicitado
        self.prompt = "Tem certeza que deseja sair? Digite 'sim' para confirmar:"

    def start(self):
        self.active = True
        self.user_text = ""
        self.alpha = 0
        self.fading_out = False

    def handle_event(self, event):
        if not self.active:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.user_text = self.user_text[:-1]
            elif event.key == pygame.K_RETURN:
                if self.user_text.lower().strip() == "sim":
                    self.fading_out = True
                else:
                    self.user_text = ""
            elif event.key == pygame.K_ESCAPE:
                self.active = False
            else:
                if len(self.user_text) < 20:
                    self.user_text += event.unicode
            return True
        return False

    def update_fade_out(self):
        if not self.fading_out:
            return False

        self.alpha += self.fade_speed
        if self.alpha > 255:
            self.alpha = 255

        fade_surface = pygame.Surface((self.width, self.height))
        fade_surface.set_alpha(self.alpha)
        fade_surface.fill((0, 0, 0))
        self.screen.blit(fade_surface, (0, 0))

        if self.alpha >= 255:
            pygame.quit()
            sys.exit()

        return True

    def draw(self):
        if not self.active:
            return

        # Fundo escuro transparente
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        # Caixa azul de entrada
        pygame.draw.rect(self.screen, self.box_color, self.input_rect, border_radius=8)

        # Prompt
        prompt_surf = self.prompt_font.render(self.prompt, True, self.text_color)
        prompt_rect = prompt_surf.get_rect(center=(self.width // 2, self.height // 2 - 20))
        self.screen.blit(prompt_surf, prompt_rect)

        # Texto digitado
        text_surf = self.font.render(self.user_text, True, self.text_color)
        text_rect = text_surf.get_rect(midleft=(self.input_rect.x + 10, self.input_rect.centery))
        self.screen.blit(text_surf, text_rect)

        # Cursor piscante
        if pygame.time.get_ticks() // 500 % 2 == 0 and self.active:
            cursor_x = text_rect.right + 3
            cursor_y_top = text_rect.top + 4
            cursor_y_bottom = text_rect.bottom - 4
            pygame.draw.line(self.screen, self.text_color, (cursor_x, cursor_y_top), (cursor_x, cursor_y_bottom), 2)
