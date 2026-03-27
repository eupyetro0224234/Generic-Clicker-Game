import pygame, random, math

class Trabalhador:
    _icon_cache = None
    _popup_font = None
    
    def __init__(self, screen, width, height, pontos_gerados=0, pontos_total=None):
        self.screen = screen
        self.window_width = width
        self.window_height = height
        self.pontos_total = pontos_total if pontos_total is not None else random.randint(100, 1200)
        self.pontos_gerados = pontos_gerados
        self.intervalo_geracao = 1000
        self.last_geracao_time = pygame.time.get_ticks()
        self.creation_time = pygame.time.get_ticks()
        self.lifetime = 30000
        self.size_factor = 0.05
        
        if Trabalhador._icon_cache is None:
            Trabalhador._icon_cache = self._load_icon()
        self.icon = Trabalhador._icon_cache
        
        if Trabalhador._popup_font is None:
            Trabalhador._popup_font = pygame.font.Font(None, 24)
        self.popup_font = Trabalhador._popup_font
        
        self.pos = self._generate_random_position()
        self.speed = [random.choice([-2, -1, 1, 2]), random.choice([-2, -1, 1, 2])]
        self.active = True
        self.visible = True
        
        self.popups = []
        self.popup_duration = 1000
        
        self.pontos_por_segundo = self.pontos_total / 30
        
        self._cached_bar_width = self.icon.get_width() if self.icon else 30
        self._cached_icon_size = (self.icon.get_width(), self.icon.get_height()) if self.icon else (30, 30)
        
        self._rect = pygame.Rect(self.pos[0], self.pos[1], self._cached_icon_size[0], self._cached_icon_size[1])

    @property
    def rect(self):
        self._rect.x = self.pos[0]
        self._rect.y = self.pos[1]
        return self._rect

    def get_state(self):
        return {
            'pontos_gerados': self.pontos_gerados,
            'pontos_total': self.pontos_total,
            'pos_x': self.pos[0],
            'pos_y': self.pos[1],
            'speed_x': self.speed[0],
            'speed_y': self.speed[1],
            'creation_time': self.creation_time,
            'lifetime': self.lifetime
        }

    def _generate_random_position(self):
        return [
            random.randint(100, self.window_width - 100),
            random.randint(100, self.window_height - 100)
        ]

    def _load_icon(self):
        try:
            from game_assets.game_assets_packed import load_image
            original_icon = load_image("trabalhador.png")
            new_width = int(original_icon.get_width() * self.size_factor)
            new_height = int(original_icon.get_height() * self.size_factor)
            return pygame.transform.smoothscale(original_icon, (new_width, new_height))
        except Exception:
            pass
        size = 30
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(surface, (0, 150, 0), (size//2, size//2), size//2)
        pygame.draw.circle(surface, (0, 200, 0), (size//2, size//2), size//2-3)
        return surface

    def _add_popup(self, pontos):
        popup_text = f"+{int(pontos)}"
        popup_x = self.pos[0] + self._cached_icon_size[0] // 2
        popup_y = self.pos[1] - 20
        self.popups.append([popup_text, [popup_x, popup_y], self.popup_duration])

    def _update_popups(self):
        for i in range(len(self.popups) - 1, -1, -1):
            popup = self.popups[i]
            popup[2] -= 16
            if popup[2] <= 0:
                self.popups.pop(i)
            else:
                popup[1][1] -= 0.5

    def _draw_popups(self):
        for popup_text, pos, time_left in self.popups:
            alpha = min(255, int(255 * (time_left / 500)))
            text_surface = self.popup_font.render(popup_text, True, (0, 0, 0))
            text_surface.set_alpha(alpha)
            text_rect = text_surface.get_rect(center=pos)
            self.screen.blit(text_surface, text_rect)

    def update(self, current_time):
        if not self.active:
            return None

        if self.lifetime is not None:
            if current_time - self.creation_time >= self.lifetime:
                self.active = False
                self.visible = False
                return None

        self._update_popups()

        self.pos[0] += self.speed[0]
        self.pos[1] += self.speed[1]
        
        icon_width, icon_height = self._cached_icon_size
        
        if self.pos[0] <= 0 or self.pos[0] >= self.window_width - icon_width:
            self.speed[0] = -self.speed[0]
            self.pos[0] = max(0, min(self.pos[0], self.window_width - icon_width))
        
        if self.pos[1] <= 0 or self.pos[1] >= self.window_height - icon_height:
            self.speed[1] = -self.speed[1]
            self.pos[1] = max(0, min(self.pos[1], self.window_height - icon_height))

        pontos_gerados_now = 0
        if current_time - self.last_geracao_time >= self.intervalo_geracao:
            milissegundos_passados = current_time - self.last_geracao_time
            segundos_passados = milissegundos_passados / 1000.0
            
            pontos_a_gerar = min(
                self.pontos_por_segundo * segundos_passados, 
                self.pontos_total - self.pontos_gerados
            )
                
            if pontos_a_gerar > 0:
                pontos_gerados_now = math.ceil(pontos_a_gerar)
                self.pontos_gerados += pontos_gerados_now
                self.last_geracao_time = current_time
                self._add_popup(pontos_gerados_now)

        return pontos_gerados_now

    def draw(self):
        if not self.visible or not self.icon:
            return

        self.screen.blit(self.icon, (self.pos[0], self.pos[1]))
        
        tempo_decorrido = pygame.time.get_ticks() - self.creation_time
        if self.lifetime:
            progresso = max(0.0, 1.0 - (tempo_decorrido / self.lifetime))
            bar_width = int(self._cached_bar_width * progresso)
            if bar_width > 0:
                pygame.draw.rect(self.screen, (255, 255, 0),
                                 (self.pos[0], self.pos[1] - 5, bar_width, 3))
        
        self._draw_popups()

    @classmethod
    def from_state(cls, screen, width, height, state):
        trabalhador = cls(
            screen=screen,
            width=width,
            height=height,
            pontos_gerados=state['pontos_gerados'],
            pontos_total=state['pontos_total']
        )
        trabalhador.pos = [state['pos_x'], state['pos_y']]
        trabalhador.speed = [state['speed_x'], state['speed_y']]
        trabalhador.creation_time = state.get('creation_time', pygame.time.get_ticks())
        trabalhador.lifetime = state.get('lifetime', 20000)
        trabalhador.pontos_por_segundo = trabalhador.pontos_total / 30
        return trabalhador
    
    @classmethod
    def clear_cache(cls):
        cls._icon_cache = None
        cls._popup_font = None