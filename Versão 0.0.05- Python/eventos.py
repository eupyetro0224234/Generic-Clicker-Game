import pygame
import urllib.request
import json
from datetime import datetime
import time

class EventManager:
    def __init__(self, screen, window_width, window_height):
        self.screen = screen
        self.width = window_width
        self.height = window_height

        # Cores e estilo consistentes com FullSettingsMenu
        self.bg_color = (180, 210, 255, 220)
        self.text_color = (40, 40, 60)
        self.highlight_color = (100, 180, 255)
        self.option_height = 44
        self.option_radius = 12
        self.padding_x = 14
        self.padding_y = 14
        self.spacing_y = 14

        self.EVENTS_JSON_URL = "https://raw.githubusercontent.com/eupyetro0224234/Generic-Clicker-Game/main/eventos.json"
        self.events = []
        self.active_events = []
        self.event_bonus = 1
        self.visible = False
        self.last_check = 0
        self.check_interval = 300  # 5 minutos

        self.font_title = pygame.font.SysFont(None, 36)
        self.font_text = pygame.font.SysFont(None, 28)
        self.font_small = pygame.font.SysFont(None, 20)

        self.close_button_rect = None
        self.close_button_hover = False
        self.load_events()

    def load_events(self):
        try:
            with urllib.request.urlopen(self.EVENTS_JSON_URL, timeout=5) as response:
                data = response.read().decode('utf-8')
                self.events = json.loads(data)
        except Exception as e:
            print(f"Erro ao carregar eventos: {e}")
            self.events = []

    def check_events(self):
        now = time.time()
        if now - self.last_check < self.check_interval:
            return
            
        self.last_check = now
        self.load_events()
        
        now = datetime.now()
        current_date_str = now.strftime("%Y-%m-%d")
        current_time_str = now.strftime("%H:%M")
        
        self.active_events = []
        self.event_bonus = 1
        
        for event in self.events:
            if not event.get("active", False):
                continue
                
            start_date = event.get("start_date")
            end_date = event.get("end_date")
            start_time = event.get("start_time", "00:00")
            end_time = event.get("end_time", "23:59")
            
            if start_date <= current_date_str <= end_date:
                if current_date_str == start_date and current_time_str < start_time:
                    continue
                if current_date_str == end_date and current_time_str > end_time:
                    continue
                    
                self.active_events.append(event)
                self.event_bonus *= event.get("bonus", 1)

    def get_current_bonus(self):
        return self.event_bonus

    def has_active_events(self):
        return len(self.active_events) > 0

    def draw_close_button(self):
        button_size = 36
        margin = 20
        self.close_button_rect = pygame.Rect(
            self.width - button_size - margin,
            margin,
            button_size,
            button_size
        )

        mouse_pos = pygame.mouse.get_pos()
        self.close_button_hover = self.close_button_rect.collidepoint(mouse_pos)

        button_color = (255, 80, 80) if self.close_button_hover else (255, 120, 120)
        pygame.draw.rect(self.screen, button_color, self.close_button_rect, border_radius=button_size//2)

        border_color = (200, 40, 40) if self.close_button_hover else (180, 60, 60)
        pygame.draw.rect(self.screen, border_color, self.close_button_rect, width=2, border_radius=button_size//2)

        if self.close_button_hover:
            shadow = pygame.Surface((button_size, button_size), pygame.SRCALPHA)
            pygame.draw.rect(shadow, (0, 0, 0, 30), (0, 0, button_size, button_size), border_radius=button_size//2)
            self.screen.blit(shadow, self.close_button_rect.topleft)

        x_size = 20
        line_width = 3
        cx, cy = self.close_button_rect.center

        pygame.draw.line(self.screen, (255, 255, 255),
                         (cx - x_size//2, cy - x_size//2),
                         (cx + x_size//2, cy + x_size//2),
                         line_width)
        pygame.draw.line(self.screen, (255, 255, 255),
                         (cx + x_size//2, cy - x_size//2),
                         (cx - x_size//2, cy + x_size//2),
                         line_width)

    def draw_event_card(self, event, x, y, width):
        event_color = tuple(event.get("color", [100, 180, 255]))
        card_rect = pygame.Rect(x, y, width, 120)
        
        # Fundo do card
        pygame.draw.rect(self.screen, (255, 255, 255), card_rect, border_radius=self.option_radius)
        pygame.draw.rect(self.screen, (200, 200, 200), card_rect, width=2, border_radius=self.option_radius)
        
        # Barra de título colorida
        title_bar_rect = pygame.Rect(x, y, width, 40)
        pygame.draw.rect(self.screen, event_color, title_bar_rect, border_top_left_radius=self.option_radius, border_top_right_radius=self.option_radius)
        
        # Textos
        title = self.font_text.render(event["name"], True, (255, 255, 255))
        self.screen.blit(title, (x + 15, y + 10))
        
        bonus_text = self.font_text.render(f"Bônus: x{event['bonus']} pontos", True, self.text_color)
        self.screen.blit(bonus_text, (x + 15, y + 50))
        
        period_text = self.font_small.render(
            f"De {event['start_date']} {event['start_time']} até {event['end_date']} {event['end_time']}",
            True, (100, 100, 100))
        self.screen.blit(period_text, (x + 15, y + 80))
        
        return y + 130

    def draw(self):
        if not self.visible:
            if self.has_active_events():
                self.draw_active_event_notice()
            return

        # Fundo semi-transparente
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((*self.bg_color[:3], 200))
        self.screen.blit(overlay, (0, 0))

        self.draw_close_button()

        # Título
        title = self.font_title.render("Eventos Ativos", True, self.text_color)
        self.screen.blit(title, (self.width//2 - title.get_width()//2, 40))

        # Conteúdo
        content_y = 100
        content_width = self.width - 2 * self.padding_x

        if not self.active_events:
            no_events = self.font_text.render("Nenhum evento ativo no momento", True, self.text_color)
            self.screen.blit(no_events, (self.width//2 - no_events.get_width()//2, content_y))
        else:
            for event in self.active_events:
                content_y = self.draw_event_card(event, self.padding_x, content_y, content_width)
                content_y += self.spacing_y

    def draw_active_event_notice(self):
        if not self.has_active_events():
            return
            
        event = self.active_events[0]
        event_color = tuple(event.get("color", [100, 180, 255]))
        
        notice_width = 400
        notice_height = 80
        notice_x = self.width - notice_width - 20
        notice_y = 20
        
        # Fundo com sombra
        shadow = pygame.Surface((notice_width + 5, notice_height + 5), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0, 0, 0, 50), (5, 5, notice_width, notice_height), border_radius=8)
        self.screen.blit(shadow, (notice_x, notice_y))
        
        # Card de notificação
        notice_rect = pygame.Rect(notice_x, notice_y, notice_width, notice_height)
        pygame.draw.rect(self.screen, (255, 255, 255), notice_rect, border_radius=8)
        pygame.draw.rect(self.screen, event_color, notice_rect, width=2, border_radius=8)
        
        # Ícone
        pygame.draw.circle(self.screen, event_color, (notice_x + 40, notice_y + 40), 25)
        icon = self.font_title.render("!", True, (255, 255, 255))
        self.screen.blit(icon, (notice_x + 40 - icon.get_width()//2, notice_y + 40 - icon.get_height()//2))
        
        # Textos
        title = self.font_text.render(f"Evento Ativo: {event['name']}", True, self.text_color)
        self.screen.blit(title, (notice_x + 80, notice_y + 20))
        
        bonus = self.font_small.render(f"Bônus: x{event['bonus']} pontos", True, (100, 100, 100))
        self.screen.blit(bonus, (notice_x + 80, notice_y + 50))

    def handle_event(self, event):
        if not self.visible:
            return False

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.hide_events_menu()
            return True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.close_button_rect and self.close_button_rect.collidepoint(event.pos):
                self.hide_events_menu()
                return True

        return False

    def show_events_menu(self):
        self.visible = True
        self.check_events()

    def hide_events_menu(self):
        self.visible = False