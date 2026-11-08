import pygame, urllib.request, json, os
from io import BytesIO
from PIL import Image
from game_assets.game_assets_packed import load_image

class ImageViewer:
    IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.tiff')

    _CONFIG_PATH = os.path.join(
        os.getenv("APPDATA", os.path.expanduser("~")),
        "genericclickergame", "config.json"
    )

    def __init__(self, screen, width, height, settings_menu=None, on_viewed_callback=None):
        self.screen = screen
        self.width = width
        self.height = height
        self.visible = False
        self.image = None
        self.image_rect = None
        self.close_button_rect = None
        self.loading = False
        self.error = False
        self.TEXT_FILE_URL = "https://raw.githack.com/eupyetro0224234/Generic-Clicker-Game/main/github_assets/imagem.txt"
        self.IMAGE_URL = None

        self._settings_menu = settings_menu
        self._on_viewed_callback = on_viewed_callback

        self.dont_show_again = False
        self.checkbox_rect = None
        self.checkbox_hit_rect = None

        self.blur_surface = None
        self.pre_blurs = []
        self.fade_alpha = 0
        self.fade_speed = 20
        self.fade_in_complete = False
        self._blur_captured = False

        self.fading_close = False
        self.close_alpha = 0
        self.close_speed = 20

        try:
            self.close_image = load_image("close.png")
            self.close_image = pygame.transform.smoothscale(self.close_image, (40, 40))
        except Exception:
            self.close_image = None

        if self._config_get_show():
            self.load_image_url_from_text_file()

    def _config_load(self):
        try:
            if os.path.isfile(self._CONFIG_PATH):
                with open(self._CONFIG_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def _config_save(self, data):
        try:
            os.makedirs(os.path.dirname(self._CONFIG_PATH), exist_ok=True)
            with open(self._CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception:
            pass

    def _config_get_show(self):
        data = self._config_load()
        return data.get("Exibir imagens", True)

    def _config_set_show(self, value: bool):
        data = self._config_load()
        data["Exibir imagens"] = value
        self._config_save(data)

        if self._settings_menu is not None:
            self._settings_menu.options["Exibir imagens"] = value

    def _capture_blur(self):
        self.blur_surface = self.screen.copy()
        small = pygame.transform.smoothscale(self.blur_surface, (self.width // 8, self.height // 8))
        self.blur_surface = pygame.transform.smoothscale(small, (self.width, self.height))
        overlay = pygame.Surface((self.width, self.height))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(100)
        self.blur_surface.blit(overlay, (0, 0))
        self.blur_surface = self.blur_surface.convert_alpha()
        self.pre_blurs = []
        for alpha in range(0, 256, 25):
            temp = self.blur_surface.copy()
            temp.set_alpha(alpha)
            self.pre_blurs.append(temp)
        self._blur_captured = True

    def _start_close(self):
        self.fading_close = True
        self.close_alpha = 0
        if self._on_viewed_callback:
            self._on_viewed_callback()

    def _is_direct_image_url(self, url):
        path = url.split('?')[0].lower()
        return path.endswith(self.IMAGE_EXTENSIONS)

    def load_image_url_from_text_file(self):
        try:
            if self._is_direct_image_url(self.TEXT_FILE_URL):
                self.IMAGE_URL = self.TEXT_FILE_URL
                self.load_image_from_url(self.IMAGE_URL)
            else:
                with urllib.request.urlopen(self.TEXT_FILE_URL, timeout=10) as response:
                    self.IMAGE_URL = response.readline().decode('utf-8').strip()
                    if self.IMAGE_URL:
                        self.load_image_from_url(self.IMAGE_URL)
        except Exception as e:
            print(f"Erro ao carregar URL da imagem: {e}")
            self.error = True

    def load_image_from_url(self, url):
        self.loading = True
        self.error = False
        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                image_data = response.read()

            pil_image = Image.open(BytesIO(image_data))

            max_width = self.width * 0.8
            max_height = self.height * 0.8

            width_ratio = max_width / pil_image.width
            height_ratio = max_height / pil_image.height
            scale_ratio = min(width_ratio, height_ratio)

            new_width = int(pil_image.width * scale_ratio)
            new_height = int(pil_image.height * scale_ratio)

            pil_image = pil_image.resize((new_width, new_height), Image.LANCZOS)

            mode = pil_image.mode
            size = pil_image.size
            data = pil_image.tobytes()

            pygame_image = pygame.image.fromstring(data, size, mode)
            self.image = pygame_image
            self.scale_image_to_fit()
            self.visible = True
            return True
        except Exception as e:
            print(f"Erro ao carregar imagem: {e}")
            self.error = True
            return False
        finally:
            self.loading = False

    def scale_image_to_fit(self):
        if self.image:
            self.image_rect = self.image.get_rect(center=(self.width // 2, self.height // 2 + 10))

    def handle_event(self, event):
        if not self.visible:
            return False

        if self.fading_close:
            return True

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self._start_close()
            return True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()

            hit = getattr(self, 'checkbox_hit_rect', self.checkbox_rect)
            if hit and hit.collidepoint(mouse_pos):
                self.dont_show_again = not self.dont_show_again
                self._config_set_show(not self.dont_show_again)
                return True

            if self.close_button_rect and self.close_button_rect.collidepoint(mouse_pos):
                self._start_close()
                return True

            container = getattr(self, 'container_rect', None)
            if container and not container.collidepoint(mouse_pos):
                self._start_close()
                return True

        return False

    def _draw_content(self, alpha):
        if self.error:
            font = pygame.font.SysFont(None, 36)
            error_surf = font.render("Erro ao carregar a imagem", True, (255, 0, 0))
            error_surf.set_alpha(alpha)
            text_rect = error_surf.get_rect(center=(self.width // 2, self.height // 2))
            self.screen.blit(error_surf, text_rect)
        elif self.image and self.image_rect:
            TOP_PAD  = 60
            BOT_PAD  = 44
            BOX_SIZE = 16

            self.container_rect = pygame.Rect(
                self.image_rect.x - 20,
                self.image_rect.y - TOP_PAD,
                self.image_rect.width + 40,
                self.image_rect.height + TOP_PAD + BOT_PAD
            )

            container_surf = pygame.Surface(
                (self.container_rect.width, self.container_rect.height), pygame.SRCALPHA
            )
            pygame.draw.rect(container_surf, (255, 182, 193, alpha),
                             container_surf.get_rect(), border_radius=30)
            pygame.draw.rect(container_surf, (200, 200, 200, alpha),
                             container_surf.get_rect(), 2, border_radius=30)
            self.screen.blit(container_surf, self.container_rect)

            img_copy = self.image.copy()
            img_copy.set_alpha(alpha)
            self.screen.blit(img_copy, self.image_rect)

            close_btn_size = 40
            self.close_button_rect = pygame.Rect(
                self.container_rect.right - close_btn_size - 15,
                self.container_rect.top + 10,
                close_btn_size,
                close_btn_size
            )

            if self.close_image:
                close_copy = self.close_image.copy()
                close_copy.set_alpha(alpha)
                image_rect = close_copy.get_rect(center=self.close_button_rect.center)
                self.screen.blit(close_copy, image_rect)
            else:
                btn_surf = pygame.Surface((close_btn_size, close_btn_size), pygame.SRCALPHA)
                pygame.draw.rect(btn_surf, (255, 100, 100, alpha), btn_surf.get_rect(), border_radius=8)
                self.screen.blit(btn_surf, self.close_button_rect)
                center_x, center_y = self.close_button_rect.center
                line_length = 15
                line_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                pygame.draw.line(line_surf, (255, 255, 255, alpha),
                                 (center_x - line_length, center_y - line_length),
                                 (center_x + line_length, center_y + line_length), 2)
                pygame.draw.line(line_surf, (255, 255, 255, alpha),
                                 (center_x - line_length, center_y + line_length),
                                 (center_x + line_length, center_y - line_length), 2)
                self.screen.blit(line_surf, (0, 0))

            checkbox_y = self.image_rect.bottom + (BOT_PAD - BOX_SIZE) // 2
            checkbox_x = self.container_rect.left + 20
            self.checkbox_rect = pygame.Rect(checkbox_x, checkbox_y, BOX_SIZE, BOX_SIZE)

            cb_surf = pygame.Surface((BOX_SIZE, BOX_SIZE), pygame.SRCALPHA)
            pygame.draw.rect(cb_surf, (255, 255, 255, alpha), cb_surf.get_rect(), border_radius=3)
            pygame.draw.rect(cb_surf, (120, 80, 100, alpha), cb_surf.get_rect(), 2, border_radius=3)
            self.screen.blit(cb_surf, self.checkbox_rect)

            if self.dont_show_again:
                check_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                cx = checkbox_x + BOX_SIZE // 2
                cy = checkbox_y + BOX_SIZE // 2
                pygame.draw.line(check_surf, (180, 60, 90, alpha),
                                 (cx - 4, cy), (cx - 1, cy + 4), 2)
                pygame.draw.line(check_surf, (180, 60, 90, alpha),
                                 (cx - 1, cy + 4), (cx + 5, cy - 4), 2)
                self.screen.blit(check_surf, (0, 0))

            font = pygame.font.SysFont(None, 22)
            label_surf = font.render("Não mostrar novamente", True, (100, 50, 70))
            label_surf.set_alpha(alpha)
            label_rect = label_surf.get_rect(
                midleft=(checkbox_x + BOX_SIZE + 8, checkbox_y + BOX_SIZE // 2)
            )
            self.screen.blit(label_surf, label_rect)

            self.checkbox_hit_rect = self.checkbox_rect.union(label_rect)

    def draw(self):
        if not self.visible or self.loading:
            return

        if self.fading_close:
            self.close_alpha += self.close_speed
            if self.close_alpha > 255:
                self.close_alpha = 255

            current_alpha = max(255 - self.close_alpha, 0)

            if self.pre_blurs:
                index = min(len(self.pre_blurs) - 1, current_alpha // 25)
                self.screen.blit(self.pre_blurs[index], (0, 0))

            self._draw_content(current_alpha)

            if self.close_alpha >= 255:
                self.visible = False
                self.fading_close = False
                self.close_alpha = 0
            return

        if not self._blur_captured:
            self._capture_blur()
            self.fade_alpha = 0
            self.fade_in_complete = False

        if not self.fade_in_complete:
            self.fade_alpha += self.fade_speed
            if self.fade_alpha >= 255:
                self.fade_alpha = 255
                self.fade_in_complete = True

        if self.pre_blurs:
            index = min(len(self.pre_blurs) - 1, self.fade_alpha // 25)
            self.screen.blit(self.pre_blurs[index], (0, 0))
        else:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

        self._draw_content(self.fade_alpha)

        if self.loading:
            font = pygame.font.SysFont(None, 36)
            loading_text = font.render("Carregando imagem...", True, (255, 255, 255))
            text_rect = loading_text.get_rect(center=(self.width // 2, self.height // 2))
            self.screen.blit(loading_text, text_rect)

    def toggle_visibility(self):
        if self.visible:
            self._start_close()
        else:
            if self._config_get_show():
                self.visible = True
                self._blur_captured = False
                self.fade_alpha = 0
                self.fade_in_complete = False
        return self.visible