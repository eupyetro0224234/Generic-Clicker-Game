import pygame
import random
import os

class MiniEvent:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        
        # Caminho para a imagem do mini evento
        localappdata = os.getenv("LOCALAPPDATA") or "."
        self.image_path = os.path.join(localappdata, ".assets", "mini-event.png")
        
        try:
            self.image = pygame.image.load(self.image_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (50, 50))  # Reduzindo o tamanho da imagem
        except Exception as e:
            # Criar um placeholder visual se a imagem não carregar
            self.image = pygame.Surface((50, 50))
            self.image.fill((255, 0, 0))  # Quadrado vermelho
            # Adicionar texto para identificação
            font = pygame.font.SysFont(None, 20)
            text = font.render("EVENTO", True, (255, 255, 255))
            self.image.blit(text, (10, 15))
            
        self.x = random.randint(0, self.width - 50)  # Posição aleatória X
        self.y = random.randint(0, self.height - 50)  # Posição aleatória Y
        self.time_to_live = 10000  # Tempo de exibição (10 segundos)
        self.spawn_time = pygame.time.get_ticks()  # Marca o tempo de spawn
        self.visible = True  # Inicialmente visível
        self.font = pygame.font.SysFont("Arial", 20)

    def update(self):
        """Atualiza o tempo de vida da imagem e a torna invisível após 10 segundos."""
        if not self.visible:
            return
            
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - self.spawn_time
        
        if elapsed_time >= self.time_to_live:
            self.visible = False  # Se passou 10 segundos, a imagem some

    def draw(self):
        """Desenha a imagem na tela, caso ainda esteja visível."""
        if self.visible:
            self.screen.blit(self.image, (self.x, self.y))
            
            # Desenha o tempo restante (tempo até desaparecer) na tela
            elapsed_time = pygame.time.get_ticks() - self.spawn_time
            time_left = max(0, self.time_to_live - elapsed_time) // 1000  # Converte para segundos
            time_text = self.font.render(f"{time_left}s", True, (255, 255, 255))  # Tempo em branco
            self.screen.blit(time_text, (self.x + 5, self.y - 25))  # Exibe o tempo no topo da imagem

    def handle_click(self, pos, score, upgrade_menu):
        """Verifica se o clique foi na imagem e gera pontos ou upgrades."""
        if not self.visible:
            return score, False
            
        # Verifica se o clique foi dentro da área do evento
        if self.x <= pos[0] <= self.x + 50 and self.y <= pos[1] <= self.y + 50:
            self.visible = False  # Esconde a imagem ao clicar
            
            if random.random() < 0.05:  # 5% de chance de ganhar upgrade
                upgrade_menu.purchase_random_upgrade()
                return score, True  # Retorna que o jogador obteve um upgrade
            else:
                points = random.randint(1, 1000)  # Quantidade aleatória de pontos
                score += points
                return score, False  # Retorna que o jogador obteve pontos
                
        return score, False