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
        self.close_button_rect = None
        self.loading = False
        self.error = False
        self.TEXT_FILE_URL = "https://raw.githubusercontent.com/eupyetro0224234/Generic-Clicker-Game/main/imagens.txt"
        self.IMAGE_URL = None
        
        # Carrega a URL da imagem do arquivo de texto
        self.load_image_url_from_text_file()

    def load_image_url_from_text_file(self):
        try:
            with urllib.request.urlopen(self.TEXT_FILE_URL, timeout=10) as response:
                # Lê a primeira linha do arquivo (assumindo que a URL está na primeira linha)
                self.IMAGE_URL = response.readline().decode('utf-8').strip()
                # Agora carrega a imagem
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
            
            # Calcula o tamanho máximo que a imagem pode ter na tela
            max_width = self.width * 0.9  # 90% da largura da tela
            max_height = self.height * 0.9  # 90% da altura da tela
            
            # Redimensiona mantendo a proporção
            width_ratio = max_width / pil_image.width
            height_ratio = max_height / pil_image.height
            scale_ratio = min(width_ratio, height_ratio)
            
            new_width = int(pil_image.width * scale_ratio)
            new_height = int(pil_image.height * scale_ratio)
            
            # Redimensiona a imagem
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
            # Centraliza a imagem na tela
            self.image_rect = self.image.get_rect(center=(self.width // 2, self.height // 2))

    def handle_event(self, event):
        if not self.visible:
            return False
            
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.visible = False
            return True
            
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            # Verifica se clicou no botão de fechar
            if self.close_button_rect and self.close_button_rect.collidepoint(mouse_pos):
                self.visible = False
                return True
                
            # Verifica se clicou fora da imagem para fechar
            if self.image_rect and not self.image_rect.collidepoint(mouse_pos):
                self.visible = False
                return True
                
        return False

    def draw(self):
        if not self.visible or self.loading:
            return
            
        # Desenha fundo semi-transparente
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        if self.error:
            # Mostra mensagem de erro se a imagem não carregou
            font = pygame.font.SysFont(None, 36)
            error_text = font.render("Erro ao carregar a imagem", True, (255, 0, 0))
            text_rect = error_text.get_rect(center=(self.width // 2, self.height // 2))
            self.screen.blit(error_text, text_rect)
        elif self.image and self.image_rect:
            # Desenha a imagem
            self.screen.blit(self.image, self.image_rect)
            
            # Desenha botão de fechar
            close_btn_size = 40
            self.close_button_rect = pygame.Rect(
                self.image_rect.right - close_btn_size - 10,
                self.image_rect.top - close_btn_size // 2,
                close_btn_size,
                close_btn_size
            )
            
            pygame.draw.rect(self.screen, (255, 50, 50), self.close_button_rect, border_radius=20)
            pygame.draw.rect(self.screen, (255, 255, 255), self.close_button_rect, 2, border_radius=20)
            
            font = pygame.font.SysFont(None, 36)
            text = font.render("×", True, (255, 255, 255))
            text_rect = text.get_rect(center=self.close_button_rect.center)
            self.screen.blit(text, text_rect)
            
        if self.loading:
            # Mostra indicador de carregamento
            font = pygame.font.SysFont(None, 36)
            loading_text = font.render("Carregando imagem...", True, (255, 255, 255))
            text_rect = loading_text.get_rect(center=(self.width // 2, self.height // 2))
            self.screen.blit(loading_text, text_rect)

    def toggle_visibility(self):
        self.visible = not self.visible
        return self.visible