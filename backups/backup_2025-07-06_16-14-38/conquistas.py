import pygame
import time

class Achievement:
    def __init__(self, id, name, description, threshold):
        self.id = id
        self.name = name
        self.description = description
        self.threshold = threshold
        self.unlocked = False

class AchievementTracker:
    def __init__(self, screen):
        self.screen = screen
        self.achievements = [
            Achievement("first_click",   "Primeiro Clique", "Dê seu primeiro clique", 1),
            Achievement("ten_clicks",    "10 Cliques",      "Alcance 10 cliques",     10),
            Achievement("hundred_points","100 Pontos",      "Chegue a 100 pontos",    100),
        ]
        self.unlocked = set()
        self.popup_text = ""
        self.popup_time = 0.0
        self.popup_duration = 3.0
        self.font = pygame.font.SysFont(None, 28)
        self.bg_color = (255, 192, 203)

    def load_unlocked(self, saved_ids):
        for ach in self.achievements:
            if ach.id in saved_ids:
                ach.unlocked = True
                self.unlocked.add(ach.id)

    def check_unlock(self, score):
        for ach in self.achievements:
            if not ach.unlocked and score >= ach.threshold:
                ach.unlocked = True
                self.unlocked.add(ach.id)
                self.popup_text = f"Conquista desbloqueada: {ach.name}"
                self.popup_time = time.time()

    def draw_popup(self):
        if not self.popup_text:
            return
        elapsed = time.time() - self.popup_time
        if elapsed > self.popup_duration:
            self.popup_text = ""
            return

        w, h = 460, 50
        x = (self.screen.get_width() - w) // 2
        y = 80
        rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(self.screen, self.bg_color, rect, border_radius=12)
        pygame.draw.rect(self.screen, (200,150,150), rect, 2, border_radius=12)
        surf = self.font.render(self.popup_text, True, (60,20,60))
        self.screen.blit(surf, surf.get_rect(center=rect.center))

class AchievementsMenu:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        self.visible = False
        self.unlocked = set()  # atualizado pelo app.py

        self.title_font = pygame.font.SysFont(None, 36, bold=True)
        self.font = pygame.font.SysFont(None, 24)
        self.desc_font = pygame.font.SysFont(None, 20)
        self.bg_color = (245,225,240)
        self.text_color = (60,0,60)
        self.border_color = (180,150,180)

    def draw(self):
        if not self.visible:
            return

        w, h = 560, 340
        x = (self.width - w)//2
        y = (self.height - h)//2
        box = pygame.Rect(x,y,w,h)
        pygame.draw.rect(self.screen, self.bg_color, box, border_radius=16)
        pygame.draw.rect(self.screen, self.border_color, box, 2, border_radius=16)

        self.screen.blit(self.title_font.render("Conquistas", True, self.text_color), (x+20, y+20))

        start_y = y + 70
        line_h = 55
        # exibe na mesma ordem de definição
        for i, ach in enumerate(self.screen and []): pass
        for i, ach in enumerate(self.screen and []): break  # placeholder

        # CORREÇÃO: iterar via screen não faz sentido; vamos iterar passado pelo app
        # Em app.py, faça: menu.unlocked = tracker.unlocked; e menu.achievements = tracker.achievements
        # Aqui simplificamos exibindo conquest por ID:

        # Na integração com app.py, atribua em menu: menu.achievements = tracker.achievements
        for i, ach in enumerate(self.achievements):
            status = "✓" if ach.id in self.unlocked else "✗"
            color = (40,180,100) if ach.id in self.unlocked else (120,120,120)
            name = f"{status} {ach.name}"
            self.screen.blit(self.font.render(name, True, color), (x+30, start_y + i*line_h))
            self.screen.blit(self.desc_font.render(ach.description, True, (100,100,100)),
                             (x+50, start_y + i*line_h + 25))

    def handle_event(self, event):
        if not self.visible:
            return False
        if event.type == pygame.MOUSEBUTTONDOWN:
            w,h=560,340; x=(self.width-w)//2; y=(self.height-h)//2
            if not pygame.Rect(x,y,w,h).collidepoint(event.pos):
                self.visible=False; return True
        elif event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE:
            self.visible=False; return True
        return False
