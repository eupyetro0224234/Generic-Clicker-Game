import pygame
import os
import urllib.request

class UpgradesMenu:
    def __init__(self, screen, window_width, window_height):
        self.screen = screen
        self.visible = False

        self.window_width = window_width
        self.window_height = window_height

        self.assets_folder = os.path.join(os.getenv("LOCALAPPDATA"), ".assests")
        os.makedirs(self.assets_folder, exist_ok=True)

        self.icon_url = "https://i.postimg.cc/yxVZWpPk/image-removebg-preview-6.png"
        self.icon_path = os.path.join(self.assets_folder, "upgrades_icon.png")

        if not os.path.isfile(self.icon_path):
            try:
                urllib.request.urlretrieve(self.icon_url, self.icon_path)
            except Exception as e:
                print("Erro ao baixar ícone de upgrades:", e)

        self.icon_image = None
        try:
            self.icon_image = pygame.image.load(self.icon_path).convert_alpha()
            self.button_size = 48
            self.icon_image = pygame.transform.smoothscale(self.icon_image, (self.button_size, self.button_size))
        except Exception as e:
            print("Erro ao carregar ícone de upgrades:", e)

        # Posição botão abaixo da pontuação (exemplo: 20px da esquerda, 90px do topo)
        self.button_pos = (20, 90)
        self.button_rect = pygame.Rect(self.button_pos[0], self.button_pos[1], self.button_size, self.button_size)

        # Dados dos upgrades: nome, descrição, custo, bônus
        self.upgrades = [
            {"name": "Upgrade 1", "desc": "Aumenta cliques em +1", "cost": 10, "multiplier": 1, "purchased": False},
            {"name": "Upgrade 2", "desc": "Aumenta cliques em +2", "cost": 50, "multiplier": 2, "purchased": False},
            {"name": "Upgrade 3", "desc": "Aumenta cliques em +5", "cost": 200, "multiplier": 5, "purchased": False},
        ]

        self.font = pygame.font.SysFont(None, 24)

        # Dimensões do menu upgrades
        self.menu_width = 300
        self.menu_height = 200
        self.menu_x = 20
        self.menu_y = 140

    def draw_button(self):
        if self.icon_image:
            self.screen.blit(self.icon_image, self.button_pos)
        else:
            pygame.draw.rect(self.screen, (200, 100, 200), self.button_rect)  # rosa claro fallback

    def draw(self):
        # Fundo do menu
        menu_rect = pygame.Rect(self.menu_x, self.menu_y, self.menu_width, self.menu_height)
        pygame.draw.rect(self.screen, (255, 182, 193), menu_rect, border_radius=10)  # rosa claro

        # Título
        title_surf = self.font.render("Upgrades", True, (60, 0, 60))
        self.screen.blit(title_surf, (self.menu_x + 10, self.menu_y + 10))

        # Lista de upgrades
        y_offset = self.menu_y + 40
        for i, upg in enumerate(self.upgrades):
            color = (100, 50, 100) if not upg["purchased"] else (80, 80, 80)  # cinza se comprado
            text = f'{upg["name"]} - Custo: {upg["cost"]} pontos'
            text_surf = self.font.render(text, True, color)
            self.screen.blit(text_surf, (self.menu_x + 10, y_offset))

            status = "COMPRADO" if upg["purchased"] else "Comprar"
            status_color = (0, 150, 0) if not upg["purchased"] else (100, 100, 100)
            status_surf = self.font.render(status, True, status_color)
            status_rect = status_surf.get_rect(topright=(self.menu_x + self.menu_width - 10, y_offset))
            self.screen.blit(status_surf, status_rect)

            y_offset += 30

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not self.visible:
                return False

            mx, my = event.pos
            # Verifica se clicou num upgrade que não foi comprado
            y_start = self.menu_y + 40
            for i, upg in enumerate(self.upgrades):
                item_rect = pygame.Rect(self.menu_x + 10, y_start + i * 30, self.menu_width - 20, 24)
                if item_rect.collidepoint(mx, my) and not upg["purchased"]:
                    # Tenta comprar
                    return ("buy", i)
            return False
        return False

    def buy_upgrade(self, index, score):
        upg = self.upgrades[index]
        if score >= upg["cost"] and not upg["purchased"]:
            upg["purchased"] = True
            return True, score - upg["cost"]
        return False, score

    def get_click_multiplier(self):
        total = 1
        for upg in self.upgrades:
            if upg["purchased"]:
                total += upg["multiplier"]
        return total
