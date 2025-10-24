import pygame
import random
import os
import math

class Trabalhador:
    def __init__(self, screen, width, height, pontos_gerados=0, pontos_total=None):
        self.screen = screen
        self.window_width = width
        self.window_height = height
        self.pontos_total = pontos_total if pontos_total is not None else random.randint(100, 1000)
        self.pontos_gerados = pontos_gerados
        self.intervalo_geracao = 1000  # 1 segundo em milissegundos
        self.last_geracao_time = pygame.time.get_ticks()
        self.creation_time = pygame.time.get_ticks()  # Tempo de criação do trabalhador
        self.lifetime = 30000  # 30 segundos em milissegundos
        self.size_factor = 0.05
        self.icon = self._load_icon()
        self.pos = self._generate_random_position()
        self.speed = [random.choice([-2, -1, 1, 2]), random.choice([-2, -1, 1, 2])]
        self.active = True
        self.visible = True
        
        # Sistema de popups
        self.popups = []  # Lista de popups ativos: [texto, posição, tempo_restante]
        self.popup_duration = 1000  # 1 segundo
        self.popup_font = pygame.font.Font(None, 24)
        
        # Calcular pontos por segundo baseado no total e tempo
        self.pontos_por_segundo = self.pontos_total / 30  # Divide pelos 30 segundos

    @property
    def rect(self):
        """Retorna o retângulo atual do trabalhador, útil para colisões."""
        return pygame.Rect(self.pos[0], self.pos[1], self.icon.get_width(), self.icon.get_height())

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
            current_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(current_dir)
            assets_dir = os.path.join(parent_dir, "game_assets")
            icon_path = os.path.join(assets_dir, "trabalhador.png")
            if os.path.exists(icon_path):
                original_icon = pygame.image.load(icon_path).convert_alpha()
                new_width = int(original_icon.get_width() * self.size_factor)
                new_height = int(original_icon.get_height() * self.size_factor)
                return pygame.transform.smoothscale(original_icon, (new_width, new_height))
        except Exception as e:
            pass
        # Fallback: círculo verde se não encontrar imagem
        size = 30
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(surface, (0, 150, 0), (size//2, size//2), size//2)
        pygame.draw.circle(surface, (0, 200, 0), (size//2, size//2), size//2-3)
        return surface

    def _add_popup(self, pontos):
        """Adiciona um popup acima do trabalhador"""
        popup_text = f"+{int(pontos)}"  # Mostra a quantidade exata sem casas decimais
        popup_x = self.pos[0] + self.icon.get_width() // 2
        popup_y = self.pos[1] - 20  # Acima do trabalhador
        self.popups.append([popup_text, [popup_x, popup_y], self.popup_duration])

    def _update_popups(self, current_time):
        """Atualiza e remove popups expirados"""
        for popup in self.popups[:]:
            popup[2] -= 16  # Reduz tempo restante (assumindo ~60 FPS)
            if popup[2] <= 0:
                self.popups.remove(popup)
            else:
                # Move o popup para cima gradualmente
                popup[1][1] -= 0.5

    def _draw_popups(self):
        """Desenha todos os popups ativos"""
        for popup_text, pos, time_left in self.popups:
            # Calcula alpha baseado no tempo restante (fade out)
            alpha = min(255, int(255 * (time_left / 500)))
            text_surface = self.popup_font.render(popup_text, True, (0, 0, 0))
            
            # Cria uma superfície temporária para aplicar alpha
            temp_surface = pygame.Surface(text_surface.get_size(), pygame.SRCALPHA)
            temp_surface.fill((0, 0, 0, 0))
            text_surface.set_alpha(alpha)
            temp_surface.blit(text_surface, (0, 0))
            
            # Desenha centralizado na posição
            text_rect = temp_surface.get_rect(center=pos)
            self.screen.blit(temp_surface, text_rect)

    def update(self, current_time):
        if not self.active:
            return None

        # Atualizar popups
        self._update_popups(current_time)

        # Verificar se o trabalhador expirou (30 segundos)
        if current_time - self.creation_time >= self.lifetime:
            self.active = False
            self.visible = False
            # Retornar pontos restantes não gerados (se houver)
            pontos_restantes = self.pontos_total - self.pontos_gerados
            if pontos_restantes > 0:
                self.pontos_gerados = self.pontos_total
                return pontos_restantes
            return 0

        # Movimento do trabalhador na tela
        if self.icon:
            self.pos[0] += self.speed[0]
            self.pos[1] += self.speed[1]
            if self.pos[0] <= 0 or self.pos[0] >= self.window_width - self.icon.get_width():
                self.speed[0] = -self.speed[0]
            if self.pos[1] <= 0 or self.pos[1] >= self.window_height - self.icon.get_height():
                self.speed[1] = -self.speed[1]

        # Geração de pontos a cada segundo
        pontos_gerados_now = 0
        if current_time - self.last_geracao_time >= self.intervalo_geracao:
            # Calcular quantos segundos se passaram desde a última geração
            segundos_passados = (current_time - self.last_geracao_time) // 1000
            if segundos_passados > 0:
                # Garantir que não ultrapasse o total
                pontos_a_gerar = min(
                    self.pontos_por_segundo * segundos_passados, 
                    self.pontos_total - self.pontos_gerados
                )
                
                if pontos_a_gerar > 0:
                    pontos_gerados_now = math.ceil(pontos_a_gerar)  # Arredonda para cima
                    self.pontos_gerados += pontos_gerados_now
                    self.last_geracao_time = current_time
                    
                    # Adicionar popup com a quantidade EXATA gerada
                    if pontos_gerados_now > 0:
                        self._add_popup(pontos_gerados_now)

        return pontos_gerados_now if pontos_gerados_now > 0 else 0

    def draw(self):
        if not self.visible or not self.icon:
            return

        # Desenha o ícone do trabalhador
        self.screen.blit(self.icon, (self.pos[0], self.pos[1]))

        # Barra de progresso de tempo restante (amarela)
        bar_width = self.icon.get_width()
        tempo_decorrido = pygame.time.get_ticks() - self.creation_time
        tempo_progresso = max(0.0, 1.0 - (tempo_decorrido / self.lifetime))
        pygame.draw.rect(self.screen, (255, 255, 0), (self.pos[0], self.pos[1]-5, bar_width * tempo_progresso, 3))
        
        # Desenha os popups
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
        trabalhador.lifetime = state.get('lifetime', 30000)
        # Recalcular pontos por segundo baseado no estado salvo
        trabalhador.pontos_por_segundo = trabalhador.pontos_total / 30
        return trabalhador