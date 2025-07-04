import pygame
import os
import requests
from PIL import Image

class AnimatedButton:
    def __init__(self, center_x, center_y, width, height, gif_url, local_folder_name=".assests", gif_filename="enchanted_book.gif", frame_duration=100):
        """
        center_x, center_y = posição central do botão
        width, height = tamanho máximo do botão
        gif_url = URL para baixar o GIF se não existir localmente
        local_folder_name = pasta dentro de %LOCALAPPDATA%
        gif_filename = nome do arquivo gif salvo localmente
        frame_duration = duração de cada frame em ms
        """
        self.center_x = center_x
        self.center_y = center_y
        self.width = width
        self.height = height
        self.frame_duration = frame_duration

        self.local_path = self._prepare_local_gif(gif_url, local_folder_name, gif_filename)

        self.frames = self._load_gif_frames(self.local_path)
        self.frame_count = len(self.frames)
        self.current_frame = 0
        self.last_update = pygame.time.get_ticks()

        # Estado da animação de clique
        self.is_animating_click = False
        self.click_anim_progress = 0  # de 0 a 1
        self.click_anim_speed = 0.1  # controla velocidade da animação

        # Calcula rect baseado no centro e tamanho atual
        self.current_scale = 1.0
        self._update_rect()

    def _update_rect(self):
        w = int(self.width * self.current_scale)
        h = int(self.height * self.current_scale)
        x = self.center_x - w // 2
        y = self.center_y - h // 2
        self.rect = pygame.Rect(x, y, w, h)

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

        # Atualiza animação de clique se estiver ativa
        if self.is_animating_click:
            self.click_anim_progress += self.click_anim_speed
            if self.click_anim_progress >= 1:
                self.click_anim_progress = 0
                self.is_animating_click = False
                self.current_scale = 1.0
            else:
                # Anima escala entre 1.0 (normal) e 0.9 (reduzido)
                if self.click_anim_progress < 0.5:
                    # Vai de 1.0 até 0.9 (redução)
                    self.current_scale = 1.0 - 0.2 * self.click_anim_progress * 2
                else:
                    # Volta de 0.9 para 1.0
                    self.current_scale = 0.9 + 0.2 * (self.click_anim_progress - 0.5) * 2
            self._update_rect()

    def draw(self, screen):
        self.update()
        frame = self.frames[self.current_frame]
        # Escala frame para tamanho atual animado
        scaled_frame = pygame.transform.smoothscale(frame, (self.rect.width, self.rect.height))
        screen.blit(scaled_frame, (self.rect.x, self.rect.y))

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

    def click(self):
        # Chama ao detectar clique para iniciar animação
        self.is_animating_click = True
        self.click_anim_progress = 0
