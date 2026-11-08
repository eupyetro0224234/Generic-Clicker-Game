import pygame, os

pygame.init()

screen_width, screen_height = 1280, 720
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Criador de Mods - Generic Clicker Game")

title_font = pygame.font.SysFont(None, 48)
section_font = pygame.font.SysFont(None, 42)
option_font = pygame.font.SysFont(None, 32)
small_font = pygame.font.SysFont(None, 24)

mod_data = {
    "TILE_SIZE": 60,
    "BASE_COLORS": [
        [200, 230, 201],
        [255, 224, 178],
        [255, 205, 210],
        [187, 222, 251],
        [255, 249, 196],
        [197, 225, 165],
    ],
    "FREQ": 0.5,
    "ENABLE_ANIMATION": True,
    "BACKGROUND_STYLE": "quadriculado"
}

default_values = {
    "tile": 60,
    "freq": 0.5
}

styles = ["quadriculado", "horizontal", "vertical", "diagonal"]

bg_color = (255, 182, 193)
text_color = (47, 24, 63)
option_height = 60
option_radius = 15
padding_x = 20
padding_y = 20
spacing_y = 20

scroll_y = 0
scroll_speed = 30
content_height = 0

gradient_dragging = False
current_hue = 0
current_saturation = 100
current_value = 100
gradient_rect = None
hue_rect = None
sv_rect = None

def hsv_to_rgb(h, s, v):
    h = h % 360
    s = max(0, min(100, s)) / 100.0
    v = max(0, min(100, v)) / 100.0
    
    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c
    
    if 0 <= h < 60:
        r, g, b = c, x, 0
    elif 60 <= h < 120:
        r, g, b = x, c, 0
    elif 120 <= h < 180:
        r, g, b = 0, c, x
    elif 180 <= h < 240:
        r, g, b = 0, x, c
    elif 240 <= h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x
    
    return [int((r + m) * 255), int((g + m) * 255), int((b + m) * 255)]

def colors_are_similar(color1, color2, tolerance=5):
    return (abs(color1[0] - color2[0]) <= tolerance and
            abs(color1[1] - color2[1]) <= tolerance and
            abs(color1[2] - color2[2]) <= tolerance)

def draw_small_text(text, x, y, color=None):
    if color is None:
        color = text_color
    surf = small_font.render(text, True, color)
    screen.blit(surf, (x, y))
    return pygame.Rect(x, y, surf.get_width(), surf.get_height())

def draw_section_title(title, x, y):
    box_width = screen_width - 2 * x
    box_height = option_height
    box_rect = pygame.Rect(x, y, box_width, box_height)

    azul_claro = (200, 190, 255, 230)
    pygame.draw.rect(screen, azul_claro, box_rect, border_radius=option_radius)
    pygame.draw.rect(screen, (150, 150, 150), box_rect, width=2, border_radius=option_radius)

    title_surf = section_font.render(title, True, text_color)
    title_rect = title_surf.get_rect(center=box_rect.center)
    screen.blit(title_surf, title_rect)

    return y + box_height + spacing_y

