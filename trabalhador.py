import pygame
import random
import os

class Trabalhador:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        self.active = False
        self.start_time = 0
        self.duration = 60 * 1000  # 1 minuto em ms
        self.total_points_to_give = 0
        self.points_given = 0
        self.speed = 3
        self.last_update_time = 0
        self.last_ended_time = 0

        self.image = self._load_image_with_absolute_fallback()
        self.pos = [random.randint(0, width), random.randint(0, height)]
        self.direction = [random.choice([-1, 1]), random.choice([-1, 1])]

    def _load_image_with_absolute_fallback(self):
        possible_paths = [
            os.path.join(os.getenv('LOCALAPPDATA', ''), '.assets', 'trabalhador.png'),
            os.path.join('assets', 'trabalhador.png'),
            os.path.join(os.path.dirname(__file__), 'assets', 'trabalhador.png'),
            'trabalhador.png'
        ]

        for path in possible_paths:
            try:
                if os.path.exists(path):
                    img = pygame.image.load(path).convert_alpha()
                    base_size = 64
                    width = img.get_width()
                    height = img.get_height()
                    scale = base_size / max(width, height)
                    return pygame.transform.smoothscale(img, (int(width * scale), int(height * scale)))
            except:
                continue

        surf = pygame.Surface((64, 64), pygame.SRCALPHA)
        pygame.draw.circle(surf, (200, 100, 50), (32, 32), 30)
        pygame.draw.circle(surf, (160, 80, 40), (32, 32), 15)
        font = pygame.font.SysFont('Arial', 24, bold=True)
        text = font.render("W", True, (255, 255, 255))
        surf.blit(text, (32 - text.get_width() // 2, 32 - text.get_height() // 2))
        return surf

    def start(self, current_time):
        self.active = True
        self.start_time = current_time
        self.points_given = 0
        self.last_update_time = current_time

        # Sorteia a quantidade total de pontos que o trabalhador vai entregar (0 a 5000)
        self.total_points_to_give = random.randint(0, 5000)

        img_width, img_height = self.image.get_size()
        max_x = max(0, self.width - img_width)
        max_y = max(0, self.height - img_height)
        self.pos = [random.randint(0, max_x), random.randint(0, max_y)]
        self.direction = [random.choice([-1, 1]), random.choice([-1, 1])]

    def update(self, current_time):
        if not self.active:
            return 0

        elapsed = current_time - self.start_time
        if elapsed >= self.duration:
            self.active = False
            self.last_ended_time = current_time
            # Já entregou todos os pontos durante o tempo, não dá mais
            return 0

        # Movimento do trabalhador
        img_width, img_height = self.image.get_size()
        for i in [0, 1]:
            self.pos[i] += self.direction[i] * self.speed
            limit = self.width - img_width if i == 0 else self.height - img_height
            if self.pos[i] < 0 or self.pos[i] > limit:
                self.direction[i] *= -1
                self.pos[i] = max(0, min(limit, self.pos[i]))

        delta_time = current_time - self.last_update_time
        self.last_update_time = current_time

        # Calcula quantos pontos ele deveria entregar até agora proporcionalmente ao tempo
        pontos_ate_agora = int(self.total_points_to_give * (elapsed / self.duration))

        # Pontos novos a entregar nesse update
        pontos_para_dar = pontos_ate_agora - self.points_given

        # Atualiza a quantidade já entregue e retorna o valor para adicionar ao score
        if pontos_para_dar > 0:
            self.points_given += pontos_para_dar
            return pontos_para_dar
        else:
            return 0

    def can_be_rehired(self, current_time):
        return not self.active and (current_time - self.last_ended_time >= 120000)

    def draw(self):
        if not self.active:
            return
        x = max(0, min(self.width - self.image.get_width(), self.pos[0]))
        y = max(0, min(self.height - self.image.get_height(), self.pos[1]))
        self.screen.blit(self.image, (x, y))
