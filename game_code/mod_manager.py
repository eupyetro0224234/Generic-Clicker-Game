import pygame, os, json, importlib.util, inspect, sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(base_path, relative_path)

def get_config_path():
    appdata = os.getenv("APPDATA")
    if not appdata:
        return None
    game_folder = os.path.join(appdata, "genericclickergame")
    if not os.path.exists(game_folder):
        os.makedirs(game_folder, exist_ok=True)
    return os.path.join(game_folder, "config.json")

def load_config():
    config_path = get_config_path()
    default_config = {
        "Ativar Mods": False,
    }
    if not config_path or not os.path.isfile(config_path):
        return default_config
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
            return {**default_config, **cfg}
    except Exception:
        return default_config

def save_config(config):
    config_path = get_config_path()
    if config_path:
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
        except Exception:
            pass

def get_mods_folder():
    appdata = os.getenv("APPDATA")
    if not appdata:
        base_path = os.path.abspath(".")
    else:
        base_path = os.path.join(appdata, "genericclickergame", "mods")
    if not os.path.exists(base_path):
        os.makedirs(base_path, exist_ok=True)
    return base_path

def load_mod_from_path(path):
    spec = importlib.util.spec_from_file_location("mod_background_temp", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def get_mod_class_info(mod_path):
    try:
        mod = load_mod_from_path(mod_path)
        classes = []
        for name, obj in inspect.getmembers(mod):
            if inspect.isclass(obj) and obj.__module__ == mod.__name__:
                classes.append((name, obj))
        if classes:
            class_name, class_obj = classes[0]
            return class_name, class_obj
        return None, None
    except Exception:
        return None, None

def group_mods_by_class(mod_files, mods_folder):
    mod_groups = {}
    for mod_file in mod_files:
        mod_path = os.path.join(mods_folder, mod_file)
        class_name, class_obj = get_mod_class_info(mod_path)
        if class_name:
            if class_name not in mod_groups:
                mod_groups[class_name] = []
            mod_groups[class_name].append(mod_file)
        else:
            if "Outros" not in mod_groups:
                mod_groups["Outros"] = []
            mod_groups["Outros"].append(mod_file)
    return mod_groups

def _draw_rounded_rect_aa(surface, color, rect, radius):
    temp_surface = pygame.Surface((rect[2] + 4, rect[3] + 4), pygame.SRCALPHA)
    temp_surface.fill((0, 0, 0, 0))
    temp_rect = pygame.Rect(2, 2, rect[2], rect[3])
    pygame.draw.rect(temp_surface, color, temp_rect, border_radius=radius)
    surface.blit(temp_surface, (rect[0] - 2, rect[1] - 2))

def _create_glass_effect(width, height, bg_color=(180, 210, 255, 180), border_color=(120, 150, 220, 160)):
    glass_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    glass_surface.fill((0, 0, 0, 0))
    _draw_rounded_rect_aa(glass_surface, bg_color, (0, 0, width, height), 20)
    highlight = pygame.Surface((width, height), pygame.SRCALPHA)
    highlight.fill((0, 0, 0, 0))
    for i in range(height):
        alpha = int(50 * (1 - i / height * 0.6))
        pygame.draw.line(highlight, (255, 255, 255, alpha), (0, i), (width, i))
    mask = pygame.Surface((width, height), pygame.SRCALPHA)
    mask.fill((0, 0, 0, 0))
    _draw_rounded_rect_aa(mask, (255, 255, 255, 255), (0, 0, width, height), 20)
    highlight.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    glass_surface.blit(highlight, (0, 0))
    border_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    border_surface.fill((0, 0, 0, 0))
    _draw_rounded_rect_aa(border_surface, (0, 0, 0, 0), (0, 0, width, height), 20)
    pygame.draw.rect(border_surface, border_color, (0, 0, width, height), 
                    width=2, border_radius=20)
    glass_surface.blit(border_surface, (0, 0))
    return glass_surface

def _create_glass_button(width, height, color, border_color=(150, 180, 230, 160)):
    button_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    button_surface.fill((0, 0, 0, 0))
    _draw_rounded_rect_aa(button_surface, color, (0, 0, width, height), 14)
    highlight = pygame.Surface((width, height), pygame.SRCALPHA)
    highlight.fill((0, 0, 0, 0))
    for i in range(height):
        alpha = int(40 * (1 - i / height * 0.7))
        pygame.draw.line(highlight, (255, 255, 255, alpha), (0, i), (width, i))
    mask = pygame.Surface((width, height), pygame.SRCALPHA)
    mask.fill((0, 0, 0, 0))
    _draw_rounded_rect_aa(mask, (255, 255, 255, 255), (0, 0, width, height), 14)
    highlight.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    button_surface.blit(highlight, (0, 0))
    border_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    border_surface.fill((0, 0, 0, 0))
    _draw_rounded_rect_aa(border_surface, (0, 0, 0, 0), (0, 0, width, height), 14)
    pygame.draw.rect(border_surface, border_color, (0, 0, width, height), 
                    width=1, border_radius=14)
    button_surface.blit(border_surface, (0, 0))
    return button_surface

def _create_glass_title(width, height, color=(120, 160, 255, 200), border_color=(100, 140, 220, 180)):
    title_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    title_surface.fill((0, 0, 0, 0))
    _draw_rounded_rect_aa(title_surface, color, (0, 0, width, height), 16)
    highlight = pygame.Surface((width, height), pygame.SRCALPHA)
    highlight.fill((0, 0, 0, 0))
    for i in range(height):
        alpha = int(60 * (1 - i / height * 0.5))
        pygame.draw.line(highlight, (255, 255, 255, alpha), (0, i), (width, i))
    mask = pygame.Surface((width, height), pygame.SRCALPHA)
    mask.fill((0, 0, 0, 0))
    _draw_rounded_rect_aa(mask, (255, 255, 255, 255), (0, 0, width, height), 16)
    highlight.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    title_surface.blit(highlight, (0, 0))
    border_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    border_surface.fill((0, 0, 0, 0))
    _draw_rounded_rect_aa(border_surface, (0, 0, 0, 0), (0, 0, width, height), 16)
    pygame.draw.rect(border_surface, border_color, (0, 0, width, height), 
                    width=2, border_radius=16)
    title_surface.blit(border_surface, (0, 0))
    return title_surface

def _create_rounded_button_with_image(image, radius=20):
    width, height = image.get_size()
    mask = pygame.Surface((width, height), pygame.SRCALPHA)
    mask.fill((0, 0, 0, 0))
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, width, height), border_radius=radius)
    rounded_image = image.copy()
    rounded_image.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return rounded_image

