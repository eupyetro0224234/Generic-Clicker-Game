import pygame, sys

class ExitHandler:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        self.active = False
        self.user_text = ""
        self.detected_console = False
        self.font = pygame.font.SysFont(None, 32)
        self.prompt_font = pygame.font.SysFont(None, 28)
        self.input_rect = pygame.Rect(self.width // 2 - 150, self.height // 2 + 10, 300, 40)
        self.bg_rect = pygame.Rect(self.width // 2 - 540, self.height // 2 - 60, 1080, 130)
        self.text_color = (40, 40, 60)
        self.bg_box_color = (180, 210, 255)
        self.box_color = (255, 255, 255)
        self.border_color = (200, 200, 200)
        self.fade_alpha = 0
        self.fade_speed = 20
        self.fade_in_complete = False
        self.fading_out = False
        self.exit_alpha = 0
        self.exit_speed = 15
        self.fading_cancel = False
        self.cancel_alpha = 0
        self.cancel_speed = 20
        self.prompt = "Tem certeza que deseja sair? Todos os trabalhadores ativos serão perdidos. Digite 'sim' para confirmar:"
        self.blur_surface = None
        self.pre_blurs = []

    def start(self):
        self.active = True
        self.user_text = ""
        self.detected_console = False
        self.fade_alpha = 0
        self.fade_in_complete = False
        self.fading_out = False
        self.exit_alpha = 0
        self.fading_cancel = False
        self.cancel_alpha = 0
        self.blur_surface = self.screen.copy()
        small = pygame.transform.smoothscale(self.blur_surface, (self.width // 8, self.height // 8))
        self.blur_surface = pygame.transform.smoothscale(small, (self.width, self.height))
        overlay = pygame.Surface((self.width, self.height))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(100)
        self.blur_surface.blit(overlay, (0, 0))
        self.blur_surface = self.blur_surface.convert_alpha()
        self.pre_blurs = []
        for alpha in range(0, 256, 25):
            temp = self.blur_surface.copy()
            temp.set_alpha(alpha)
            self.pre_blurs.append(temp)

    def handle_event(self, event):
        if not self.active:
            return False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not self.bg_rect.collidepoint(event.pos):
                self.fading_cancel = True
                return True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.user_text = self.user_text[:-1]
                return True
            elif event.key == pygame.K_RETURN:
                txt = self.user_text.strip().lower()
                if txt == "sim":
                    self.fading_out = True
                elif txt == "console":
                    self.detected_console = True
                    self.active = False
                return True
            elif event.key == pygame.K_ESCAPE:
                self.fading_cancel = True
                return True
            else:
                if len(event.unicode) == 1 and event.unicode.isprintable() and len(self.user_text) < 20:
                    self.user_text += event.unicode
                return True
        return False

    def update_fade_in(self):
        if not self.fade_in_complete:
            self.fade_alpha += self.fade_speed
            if self.fade_alpha >= 255:
                self.fade_alpha = 255
                self.fade_in_complete = True

    def update_fade_out_exit(self):
        if not self.fading_out:
            return False
        self.exit_alpha += self.exit_speed
        if self.exit_alpha > 255:
            self.exit_alpha = 255
        fade_surface = pygame.Surface((self.width, self.height))
        fade_surface.fill((0, 0, 0))
        fade_surface.set_alpha(self.exit_alpha)
        self.screen.blit(fade_surface, (0, 0))
        if self.exit_alpha >= 255:
            pygame.quit()
            sys.exit()
        return True

    def update_fade_out_cancel(self):
        if not self.fading_cancel:
            return False
        self.cancel_alpha += self.cancel_speed
        if self.cancel_alpha > 255:
            self.cancel_alpha = 255
        alpha = max(255 - self.cancel_alpha, 0)
        if self.blur_surface:
            index = min(len(self.pre_blurs) - 1, alpha // 25)
            self.screen.blit(self.pre_blurs[index], (0, 0))
        self._draw_box(alpha)
        if self.cancel_alpha >= 255:
            self.active = False
            self.fading_cancel = False
        return True

    def _draw_box(self, alpha):
        bg_surf = pygame.Surface((self.bg_rect.width, self.bg_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(bg_surf, (*self.bg_box_color, alpha), bg_surf.get_rect(), border_radius=20)
        self.screen.blit(bg_surf, self.bg_rect)
        prompt_surf = self.prompt_font.render(self.prompt, True, self.text_color)
        prompt_surf.set_alpha(alpha)
        prompt_rect = prompt_surf.get_rect(center=(self.width // 2, self.bg_rect.y + 40))
        self.screen.blit(prompt_surf, prompt_rect)
        input_surf = pygame.Surface((self.input_rect.width, self.input_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(input_surf, (*self.box_color, alpha), input_surf.get_rect(), border_radius=10)
        pygame.draw.rect(input_surf, (*self.border_color, alpha), input_surf.get_rect(), width=3, border_radius=10)
        self.screen.blit(input_surf, self.input_rect)
        if self.user_text:
            user_surface = self.font.render(self.user_text, True, self.text_color)
            user_surface.set_alpha(alpha)
            user_x = self.input_rect.x + 12
            user_y = self.input_rect.y + (self.input_rect.height - user_surface.get_height()) // 2
            self.screen.blit(user_surface, (user_x, user_y))

    def draw(self):
        if not self.active:
            return
        if self.fading_out:
            self.update_fade_out_exit()
            return
        if self.fading_cancel:
            self.update_fade_out_cancel()
            return
        self.update_fade_in()
        if self.blur_surface:
            index = min(len(self.pre_blurs) - 1, self.fade_alpha // 25)
            self.screen.blit(self.pre_blurs[index], (0, 0))
        self._draw_box(self.fade_alpha)
