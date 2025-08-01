import pygame
import urllib.request
import json
from datetime import datetime
import time

class EventManager:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        self.events = []
        self.active_events = []
        self.event_bonus = 1
        self.visible = False
        self.notification = None
        self.EVENTS_JSON_URL = "https://raw.githubusercontent.com/eupyetro0224234/Generic-Clicker-Game/main/eventos.json"
        self.last_check = 0
        self.check_interval = 300  # 5 minutos
        self.close_button_rect = None
        self.close_button_hover = False
        
        # Configurações de estilo
        self.bg_color = (30, 30, 50, 200)
        self.box_color = (255, 255, 255)
        self.border_color = (150, 180, 230)
        self.text_color = (40, 40, 60)
        self.font_title = pygame.font.SysFont(None, 36)
        self.font_text = pygame.font.SysFont(None, 28)
        self.font_small = pygame.font.SysFont(None, 24)
        
        self.load_events()

    def load_events(self):
        try:
            with urllib.request.urlopen(self.EVENTS_JSON_URL, timeout=5) as response:
                data = response.read().decode('utf-8')
                self.events = json.loads(data)
        except (urllib.error.URLError, json.JSONDecodeError) as e:
            print(f"Erro ao carregar eventos do GitHub: {e}")
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

    def show_events_menu(self):
        self.visible = True

    def hide_events_menu(self):
        self.visible = False

    def draw_active_event_notice(self):
        if not self.has_active_events():
            return
            
        event = self.active_events[0]
        border_color = tuple(event.get("color", [255, 100, 100]))
        
        s = pygame.Surface((self.width - 40, 60), pygame.SRCALPHA)
        pygame.draw.rect(s, self.bg_color, (0, 0, s.get_width(), s.get_height()), border_radius=8)
        pygame.draw.rect(s, border_color, (0, 0, s.get_width(), s.get_height()), 2, border_radius=8)
        
        title = self.font_text.render(f"EVENTO ATIVO: {event['name']} (x{event['bonus']} pontos)", True, border_color)
        period = self.font_small.render(
            f"De {event['start_date']} {event['start_time']} até {event['end_date']} {event['end_time']}",
            True, (255, 255, 255)
        )
        
        s.blit(title, (10, 10))
        s.blit(period, (10, 35))
        self.screen.blit(s, (20, 20))

    def draw_events_menu(self):
        if not self.visible:
            return
            
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        
        box_width = self.width - 100
        box_height = self.height - 100
        box_x = 50
        box_y = 50
        
        pygame.draw.rect(self.screen, self.bg_color, 
                        (box_x, box_y, box_width, box_height),
                        border_radius=12)
        pygame.draw.rect(self.screen, self.border_color, 
                        (box_x, box_y, box_width, box_height),
                        2, border_radius=12)
        
        title_text = self.font_title.render("Eventos Ativos", True, self.text_color)
        title_rect = title_text.get_rect(center=(self.width // 2, box_y + 40))
        self.screen.blit(title_text, title_rect)
        
        if not self.active_events:
            no_events_text = self.font_text.render("Nenhum evento ativo", True, self.text_color)
            no_events_rect = no_events_text.get_rect(center=(self.width // 2, self.height // 2))
            self.screen.blit(no_events_text, no_events_rect)
        else:
            y_offset = box_y + 80
            for event in self.active_events:
                event_box = pygame.Rect(box_x + 30, y_offset, box_width - 60, 100)
                pygame.draw.rect(self.screen, self.box_color, event_box, border_radius=10)
                pygame.draw.rect(self.screen, self.border_color, event_box, 2, border_radius=10)
                
                event_color = tuple(event.get("color", [255, 100, 100]))
                
                name_text = self.font_text.render(event["name"], True, event_color)
                self.screen.blit(name_text, (event_box.x + 20, event_box.y + 15))
                
                bonus_text = self.font_text.render(f"Bônus: x{event['bonus']} pontos", True, self.text_color)
                self.screen.blit(bonus_text, (event_box.x + 20, event_box.y + 45))
                
                start_date = datetime.strptime(event['start_date'], "%Y-%m-%d").strftime("%d/%m/%Y")
                end_date = datetime.strptime(event['end_date'], "%Y-%m-%d").strftime("%d/%m/%Y")
                period_text = self.font_small.render(
                    f"De {start_date} {event['start_time']} até {end_date} {event['end_time']}",
                    True, (100, 100, 100))
                self.screen.blit(period_text, (event_box.x + 20, event_box.y + 75))
                
                y_offset += 110
        
        self.draw_close_button()

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
        pygame.draw.rect(self.screen, button_color, self.close_button_rect, border_radius=button_size // 2)

        border_color = (200, 40, 40) if self.close_button_hover else (180, 60, 60)
        pygame.draw.rect(self.screen, border_color, self.close_button_rect, width=2, border_radius=button_size // 2)

        if self.close_button_hover:
            shadow = pygame.Surface((button_size, button_size), pygame.SRCALPHA)
            pygame.draw.rect(shadow, (0, 0, 0, 30), (0, 0, button_size, button_size), border_radius=button_size // 2)
            self.screen.blit(shadow, self.close_button_rect.topleft)

        x_size = 20
        line_width = 3
        cx, cy = self.close_button_rect.center

        pygame.draw.line(self.screen, (255, 255, 255),
                         (cx - x_size // 2, cy - x_size // 2),
                         (cx + x_size // 2, cy + x_size // 2),
                         line_width)
        pygame.draw.line(self.screen, (255, 255, 255),
                         (cx + x_size // 2, cy - x_size // 2),
                         (cx - x_size // 2, cy + x_size // 2),
                         line_width)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.hide_events_menu()
            return True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.close_button_rect and self.close_button_rect.collidepoint(event.pos):
                self.hide_events_menu()
                return True
        return False