import pygame

# RESOLUÇÃO GLOBAL
WIDTH, HEIGHT = 1280, 720

def draw_background(screen):
    top_color = (10, 10, 50)
    bottom_color = (40, 80, 180)

    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))
