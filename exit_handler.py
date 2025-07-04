import pygame
import sys

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
                sys.exit()
            return True
        return False

    def draw_confirmation(self):
        if not self.confirming:
            return

        font = pygame.font.SysFont(None, 28)
        box_w, box_h = 360, 150
        box_x = (self.width - box_w) // 2
        box_y = (self.height - box_h) // 2
        box_rect = pygame.Rect(box_x, box_y, box_w, box_h)

        # Caixa
        pygame.draw.rect(self.screen, (240, 245, 255), box_rect, border_radius=12)
        pygame.draw.rect(self.screen, (80, 120, 255), box_rect, 2, border_radius=12)

        # Texto principal
        message = "Tem certeza que deseja sair?"
        text_surface = font.render(message, True, (20, 20, 40))
        text_rect = text_surface.get_rect(center=(self.width // 2, box_y + 45))
        self.screen.blit(text_surface, text_rect)

        # Botões
        btn_w, btn_h = 110, 36
        spacing = 30
        btn_y = box_y + box_h - btn_h - 20

        yes_rect = pygame.Rect(box_x + spacing, btn_y, btn_w, btn_h)
        no_rect = pygame.Rect(box_x + box_w - btn_w - spacing, btn_y, btn_w, btn_h)

        pygame.draw.rect(self.screen, (200, 80, 80), yes_rect, border_radius=10)
        pygame.draw.rect(self.screen, (80, 180, 120), no_rect, border_radius=10)

        yes_text = font.render("Sim", True, (255, 255, 255))
        no_text = font.render("Não", True, (255, 255, 255))

        self.screen.blit(yes_text, yes_text.get_rect(center=yes_rect.center))
        self.screen.blit(no_text, no_text.get_rect(center=no_rect.center))

    def handle_event(self, event):
        if not self.confirming:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            box_w, box_h = 360, 150
            box_x = (self.width - box_w) // 2
            box_y = (self.height - box_h) // 2

            btn_w, btn_h = 110, 36
            spacing = 30
            btn_y = box_y + box_h - btn_h - 20

            yes_rect = pygame.Rect(box_x + spacing, btn_y, btn_w, btn_h)
            no_rect = pygame.Rect(box_x + box_w - btn_w - spacing, btn_y, btn_w, btn_h)

            if yes_rect.collidepoint(mouse_pos):
                self.confirm_exit()
                return True
            elif no_rect.collidepoint(mouse_pos):
                self.cancel_exit()
                return True

        return False
