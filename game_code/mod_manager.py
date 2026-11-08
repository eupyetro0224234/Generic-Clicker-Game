import pygame, os, json, importlib.util, inspect, sys, io
from game_assets.game_assets_packed import load_image_raw
from PIL import Image

def get_config_path():
    appdata = os.getenv("APPDATA")
    if not appdata:
        return None
    game_folder = os.path.join(appdata, "genericclickergame")
    os.makedirs(game_folder, exist_ok=True)
    return os.path.join(game_folder, "config.json")

def load_config():
    config_path = get_config_path()
    default_config = {"Ativar Mods": False}
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
    base_path = os.path.join(appdata, "genericclickergame", "mods") if appdata else os.path.abspath(".")
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
        classes = [(name, obj) for name, obj in inspect.getmembers(mod)
                   if inspect.isclass(obj) and obj.__module__ == mod.__name__]
        if classes:
            return classes[0]
        return None, None
    except Exception:
        return None, None

def group_mods_by_class(mod_files, mods_folder):
    mod_groups = {}
    for mod_file in mod_files:
        mod_path = os.path.join(mods_folder, mod_file)
        class_name, class_obj = get_mod_class_info(mod_path)
        key = class_name if class_name else "Outros"
        mod_groups.setdefault(key, []).append(mod_file)
    return mod_groups

def _draw_rounded_rect_aa(surface, color, rect, radius):
    temp_surface = pygame.Surface((rect[2] + 4, rect[3] + 4), pygame.SRCALPHA)
    temp_surface.fill((0, 0, 0, 0))
    pygame.draw.rect(temp_surface, color, pygame.Rect(2, 2, rect[2], rect[3]), border_radius=radius)
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
    pygame.draw.rect(border_surface, border_color, (0, 0, width, height), width=2, border_radius=20)
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
    pygame.draw.rect(border_surface, border_color, (0, 0, width, height), width=1, border_radius=14)
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
    pygame.draw.rect(border_surface, border_color, (0, 0, width, height), width=2, border_radius=16)
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

def _ease_out_cubic(t):
    return 1 - (1 - t) ** 3

def _ease_in_cubic(t):
    return t ** 3

def _draw_mod_item(surface, rect, mod_file, small_font, text_color, is_hovered, alpha=255, clip_rect=None):
    """Draws a single mod item button, optionally clipped to clip_rect."""
    old_clip = surface.get_clip()
    if clip_rect:
        surface.set_clip(clip_rect)

    btn = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    color = (220, 235, 255) if is_hovered else (255, 255, 255)
    pygame.draw.rect(btn, color, (0, 0, rect.width, rect.height), border_radius=20)
    pygame.draw.rect(btn, (150, 150, 150), (0, 0, rect.width, rect.height), width=2, border_radius=20)
    btn.set_alpha(alpha)

    # Shadow (drawn separately so it respects clip too)
    shadow = pygame.Surface((rect.width + 6, rect.height + 6), pygame.SRCALPHA)
    pygame.draw.rect(shadow, (0, 0, 0, 20), (0, 0, rect.width + 6, rect.height + 6), border_radius=20)
    shadow.set_alpha(alpha)
    surface.blit(shadow, (rect.x - 3, rect.y - 3))
    surface.blit(btn, (rect.x, rect.y))

    display_name = mod_file[:-7] if mod_file.endswith('_mod.py') else mod_file
    text_surf = small_font.render(display_name, True, text_color)
    text_surf.set_alpha(alpha)
    surface.blit(text_surf, text_surf.get_rect(center=(rect.centerx, rect.centery)))

    surface.set_clip(old_clip)

