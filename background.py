import pygame
import math
import time

WIDTH, HEIGHT = 1280, 720
TILE_SIZE = 40  # tamanho do quadrado

# Paleta de cores base pastel
BASE_COLORS = [
    (200, 230, 201),  # verde claro
    (255, 224, 178),  # laranja claro
    (255, 205, 210),  # rosa claro
    (187, 222, 251),  # azul claro
    (255, 249, 196),  # amarelo claro
    (197, 225, 165),  # verde limão claro
]

# Criar uma grid fixa de cores base para os tiles (para não mudar toda hora)
GRID_WIDTH = WIDTH // TILE_SIZE + 1
GRID_HEIGHT = HEIGHT // TILE_SIZE + 1

grid_colors = []

for y in range(GRID_HEIGHT):
    row = []
    for x in range(GRID_WIDTH):
        # Escolhe uma cor base aleatória para o tile
        row.append(BASE_COLORS[(x + y) % len(BASE_COLORS)])
    grid_colors.append(row)

def adjust_brightness(color, factor):
    """Ajusta o brilho da cor multiplicando cada canal RGB pelo fator (0 a 1+)."""
    r = max(0, min(255, int(color[0] * factor)))
    g = max(0, min(255, int(color[1] * factor)))
    b = max(0, min(255, int(color[2] * factor)))
    return (r, g, b)

def draw_background(screen):
    t = time.time()
    # Frequência da oscilação de brilho (mais lento = menor frequência)
    freq = 0.5  # ciclos por segundo
    
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            base_color = grid_colors[y][x]
            # Calcula fator de brilho entre 0.85 e 1.15 para suavizar piscada
            brightness = 1 + 0.15 * math.sin(2 * math.pi * freq * t + (x + y))
            color = adjust_brightness(base_color, brightness)
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, color, rect)
