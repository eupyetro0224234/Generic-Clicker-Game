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
        self.input_rect = pygame.Rect(width // 2 - 130, height // 2 + 50, 260, 40)  # subiu um pouco
        self.alpha = 0
        self.fading_out = False
        self.fade_speed = 8
        self.text_color = (40, 40, 60)
        self.prompt = "Tem certeza que deseja sair? Digite 'sim' para confirmar e 'esc' pra cancelar:"
        self.box_color = (255, 255, 255)
        self.bg_box_color = (180, 210, 255)

        # 🔹 Caixa aumentada verticalmente para suportar texto grande
        self.bg_rect = pygame.Rect(width // 2 - 340, height // 2 - 200, 680, 240)

    def start(self):
        self.active = True
        self.user_text = ""
        self.alpha = 0
        self.fading_out = False

    def handle_event(self, event):
        if not self.active:
            return False

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.user_text = self.user_text[:-1]
            elif event.key == pygame.K_RETURN:
                if self.user_text.strip().lower() == "sim":
                    self.fading_out = True
                else:
                    self.user_text = ""
            elif event.key == pygame.K_ESCAPE:
                self.active = False
            else:
                if len(event.unicode) == 1 and event.unicode.isprintable():
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

        pygame.draw.rect(self.screen, self.bg_box_color, self.bg_rect, border_radius=12)

        prompt_surface = self.prompt_font.render(self.prompt, True, self.text_color)
        prompt_rect = prompt_surface.get_rect(center=(self.width // 2, self.bg_rect.y + 40))
        self.screen.blit(prompt_surface, prompt_rect)

        pygame.draw.rect(self.screen, self.box_color, self.input_rect, border_radius=6)
        pygame.draw.rect(self.screen, (200, 200, 200), self.input_rect, 2, border_radius=6)

        user_text_surface = self.font.render(self.user_text, True, self.text_color)
        text_pos = self.input_rect.x + 10, self.input_rect.y + (self.input_rect.height - user_text_surface.get_height()) // 2
        self.screen.blit(user_text_surface, text_pos)
