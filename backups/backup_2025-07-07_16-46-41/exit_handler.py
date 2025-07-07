import pygame
import sys

class ExitHandler:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        self.active = False
        self.user_text = ""
        self.detected_console = False  # flag para detectar 'console'
        self.font = pygame.font.SysFont(None, 32)
        self.prompt_font = pygame.font.SysFont(None, 28)
        self.input_rect = pygame.Rect(0, 0, 300, 40)  # Largura um pouco maior para mais conforto
        self.alpha = 0
        self.fading_out = False
        self.fade_speed = 10
        self.text_color = (40, 40, 60)
        self.prompt = "Tem certeza que deseja sair? Digite 'sim' para confirmar, 'esc' para cancelar:"
        self.box_color = (255, 255, 255)
        self.bg_box_color = (180, 210, 255)
        self.bg_rect = pygame.Rect(
            self.width // 2 - 400,
            self.height // 2 - 60,
            800,
            130
        )

    def start(self):
        self.active = True
        self.user_text = ""
        self.detected_console = False
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
                txt = self.user_text.strip().lower()
                if txt == "sim":
                    self.fading_out = True
                elif txt == "console":
                    self.detected_console = True
                    self.active = False
                else:
                    self.user_text = ""
            elif event.key == pygame.K_ESCAPE:
                self.active = False
            else:
                if len(event.unicode) == 1 and event.unicode.isprintable() and len(self.user_text) < 20:
                    self.user_text += event.unicode
            return True
        return False

    def update_fade_out(self):
        if not self.fading_out:
            return False
        self.alpha = min(255, self.alpha + self.fade_speed)
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

        # Fundo da caixa com borda arredondada
        pygame.draw.rect(self.screen, self.bg_box_color, self.bg_rect, border_radius=16)

        # Texto do prompt centralizado horizontalmente na caixa, e com espaçamento vertical
        prompt_surf = self.prompt_font.render(self.prompt, True, self.text_color)
        prompt_rect = prompt_surf.get_rect(center=(self.width // 2, self.bg_rect.y + 40))
        self.screen.blit(prompt_surf, prompt_rect)

        # Caixa de entrada de texto
        self.input_rect.centerx = self.width // 2
        self.input_rect.top = prompt_rect.bottom + 15

        pygame.draw.rect(self.screen, self.box_color, self.input_rect, border_radius=8)
        pygame.draw.rect(self.screen, (200, 200, 200), self.input_rect, 3, border_radius=8)

        # Texto digitado pelo usuário, com pequeno padding horizontal e vertical alinhado ao centro verticalmente
        user_surface = self.font.render(self.user_text, True, self.text_color)
        user_x = self.input_rect.x + 12
        user_y = self.input_rect.y + (self.input_rect.height - user_surface.get_height()) // 2
        self.screen.blit(user_surface, (user_x, user_y))
