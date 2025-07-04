import pygame
import os
import requests
from PIL import Image

class AnimatedButton:
    def __init__(self, x, y, width, height, gif_url, local_folder_name=".assests", gif_filename="enchanted_book.gif", frame_duration=100):
        """
        x, y = posição do botão
        width, height = tamanho do botão máximo
        gif_url = URL para baixar o GIF se não existir localmente
        local_folder_name = pasta dentro de %LOCALAPPDATA%
        gif_filename = nome do arquivo gif salvo localmente
        frame_duration = duração de cada frame em ms
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.frame_duration = frame_duration

        self.local_path = self._prepare_local_gif(gif_url, local_folder_name, gif_filename)

        self.frames = self._load_gif_frames(self.local_path)
        self.frame_count = len(self.frames)
        self.current_frame = 0
        self.last_update = pygame.time.get_ticks()

        self.rect = pygame.Rect(x, y, width, height)

    def _prepare_local_gif(self, gif_url, local_folder_name, gif_filename):
        localappdata = os.getenv("LOCALAPPDATA")
        if not localappdata:
            raise EnvironmentError("Variável LOCALAPPDATA não encontrada no sistema.")

        folder_path = os.path.join(localappdata, local_folder_name)
        os.makedirs(folder_path, exist_ok=True)

        file_path = os.path.join(folder_path, gif_filename)

        if not os.path.isfile(file_path):
            print(f"GIF não encontrado localmente. Baixando e salvando em {file_path} ...")
            response = requests.get(gif_url)
            response.raise_for_status()
            with open(file_path, "wb") as f:
                f.write(response.content)
            print("Download concluído.")
        else:
            #print("GIF encontrado localmente.")
            pass

        return file_path

    def _load_gif_frames(self, file_path):
        pil_gif = Image.open(file_path)
        frames = []
        try:
            while True:
                pil_frame = pil_gif.convert("RGBA")
                pil_w, pil_h = pil_frame.size
                scale = min(self.width / pil_w, self.height / pil_h)
                new_size = (int(pil_w * scale), int(pil_h * scale))
                pil_frame = pil_frame.resize(new_size, Image.Resampling.LANCZOS)

                mode = pil_frame.mode
                size = pil_frame.size
                data = pil_frame.tobytes()
                frame = pygame.image.fromstring(data, size, mode)
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
