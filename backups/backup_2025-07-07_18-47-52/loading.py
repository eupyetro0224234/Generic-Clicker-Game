import pygame
import sys
import os
import urllib.request
import time

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
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
        'Referer': url,
        'Accept': '*/*',
    }
    req = urllib.request.Request(url, headers=headers)

    with urllib.request.urlopen(req) as response, open(filepath, 'wb') as out_file:
        total_size = response.getheader('Content-Length')
        if total_size is None:
            total_size = 0
        else:
            total_size = int(total_size.strip())
        downloaded = 0
        block_size = 8192

        while True:
            buffer = response.read(block_size)
            if not buffer:
                break
            out_file.write(buffer)
            downloaded += len(buffer)
            if total_size > 0:
                percent_downloaded = min(downloaded / total_size, 1.0)
            else:
                percent_downloaded = 1.0
            percent_overall = start_percent + (end_percent - start_percent) * percent_downloaded
            loading_screen.draw(percent_overall, f"Baixando {os.path.basename(filepath)}...")

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

    time.sleep(0.5)  # pausa entre downloads para não forçar servidor

def download_assets(screen, width, height):
    assets_path = os.path.join(os.getenv("LOCALAPPDATA"), ".assets")
    os.makedirs(assets_path, exist_ok=True)

    loading_screen = LoadingScreen(screen, width, height)

    assets = [
        ("https://minecraft.wiki/images/Enchanted_Book.gif?b21c4", "enchanted_book.gif"),
        ("https://i.postimg.cc/hGf3VRqY/image-removebg-preview-5.png", "image-removebg-preview-5.png"),
        ("https://i.postimg.cc/yxVZWpPk/image-removebg-preview-6.png", "image-removebg-preview-6.png"),
    ]

    n = len(assets)
    for i, (url, filename) in enumerate(assets, start=1):
        filepath = os.path.join(assets_path, filename)
        if not os.path.exists(filepath):
            download_with_progress(url, filepath, loading_screen, (i-1)/n*100, i/n*100)
        else:
            # Se arquivo já existe, só mostra progresso parcialmente preenchido
            loading_screen.draw(i / n * 100, f"Arquivo {filename} já existe")

    # Pequena pausa final para mostrar 100%
    time.sleep(0.3)
