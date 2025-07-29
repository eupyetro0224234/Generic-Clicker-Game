import pygame
import json
from datetime import datetime

class EventoManager:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        self.active_event = None
        self.event_bonus = 1
        self.font_large = pygame.font.SysFont(None, 36)
        self.font_small = pygame.font.SysFont(None, 24)
        self.last_check = 0
        self.check_interval = 60  # Verificar a cada 60 segundos

        # Carrega os eventos imediatamente
        self.load_events()
        self.check_events()

    def load_events(self):
        try:
            with open("eventos.json", "r", encoding="utf-8") as f:
                self.events = json.load(f)
        except FileNotFoundError:
            print("[ERRO] eventos.json não encontrado.")
            self.events = []
        except json.JSONDecodeError:
            print("[ERRO] JSON inválido em eventos.json.")
            self.events = []

    def check_events(self):
        now = datetime.now()
        current_date_str = now.strftime("%Y-%m-%d")
        current_time_str = now.strftime("%H:%M")
        
        previous_event = self.active_event
        self.active_event = None
        self.event_bonus = 1  # Bônus padrão

        for event in self.events:
            if not event.get("active", False):
                continue
                
            start_date = event.get("start_date")
            end_date = event.get("end_date")
            start_time = event.get("start_time", "00:00")
            end_time = event.get("end_time", "23:59")
            
            # Verifica se está dentro do período de datas
            if start_date <= current_date_str <= end_date:
                # Se for o primeiro dia, verifica o horário de início
                if current_date_str == start_date and current_time_str < start_time:
                    continue
                # Se for o último dia, verifica o horário de término
                if current_date_str == end_date and current_time_str > end_time:
                    continue
                    
                self.active_event = event
                self.event_bonus = event.get("bonus", 1)
                break

    def update(self, current_time):
        # Verifica eventos periodicamente
        if current_time - self.last_check > self.check_interval * 1000:  # ms para s
            self.check_events()
            self.last_check = current_time

    def draw(self):
        if not self.active_event:
            return

        # Configurações do retângulo do evento
        box_width = self.width - 40
        box_height = 80
        box_x = 20
        box_y = 20
        
        # Cor do evento (padrão: amarelo se não especificado)
        event_color = tuple(self.active_event.get("color", [255, 255, 0]))
        
        # Desenha o fundo do aviso
        pygame.draw.rect(self.screen, (30, 30, 50), 
                        (box_x, box_y, box_width, box_height), 
                        border_radius=10)
        pygame.draw.rect(self.screen, event_color, 
                        (box_x, box_y, box_width, box_height), 
                        2, border_radius=10)
        
        # Texto do título do evento
        title_text = self.font_large.render(
            f"EVENTO ATIVO: {self.active_event['name']} (x{self.event_bonus} PONTOS)", 
            True, 
            event_color
        )
        self.screen.blit(title_text, (box_x + 20, box_y + 15))
        
        # Texto do período do evento
        time_text = self.font_small.render(
            f"Período: {self.active_event['start_date']} {self.active_event['start_time']} até {self.active_event['end_date']} {self.active_event['end_time']}", 
            True, 
            (200, 200, 200)
        )
        self.screen.blit(time_text, (box_x + 20, box_y + 50))

    def get_current_bonus(self):
        return self.event_bonus

    def is_event_active(self):
        return self.active_event is not None