import pygame
import os
import sys
import requests

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

def download_file_requests(url, path, loading_screen, start_pct, end_pct):
    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            total_length = r.headers.get('content-length')
            total_length = int(total_length) if total_length else 0
            downloaded = 0
            chunk_size = 65536  # 64 KB

            with open(path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        pct = start_pct + (end_pct - start_pct) * (downloaded / total_length if total_length else 1)
                        loading_screen.draw(pct, f"Baixando {os.path.basename(path)}...")
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit()
    except Exception as e:
        print(f"Erro ao baixar {url}: {e}")

def download_assets(screen, width, height):
    loading_screen = LoadingScreen(screen, width, height)

    # Pasta para salvar as imagens
    localappdata = os.getenv("LOCALAPPDATA") or "."
    assets_path = os.path.join(localappdata, ".assets")
    os.makedirs(assets_path, exist_ok=True)

    assets = [
        ("https://minecraft.wiki/images/Enchanted_Book.gif?b21c4", os.path.join(assets_path, "button.gif")),
        ("https://i.postimg.cc/hGf3VRqY/image-removebg-preview-5.png", os.path.join(assets_path, "menu.png")),
        ("https://i.postimg.cc/yxVZWpPk/image-removebg-preview-6.png", os.path.join(assets_path, "upgrades.png")),
        ("https://i.postimg.cc/MKwpfL8Z/image-removebg-preview-7.png", os.path.join(assets_path, "mini-event.png")),  # Nova imagem
    ]

    total = len(assets)
    for i, (url, path) in enumerate(assets, start=1):
        if not os.path.exists(path):
            start_pct = (i-1) / total * 100
            end_pct = i / total * 100
            download_file_requests(url, path, loading_screen, start_pct, end_pct)
        else:
            # Se arquivo já existe, só mostra progresso rápido
            pct = i / total * 100
            loading_screen.draw(pct, f"Arquivo já existe: {os.path.basename(path)}")
            pygame.time.delay(500)

    # Finaliza carregamento e exibe mensagem de conclusão
    loading_screen.draw(100, "Carregamento concluído! Iniciando o jogo...")
    pygame.time.delay(1000)  # Exibe por 1 segundo antes de continuar
