import pygame
import os
import urllib.request

class Upgrade:
    def __init__(self, name, cost, multiplier):
        self.name = name
        self.cost = cost
        self.multiplier = multiplier
        self.purchased = False

class UpgradeMenu:
    def __init__(self, screen, window_width, window_height):
        self.screen = screen
        self.window_width = window_width
        self.window_height = window_height
        self.font = pygame.font.SysFont(None, 22)
        self.bg_color = (240, 210, 230)  # rosa claro
        self.border_color = (200, 120, 180)
        self.text_color = (50, 20, 50)

        self.upgrades = [
            Upgrade("Clique Dourado", 50, 2),
            Upgrade("Livro Encantado", 100, 3),
            Upgrade("Poção Mágica", 300, 5),
        ]

        # Tamanho e posição do menu fixo embaixo da tela
        self.menu_height = 140
        self.menu_rect = pygame.Rect(20, window_height - self.menu_height - 20, window_width - 40, self.menu_height)
        
        # Botão para abrir/fechar o menu
        self.button_size = 48
        self.button_rect = pygame.Rect(20, window_height - self.button_size - 10, self.button_size, self.button_size)

        # Ícone do botão
        self.icon_url = "https://i.postimg.cc/yxVZWpPk/image-removebg-preview-6.png"
        self.assets_folder = os.path.join(os.getenv("LOCALAPPDATA"), ".assests")
        os.makedirs(self.assets_folder, exist_ok=True)
        self.icon_path = os.path.join(self.assets_folder, "upgrades_icon.png")

        if not os.path.isfile(self.icon_path):
            try:
                urllib.request.urlretrieve(self.icon_url, self.icon_path)
            except Exception as e:
                print("Erro ao baixar ícone de upgrades:", e)

        try:
            self.icon_image = pygame.image.load(self.icon_path).convert_alpha()
            self.icon_image = pygame.transform.smoothscale(self.icon_image, (self.button_size, self.button_size))
        except Exception as e:
            print("Erro ao carregar ícone de upgrades:", e)
            self.icon_image = None

        self.visible = False

    def toggle_visible(self):
        self.visible = not self.visible

    def draw_button(self):
        # desenha o botão fixo
        if self.icon_image:
            self.screen.blit(self.icon_image, self.button_rect)
        else:
            pygame.draw.rect(self.screen, (200, 120, 180), self.button_rect)
            pygame.draw.rect(self.screen, (150, 80, 130), self.button_rect, 2)

    def draw(self, score):
        if not self.visible:
            return

        pygame.draw.rect(self.screen, self.bg_color, self.menu_rect, border_radius=12)
        pygame.draw.rect(self.screen, self.border_color, self.menu_rect, 2, border_radius=12)

        title = self.font.render("Upgrades Disponíveis", True, self.text_color)
        self.screen.blit(title, (self.menu_rect.x + 10, self.menu_rect.y + 10))

        for i, upgrade in enumerate(self.upgrades):
            y = self.menu_rect.y + 40 + i * 30
            status = "✓ Comprado" if upgrade.purchased else f"Custo: {upgrade.cost}"
            color = (100, 60, 110) if upgrade.purchased else (50, 20, 50)

            text_name = self.font.render(upgrade.name, True, self.text_color)
            text_status = self.font.render(status, True, color)

            self.screen.blit(text_name, (self.menu_rect.x + 20, y))
            self.screen.blit(text_status, (self.menu_rect.x + 180, y))

    def handle_event(self, event, score):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Clique no botão abrir/fechar
            if self.button_rect.collidepoint(event.pos):
                self.toggle_visible()
                return True, 0

            # Se menu não visível, não processa compra
            if not self.visible:
                return False, 0

            # Processa clique nos upgrades para comprar
            for i, upgrade in enumerate(self.upgrades):
                if upgrade.purchased:
                    continue
                y = self.menu_rect.y + 40 + i * 30
                upgrade_rect = pygame.Rect(self.menu_rect.x + 20, y, 250, 25)
                if upgrade_rect.collidepoint(event.pos):
                    if score >= upgrade.cost:
                        upgrade.purchased = True
                        return True, upgrade.multiplier
                    else:
                        # Sem pontos suficientes para comprar
                        return True, 0
        return False, 0

    def get_total_multiplier(self):
        mult = 1
        for upgrade in self.upgrades:
            if upgrade.purchased:
                mult *= upgrade.multiplier
        return mult

    def save_upgrades(self, filepath):
        data = [str(int(up.purchased)) for up in self.upgrades]
        with open(filepath, "w") as f:
            f.write(",".join(data))

    def load_upgrades(self, filepath):
        if not os.path.isfile(filepath):
            return
        with open(filepath, "r") as f:
            data = f.read().split(",")
        for i, val in enumerate(data):
            if i < len(self.upgrades):
                self.upgrades[i].purchased = bool(int(val))
