import pygame
import urllib.request
import os
import sys

class LoadingScreen:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        self.bg_color = (20, 30, 60)
        self.bar_color = (100, 200, 255)
        self.bar_border = (255, 255, 255)
        self.text_color = (255, 255, 255)
        self.font = pygame.font.SysFont(None, 32)

    def draw(self, percent, message="Carregando..."):
        self.screen.fill(self.bg_color)

        # Mensagem de texto
        text = self.font.render(message, True, self.text_color)
        text_rect = text.get_rect(center=(self.width // 2, self.height // 2 - 50))
        self.screen.blit(text, text_rect)

        # Barra de progresso
        bar_width = 400
        bar_height = 30
        bar_x = (self.width - bar_width) // 2
        bar_y = self.height // 2

        pygame.draw.rect(self.screen, self.bar_border, (bar_x, bar_y, bar_width, bar_height), 2)
        inner_width = int((percent / 100) * (bar_width - 4))
        pygame.draw.rect(self.screen, self.bar_color, (bar_x + 2, bar_y + 2, inner_width, bar_height - 4))

        percent_text = self.font.render(f"{int(percent)}%", True, self.text_color)
        percent_rect = percent_text.get_rect(center=(self.width // 2, bar_y + bar_height + 25))
        self.screen.blit(percent_text, percent_rect)

        pygame.display.update()

def download_with_progress(url, filepath, loading_screen, start_percent, end_percent):
    headers = {'User-Agent': 'Mozilla/5.0'}
    req = urllib.request.Request(url, headers=headers)

    with urllib.request.urlopen(req) as response, open(filepath, 'wb') as out_file:
        total_size = int(response.getheader('Content-Length').strip())
        downloaded = 0
        block_size = 8192
        while True:
            buffer = response.read(block_size)
            if not buffer:
                break
            out_file.write(buffer)
            downloaded += len(buffer)
            percent_downloaded = min(downloaded / total_size, 1.0)
            percent_overall = start_percent + (end_percent - start_percent) * percent_downloaded
            loading_screen.draw(percent_overall, f"Baixando {os.path.basename(filepath)}...")

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

def download_assets(screen, width, height):
    loading_screen = LoadingScreen(screen, width, height)

    assets = [
        ("https://minecraft.wiki/images/Enchanted_Book.gif?b21c4", os.path.join(os.getenv("LOCALAPPDATA"), ".assets", "enchanted_book.gif")),
        ("https://i.postimg.cc/hGf3VRqY/image-removebg-preview-5.png", os.path.join(os.getenv("LOCALAPPDATA"), ".assets", "image-removebg-preview-5.png")),
        ("https://i.postimg.cc/yxVZWpPk/image-removebg-preview-6.png", os.path.join(os.getenv("LOCALAPPDATA"), ".assets", "image-removebg-preview-6.png")),
    ]

    os.makedirs(os.path.join(os.getenv("LOCALAPPDATA"), ".assets"), exist_ok=True)

    steps = len(assets)
    for i, (url, path) in enumerate(assets, start=1):
        if not os.path.exists(path):
            download_with_progress(url, path, loading_screen, (i-1)/steps*100, i/steps*100)
        else:
            # arquivo já existe, mostrar progresso direto
            loading_screen.draw(i/steps*100, f"{os.path.basename(path)} já existe")

    loading_screen.draw(100, "Todos os assets carregados!")

