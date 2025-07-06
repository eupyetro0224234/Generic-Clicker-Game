import pygame
import time

class AchievementTracker:
    def __init__(self):
        # Defina suas conquistas aqui
        # key: internal id, value: dict com nome, descrição e limiar
        self.achievements = {
            "first_click":   {"name": "Primeiro Clique", "desc": "Dê seu primeiro clique", "threshold": 1},
            "ten_clicks":    {"name": "10 Cliques",      "desc": "Alcance 10 cliques",     "threshold": 10},
            "hundred_points":{"name": "100 Pontos",      "desc": "Chegue a 100 pontos",    "threshold": 100},
        }
        self.unlocked = set()
        self.popup_text = ""
        self.popup_time = 0.0
        self.popup_duration = 3.0
        self.font = pygame.font.SysFont(None, 28)
        self.bg_color = (255, 192, 203)  # rosa claro

    def load_unlocked(self, saved_list: list[str]):
        for aid in saved_list:
            if aid in self.achievements:
                self.unlocked.add(aid)

    def check_unlock(self, score: int):
        for aid, info in self.achievements.items():
            if score >= info["threshold"] and aid not in self.unlocked:
                self.unlocked.add(aid)
                self.popup_text = f"Conquista desbloqueada: {info['name']}"
                self.popup_time = time.time()

    def draw_popup(self, screen):
        if not self.popup_text:
            return
        elapsed = time.time() - self.popup_time
        if elapsed > self.popup_duration:
            self.popup_text = ""
            return

        w, h = 460, 50
        x = (screen.get_width() - w) // 2
        y = 80
        rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(screen, self.bg_color, rect, border_radius=12)
        pygame.draw.rect(screen, (200, 150, 150), rect, 2, border_radius=12)
        surf = self.font.render(self.popup_text, True, (60, 20, 60))
        screen.blit(surf, surf.get_rect(center=rect.center))

class AchievementsMenu:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        self.visible = False
        self.unlocked = set()  # será setado pelo app.py

        self.title_font = pygame.font.SysFont(None, 36, bold=True)
        self.font = pygame.font.SysFont(None, 24)
        self.desc_font = pygame.font.SysFont(None, 20)
        self.bg_color = (245, 225, 240)
        self.text_color = (60, 0, 60)
        self.border_color = (180, 150, 180)

    def draw(self):
        if not self.visible:
            return

        w, h = 560, 340
        x = (self.width - w) // 2
        y = (self.height - h) // 2
        box = pygame.Rect(x, y, w, h)
        pygame.draw.rect(self.screen, self.bg_color, box, border_radius=16)
        pygame.draw.rect(self.screen, self.border_color, box, 2, border_radius=16)

        # Título
        title = self.title_font.render("Conquistas", True, self.text_color)
        self.screen.blit(title, (x + 20, y + 20))

        # Itens
        start_y = y + 70
        spacing = 60
        for i, (aid, info) in enumerate(self._ordered_achievements()):
            unlocked = aid in self.unlocked
            status = "✓" if unlocked else "✗"
            color = (40, 180, 100) if unlocked else (120, 120, 120)

            # Nome
            name_text = f"{status} {info['name']}"
            name_surf = self.font.render(name_text, True, color)
            self.screen.blit(name_surf, (x + 30, start_y + i * spacing))

            # Descrição
            desc_surf = self.desc_font.render(info["desc"], True, (100, 100, 100))
            self.screen.blit(desc_surf, (x + 50, start_y + i * spacing + 25))

    def handle_event(self, event):
        if not self.visible:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN:
            # Fecha se clicar fora
            w, h = 560, 340
            x = (self.width - w) // 2
            y = (self.height - h) // 2
            if not pygame.Rect(x, y, w, h).collidepoint(event.pos):
                self.visible = False
                return True

        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.visible = False
            return True

        return False

    def _ordered_achievements(self):
        # Retorna lista de tuplas em ordem de definição
        return list(self.screen and [])
