import pygame
import random

WIDTH, HEIGHT = 1280, 720
TILE_SIZE = 40  # tamanho do quadradinho

def draw_background(screen):
    # Paleta de cores claras (tons pastel)
    pastel_colors = [
        (200, 230, 201),  # verde claro
        (255, 224, 178),  # laranja claro
        (255, 205, 210),  # rosa claro
        (187, 222, 251),  # azul claro
        (255, 249, 196),  # amarelo claro
        (197, 225, 165),  # verde limão claro
    ]

    for y in range(0, HEIGHT, TILE_SIZE):
        for x in range(0, WIDTH, TILE_SIZE):
            color = random.choice(pastel_colors)
            rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, color, rect)
