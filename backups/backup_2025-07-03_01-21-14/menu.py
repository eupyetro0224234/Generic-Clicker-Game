import pygame
import os
import urllib.request

class ConfigMenu:
    def __init__(self, screen, window_width, window_height, w=300, h=200):
        self.screen = screen
        self.rect = pygame.Rect(window_width - w - 20, 50, w, h)
        self.is_open = False
        self.font = pygame.font.SysFont(None, 32)
        self.bg_color = (180, 210, 255)
        self.shadow_color = (0, 0, 0, 50)
        self.square_size = 12
        self.color1 = (200, 220, 255, 60)
        self.color2 = (170, 200, 250, 60)

        # Pasta assets no LOCALAPPDATA
        localappdata = os.getenv("LOCALAPPDATA")
        self.assets_folder = os.path.join(localappdata, ".assests")
        os.makedirs(self.assets_folder, exist_ok=True)

        # Novo link do ícone de configurações
        self.icon_url = "https://i.postimg.cc/hGf3VRqY/image-removebg-preview-5.png"
        self.icon_path = os.path.join(self.assets_folder, "config_icon.png")

        # Baixa o ícone se ainda não existir
        if not os.path.isfile(self.icon_path):
            try:
                urllib.request.urlretrieve(self.icon_url, self.icon_path)
            except Exception as e:
                print("Erro ao baixar ícone de configurações:", e)

        self.icon_image = None
        try:
            self.icon_image = pygame.image.load(self.icon_path).convert_alpha()
            self.icon_image = pygame.transform.smoothscale(self.icon_image, (48, 48))
        except Exception as e:
            print("Erro ao carregar ícone:", e)

        self.icon_rect = self.icon_image.get_rect() if self.icon_image else pygame.Rect(0, 0, 48, 48)
        self.icon_rect.topright = (window_width - 20, 20)

    def draw_rounded_rect(self, surface, rect, color, radius=15):
        pygame.draw.rect(surface, color, rect, border_radius=radius)

    def draw_background(self):
        shadow_surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, self.shadow_color, (5, 5, self.rect.width, self.rect.height), border_radius=15)
        self.screen.blit(shadow_surf, (self.rect.x, self.rect.y))

        self.draw_rounded_rect(self.screen, self.rect, self.bg_color, radius=15)

        sq_surf = pygame.Surface((self.square_size, self.square_size), pygame.SRCALPHA)
        for i in range(0, self.rect.width, self.square_size):
            for j in range(0, self.rect.height, self.square_size):
                col = self.color1 if (i//self.square_size + j//self.square_size) % 2 == 0 else self.color2
                sq_surf.fill(col)
                self.screen.blit(sq_surf, (self.rect.x + i, self.rect.y + j))

    def draw_icon(self):
        if self.icon_image:
            self.screen.blit(self.icon_image, self.icon_rect)
        else:
            pygame.draw.rect(self.screen, (70,130,180), self.icon_rect)

    def draw_menu(self):
        if not self.is_open:
            return
        self.draw_background()
        title_surf = self.font.render("Configurações", True, (40, 40, 60))
        self.screen.blit(title_surf, (self.rect.x + 15, self.rect.y + 15))

        options = ["Volume: [•••••]", "Tema: Claro", "Outro: Placeholder"]
        for i, opt in enumerate(options):
            opt_surf = self.font.render(opt, True, (60, 60, 80))
            self.screen.blit(opt_surf, (self.rect.x + 15, self.rect.y + 60 + i*40))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.icon_rect.collidepoint(event.pos):
                self.is_open = not self.is_open
                return True
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
