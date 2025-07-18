import pygame
import random
import os
import math

class Trabalhador:
    def __init__(self, screen, width, height, remaining_time=None, pontos_gerados=0, pontos_total=None):
        self.screen = screen
        self.window_width = width
        self.window_height = height
        
        # Sistema de pontos progressivos
        self.pontos_total = pontos_total if pontos_total is not None else random.randint(3000, 5000)
        self.pontos_gerados = pontos_gerados
        self.intervalo_geracao = 1000  # Verifica a cada 1 segundo
        self.last_geracao_time = pygame.time.get_ticks()
        
        # Configuração visual
        self.size_factor = 0.05
        self.icon = self._load_icon()
        self.pos = self._generate_random_position()
        self.speed = [random.choice([-2, -1, 1, 2]), random.choice([-2, -1, 1, 2])]
        
        # Tempo de vida
        self.start_time = pygame.time.get_ticks()
        self.lifetime = remaining_time if remaining_time is not None else 60000  # 1 minuto ou tempo restante
        self.active = True
        self.visible = True

    def get_remaining_time(self):
        """Retorna o tempo restante de vida em milissegundos"""
        elapsed = pygame.time.get_ticks() - self.start_time
        return max(0, self.lifetime - elapsed)

    def get_state(self):
        """Retorna o estado atual do trabalhador para ser salvo"""
        return {
            'remaining_time': self.get_remaining_time(),
            'pontos_gerados': self.pontos_gerados,
            'pontos_total': self.pontos_total,
            'pos_x': self.pos[0],
            'pos_y': self.pos[1],
            'speed_x': self.speed[0],
            'speed_y': self.speed[1]
        }

    def _generate_random_position(self):
        """Gera uma posição aleatória na tela"""
        return [
            random.randint(100, self.window_width - 100),
            random.randint(100, self.window_height - 100)
        ]

    def _load_icon(self):
        """Carrega o ícone do trabalhador ou cria um fallback"""
        try:
            assets_dir = os.path.join(os.getenv("LOCALAPPDATA", "."), ".assets")
            icon_path = os.path.join(assets_dir, "trabalhador.png")
            
            if os.path.exists(icon_path):
                original_icon = pygame.image.load(icon_path).convert_alpha()
                new_width = int(original_icon.get_width() * self.size_factor)
                new_height = int(original_icon.get_height() * self.size_factor)
                return pygame.transform.smoothscale(original_icon, (new_width, new_height))
            
        except Exception as e:
            print(f"Erro ao carregar ícone: {e}")

        # Fallback visual
        size = 30
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(surface, (0, 150, 0), (size//2, size//2), size//2)
        pygame.draw.circle(surface, (0, 200, 0), (size//2, size//2), size//2-3)
        return surface

    def update(self, current_time):
        """
        Atualiza o trabalhador e retorna os pontos gerados
        Retorna None se o trabalhador expirou
        """
        if current_time - self.start_time > self.lifetime:
            # Gera os pontos restantes antes de morrer
            pontos_restantes = self.pontos_total - self.pontos_gerados
            self.pontos_gerados = self.pontos_total
            return pontos_restantes if pontos_restantes > 0 else None

        # Movimento
        if self.icon:
            self.pos[0] += self.speed[0]
            self.pos[1] += self.speed[1]

            # Colisão com bordas
            if self.pos[0] <= 0 or self.pos[0] >= self.window_width - self.icon.get_width():
                self.speed[0] = -self.speed[0]
            if self.pos[1] <= 0 or self.pos[1] >= self.window_height - self.icon.get_height():
                self.speed[1] = -self.speed[1]

        # Geração progressiva de pontos
        pontos_gerados_now = 0
        if current_time - self.last_geracao_time >= self.intervalo_geracao:
            tempo_decorrido = current_time - self.start_time
            progresso = min(1.0, tempo_decorrido / self.lifetime)
            
            pontos_devidos = math.floor(self.pontos_total * progresso)
            pontos_gerados_now = max(0, pontos_devidos - self.pontos_gerados)
            
            self.pontos_gerados += pontos_gerados_now
            self.last_geracao_time = current_time

        return pontos_gerados_now if pontos_gerados_now > 0 else 0

    def draw(self):
        """Desenha o trabalhador e sua barra de progresso"""
        if not self.visible or not self.icon:
            return

        # Desenha o ícone
        self.screen.blit(self.icon, (self.pos[0], self.pos[1]))

        # Barra de progresso (tempo e pontos)
        progresso = min(1.0, (pygame.time.get_ticks() - self.start_time) / self.lifetime)
        bar_width = self.icon.get_width()
        
        # Barra de tempo (verde)
        pygame.draw.rect(self.screen, (200, 200, 200), 
                         (self.pos[0], self.pos[1]-10, bar_width, 5))
        pygame.draw.rect(self.screen, (0, 200, 0), 
                         (self.pos[0], self.pos[1]-10, bar_width * (1 - progresso), 5))
        
        # Barra de pontos (azul)
        pontos_progresso = min(1.0, self.pontos_gerados / self.pontos_total)
        pygame.draw.rect(self.screen, (100, 100, 255), 
                         (self.pos[0], self.pos[1]-5, bar_width * pontos_progresso, 3))

    @classmethod
    def from_state(cls, screen, width, height, state):
        """Cria um novo trabalhador a partir de um estado salvo"""
        trabalhador = cls(
            screen=screen,
            width=width,
            height=height,
            remaining_time=state['remaining_time'],
            pontos_gerados=state['pontos_gerados'],
            pontos_total=state['pontos_total']
        )
        trabalhador.pos = [state['pos_x'], state['pos_y']]
        trabalhador.speed = [state['speed_x'], state['speed_y']]
        trabalhador.start_time = pygame.time.get_ticks()  # Reinicia o timer
        return trabalhador