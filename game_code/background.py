import pygame, math, time

pygame.init()
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
pygame.quit()

mod = None

def set_mod(mod_instance):
    global mod
    mod = mod_instance
    _apply_mod_settings()

def _apply_mod_settings():
    global TILE_SIZE, BASE_COLORS, FREQ, ENABLE_ANIMATION, BACKGROUND_STYLE
    global adjust_brightness, draw_background_override
    
    if mod and hasattr(mod, 'CustomBackground'):
        custom_bg = mod.CustomBackground()
        TILE_SIZE = custom_bg.tile_size
        BASE_COLORS = custom_bg.base_colors
        FREQ = custom_bg.freq
        ENABLE_ANIMATION = custom_bg.enable_animation
        BACKGROUND_STYLE = custom_bg.background_style
    else:
        TILE_SIZE = 60
        BASE_COLORS = [
            (200, 230, 201),
            (255, 224, 178),
            (255, 205, 210),
            (187, 222, 251),
            (255, 249, 196),
            (197, 225, 165),
        ]
        FREQ = 0.5
        ENABLE_ANIMATION = True
        BACKGROUND_STYLE = 'quadriculado'
    
    adjust_brightness = getattr(mod, 'adjust_brightness', None) if mod else None
    draw_background_override = getattr(mod, 'draw_background_override', None) if mod else None

TILE_SIZE = 60
BASE_COLORS = [
    (200, 230, 201),
    (255, 224, 178),
    (255, 205, 210),
    (187, 222, 251),
    (255, 249, 196),
    (197, 225, 165),
]
FREQ = 0.5
ENABLE_ANIMATION = True
BACKGROUND_STYLE = 'quadriculado'
adjust_brightness = None
draw_background_override = None

def generate_grid_colors(screen_width, screen_height, tile_size):
    grid_width = screen_width // tile_size + 2
    grid_height = screen_height // tile_size + 2
    grid = []
    for y in range(grid_height):
        row = []
        for x in range(grid_width):
            if BACKGROUND_STYLE == 'horizontal':
                index = y % len(BASE_COLORS)
            elif BACKGROUND_STYLE == 'vertical':
                index = x % len(BASE_COLORS)
            elif BACKGROUND_STYLE == 'diagonal':
                index = (x * y) % len(BASE_COLORS)
            else:
                index = (x + y) % len(BASE_COLORS)
            row.append(BASE_COLORS[index])
        grid.append(row)
    return grid, grid_width, grid_height

def default_adjust_brightness(color, factor):
    r = max(0, min(255, int(color[0] * factor)))
    g = max(0, min(255, int(color[1] * factor)))
    b = max(0, min(255, int(color[2] * factor)))
    return (r, g, b)

def adjust_brightness_func(color, factor):
    if adjust_brightness:
        return adjust_brightness(color, factor)
    else:
        return default_adjust_brightness(color, factor)

game_reference = None

def set_game_reference(game):
    global game_reference
    game_reference = game

def draw_background(screen):
    screen_width, screen_height = screen.get_size()
    
    grid_colors, grid_width, grid_height = generate_grid_colors(screen_width, screen_height, TILE_SIZE)
    
    if draw_background_override:
        return draw_background_override(screen, grid_colors, TILE_SIZE)
    
    t = time.time()
    
    brightness_factor = 1.0
    if game_reference and hasattr(game_reference, 'config_menu'):
        brightness_factor = game_reference.config_menu.settings_menu.get_brightness_settings()
    
    for y in range(grid_height):
        for x in range(grid_width):
            base_color = grid_colors[y][x]
            brightness = 1
            if ENABLE_ANIMATION:
                brightness = 1 + 0.15 * math.sin(2 * math.pi * FREQ * t + (x + y))
            
            final_brightness = brightness * brightness_factor
            color = adjust_brightness_func(base_color, final_brightness)
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, color, rect)

class Background:
    def __init__(self, tile_size=60, base_colors=None, freq=0.5, enable_animation=True, background_style='quadriculado'):
        self.tile_size = tile_size
        self.base_colors = base_colors if base_colors else [
            (200, 230, 201),
            (255, 224, 178),
            (255, 205, 210),
            (187, 222, 251),
            (255, 249, 196),
            (197, 225, 165),
        ]
        self.freq = freq
        self.enable_animation = enable_animation
        self.background_style = background_style