def draw_option_box(text, value_text, x, y, width, is_hovered=False, is_editing=False, input_text="", default_value=None):
    container_rect = pygame.Rect(x, y, width, option_height)

    shadow_surface = pygame.Surface((width + 6, option_height + 6), pygame.SRCALPHA)
    pygame.draw.rect(shadow_surface, (0, 0, 0, 20), (0, 0, width + 6, option_height + 6), border_radius=15)
    screen.blit(shadow_surface, (x - 3, y - 3))

    if is_editing:
        color = (200, 230, 255)
        border_color = (100, 150, 255)
        border_width = 3
    else:
        color = (220, 235, 255) if is_hovered else (255, 255, 255)
        border_color = (150, 150, 150)
        border_width = 2

    pygame.draw.rect(screen, color, container_rect, border_radius=option_radius)
    pygame.draw.rect(screen, border_color, container_rect, width=border_width, border_radius=option_radius)

    text_surf = option_font.render(text, True, text_color)
    text_rect = text_surf.get_rect(midleft=(x + 20, y + option_height // 2))
    screen.blit(text_surf, text_rect)

    if is_editing:
        if input_text == "":
            display_text = "padrão"
            display_color = (150, 150, 150)
        else:
            display_text = input_text
            display_color = text_color
    else:
        display_text = str(value_text)
        display_color = text_color

    val_surf = option_font.render(display_text, True, display_color)
    val_rect = val_surf.get_rect(midright=(x + width - 20, y + option_height // 2))
    screen.blit(val_surf, val_rect)

    return container_rect

def draw_color_box(colors, x, y):
    container_height = 80
    container_rect = pygame.Rect(x, y, screen_width - 2 * x, container_height)

    shadow_surface = pygame.Surface((container_rect.width + 6, container_height + 6), pygame.SRCALPHA)
    pygame.draw.rect(shadow_surface, (0, 0, 0, 20), (0, 0, container_rect.width + 6, container_height + 6), border_radius=15)
    screen.blit(shadow_surface, (x - 3, y - 3))

    pygame.draw.rect(screen, (255, 255, 255), container_rect, border_radius=option_radius)
    pygame.draw.rect(screen, (150, 150, 150), container_rect, width=2, border_radius=option_radius)

    text_surf = option_font.render("Cores Base:", True, text_color)
    text_rect = text_surf.get_rect(midleft=(x + 20, y + 20))
    screen.blit(text_surf, text_rect)

    color_rects = []
    for i, color in enumerate(colors):
        rect = pygame.Rect(x + 200 + i * 60, y + 15, 50, 50)
        pygame.draw.rect(screen, color, rect, border_radius=6)
        pygame.draw.rect(screen, (50, 50, 50), rect, 2, border_radius=6)
        color_rects.append(rect)

    return container_rect, color_rects

def draw_gradient_editor(x, y):
    global gradient_rect, hue_rect, sv_rect
    
    container_height = 350
    container_rect = pygame.Rect(x, y, screen_width - 2 * x, container_height)
    gradient_rect = container_rect

    shadow_surface = pygame.Surface((container_rect.width + 6, container_height + 6), pygame.SRCALPHA)
    pygame.draw.rect(shadow_surface, (0, 0, 0, 20), (0, 0, container_rect.width + 6, container_height + 6), border_radius=15)
    screen.blit(shadow_surface, (x - 3, y - 3))

    pygame.draw.rect(screen, (255, 255, 255), container_rect, border_radius=option_radius)
    pygame.draw.rect(screen, (150, 150, 150), container_rect, width=2, border_radius=option_radius)

    text_surf = option_font.render("Editor de Cores - Clique para adicionar cores", True, text_color)
    text_rect = text_surf.get_rect(midleft=(x + 20, y + 20))
    screen.blit(text_surf, text_rect)

    hue_width = 400
    hue_height = 25
    hue_x = x + 20
    hue_y = y + 60
    hue_rect = pygame.Rect(hue_x, hue_y, hue_width, hue_height)
    
    for i in range(hue_width):
        hue = (i / hue_width) * 360
        color = hsv_to_rgb(hue, 100, 100)
        pygame.draw.line(screen, color, (hue_x + i, hue_y), (hue_x + i, hue_y + hue_height), 1)
    
    pygame.draw.rect(screen, (0, 0, 0), hue_rect, 2)
    
    hue_indicator_x = hue_x + (current_hue / 360) * hue_width
    pygame.draw.circle(screen, (255, 255, 255), (int(hue_indicator_x), hue_y + hue_height // 2), 6)
    pygame.draw.circle(screen, (0, 0, 0), (int(hue_indicator_x), hue_y + hue_height // 2), 6, 2)

    sv_size = 180
    sv_x = x + 20
    sv_y = y + 100
    sv_rect = pygame.Rect(sv_x, sv_y, sv_size, sv_size)
    
    for i in range(sv_size):
        for j in range(sv_size):
            sat = (i / sv_size) * 100
            val = 100 - (j / sv_size) * 100
            color = hsv_to_rgb(current_hue, sat, val)
            screen.set_at((sv_x + i, sv_y + j), color)
    
    pygame.draw.rect(screen, (0, 0, 0), sv_rect, 2)
    
    sv_indicator_x = sv_x + (current_saturation / 100) * sv_size
    sv_indicator_y = sv_y + ((100 - current_value) / 100) * sv_size
    pygame.draw.circle(screen, (255, 255, 255), (int(sv_indicator_x), int(sv_indicator_y)), 5)
    pygame.draw.circle(screen, (0, 0, 0), (int(sv_indicator_x), int(sv_indicator_y)), 5, 2)

    current_color = hsv_to_rgb(current_hue, current_saturation, current_value)
    color_preview_rect = pygame.Rect(sv_x + sv_size + 20, sv_y, 70, 70)
    pygame.draw.rect(screen, current_color, color_preview_rect, border_radius=8)
    pygame.draw.rect(screen, (0, 0, 0), color_preview_rect, 2, border_radius=8)

    add_button_rect = pygame.Rect(sv_x + sv_size + 20, sv_y + 80, 70, 35)
    pygame.draw.rect(screen, (150, 255, 150), add_button_rect, border_radius=6)
    pygame.draw.rect(screen, (0, 100, 0), add_button_rect, 2, border_radius=6)
    add_text = small_font.render("Adicionar", True, text_color)
    add_text_rect = add_text.get_rect(center=add_button_rect.center)
    screen.blit(add_text, add_text_rect)

    clear_button_rect = pygame.Rect(sv_x + sv_size + 20, sv_y + 125, 70, 35)
    pygame.draw.rect(screen, (255, 150, 150), clear_button_rect, border_radius=6)
    pygame.draw.rect(screen, (100, 0, 0), clear_button_rect, 2, border_radius=6)
    clear_text = small_font.render("Limpar", True, text_color)
    clear_text_rect = clear_text.get_rect(center=clear_button_rect.center)
    screen.blit(clear_text, clear_text_rect)

    colors_text = small_font.render(f"Cores selecionadas: {len(mod_data['BASE_COLORS'])}", True, text_color)
    screen.blit(colors_text, (sv_x + sv_size + 110, sv_y))

    colors_display_x = sv_x + sv_size + 110
    colors_display_y = sv_y + 25
    colors_display_width = container_rect.width - (colors_display_x - x) - 20
    
    colors_container = pygame.Rect(colors_display_x, colors_display_y, colors_display_width, 120)
    pygame.draw.rect(screen, (240, 240, 240), colors_container, border_radius=8)
    pygame.draw.rect(screen, (200, 200, 200), colors_container, 1, border_radius=8)
    
    colors_per_row = min(6, max(1, colors_display_width // 45))
    
    for i, color in enumerate(mod_data['BASE_COLORS']):
        row = i // colors_per_row
        col = i % colors_per_row
        color_display_rect = pygame.Rect(
            colors_display_x + 10 + col * 42,
            colors_display_y + 10 + row * 42,
            38, 38
        )
        pygame.draw.rect(screen, color, color_display_rect, border_radius=5)
        pygame.draw.rect(screen, (50, 50, 50), color_display_rect, 1, border_radius=5)
        
        remove_rect = pygame.Rect(color_display_rect.right - 12, color_display_rect.top - 6, 18, 18)
        pygame.draw.rect(screen, (255, 100, 100), remove_rect, border_radius=9)
        pygame.draw.rect(screen, (150, 0, 0), remove_rect, 1, border_radius=9)
        x_text = small_font.render("×", True, (255, 255, 255))
        x_rect = x_text.get_rect(center=remove_rect.center)
        screen.blit(x_text, x_rect)

    return container_rect, add_button_rect, clear_button_rect

def draw_button(text, x, y, w, h, active=True):
    color = (150, 200, 255) if active else (100, 150, 200)

    shadow_surface = pygame.Surface((w + 6, h + 6), pygame.SRCALPHA)
    pygame.draw.rect(shadow_surface, (0, 0, 0, 20), (0, 0, w + 6, h + 6), border_radius=15)
    screen.blit(shadow_surface, (x - 3, y - 3))

    pygame.draw.rect(screen, color, (x, y, w, h), border_radius=10)
    pygame.draw.rect(screen, (50, 80, 120), (x, y, w, h), 2, border_radius=10)

    text_surf = option_font.render(text, True, text_color)
    rect = text_surf.get_rect(center=(x + w/2, y + h/2))
    screen.blit(text_surf, rect)

    return pygame.Rect(x, y, w, h)

def draw_input_field(prompt, value, x, y, width, is_editing=False):
    container_rect = pygame.Rect(x, y, width, option_height)

    if is_editing:
        pygame.draw.rect(screen, (255, 255, 255), container_rect, border_radius=option_radius)
        pygame.draw.rect(screen, (100, 150, 255), container_rect, width=3, border_radius=option_radius)
    else:
        shadow_surface = pygame.Surface((width + 6, option_height + 6), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, (0, 0, 0, 20), (0, 0, width + 6, option_height + 6), border_radius=15)
        screen.blit(shadow_surface, (x - 3, y - 3))

        pygame.draw.rect(screen, (255, 255, 255), container_rect, border_radius=option_radius)
        pygame.draw.rect(screen, (150, 150, 150), container_rect, width=2, border_radius=option_radius)

    text = f"{prompt}: {value}"
    text_surf = option_font.render(text, True, text_color)
    text_rect = text_surf.get_rect(midleft=(x + 20, y + option_height // 2))
    screen.blit(text_surf, text_rect)

    return container_rect

def save_mod(name, author, description):
    appdata = os.getenv("APPDATA")
    if appdata:
        mods_folder = os.path.join(appdata, "genericclickergame", "mods")
    else:
        mods_folder = os.path.join(os.getcwd(), "mods")
    os.makedirs(mods_folder, exist_ok=True)

    filename = os.path.join(mods_folder, f"{name}_mod.py")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# Mod: {name}\n")
        f.write(f"# Autor: {author}\n")
        f.write(f"# Descrição: {description}\n\n")
        f.write("from background import Background\n\n")
        f.write(f"TILE_SIZE = {mod_data['TILE_SIZE']}\n")
        f.write("BASE_COLORS = [\n")
        for color in mod_data['BASE_COLORS']:
            f.write(f"    {color},\n")
        f.write("]\n")
        f.write(f"FREQ = {mod_data['FREQ']}\n")
        f.write(f"ENABLE_ANIMATION = {mod_data['ENABLE_ANIMATION']}\n")
        f.write(f"BACKGROUND_STYLE = '{mod_data['BACKGROUND_STYLE']}'\n\n")
        f.write("class CustomBackground(Background):\n")
        f.write("    def __init__(self):\n")
        f.write("        super().__init__(TILE_SIZE, BASE_COLORS, FREQ, ENABLE_ANIMATION, BACKGROUND_STYLE)\n")
    print(f"✅ Mod salvo em: {filename}")
    return filename

message = ""
color_index = 0
running = True

editing_field = None
input_text = ""

rects = {}
pre_save_inputs = {"name": "", "author": "", "desc": ""}
pre_save_editing = None

def calculate_content_height():
    if pre_save_editing is None:
        return 130 + 4*(option_height + spacing_y) + 370 + 100 + 80
    else:
        return 130 + 3*(option_height + spacing_y) + 40 + 50 + 80

content_height = calculate_content_height()

while running:
    screen.fill(bg_color)

    title_surf = title_font.render("🎨 Criador de Mods", True, text_color)
    title_rect = title_surf.get_rect(center=(screen_width // 2, 50))
    screen.blit(title_surf, title_rect)

    y_position = 130 - scroll_y

    if pre_save_editing is None:
        y_position = draw_section_title("Configurações do Mod", padding_x, y_position)

        option_width = screen_width - 2 * padding_x
        mouse_pos = pygame.mouse.get_pos()
        adjusted_mouse_pos = mouse_pos

        hovered_tile = rects.get("tile", pygame.Rect(0,0,0,0)).collidepoint(mouse_pos) if "tile" in rects else False
        hovered_freq = rects.get("freq", pygame.Rect(0,0,0,0)).collidepoint(mouse_pos) if "freq" in rects else False
        hovered_anim = rects.get("anim", pygame.Rect(0,0,0,0)).collidepoint(mouse_pos) if "anim" in rects else False
        hovered_style = rects.get("style", pygame.Rect(0,0,0,0)).collidepoint(mouse_pos) if "style" in rects else False

        rects["tile"] = draw_option_box(
            "Tamanho dos blocos",
            mod_data['TILE_SIZE'],
            padding_x, y_position, option_width,
            hovered_tile,
            editing_field == "tile",
            input_text if editing_field == "tile" else "",
            default_values["tile"]
        )
        y_position += option_height + spacing_y

        rects["freq"] = draw_option_box(
            "Frequência da animação",
            mod_data['FREQ'],
            padding_x, y_position, option_width,
            hovered_freq,
            editing_field == "freq",
            input_text if editing_field == "freq" else "",
            default_values["freq"]
        )
        y_position += option_height + spacing_y

        rects["anim"] = draw_option_box(
            "Animações ativas",
            "Sim" if mod_data['ENABLE_ANIMATION'] else "Não",
            padding_x, y_position, option_width,
            hovered_anim,
            False,
            ""
        )
        y_position += option_height + spacing_y

        rects["style"] = draw_option_box(
            "Estilo de fundo",
            mod_data['BACKGROUND_STYLE'],
            padding_x, y_position, option_width,
            hovered_style,
            False,
            ""
        )
        y_position += option_height + spacing_y

        y_position += 20
        y_position = draw_section_title("Cores Personalizadas", padding_x, y_position)

        gradient_container, add_button_rect, clear_button_rect = draw_gradient_editor(padding_x, y_position)
        rects["gradient"] = gradient_container
        rects["add_color"] = add_button_rect
        rects["clear_colors"] = clear_button_rect
        y_position += 350

        save_rect = draw_button("💾 Salvar Mod", screen_width // 2 - 100, y_position, 200, 50, True)
        rects["save"] = save_rect
        y_position += 80

        if message:
            message_rect = pygame.Rect(padding_x, y_position, screen_width - 2 * padding_x, 50)
            pygame.draw.rect(screen, (255, 255, 200), message_rect, border_radius=option_radius)
            pygame.draw.rect(screen, (200, 200, 100), message_rect, width=2, border_radius=option_radius)
            draw_small_text(message, padding_x + 20, y_position + 15, (100, 80, 0))
    else:
        y_position = draw_section_title("Informações do Mod", padding_x, y_position)

        option_width = screen_width - 2 * padding_x
        mouse_pos = pygame.mouse.get_pos()
        adjusted_mouse_pos = mouse_pos

        rects["name"] = draw_input_field(
            "Nome do Mod",
            pre_save_inputs["name"],
            padding_x, y_position, option_width,
            pre_save_editing == "name"
        )
        y_position += option_height + spacing_y

        rects["author"] = draw_input_field(
            "Autor",
            pre_save_inputs["author"],
            padding_x, y_position, option_width,
            pre_save_editing == "author"
        )
        y_position += option_height + spacing_y

        rects["desc"] = draw_input_field(
            "Descrição",
            pre_save_inputs["desc"],
            padding_x, y_position, option_width,
            pre_save_editing == "desc"
        )
        y_position += option_height + spacing_y

        y_position += 40

        cancel_rect = draw_button("Cancelar", screen_width // 2 - 220, y_position, 200, 50, True)
        confirm_rect = draw_button("Salvar Mod", screen_width // 2 + 20, y_position, 200, 50, True)
        rects["cancel"] = cancel_rect
        rects["confirm"] = confirm_rect

        if message:
            message_rect = pygame.Rect(padding_x, y_position + 80, screen_width - 2 * padding_x, 50)
            pygame.draw.rect(screen, (255, 255, 200), message_rect, border_radius=option_radius)
            pygame.draw.rect(screen, (200, 200, 100), message_rect, width=2, border_radius=option_radius)
            draw_small_text(message, padding_x + 20, y_position + 95, (100, 80, 0))

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEWHEEL:
            scroll_y -= event.y * scroll_speed
            scroll_y = max(0, min(scroll_y, content_height - screen_height))

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_PAGEDOWN:
                scroll_y += scroll_speed * 3
                scroll_y = min(scroll_y, content_height - screen_height)
            elif event.key == pygame.K_PAGEUP:
                scroll_y -= scroll_speed * 3
                scroll_y = max(0, scroll_y)
            elif event.key == pygame.K_DOWN and not (editing_field or pre_save_editing):
                scroll_y += scroll_speed
                scroll_y = min(scroll_y, content_height - screen_height)
            elif event.key == pygame.K_UP and not (editing_field or pre_save_editing):
                scroll_y -= scroll_speed
                scroll_y = max(0, scroll_y)

            if pre_save_editing:
                if event.key == pygame.K_RETURN:
                    if pre_save_inputs[pre_save_editing].strip() == "":
                        pre_save_inputs[pre_save_editing] = "Desconhecido" if pre_save_editing != "desc" else "Sem descrição"
                    if pre_save_editing == "name":
                        pre_save_editing = "author"
                    elif pre_save_editing == "author":
                        pre_save_editing = "desc"
                    else:
                        save_mod(pre_save_inputs["name"], pre_save_inputs["author"], pre_save_inputs["desc"])
                        message = f"Mod salvo como: {pre_save_inputs['name']}_mod.py ✅"
                        pre_save_editing = None
                        pre_save_inputs = {"name": "", "author": "", "desc": ""}
                        scroll_y = 0
                elif event.key == pygame.K_ESCAPE:
                    pre_save_editing = None
                elif event.key == pygame.K_BACKSPACE:
                    pre_save_inputs[pre_save_editing] = pre_save_inputs[pre_save_editing][:-1]
                else:
                    pre_save_inputs[pre_save_editing] += event.unicode
                continue

            if editing_field:
                if event.key == pygame.K_RETURN:
                    if input_text.strip() == "":
                        val = default_values[editing_field]
                    else:
                        try:
                            val = float(input_text) if editing_field == "freq" else int(input_text)
                        except ValueError:
                            message = "Valor inválido!"
                            editing_field = None
                            input_text = ""
                            continue
                    if editing_field == "tile":
                        mod_data["TILE_SIZE"] = val
                    elif editing_field == "freq":
                        mod_data["FREQ"] = val
                    message = f"{editing_field.upper()} atualizado!"
                    editing_field = None
                    input_text = ""
                elif event.key == pygame.K_ESCAPE:
                    editing_field = None
                    input_text = ""
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    if event.unicode.isdigit() or event.unicode in '.-':
                        input_text += event.unicode
                continue

            if event.key == pygame.K_ESCAPE:
                if editing_field:
                    editing_field = None
                    input_text = ""
                else:
                    running = False
            elif event.key == pygame.K_UP and not editing_field:
                mod_data["TILE_SIZE"] += 5
            elif event.key == pygame.K_DOWN and not editing_field:
                mod_data["TILE_SIZE"] = max(10, mod_data["TILE_SIZE"] - 5)
            elif event.key == pygame.K_RIGHT and not editing_field:
                mod_data["FREQ"] = round(mod_data["FREQ"] + 0.1, 2)
            elif event.key == pygame.K_LEFT and not editing_field:
                mod_data["FREQ"] = round(max(0.1, mod_data["FREQ"] - 0.1), 2)
            elif event.key == pygame.K_a and not editing_field:
                mod_data["ENABLE_ANIMATION"] = not mod_data["ENABLE_ANIMATION"]
            elif event.key == pygame.K_e and not editing_field:
                i = styles.index(mod_data["BACKGROUND_STYLE"])
                mod_data["BACKGROUND_STYLE"] = styles[(i + 1) % len(styles)]

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mx, my = event.pos

                if pre_save_editing:
                    if rects.get("name", pygame.Rect(0,0,0,0)).collidepoint(mx, my):
                        pre_save_editing = "name"
                    elif rects.get("author", pygame.Rect(0,0,0,0)).collidepoint(mx, my):
                        pre_save_editing = "author"
                    elif rects.get("desc", pygame.Rect(0,0,0,0)).collidepoint(mx, my):
                        pre_save_editing = "desc"
                    elif rects.get("cancel", pygame.Rect(0,0,0,0)).collidepoint(mx, my):
                        pre_save_editing = None
                        scroll_y = 0
                    elif rects.get("confirm", pygame.Rect(0,0,0,0)).collidepoint(mx, my):
                        if pre_save_inputs["name"].strip() == "":
                            pre_save_inputs["name"] = "MeuMod"
                        if pre_save_inputs["author"].strip() == "":
                            pre_save_inputs["author"] = "Desconhecido"
                        if pre_save_inputs["desc"].strip() == "":
                            pre_save_inputs["desc"] = "Sem descrição"
                        save_mod(pre_save_inputs["name"], pre_save_inputs["author"], pre_save_inputs["desc"])
                        message = f"Mod salvo como: {pre_save_inputs['name']}_mod.py ✅"
                        pre_save_editing = None
                        pre_save_inputs = {"name": "", "author": "", "desc": ""}
                        scroll_y = 0
                    continue

                if editing_field and not rects[editing_field].collidepoint(mx, my):
                    if input_text.strip() != "":
                        try:
                            val = float(input_text) if editing_field == "freq" else int(input_text)
                            if editing_field == "tile":
                                mod_data["TILE_SIZE"] = val
                            elif editing_field == "freq":
                                mod_data["FREQ"] = val
                            message = f"{editing_field.upper()} atualizado!"
                        except ValueError:
                            message = "Valor inválido!"
                    editing_field = None
                    input_text = ""
                    continue

                if hue_rect and hue_rect.collidepoint(mx, my):
                    relative_x = mx - hue_rect.x
                    current_hue = (relative_x / hue_rect.width) * 360
                elif sv_rect and sv_rect.collidepoint(mx, my):
                    relative_x = mx - sv_rect.x
                    relative_y = my - sv_rect.y
                    current_saturation = (relative_x / sv_rect.width) * 100
                    current_value = 100 - (relative_y / sv_rect.height) * 100
                elif rects.get("add_color", pygame.Rect(0,0,0,0)).collidepoint(mx, my):
                    new_color = hsv_to_rgb(current_hue, current_saturation, current_value)
                    
                    color_exists = any(colors_are_similar(new_color, existing_color) for existing_color in mod_data["BASE_COLORS"])
                    
                    if not color_exists:
                        mod_data["BASE_COLORS"].append(new_color)
                        message = f"Cor adicionada! Total: {len(mod_data['BASE_COLORS'])}"
                    else:
                        message = "❌ Esta cor já existe na lista!"
                elif rects.get("clear_colors", pygame.Rect(0,0,0,0)).collidepoint(mx, my):
                    mod_data["BASE_COLORS"] = []
                    message = "Todas as cores foram removidas"
                else:
                    colors_display_x = padding_x + 20 + 180 + 110
                    colors_display_y = y_position + 125
                    
                    colors_per_row = 6
                    for i, color in enumerate(mod_data['BASE_COLORS']):
                        row = i // colors_per_row
                        col = i % colors_per_row
                        color_display_rect = pygame.Rect(
                            colors_display_x + 10 + col * 42,
                            colors_display_y + 10 + row * 42,
                            38, 38
                        )
                        remove_rect = pygame.Rect(color_display_rect.right - 12, color_display_rect.top - 6, 18, 18)
                        
                        if remove_rect.collidepoint(mx, my):
                            mod_data["BASE_COLORS"].pop(i)
                            message = f"Cor removida! Total: {len(mod_data['BASE_COLORS'])}"
                            break

                if rects["tile"].collidepoint(mx, my):
                    editing_field = "tile"
                    input_text = str(mod_data["TILE_SIZE"])
                elif rects["freq"].collidepoint(mx, my):
                    editing_field = "freq"
                    input_text = str(mod_data["FREQ"])
                elif rects["anim"].collidepoint(mx, my):
                    mod_data["ENABLE_ANIMATION"] = not mod_data["ENABLE_ANIMATION"]
                elif rects["style"].collidepoint(mx, my):
                    i = styles.index(mod_data["BACKGROUND_STYLE"])
                    mod_data["BACKGROUND_STYLE"] = styles[(i + 1) % len(styles)]
                elif rects["save"].collidepoint(mx, my):
                    pre_save_editing = "name"
                    scroll_y = 0

        elif event.type == pygame.MOUSEMOTION:
            if event.buttons[0]:
                mx, my = event.pos
                if hue_rect and hue_rect.collidepoint(mx, my):
                    relative_x = mx - hue_rect.x
                    current_hue = (relative_x / hue_rect.width) * 360
                elif sv_rect and sv_rect.collidepoint(mx, my):
                    relative_x = mx - sv_rect.x
                    relative_y = my - sv_rect.y
                    current_saturation = (relative_x / sv_rect.width) * 100
                    current_value = 100 - (relative_y / sv_rect.height) * 100

    content_height = calculate_content_height()

pygame.quit()