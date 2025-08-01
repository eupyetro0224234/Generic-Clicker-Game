import pygame
import urllib.request
from io import BytesIO
from PIL import Image

class ImageViewer:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        self.visible = False
        self.image = None
        self.image_rect = None
        self.IMAGE_URL = "https://raw.githubusercontent.com/eupyetro0224234/Generic-Clicker-Game/main/imagem.png"  # URL direta da imagem
        self.loading = False
        self.load_image_from_url(self.IMAGE_URL)  # Carrega a imagem automaticamente

    def load_image_from_url(self, url):
        self.loading = True
        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                image_data = response.read()
            
            pil_image = Image.open(BytesIO(image_data))
            
            # Redimensiona para 1000x1000
            pil_image = pil_image.resize((1000, 1000))
            
            mode = pil_image.mode
            size = pil_image.size
            data = pil_image.tobytes()

            if mode == "RGB":
                pygame_image = pygame.image.fromstring(data, size, "RGB")
            elif mode in ("RGBA", "P"):
                pygame_image = pygame.image.fromstring(data, size, "RGBA")
            else:
                pygame_image = pygame.image.fromstring(data, size, mode)

            self.image = pygame_image
            self.scale_image_to_fit()
            self.visible = True  # Torna visível após carregar
            return True
        except Exception as e:
            print(f"Erro ao carregar imagem: {e}")
            return False
        finally:
            self.loading = False

    def scale_image_to_fit(self):
        if self.image:
            # Centraliza a imagem de 1000x1000
            self.image_rect = self.image.get_rect(center=(self.width // 2, self.height // 2))