def choose_mod(mod_groups, current_setting):
    pygame.init()
    info = pygame.display.Info()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    screen_width, screen_height = screen.get_size()
    pygame.display.set_caption("Selecionar Mod")

    bg_main = (255, 182, 193)
    text_color = (47, 24, 63)
    button_disabled_color = (255, 255, 255, 220)
    button_disabled_hover = (255, 220, 230, 240)
    button_enabled_color = (180, 255, 180, 220)
    button_enabled_hover = (150, 240, 150, 240)
    title_color = (120, 160, 255, 200)
    title_border_color = (100, 140, 220, 180)
    blue_glass_bg = (180, 210, 255, 180)
    blue_glass_border = (120, 150, 220, 160)
    background_box_color = (240, 240, 255, 100)
    background_box_border = (200, 200, 255, 140)
    option_height = 60
    padding_x = 20
    padding_y = 20
    spacing_y = 10
    title_font = pygame.font.SysFont(None, 56)
    font = pygame.font.SysFont(None, 36)
    small_font = pygame.font.SysFont(None, 26)

    try:
        start_image_path = resource_path("game_assets/start.png")
        start_image = pygame.image.load(start_image_path).convert_alpha()
        original_width, original_height = start_image.get_size()
        button_width = original_width
        button_height = original_height
        start_image_rounded = _create_rounded_button_with_image(start_image, radius=20)
        start_image_hover = _create_rounded_button_with_image(start_image, radius=20)
        start_image_hover.fill((30, 30, 30, 0), special_flags=pygame.BLEND_RGBA_SUB)
    except Exception as e:
        start_image_rounded = None
        start_image_hover = None

    main_box_width = min(1200, screen_width - 100)
    main_box_height = min(700, screen_height - 100)
    main_box_x = (screen_width - main_box_width) // 2
    main_box_y = (screen_height - main_box_height) // 2

    disabled_mods = []
    enabled_mods = []
    mod_to_class = {}
    for class_name, mods in mod_groups.items():
        for mod_file in mods:
            mod_to_class[mod_file] = class_name
            disabled_mods.append(mod_file)

    scroll_y = 0
    max_scroll = 0
    clock = pygame.time.Clock()
    running = True

    while running:
        screen.fill(bg_main)
        main_surface = _create_glass_effect(main_box_width, main_box_height, blue_glass_bg, blue_glass_border)
        title_surf = title_font.render("Seleção de Mods", True, text_color)
        title_rect = title_surf.get_rect(center=(main_box_width // 2, 50))
        main_surface.blit(title_surf, title_rect)
        mouse_pos = pygame.mouse.get_pos()
        relative_mouse = (mouse_pos[0] - main_box_x, mouse_pos[1] - main_box_y)
        col_width = (main_box_width - 3 * padding_x) // 2
        left_col_x = padding_x
        left_title_y = 100
        left_title_surface = _create_glass_title(col_width, option_height, title_color, title_border_color)
        main_surface.blit(left_title_surface, (left_col_x, left_title_y))
        left_title = font.render("Mods Desativados", True, text_color)
        left_title_pos = left_title.get_rect(center=(left_col_x + col_width // 2, left_title_y + option_height // 2))
        main_surface.blit(left_title, left_title_pos)
        right_col_x = left_col_x + col_width + padding_x
        right_title_surface = _create_glass_title(col_width, option_height, title_color, title_border_color)
        main_surface.blit(right_title_surface, (right_col_x, left_title_y))
        right_title = font.render("Mods Ativos", True, text_color)
        right_title_pos = right_title.get_rect(center=(right_col_x + col_width // 2, left_title_y + option_height // 2))
        main_surface.blit(right_title, right_title_pos)
        content_start_y = left_title_y + option_height + spacing_y
        content_height = main_box_height - content_start_y - 150
        left_background = _create_glass_effect(col_width, content_height, background_box_color, background_box_border)
        main_surface.blit(left_background, (left_col_x, content_start_y))
        right_background = _create_glass_effect(col_width, content_height, background_box_color, background_box_border)
        main_surface.blit(right_background, (right_col_x, content_start_y))
        current_y = content_start_y + 10 - scroll_y
        buttons_disabled = []
        for mod_file in disabled_mods:
            mod_rect_rel = pygame.Rect(left_col_x + 15, current_y, col_width - 30, option_height)
            mod_rect_abs = pygame.Rect(main_box_x + mod_rect_rel.x, main_box_y + mod_rect_rel.y, 
                                      mod_rect_rel.width, mod_rect_rel.height)
            buttons_disabled.append((mod_rect_abs, mod_file))
            is_hovered = mod_rect_rel.collidepoint(relative_mouse)
            color = button_disabled_hover if is_hovered else button_disabled_color
            button_surface = _create_glass_button(mod_rect_rel.width, mod_rect_rel.height, color, blue_glass_border)
            main_surface.blit(button_surface, (mod_rect_rel.x, mod_rect_rel.y))
            mod_text = small_font.render(mod_file, True, text_color)
            mod_text_rect = mod_text.get_rect(midleft=(mod_rect_rel.x + 15, mod_rect_rel.centery))
            main_surface.blit(mod_text, mod_text_rect)
            current_y += option_height + spacing_y
        current_y_right = content_start_y + 10 - scroll_y
        buttons_enabled = []
        for mod_file in enabled_mods:
            mod_rect_rel = pygame.Rect(right_col_x + 15, current_y_right, col_width - 30, option_height)
            mod_rect_abs = pygame.Rect(main_box_x + mod_rect_rel.x, main_box_y + mod_rect_rel.y,
                                      mod_rect_rel.width, mod_rect_rel.height)
            buttons_enabled.append((mod_rect_abs, mod_file))
            is_hovered = mod_rect_rel.collidepoint(relative_mouse)
            color = button_enabled_hover if is_hovered else button_enabled_color
            button_surface = _create_glass_button(mod_rect_rel.width, mod_rect_rel.height, color, blue_glass_border)
            main_surface.blit(button_surface, (mod_rect_rel.x, mod_rect_rel.y))
            mod_text = small_font.render(mod_file, True, text_color)
            mod_text_rect = mod_text.get_rect(midleft=(mod_rect_rel.x + 15, mod_rect_rel.centery))
            main_surface.blit(mod_text, mod_text_rect)
            current_y_right += option_height + spacing_y
        total_height_left = len(disabled_mods) * (option_height + spacing_y) + 20
        total_height_right = len(enabled_mods) * (option_height + spacing_y) + 20
        max_content_height = max(total_height_left, total_height_right)
        visible_height = content_height - 20
        max_scroll = max(0, max_content_height - visible_height)
        counter_text = f"Mods ativados: {len(enabled_mods)}"
        counter_surf = small_font.render(counter_text, True, (80, 120, 80))
        counter_rect = counter_surf.get_rect(center=(main_box_width // 2, main_box_height - 110))
        main_surface.blit(counter_surf, counter_rect)

        if start_image_rounded and start_image_hover:
            button_width = start_image_rounded.get_width()
            button_height = start_image_rounded.get_height()
            button_x = (main_box_width - button_width) // 2
            button_y = main_box_height - 70
            concluido_rect_rel = pygame.Rect(button_x, button_y, button_width, button_height)
            concluido_rect_abs = pygame.Rect(main_box_x + button_x, main_box_y + button_y, button_width, button_height)
            is_concluido_hovered = concluido_rect_rel.collidepoint(relative_mouse)
            if is_concluido_hovered:
                main_surface.blit(start_image_hover, (button_x, button_y))
            else:
                main_surface.blit(start_image_rounded, (button_x, button_y))
        else:
            button_width = 200
            button_height = 50
            button_x = (main_box_width - button_width) // 2
            button_y = main_box_height - 60
            concluido_rect_rel = pygame.Rect(button_x, button_y, button_width, button_height)
            concluido_rect_abs = pygame.Rect(main_box_x + button_x, main_box_y + button_y, button_width, button_height)
            is_concluido_hovered = concluido_rect_rel.collidepoint(relative_mouse)
            concluido_color = (150, 200, 255, 220) if not is_concluido_hovered else (120, 180, 240, 240)
            concluido_surface = _create_glass_button(button_width, button_height, concluido_color, blue_glass_border)
            main_surface.blit(concluido_surface, (button_x, button_y))
            concluido_text = font.render("Concluído", True, text_color)
            concluido_text_rect = concluido_text.get_rect(center=(button_x + button_width // 2, button_y + button_height // 2))
            main_surface.blit(concluido_text, concluido_text_rect)

        if max_scroll > 0:
            scroll_ratio = scroll_y / max_scroll
            scroll_bar_height = max(50, (visible_height / max_content_height) * visible_height)
            scroll_bar_y = content_start_y + (scroll_ratio * (visible_height - scroll_bar_height))
            scroll_surface = _create_glass_button(10, int(scroll_bar_height), (180, 180, 200, 180), blue_glass_border)
            main_surface.blit(scroll_surface, (main_box_width - 20, scroll_bar_y))

        screen.blit(main_surface, (main_box_x, main_box_y))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                enabled_mods = []
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for rect, mod_file in buttons_disabled:
                        if rect.collidepoint(mouse_pos):
                            mod_class = mod_to_class[mod_file]
                            existing_mod_same_class = None
                            for enabled_mod in enabled_mods:
                                if mod_to_class[enabled_mod] == mod_class:
                                    existing_mod_same_class = enabled_mod
                                    break
                            if existing_mod_same_class:
                                enabled_mods.remove(existing_mod_same_class)
                                disabled_mods.append(existing_mod_same_class)
                            disabled_mods.remove(mod_file)
                            enabled_mods.append(mod_file)
                            break
                    for rect, mod_file in buttons_enabled:
                        if rect.collidepoint(mouse_pos):
                            enabled_mods.remove(mod_file)
                            disabled_mods.append(mod_file)
                            break
                    if 'concluido_rect_abs' in locals() and concluido_rect_abs.collidepoint(mouse_pos):
                        running = False
                elif event.button == 4:
                    scroll_y = max(0, scroll_y - 40)
                elif event.button == 5:
                    scroll_y = min(max_scroll, scroll_y + 40)

            if event.type == pygame.MOUSEWHEEL:
                scroll_y = max(0, min(max_scroll, scroll_y - event.y * 40))

        clock.tick(60)

    pygame.quit()

    return enabled_mods

def load_selected_mod(mods_folder, current_setting):
    if not current_setting:
        return None

    mod_files = [f for f in os.listdir(mods_folder) if f.endswith('_mod.py')]
    if not mod_files:
        return None

    mod_groups = group_mods_by_class(mod_files, mods_folder)

    if not mod_groups:
        return None

    selected_mods = choose_mod(mod_groups, current_setting)
    if selected_mods:
        return os.path.join(mods_folder, selected_mods[0])
    else:
        return None

def load_mod():
    config = load_config()
    ativar_mods = config.get("Ativar Mods", False)

    if not ativar_mods:
        return None

    mods_folder = get_mods_folder()
    selected_mod_file = load_selected_mod(mods_folder, ativar_mods)

    if selected_mod_file:
        try:
            return load_mod_from_path(selected_mod_file)
        except Exception:
            return None

    return None