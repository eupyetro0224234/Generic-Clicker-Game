import pygame
import urllib.request
import os

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

        self.percent = 0
        self.message = "Carregando..."

    def draw(self, percent=None, message=None):
        if percent is not None:
            self.percent = percent
        if message is not None:
            self.message = message

        self.screen.fill(self.bg_color)

        # Mensagem de texto
        text = self.font.render(self.message, True, self.text_color)
        text_rect = text.get_rect(center=(self.width // 2, self.height // 2 - 50))
        self.screen.blit(text, text_rect)

        # Barra de progresso
        bar_width = 400
        bar_height = 30
        bar_x = (self.width - bar_width) // 2
        bar_y = self.height // 2

        pygame.draw.rect(self.screen, self.bar_border, (bar_x, bar_y, bar_width, bar_height), 2)
        inner_width = int((self.percent / 100) * (bar_width - 4))
        pygame.draw.rect(self.screen, self.bar_color, (bar_x + 2, bar_y + 2, inner_width, bar_height - 4))

        percent_text = self.font.render(f"{int(self.percent)}%", True, self.text_color)
        percent_rect = percent_text.get_rect(center=(self.width // 2, bar_y + bar_height + 25))
        self.screen.blit(percent_text, percent_rect)

        pygame.display.update()

def download_with_progress(url, filepath, loading_screen, start_percent, end_percent):
    def reporthook(blocknum, blocksize, totalsize):
        if totalsize > 0:
            downloaded = blocknum * blocksize
            percent_downloaded = min(downloaded / totalsize, 1.0)
            percent_overall = start_percent + (end_percent - start_percent) * percent_downloaded
            loading_screen.draw(percent_overall, f"Baixando {os.path.basename(filepath)}...")

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

    urllib.request.urlretrieve(url, filepath, reporthook)

def download_assets(screen, width, height):
    loading_screen = LoadingScreen(screen, width, height)

    assets = [
        (
            "https://minecraft.wiki/images/Enchanted_Book.gif?b21c4",
            os.path.join(os.getenv("LOCALAPPDATA"), ".assets", "enchanted_book.gif")
        ),
        (
            "https://i.postimg.cc/hGf3VRqY/image-removebg-preview-5.png",
            os.path.join(os.getenv("LOCALAPPDATA"), ".assets", "image-removebg-preview-5.png")
        ),
        (
            "https://i.postimg.cc/yxVZWpPk/image-removebg-preview-6.png",
            os.path.join(os.getenv("LOCALAPPDATA"), ".assets", "upg.png")
        )
    ]

    # Cria pasta .assets se não existir
    for _, path in assets:
        pasta = os.path.dirname(path)
        os.makedirs(pasta, exist_ok=True)

    total_files = len(assets)
    for i, (url, path) in enumerate(assets, start=1):
        start_pct = ((i - 1) / total_files) * 100
        end_pct = (i / total_files) * 100
        download_with_progress(url, path, loading_screen, start_pct, end_pct)

    loading_screen.draw(100, "Download concluído!")
    pygame.time.delay(700)
