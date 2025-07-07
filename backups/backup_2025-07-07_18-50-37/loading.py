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

def download_file(url, path, loading_screen, start_pct, end_pct):
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Referer': url,
        'Accept': '*/*',
    }
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response, open(path, 'wb') as out_file:
        total_size = response.getheader('Content-Length')
        total_size = int(total_size) if total_size else 0
        downloaded = 0
        block_size = 8192
        while True:
            buffer = response.read(block_size)
            if not buffer:
                break
            out_file.write(buffer)
            downloaded += len(buffer)
            pct = start_pct + (end_pct - start_pct) * (downloaded / total_size if total_size else 1)
            loading_screen.draw(pct, f"Baixando {os.path.basename(path)}...")
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
    time.sleep(0.5)  # pequena pausa entre downloads

def download_assets(screen, width, height):
    assets_path = os.path.join(os.getenv("LOCALAPPDATA"), ".assets")
    os.makedirs(assets_path, exist_ok=True)

    loading_screen = LoadingScreen(screen, width, height)

    files = [
        ("https://minecraft.wiki/images/Enchanted_Book.gif?b21c4", "enchanted_book.gif"),
        ("https://i.postimg.cc/hGf3VRqY/image-removebg-preview-5.png", "image-removebg-preview-5.png"),
        ("https://i.postimg.cc/yxVZWpPk/image-removebg-preview-6.png", "image-removebg-preview-6.png"),
    ]

    total = len(files)
    for i, (url, filename) in enumerate(files, 1):
        path = os.path.join(assets_path, filename)
        if not os.path.exists(path):
            start_pct = (i - 1) / total * 100
            end_pct = i / total * 100
            download_file(url, path, loading_screen, start_pct, end_pct)
        else:
            loading_screen.draw(i / total * 100, f"Arquivo {filename} já existe")
            pygame.time.wait(300)

    loading_screen.draw(100, "Download concluído!")
    pygame.time.wait(500)
