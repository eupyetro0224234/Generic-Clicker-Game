import pygame
import sys  # <--- ESSENCIAL

class ExitHandler:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        self.confirming = False
        self.fading_out = False
        self.alpha = 0
        self.overlay = pygame.Surface((width, height))
        self.overlay.fill((0, 0, 0))
        self.clock = pygame.time.Clock()

    def start_exit(self):
        self.confirming = True

    def cancel_exit(self):
        self.confirming = False

    def confirm_exit(self):
        self.fading_out = True

    def update_fade_out(self):
        if self.fading_out:
            self.alpha += 6
            self.overlay.set_alpha(self.alpha)
            self.screen.blit(self.overlay, (0, 0))
            pygame.display.flip()
            self.clock.tick(60)
            if self.alpha >= 255:
                pygame.quit()
                sys.exit()  # <---- aqui dava erro sem o import
            return True
        return False

    def draw_confirmation(self):
        if not self.confirming:
            return

        font = pygame.font.SysFont(None, 32)
        box_w, box_h = 300, 160
        box_x = (self.width - box_w) // 2
        box_y = (self.height - box_h) // 2
        box_rect = pygame.Rect(box_x, box_y, box_w, box_h)

        pygame.draw.rect(self.screen, (250, 250, 250), box_rect, border_radius=12)
        pygame.draw.rect(self.screen, (80, 80, 80), box_rect, 2, border_radius=12)

        text = font.render("Tem certeza que deseja sair?", True, (0, 0, 0))
        text_rect = text.get_rect(center=(self.width // 2, box_y + 40))
        self.screen.blit(text, text_rect)

        yes_rect = pygame.Rect(box_x + 40, box_y + 100, 80, 32)
        no_rect = pygame.Rect(box_x + 180, box_y + 100, 80, 32)

        pygame.draw.rect(self.screen, (220, 100, 100), yes_rect, border_radius=8)
        pygame.draw.rect(self.screen, (100, 180, 100), no_rect, border_radius=8)

        yes_text = font.render("Sim", True, (255, 255, 255))
        no_text = font.render("Não", True, (255, 255, 255))

        self.screen.blit(yes_text, yes_text.get_rect(center=yes_rect.center))
        self.screen.blit(no_text, no_text.get_rect(center=no_rect.center))

    def handle_event(self, event):
        if not self.confirming:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            box_w, box_h = 300, 160
            box_x = (self.width - box_w) // 2
            box_y = (self.height - box_h) // 2
            yes_rect = pygame.Rect(box_x + 40, box_y + 100, 80, 32)
            no_rect = pygame.Rect(box_x + 180, box_y + 100, 80, 32)

            if yes_rect.collidepoint(mouse_pos):
                self.confirm_exit()
                return True
            elif no_rect.collidepoint(mouse_pos):
                self.cancel_exit()
                return True

        return False
