import pygame
import json
from datetime import datetime

class EventNotification:
    def __init__(self, screen, width, height, event):
        self.screen = screen
        self.width = width
        self.height = height
        self.event = event
        self.alpha = 255
        self.fade_out = False
        self.start_time = pygame.time.get_ticks()
        
        self.font_large = pygame.font.SysFont(None, 32)
        self.font_small = pygame.font.SysFont(None, 24)
        
        # Criar superfície para a notificação
        self.notification_surf = pygame.Surface((400, 120), pygame.SRCALPHA)
        
        # Desenhar a notificação
        event_color = tuple(self.event.get("color", [255, 100, 100]))
        
        # Fundo com gradiente
        for i in range(120):
            alpha = int(230 * (1 - i/240))
            pygame.draw.line(
                self.notification_surf, 
                (*event_color, alpha), 
                (0, i), 
                (400, i)
            )
        
        # Borda
        pygame.draw.rect(self.notification_surf, (255, 255, 255, 150), 
                        (0, 0, 400, 120), 2, border_radius=12)
        
        # Ícone de evento
        pygame.draw.circle(self.notification_surf, (255, 255, 255, 200), (60, 60), 30)
        event_icon = self.font_large.render("!", True, event_color)
        self.notification_surf.blit(event_icon, (60 - event_icon.get_width()//2, 60 - event_icon.get_height()//2))
        
        # Textos
        title = self.font_large.render("Novo Evento!", True, (255, 255, 255))
        self.notification_surf.blit(title, (120, 30))
        
        event_name = self.font_small.render(self.event["name"], True, (255, 255, 255))
        self.notification_surf.blit(event_name, (120, 60))
        
        bonus_text = self.font_small.render(f"Bônus: x{self.event['bonus']} pontos", True, (255, 255, 255))
        self.notification_surf.blit(bonus_text, (120, 85))

    def show(self):
        # Mostra a notificação por 3 segundos
        current_time = pygame.time.get_ticks()
        if current_time - self.start_time > 3000:
            self.fade_out = True
        
        if self.fade_out:
            self.alpha = max(0, self.alpha - 5)
            if self.alpha == 0:
                return False
        
        # Posiciona no canto superior direito
        pos_x = self.width - 420
        pos_y = 20
        
        temp_surf = self.notification_surf.copy()
        temp_surf.set_alpha(self.alpha)
        self.screen.blit(temp_surf, (pos_x, pos_y))
        
        return True

class EventsMenu:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        self.visible = False
        
        self.font_title = pygame.font.SysFont(None, 36)
        self.font_text = pygame.font.SysFont(None, 24)
        self.font_small = pygame.font.SysFont(None, 20)
        
        self.bg_color = (180, 210, 255, 230)
        self.box_color = (255, 255, 255)
        self.border_color = (150, 180, 230)
        self.text_color = (40, 40, 60)
        self.active_color = (100, 255, 100)
        
        self.padding = 20
        self.option_height = 40
        self.border_radius = 12
        
        self.close_button_rect = None
        self.notification_shown = False
        self.events = []
        self.load_events()

    def load_events(self):
        try:
            with open("eventos.json", "r", encoding="utf-8") as f:
                self.events = json.load(f)
                return True
        except (FileNotFoundError, json.JSONDecodeError):
            self.events = []
            return False

    def check_active_events(self):
        now = datetime.now()
        current_date_str = now.strftime("%Y-%m-%d")
        current_time_str = now.strftime("%H:%M")
        
        active_events = []
        
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
                    
                active_events.append(event)
                
                # Mostrar notificação apenas uma vez
                if not event.get("notification_shown", False):
                    notification = EventNotification(
                        self.screen,
                        self.width,
                        self.height,
                        event
                    )
                    notification.show()
                    event["notification_shown"] = True
                    self.save_events()
        
        return active_events

    def save_events(self):
        try:
            with open("eventos.json", "w", encoding="utf-8") as f:
                json.dump(self.events, f, indent=4)
        except Exception as e:
            print(f"Erro ao salvar eventos: {e}")

    def draw(self):
        if not self.visible:
            return
            
        # Fundo semi-transparente
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        
        # Caixa principal
        box_width = self.width - 100
        box_height = self.height - 100
        box_x = (self.width - box_width) // 2
        box_y = (self.height - box_height) // 2
        
        pygame.draw.rect(self.screen, self.bg_color, 
                        (box_x, box_y, box_width, box_height),
                        border_radius=self.border_radius)
        pygame.draw.rect(self.screen, self.border_color, 
                        (box_x, box_y, box_width, box_height),
                        2, border_radius=self.border_radius)
        
        # Título
        title_text = self.font_title.render("Eventos Ativos", True, self.text_color)
        title_rect = title_text.get_rect(center=(self.width // 2, box_y + 40))
        self.screen.blit(title_text, title_rect)
        
        # Lista de eventos
        active_events = self.check_active_events()
        if not active_events:
            no_events_text = self.font_text.render("Nenhum evento ativo no momento", True, self.text_color)
            no_events_rect = no_events_text.get_rect(center=(self.width // 2, self.height // 2))
            self.screen.blit(no_events_text, no_events_rect)
        else:
            y_offset = box_y + 80
            for event in active_events:
                # Caixa do evento
                event_box = pygame.Rect(box_x + 30, y_offset, box_width - 60, 80)
                pygame.draw.rect(self.screen, self.box_color, event_box, 
                                border_radius=self.border_radius)
                pygame.draw.rect(self.screen, self.border_color, event_box, 
                                2, border_radius=self.border_radius)
                
                # Cor do evento
                event_color = tuple(event.get("color", [255, 100, 100]))
                
                # Nome do evento
                name_text = self.font_text.render(event["name"], True, event_color)
                self.screen.blit(name_text, (event_box.x + 15, event_box.y + 10))
                
                # Bônus
                bonus_text = self.font_text.render(f"Bônus: x{event['bonus']} pontos", True, self.text_color)
                self.screen.blit(bonus_text, (event_box.x + 15, event_box.y + 35))
                
                # Período
                period_text = self.font_small.render(
                    f"De {event['start_date']} {event['start_time']} a {event['end_date']} {event['end_time']}",
                    True, (100, 100, 100)
                )
                self.screen.blit(period_text, (event_box.x + 15, event_box.y + 55))
                
                y_offset += 90
        
        # Botão de fechar
        close_button = pygame.Rect(
            self.width // 2 - 60,
            box_y + box_height - 60,
            120,
            40
        )
        pygame.draw.rect(self.screen, (200, 70, 70), close_button, border_radius=8)
        pygame.draw.rect(self.screen, (150, 50, 50), close_button, 2, border_radius=8)
        
        close_text = self.font_text.render("Fechar", True, (255, 255, 255))
        close_text_rect = close_text.get_rect(center=close_button.center)
        self.screen.blit(close_text, close_text_rect)
        
        self.close_button_rect = close_button

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.close_button_rect and self.close_button_rect.collidepoint(event.pos):
                self.visible = False
                return True
        return False

class EventManager:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        self.active_events = []
        self.event_bonus = 1
        self.events_menu = EventsMenu(screen, width, height)
        
    def check_events(self):
        self.active_events = self.events_menu.check_active_events()
        self.event_bonus = 1
        for event in self.active_events:
            self.event_bonus *= event.get("bonus", 1)
        
    def get_current_bonus(self):
        return self.event_bonus
    
    def show_events_menu(self):
        self.events_menu.visible = True
        
    def update(self):
        self.check_events()
        
    def draw(self):
        self.events_menu.draw()
        
    def handle_event(self, event):
        return self.events_menu.handle_event(event)