import pygame
import json
import urllib.request
from datetime import datetime
import os
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
        self.last_check = 0
        self.check_interval = 60
        self.notification = None
        self.bg_color = (180, 210, 255, 230)
        self.box_color = (255, 255, 255)
        self.border_color = (150, 180, 230)
        self.text_color = (40, 40, 60)
        self.font_title = pygame.font.SysFont(None, 36)
        self.font_text = pygame.font.SysFont(None, 28)
        self.font_small = pygame.font.SysFont(None, 24)
        self.EVENTS_JSON_URL = "https://raw.githubusercontent.com/eupyetro0224234/Generic-Clicker-Game/main/eventos.json"
        self.local_events_path = os.path.join(os.getenv("LOCALAPPDATA"), ".assets", "eventos.json")
        os.makedirs(os.path.dirname(self.local_events_path), exist_ok=True)
        self.close_button_rect = None
        self.close_button_hover = False
        self.load_events()
        self.check_events()

    def load_events(self):
        try:
            with urllib.request.urlopen(self.EVENTS_JSON_URL, timeout=5) as response:
                self.events = json.loads(response.read().decode())
                with open(self.local_events_path, 'w', encoding='utf-8') as f:
                    json.dump(self.events, f, indent=4)
        except Exception:
            try:
                if os.path.exists(self.local_events_path):
                    with open(self.local_events_path, 'r', encoding='utf-8') as f:
                        self.events = json.load(f)
                else:
                    self.events = []
            except Exception:
                self.events = []

    def check_events(self):
        now = datetime.now()
        current_date_str = now.strftime("%d/%m/%Y")
        current_time_str = now.strftime("%H:%M")
        
        self.active_events = []
        self.event_bonus = 1
        
        for event in self.events:
            if not event.get("active", False):
                continue
                
            start_date = datetime.strptime(event.get("start_date"), "%Y-%m-%d").strftime("%d/%m/%Y")
            end_date = datetime.strptime(event.get("end_date"), "%Y-%m-%d").strftime("%d/%m/%Y")
            start_time = event.get("start_time", "00:00")
            end_time = event.get("end_time", "23:59")
            
            date_check = datetime.strptime(current_date_str, "%d/%m/%Y") >= datetime.strptime(start_date, "%d/%m/%Y") and \
                        datetime.strptime(current_date_str, "%d/%m/%Y") <= datetime.strptime(end_date, "%d/%m/%Y")
            
            if date_check:
                if current_date_str == start_date and current_time_str < start_time:
                    continue
                if current_date_str == end_date and current_time_str > end_time:
                    continue
                    
                self.active_events.append(event)
                self.event_bonus *= event.get("bonus", 1)
                
                if not event.get("notification_shown", False):
                    self.notification = EventNotification(
                        self.screen,
                        self.width,
                        self.height,
                        event
                    )
                    event["notification_shown"] = True
                    self.save_events()

    def save_events(self):
        try:
            with open(self.local_events_path, 'w', encoding='utf-8') as f:
                json.dump(self.events, f, indent=4)
        except Exception:
            pass

    def show_events_menu(self):
        self.visible = True

    def update(self):
        current_time = time.time()
        if current_time - self.last_check > self.check_interval:
            self.check_events()
            self.last_check = current_time

        if self.notification and not self.notification.show():
            self.notification = None

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

    def draw(self):
        if self.notification:
            self.notification.show()

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

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.visible = False
            return True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.close_button_rect and self.close_button_rect.collidepoint(event.pos):
                self.visible = False
                return True
        return False

    def get_current_bonus(self):
        return self.event_bonus

    def is_event_active(self):
        return len(self.active_events) > 0


class EventNotification:
    def __init__(self, screen, width, height, event):
        self.screen = screen
        self.width = width
        self.height = height
        self.event = event
        self.alpha = 0
        self.fade_in = True
        self.fade_out = False
        self.start_time = pygame.time.get_ticks()
        self.font_large = pygame.font.SysFont(None, 32)
        self.font_small = pygame.font.SysFont(None, 24)
        self.notification_surf = pygame.Surface((400, 120), pygame.SRCALPHA)
        event_color = tuple(event.get("color", [255, 100, 100]))
        
        for i in range(120):
            alpha = int(200 * (1 - i/240))
            pygame.draw.line(
                self.notification_surf, 
                (*event_color, alpha), 
                (0, i), 
                (400, i)
            )
        
        pygame.draw.rect(self.notification_surf, (255, 255, 255, 150), 
                        (0, 0, 400, 120), 2, border_radius=12)
        
        pygame.draw.circle(self.notification_surf, (255, 255, 255, 200), (60, 60), 30)
        event_icon = self.font_large.render("!", True, event_color)
        self.notification_surf.blit(event_icon, (60 - event_icon.get_width()//2, 60 - event_icon.get_height()//2))
        
        title = self.font_large.render("Novo Evento!", True, (255, 255, 255))
        self.notification_surf.blit(title, (120, 20))
        
        event_name = self.font_small.render(self.event["name"], True, (255, 255, 255))
        self.notification_surf.blit(event_name, (120, 55))
        
        bonus_text = self.font_small.render(f"Bônus: x{self.event['bonus']} pontos", True, (255, 255, 255))
        self.notification_surf.blit(bonus_text, (120, 85))

    def show(self):
        current_time = pygame.time.get_ticks()
        
        if self.fade_in:
            self.alpha = min(255, self.alpha + 15)
            if self.alpha == 255:
                self.fade_in = False
                self.start_time = current_time
        
        elif current_time - self.start_time > 3000:
            self.fade_out = True
        
        if self.fade_out:
            self.alpha = max(0, self.alpha - 10)
            if self.alpha == 0:
                return False
        
        pos_x = self.width - 420
        pos_y = 20
        
        temp_surf = self.notification_surf.copy()
        temp_surf.set_alpha(self.alpha)
        self.screen.blit(temp_surf, (pos_x, pos_y))
        
        return True