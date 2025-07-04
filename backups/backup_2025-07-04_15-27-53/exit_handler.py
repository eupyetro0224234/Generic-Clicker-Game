# exit_handler.py

import pygame
import sys

class ExitHandler:
    def __init__(self, screen, fade_speed=10):
        self.screen = screen
        self.fading_out = False
        self.fade_alpha = 0
        self.fade_speed = fade_speed
        self.fade_surface = pygame.Surface(screen.get_size())
        self.fade_surface.fill((0, 0, 0))
        self.fade_surface.set_alpha(self.fade_alpha)

        self.confirm_exit = False

        self.btn_sim_rect = None
        self.btn_nao_rect = None

        self.font = pygame.font.SysFont(None, 24)

    def draw_confirm_exit(self):
        # Tela escurecida
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        w, h = 300, 140
        x = (self.screen.get_width() - w) // 2
        y = (self.screen.get_height() - h) // 2
        rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(self.screen, (255, 255, 255), rect, border_radius=12)
        pygame.draw.rect(self.screen, (0, 0, 0), rect, width=2, border_radius=12)

        msg_surf = self.font.render("Tem certeza que deseja sair?", True, (40, 40, 40))
        msg_rect = msg_surf.get_rect(center=(x + w // 2, y + 40))
        self.screen.blit(msg_surf, msg_rect)

        # Botões Sim e Não
        btn_w, btn_h = 80, 35
        btn_spacing = 40
        btn_y = y + h - 55

        self.btn_sim_rect = pygame.Rect(x + w // 2 - btn_w - btn_spacing//2, btn_y, btn_w, btn_h)
        self.btn_nao_rect = pygame.Rect(x + w // 2 + btn_spacing//2, btn_y, btn_w, btn_h)

        pygame.draw.rect(self.screen, (100, 200, 100), self.btn_sim_rect, border_radius=8)
        pygame.draw.rect(self.screen, (200, 100, 100), self.btn_nao_rect, border_radius=8)

        sim_text = self.font.render("Sim", True, (255, 255, 255))
        nao_text = self.font.render("Não", True, (255, 255, 255))

        self.screen.blit(sim_text, sim_text.get_rect(center=self.btn_sim_rect.center))
        self.screen.blit(nao_text, nao_text.get_rect(center=self.btn_nao_rect.center))

    def handle_event(self, event):
        if not self.confirm_exit:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.btn_sim_rect and self.btn_sim_rect.collidepoint(event.pos):
                self.fading_out = True
                self.confirm_exit = False
                return True
            elif self.btn_nao_rect and self.btn_nao_rect.collidepoint(event.pos):
                self.confirm_exit = False
                return True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.confirm_exit = False
                return True
        return False

    def start_confirm(self):
        self.confirm_exit = True

    def update_fade_out(self):
        if self.fading_out:
            self.fade_alpha += self.fade_speed
            if self.fade_alpha >= 255:
                pygame.quit()
                sys.exit()
            else:
                self.fade_surface.set_alpha(self.fade_alpha)
                self.screen.blit(self.fade_surface, (0, 0))
                pygame.display.flip()
                return True
        return False

    def draw(self):
        if self.confirm_exit:
            self.draw_confirm_exit()
        if self.fading_out:
            self.fade_surface.set_alpha(self.fade_alpha)
            self.screen.blit(self.fade_surface, (0, 0))