def choose_mod(mod_groups, current_setting):
    pygame.init()
    info = pygame.display.Info()
    screen_width, screen_height = info.current_w, info.current_h
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.NOFRAME)
    pygame.display.set_caption("Selecionar Mod")

    bg_main = (255, 182, 193)
    text_color = (47, 24, 63)
    title_color = (120, 160, 255, 200)
    title_border_color = (100, 140, 220, 180)
    blue_glass_bg = (180, 210, 255, 180)
    blue_glass_border = (120, 150, 220, 160)
    background_box_color = (240, 240, 255, 100)
    background_box_border = (200, 200, 255, 140)
    option_height = 50
    padding_x = 20
    spacing_y = 8
    title_font = pygame.font.SysFont(None, 56)
    font = pygame.font.SysFont(None, 36)
    small_font = pygame.font.SysFont(None, 26)

    HALF_ANIM = 130  # ms per phase (out then in)

    try:
        start_bytes = load_image_raw("start.png")
        start_image = pygame.image.load(io.BytesIO(start_bytes)).convert_alpha()
        start_image_rounded = _create_rounded_button_with_image(start_image, radius=20)
        start_image_hover = _create_rounded_button_with_image(start_image, radius=20)
        start_image_hover.fill((30, 30, 30, 0), special_flags=pygame.BLEND_RGBA_SUB)
    except Exception:
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

    # anim dict: mod_file, from_col ('left'|'right'), phase ('out'|'in'),
    #            start_time (ms), pending_action (callable)
    anim = None

    while running:
        now = pygame.time.get_ticks()

        # Advance animation phases
        if anim:
            elapsed = now - anim['start_time']
            if anim['phase'] == 'out' and elapsed >= HALF_ANIM:
                anim['pending_action']()       # actually move the mod in the lists
                anim['phase'] = 'in'
                anim['start_time'] = now
            elif anim['phase'] == 'in' and elapsed >= HALF_ANIM:
                anim = None                    # animation complete

        screen.fill(bg_main)
        main_surface = _create_glass_effect(main_box_width, main_box_height, blue_glass_bg, blue_glass_border)
        title_surf = title_font.render("Seleção de Mods", True, text_color)
        main_surface.blit(title_surf, title_surf.get_rect(center=(main_box_width // 2, 50)))

        mouse_pos = pygame.mouse.get_pos()
        relative_mouse = (mouse_pos[0] - main_box_x, mouse_pos[1] - main_box_y)

        col_width = (main_box_width - 3 * padding_x) // 2
        left_col_x = padding_x
        right_col_x = left_col_x + col_width + padding_x
        title_h = option_height + 20
        left_title_y = 100

        # Column titles
        for col_x, label in [(left_col_x, "Mods Desativados"), (right_col_x, "Mods Ativos")]:
            ts = _create_glass_title(col_width, title_h, title_color, title_border_color)
            main_surface.blit(ts, (col_x, left_title_y))
            t = font.render(label, True, text_color)
            main_surface.blit(t, t.get_rect(center=(col_x + col_width // 2, left_title_y + title_h // 2)))

        content_start_y = left_title_y + title_h + spacing_y
        content_height = main_box_height - content_start_y - 150

        left_background = _create_glass_effect(col_width, content_height, background_box_color, background_box_border)
        main_surface.blit(left_background, (left_col_x, content_start_y))
        right_background = _create_glass_effect(col_width, content_height, background_box_color, background_box_border)
        main_surface.blit(right_background, (right_col_x, content_start_y))

        # Clip regions (in main_surface coords) so items don't bleed outside boxes
        left_clip  = pygame.Rect(left_col_x + 2,  content_start_y + 2, col_width - 4,  content_height - 4)
        right_clip = pygame.Rect(right_col_x + 2, content_start_y + 2, col_width - 4,  content_height - 4)

        # Pre-compute alpha for the animated item (fade only, no sliding)
        anim_alpha = 255
        if anim:
            elapsed = now - anim['start_time']
            t = min(elapsed / HALF_ANIM, 1.0)
            if anim['phase'] == 'out':
                anim_alpha = int(255 * (1 - t))
            else:  # 'in'
                anim_alpha = int(255 * t)

        # Draw disabled column
        current_y = content_start_y + 10 - scroll_y
        buttons_disabled = []
        for mod_file in disabled_mods:
            r = pygame.Rect(left_col_x + 15, current_y, col_width - 30, option_height)
            buttons_disabled.append((
                pygame.Rect(main_box_x + r.x, main_box_y + r.y, r.width, r.height),
                mod_file
            ))
            is_anim = anim and anim['mod_file'] == mod_file
            if is_anim:
                _draw_mod_item(main_surface, r, mod_file, small_font, text_color, False, anim_alpha, left_clip)
            else:
                hov = r.collidepoint(relative_mouse) and not anim
                _draw_mod_item(main_surface, r, mod_file, small_font, text_color, hov, 255, left_clip)
            current_y += option_height + spacing_y

        # Draw enabled column
        current_y_right = content_start_y + 10 - scroll_y
        buttons_enabled = []
        for mod_file in enabled_mods:
            r = pygame.Rect(right_col_x + 15, current_y_right, col_width - 30, option_height)
            buttons_enabled.append((
                pygame.Rect(main_box_x + r.x, main_box_y + r.y, r.width, r.height),
                mod_file
            ))
            is_anim = anim and anim['mod_file'] == mod_file
            if is_anim:
                _draw_mod_item(main_surface, r, mod_file, small_font, text_color, False, anim_alpha, right_clip)
            else:
                hov = r.collidepoint(relative_mouse) and not anim
                _draw_mod_item(main_surface, r, mod_file, small_font, text_color, hov, 255, right_clip)
            current_y_right += option_height + spacing_y

        # Scrollbar math
        total_height_left  = len(disabled_mods) * (option_height + spacing_y) + 20
        total_height_right = len(enabled_mods)  * (option_height + spacing_y) + 20
        max_content_height = max(total_height_left, total_height_right)
        visible_height = content_height - 20
        max_scroll = max(0, max_content_height - visible_height)

        counter_surf = small_font.render(f"Mods ativados: {len(enabled_mods)}", True, (80, 120, 80))
        main_surface.blit(counter_surf, counter_surf.get_rect(center=(main_box_width // 2, main_box_height - 110)))

        # Conclude / start button
        if start_image_rounded and start_image_hover:
            bw, bh = start_image_rounded.get_size()
            bx = (main_box_width - bw) // 2
            by = main_box_height - 70
            concluido_rect_rel = pygame.Rect(bx, by, bw, bh)
            concluido_rect_abs = pygame.Rect(main_box_x + bx, main_box_y + by, bw, bh)
            img = start_image_hover if concluido_rect_rel.collidepoint(relative_mouse) else start_image_rounded
            main_surface.blit(img, (bx, by))
        else:
            bw, bh = 200, 50
            bx = (main_box_width - bw) // 2
            by = main_box_height - 60
            concluido_rect_rel = pygame.Rect(bx, by, bw, bh)
            concluido_rect_abs = pygame.Rect(main_box_x + bx, main_box_y + by, bw, bh)
            is_hov = concluido_rect_rel.collidepoint(relative_mouse)
            cs = _create_glass_button(bw, bh, (120, 180, 240, 240) if is_hov else (150, 200, 255, 220), blue_glass_border)
            main_surface.blit(cs, (bx, by))
            ct = font.render("Concluído", True, text_color)
            main_surface.blit(ct, ct.get_rect(center=(bx + bw // 2, by + bh // 2)))

        if max_scroll > 0:
            ratio = scroll_y / max_scroll
            sb_h = max(50, (visible_height / max_content_height) * visible_height)
            sb_y = content_start_y + ratio * (visible_height - sb_h)
            ss = _create_glass_button(10, int(sb_h), (180, 180, 200, 180), blue_glass_border)
            main_surface.blit(ss, (main_box_width - 20, sb_y))

        screen.blit(main_surface, (main_box_x, main_box_y))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.ACTIVEEVENT:
                if event.state == 2 and event.gain == 0:
                    waiting = True
                    while waiting:
                        for e in pygame.event.get():
                            if e.type == pygame.ACTIVEEVENT and e.state == 2 and e.gain == 1:
                                waiting = False
                            if e.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit()
                        clock.tick(15)
                    continue

            if event.type == pygame.QUIT:
                running = False
                enabled_mods = []
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and not anim:
                    clicked = False
                    for rect, mod_file in buttons_disabled:
                        if rect.collidepoint(mouse_pos):
                            clicked = True
                            mod_class = mod_to_class[mod_file]
                            # Evict conflicting enabled mod instantly (no animation for the eviction)
                            for em in list(enabled_mods):
                                if mod_to_class[em] == mod_class:
                                    enabled_mods.remove(em)
                                    disabled_mods.append(em)
                                    break
                            _m = mod_file
                            def _enable(m=_m):
                                disabled_mods.remove(m)
                                enabled_mods.append(m)
                            anim = {'mod_file': mod_file, 'from_col': 'left',
                                    'phase': 'out', 'start_time': pygame.time.get_ticks(),
                                    'pending_action': _enable}
                            break
                    if not clicked:
                        for rect, mod_file in buttons_enabled:
                            if rect.collidepoint(mouse_pos):
                                _m = mod_file
                                def _disable(m=_m):
                                    enabled_mods.remove(m)
                                    disabled_mods.append(m)
                                anim = {'mod_file': mod_file, 'from_col': 'right',
                                        'phase': 'out', 'start_time': pygame.time.get_ticks(),
                                        'pending_action': _disable}
                                break

                    if concluido_rect_abs.collidepoint(mouse_pos):
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
    return None

def load_mod():
    config = load_config()
    if not config.get("Ativar Mods", False):
        return None
    mods_folder = get_mods_folder()
    selected_mod_file = load_selected_mod(mods_folder, True)
    if selected_mod_file:
        try:
            return load_mod_from_path(selected_mod_file)
        except Exception:
            return None
    return None