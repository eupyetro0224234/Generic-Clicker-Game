import pygame
import os
import urllib.request

class UpgradeMenu:
    def __init__(self, screen, x, y):
        self.screen = screen
        self.x = x
        self.y = y
        self.width = 64
        self.height = 64

        # Pasta de assets
        localappdata = os.getenv("LOCALAPPDATA")
        self.assets_path = os.path.join(localappdata, ".assests")
        os.makedirs(self.assets_path, exist_ok=True)

        # Ícone do menu de upgrades
        self.icon_url = "https://i.postimg.cc/yxVZWpPk/image-removebg-preview-6.png"
        self.icon_path = os.path.join(self.assets_path, "upgrade_icon.png")
        if not os.path.isfile(self.icon_path):
            try:
                urllib.request.urlretrieve(self.icon_url, self.icon_path)
            except Exception as e:
                print("Erro ao baixar imagem de upgrade:", e)

        try:
            img = pygame.image.load(self.icon_path).convert_alpha()
            self.icon_image = pygame.transform.smoothscale(img, (self.width, self.height))
        except Exception as e:
            print("Erro ao carregar imagem de upgrade:", e)
            self.icon_image = None

        self.icon_rect = pygame.Rect(self.x, self.y, self.width, self.height)

        # Dados do único upgrade
        self.upgrade = {
            "name": "Incremento +0.1",
            "cost": 50,
            "bonus": 0.1,
            "bought": False
        }
        self.click_bonus = 0.0
        self.visible = False

        # Retângulo do painel de upgrades
        self.panel_rect = pygame.Rect(self.x, self.y + self.height + 10, 200, 60)
        self.font = pygame.font.SysFont(None, 20)

    def draw(self):
        # Desenha o ícone
        if self.icon_image:
            self.screen.blit(self.icon_image, self.icon_rect)
        else:
            pygame.draw.rect(self.screen, (200, 100, 200), self.icon_rect)
        # Se estiver visível, desenha o painel
        if self.visible:
            pygame.draw.rect(self.screen, (240, 210, 230), self.panel_rect, border_radius=8)
            pygame.draw.rect(self.screen, (180, 150, 180), self.panel_rect, 2, border_radius=8)

            name_s = self.font.render(self.upgrade["name"], True, (50, 20, 50))
            self.screen.blit(name_s, (self.panel_rect.x + 10, self.panel_rect.y + 5))

            status = "COMPRADO" if self.upgrade["bought"] else f"Custo: {self.upgrade['cost']}"
            status_s = self.font.render(status, True, (50, 20, 50))
            self.screen.blit(status_s, (self.panel_rect.x + 10, self.panel_rect.y + 30))

    def handle_event(self, event, score):
        """
        Retorna: (consumed: bool, delta_score: float)
         - consumed: se o evento foi consumido pelo menu
         - delta_score: valor a subtrair (custo) ou 0
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            # clique no ícone de abrir/fechar
            if self.icon_rect.collidepoint(event.pos):
                self.visible = not self.visible
                return True, 0.0

            if self.visible:
                # clique dentro do painel, tenta comprar
                if self.panel_rect.collidepoint(event.pos):
                    if (not self.upgrade["bought"]) and score >= self.upgrade["cost"]:
                        self.upgrade["bought"] = True
                        self.click_bonus += self.upgrade["bonus"]
                        return True, -self.upgrade["cost"]
                    return True, 0.0

        return False, 0.0

    def get_click_increment(self):
        # clique normal (1) + bônus acumulado
        return 1.0 + self.click_bonus
