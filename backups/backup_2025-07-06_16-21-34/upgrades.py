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

        try:
            img = pygame.image.load(self.icon_path).convert_alpha()
            self.button_size = 48
            self.icon_image = pygame.transform.smoothscale(img, (self.button_size, self.button_size))
        except Exception as e:
            print("Erro ao carregar ícone de upgrades:", e)
            self.icon_image = None
            self.button_size = 48

        self.button_rect = pygame.Rect(20, 90, self.button_size, self.button_size)

        self.upgrades = [
            {"name": "Upgrade 1", "desc": "+1 por clique", "cost": 10, "mult": 1, "bought": False},
            {"name": "Upgrade 2", "desc": "+2 por clique", "cost": 50, "mult": 2, "bought": False},
            {"name": "Upgrade 3", "desc": "+5 por clique", "cost": 200,"mult":5, "bought": False},
        ]

        self.font = pygame.font.SysFont(None, 24)
        self.menu_rect = pygame.Rect(20, 140, 300, 30 + len(self.upgrades)*30)

    def draw_button(self):
        if self.icon_image:
            self.screen.blit(self.icon_image, self.button_rect)
        else:
            pygame.draw.rect(self.screen, (200,100,200), self.button_rect)
            pygame.draw.rect(self.screen, (150,50,150), self.button_rect, 2)

    def draw(self, score):
        if not self.visible:
            return
        pygame.draw.rect(self.screen, (255,182,193), self.menu_rect, border_radius=10)
        pygame.draw.rect(self.screen, (200,150,180), self.menu_rect, 2, border_radius=10)
        self.screen.blit(self.font.render("Upgrades", True, (60,0,60)), (self.menu_rect.x+10, self.menu_rect.y+5))

        y = self.menu_rect.y + 30
        for up in self.upgrades:
            color = (50,20,50) if not up["bought"] else (100,100,100)
            self.screen.blit(self.font.render(f'{up["name"]} ({up["desc"]})', True, color),
                             (self.menu_rect.x+10, y))
            status = f'{"COMPRADO" if up["bought"] else up["cost"]}'
            self.screen.blit(self.font.render(status, True, color),
                             (self.menu_rect.x+200, y))
            y += 30

    def handle_event(self, event, score):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.button_rect.collidepoint(event.pos):
                self.visible = not self.visible
                return True, 0
            if not self.visible:
                return False, 0
            # loop upgrades
            y = self.menu_rect.y + 30
            for idx, up in enumerate(self.upgrades):
                rect = pygame.Rect(self.menu_rect.x+10, y, 280, 24)
                if rect.collidepoint(event.pos) and not up["bought"] and score >= up["cost"]:
                    up["bought"] = True
                    return True, up["mult"]
                y += 30
        return False, 0

    def get_click_multiplier(self):
        total = 1
        for up in self.upgrades:
            if up["bought"]:
                total += up["mult"]
        return total

    def save_upgrades(self, path):
        data = ",".join(str(int(up["bought"])) for up in self.upgrades)
        with open(path, "w") as f:
            f.write(data)

    def load_upgrades(self, path):
        if not os.path.isfile(path):
            return
        vals = open(path).read().split(",")
        for i, val in enumerate(vals):
            if i < len(self.upgrades):
                self.upgrades[i]["bought"] = bool(int(val))
