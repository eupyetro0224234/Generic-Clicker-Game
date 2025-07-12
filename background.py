import pygame
import math
import time
import os
import importlib.util
import json

WIDTH, HEIGHT = 1280, 720

def load_mod_from_path(path):
    spec = importlib.util.spec_from_file_location("mod_background_temp", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def choose_mod(mod_files):
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Selecionar Mod")

    title_font = pygame.font.SysFont(None, 36)
    font = pygame.font.SysFont(None, 28)

    bg_color = (180, 210, 255, 220)
    text_color = (40, 40, 60)
    btn_color_normal = (255, 255, 255)
    btn_color_hover = (220, 235, 255)
    border_color = (150, 150, 150)
    option_radius = 12

    padding_x = 50
    padding_y = 50
    btn_height = 44
    spacing_y = 14
    btn_width = 600
    btn_x = (1280 - btn_width) // 2

    buttons = []
    for i, f in enumerate(mod_files):
        btn_rect = pygame.Rect(btn_x, padding_y + 120 + i * (btn_height + spacing_y), btn_width, btn_height)
        buttons.append((btn_rect, f))

    clock = pygame.time.Clock()
    running = True
    while running:
        screen.fill((30, 30, 40))

        overlay = pygame.Surface((1280, 720), pygame.SRCALPHA)
        pygame.draw.rect(overlay, bg_color, (0, 0, 1280, 720))
        screen.blit(overlay, (0, 0))

        title_surf = title_font.render("Mods disponíveis:", True, text_color)
        title_rect = title_surf.get_rect(center=(1280 // 2, padding_y + 40))
        screen.blit(title_surf, title_rect)

        instr_text = "Clique em um mod para selecionar ou [ESC] para nenhum"
        instr_surf = font.render(instr_text, True, (100, 100, 130))
        instr_rect = instr_surf.get_rect(center=(1280 // 2, padding_y + 85))
        screen.blit(instr_surf, instr_rect)

        mouse_pos = pygame.mouse.get_pos()

        for i, (rect, f) in enumerate(buttons):
            color = btn_color_hover if rect.collidepoint(mouse_pos) else btn_color_normal
            pygame.draw.rect(screen, color, rect, border_radius=option_radius)
            pygame.draw.rect(screen, border_color, rect, width=2, border_radius=option_radius)

            text_surf = font.render(f"[{i+1}] {f}", True, text_color)
            text_rect = text_surf.get_rect(midleft=(rect.x + 14, rect.y + btn_height // 2))
            screen.blit(text_surf, text_rect)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                return None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return None
                if pygame.K_1 <= event.key <= pygame.K_9:
                    num = event.key - pygame.K_1 + 1
                    if num <= len(mod_files):
                        pygame.quit()
                        return mod_files[num - 1]

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, (rect, f) in enumerate(buttons):
                    if rect.collidepoint(event.pos):
                        pygame.quit()
                        return mod_files[i]

def get_config_path():
    localappdata = os.getenv("LOCALAPPDATA")
    if not localappdata:
        return None
    assets_folder = os.path.join(localappdata, ".assets")
    if not os.path.exists(assets_folder):
        os.makedirs(assets_folder, exist_ok=True)
    return os.path.join(assets_folder, "config.json")

def load_config():
    config_path = get_config_path()
    default_config = {
        "Ativar Mods": False,
    }
    if not config_path or not os.path.isfile(config_path):
        print("Configuração não encontrada, usando padrão (mods desativados).")
        return default_config
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
            return {**default_config, **cfg}
    except Exception as e:
        print(f"Erro ao ler config: {e}. Usando padrão.")
        return default_config

def get_mods_folder():
    localappdata = os.getenv("LOCALAPPDATA")
    if not localappdata:
        print("LOCALAPPDATA não definido, usando pasta atual para mods.")
        base_path = os.path.abspath(".")
    else:
        base_path = os.path.join(localappdata, ".assets", "mods")
    if not os.path.exists(base_path):
        os.makedirs(base_path, exist_ok=True)
        print(f"Pasta de mods criada em: {base_path}")
    return base_path

def load_selected_mod(mods_folder):
    mod_files = [f for f in os.listdir(mods_folder) if f.endswith('_mod.py')]
    if not mod_files:
        print(f"Nenhum mod encontrado na pasta {mods_folder}, usando configurações padrão.")
        return None
    elif len(mod_files) == 1:
        print(f"Carregando mod único encontrado: {mod_files[0]}")
        return os.path.join(mods_folder, mod_files[0])
    else:
        selected = choose_mod(mod_files)
        if selected:
            print(f"Mod selecionado: {selected}")
            return os.path.join(mods_folder, selected)
        else:
            print("Nenhum mod selecionado, usando padrão.")
            return None

config = load_config()
ativar_mods = config.get("Ativar Mods", False)

mod = None
if ativar_mods:
    mods_folder = get_mods_folder()
    selected_mod_file = load_selected_mod(mods_folder)
    if selected_mod_file:
        try:
            mod = load_mod_from_path(selected_mod_file)
        except Exception as e:
            print(f"Erro ao carregar mod {selected_mod_file}: {e}")
            mod = None
else:
    print("Mods desativados pela configuração.")

TILE_SIZE = getattr(mod, 'TILE_SIZE', 40)
BASE_COLORS = getattr(mod, 'BASE_COLORS', [
    (200, 230, 201),
    (255, 224, 178),
    (255, 205, 210),
    (187, 222, 251),
    (255, 249, 196),
    (197, 225, 165),
])
FREQ = getattr(mod, 'FREQ', 0.5)
ENABLE_ANIMATION = getattr(mod, 'ENABLE_ANIMATION', True)
BACKGROUND_STYLE = getattr(mod, 'BACKGROUND_STYLE', 'quadriculado')

adjust_brightness = getattr(mod, 'adjust_brightness', None)
draw_background_override = getattr(mod, 'draw_background_override', None)

GRID_WIDTH = WIDTH // TILE_SIZE + 1
GRID_HEIGHT = HEIGHT // TILE_SIZE + 1

def generate_grid_colors():
    grid = []
    for y in range(GRID_HEIGHT):
        row = []
        for x in range(GRID_WIDTH):
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
    return grid

grid_colors = generate_grid_colors()

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

def draw_background(screen):
    if draw_background_override:
        return draw_background_override(screen, grid_colors, TILE_SIZE)
    t = time.time()
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            base_color = grid_colors[y][x]
            brightness = 1
            if ENABLE_ANIMATION:
                brightness = 1 + 0.15 * math.sin(2 * math.pi * FREQ * t + (x + y))
            color = adjust_brightness_func(base_color, brightness)
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, color, rect)
