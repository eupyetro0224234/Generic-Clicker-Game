# splash_screen.py
import pygame
import requests
import sys
import os
from io import BytesIO

class SplashScreen:
    def __init__(self, screen):
        self.screen = screen
        self.splash_image = None
        self.load_image()
    
    def load_image(self):
        """Carrega a imagem do URL especificado"""
        try:
            # Obtém a URL do arquivo texto
            response = requests.get(
                "https://raw.githack.com/eupyetro0224234/Generic-Clicker-Game/main/github_assets/imagem.txt", 
                timeout=10
            )
            
            if response.status_code == 200:
                image_url = response.text.strip()
                
                # Verifica se há uma URL válida
                if image_url and image_url.startswith(('http://', 'https://')):
                    # Baixa a imagem
                    img_response = requests.get(image_url, timeout=15)
                    
                    if img_response.status_code == 200:
                        # Converte para surface do pygame
                        image_data = BytesIO(img_response.content)
                        self.splash_image = pygame.image.load(image_data)
                        
                        # Redimensiona para 1280x720 se necessário
                        if self.splash_image.get_size() != (1280, 720):
                            self.splash_image = pygame.transform.scale(self.splash_image, (1280, 720))
                        
                        print("Splash screen carregada com sucesso!")
                    else:
                        print("Erro ao baixar a imagem")
                else:
                    print("URL de imagem inválida ou vazia")
            else:
                print("Não foi possível acessar o arquivo de URL")
                
        except Exception as e:
            print(f"Erro ao carregar splash screen: {e}")
    
    def show(self):
        """Exibe a splash screen até que ESC seja pressionado"""
        if self.splash_image is None:
            return False  # Não há imagem para mostrar
        
        showing_splash = True
        
        while showing_splash:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        showing_splash = False
            
            # Desenha a imagem cobrindo toda a tela
            self.screen.blit(self.splash_image, (0, 0))
            pygame.display.flip()
            
            # Pequeno delay
            pygame.time.delay(10)
        
        return True

def main():
    """Função principal modificada para incluir splash screen"""
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Generic Clicker Game")
    
    # Mostra a splash screen
    splash = SplashScreen(screen)
    splash_shown = splash.show()
    
    if splash_shown:
        print("Splash screen fechada, iniciando jogo...")
    else:
        print("Nenhuma splash screen disponível, iniciando jogo normalmente...")
    
    # Importa e inicia o jogo (ajuste o caminho conforme necessário)
    try:
        from game import Game
        from game_code.background import WIDTH, HEIGHT
        
        game = Game(screen)
        game.run()
    except ImportError as e:
        print(f"Erro ao importar o jogo: {e}")
        print("Certifique-se de que todos os módulos estão disponíveis")

if __name__ == "__main__":
    main()