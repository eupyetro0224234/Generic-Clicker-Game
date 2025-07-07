import pygame

class ConfigMenu:
    def __init__(self, screen, x, y, w=300, h=200):
        self.screen = screen
        self.rect = pygame.Rect(x, y, w, h)
        self.is_open = False
        self.font = pygame.font.SysFont(None, 32)
        self.bg_color = (180, 210, 255)
        self.shadow_color = (0, 0, 0, 50)
        self.square_size = 12
        self.color1 = (200, 220, 255, 60)
        self.color2 = (170, 200, 250, 60)
        self.icon_rect = pygame.Rect(x - 50, y + 10, 40, 40)  # posição do botão ícone

    def draw_rounded_rect(self, surface, rect, color, radius=15):
        pygame.draw.rect(surface, color, rect, border_radius=radius)

    def draw_background(self):
        # sombra
        shadow_surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, self.shadow_color, (5, 5, self.rect.width, self.rect.height), border_radius=15)
        self.screen.blit(shadow_surf, (self.rect.x, self.rect.y))
        # fundo
        self.draw_rounded_rect(self.screen, self.rect, self.bg_color, radius=15)
        # quadradinhos sutis
        sq_surf = pygame.Surface((self.square_size, self.square_size), pygame.SRCALPHA)
        for i in range(0, self.rect.width, self.square_size):
            for j in range(0, self.rect.height, self.square_size):
                col = self.color1 if (i//self.square_size + j//self.square_size) % 2 == 0 else self.color2
                sq_surf.fill(col)
                self.screen.blit(sq_surf, (self.rect.x + i, self.rect.y + j))

    def draw_icon(self):
        # desenha um ícone de engrenagem simples no botão
        center = self.icon_rect.center
        radius = 15
        # círculo externo
        pygame.draw.circle(self.screen, (70, 130, 180), center, radius)
        pygame.draw.circle(self.screen, (230, 230, 250), center, radius - 5)
        # "dentes" simples da engrenagem
        for angle in range(0, 360, 45):
            end_x = center[0] + int(radius * 1.2 * pygame.math.Vector2(1, 0).rotate(angle).x)
            end_y = center[1] + int(radius * 1.2 * pygame.math.Vector2(1, 0).rotate(angle).y)
            pygame.draw.line(self.screen, (70, 130, 180), center, (end_x, end_y), 3)

    def draw_menu(self):
        if not self.is_open:
            return
        self.draw_background()
        # Título
        title_surf = self.font.render("Configurações", True, (40, 40, 60))
        self.screen.blit(title_surf, (self.rect.x + 15, self.rect.y + 15))

        # Opções de exemplo
        options = ["Volume: [•••••]", "Tema: Claro", "Outro: Placeholder"]
        for i, opt in enumerate(options):
            opt_surf = self.font.render(opt, True, (60, 60, 80))
            self.screen.blit(opt_surf, (self.rect.x + 15, self.rect.y + 60 + i*40))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.icon_rect.collidepoint(event.pos):
                self.is_open = not self.is_open
                return True  # evento consumido
            if self.is_open and not self.rect.collidepoint(event.pos):
                self.is_open = False
                return True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and self.is_open:
                self.is_open = False
                return True
        return False

    def is_icon_hovered(self):
        return self.icon_rect.collidepoint(pygame.mouse.get_pos())
