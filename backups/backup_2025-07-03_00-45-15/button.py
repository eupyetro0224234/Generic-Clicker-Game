import pygame
import requests
import io
from PIL import Image

class AnimatedButton:
    def __init__(self, x, y, width, height, gif_url, frame_duration=100):
        """
        x, y = posição do botão
        width, height = tamanho do botão
        gif_url = URL do GIF animado
        frame_duration = tempo (ms) de cada frame
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.frame_duration = frame_duration

        # Baixar o GIF da internet e carregar os frames
        self.frames = self.load_gif_frames(gif_url)
        self.frame_count = len(self.frames)
        self.current_frame = 0
        self.last_update = pygame.time.get_ticks()

        # Criar rect para detectar clique
        self.rect = pygame.Rect(x, y, width, height)

    def load_gif_frames(self, url):
        # Baixar GIF em memória
        response = requests.get(url)
        gif_bytes = io.BytesIO(response.content)
        pil_gif = Image.open(gif_bytes)

        frames = []
        try:
            while True:
                pil_frame = pil_gif.convert("RGBA")
                # Converter PIL para Surface do Pygame
                mode = pil_frame.mode
                size = pil_frame.size
                data = pil_frame.tobytes()

                frame = pygame.image.fromstring(data, size, mode)
                frame = pygame.transform.scale(frame, (self.width, self.height))
                frames.append(frame)

                pil_gif.seek(pil_gif.tell() + 1)
        except EOFError:
            pass

        return frames

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_duration:
            self.current_frame = (self.current_frame + 1) % self.frame_count
            self.last_update = now

    def draw(self, screen):
        self.update()
        screen.blit(self.frames[self.current_frame], (self.x, self.y))

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)
