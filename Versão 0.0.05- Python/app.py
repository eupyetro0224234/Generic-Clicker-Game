import os
import pygame
import sys
from game import Game
from background import WIDTH, HEIGHT

def carregar_icone():
    """Carrega o ícone do jogo com fallbacks para diferentes métodos"""
    icon_path = os.path.join(os.getenv("LOCALAPPDATA") or ".", ".assets", "icone.ico")
    if not os.path.exists(icon_path):
        return None

    try:

        try:
            from PIL import Image
            img = Image.open(icon_path)
            icon = pygame.image.fromstring(img.tobytes(), img.size, img.mode)
            return icon
        except ImportError:
            icon = pygame.image.load(icon_path)
            return icon
    except Exception as e:
        print(f"Erro ao carregar ícone: {e}")
        return None

def configurar_pygame():
    """Configurações iniciais do pygame"""
    pygame.init()
    pygame.mixer.init()
    
    if sys.platform == 'win32':
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("GenericClickerGame.1.0")
        except Exception as e:
            print(f"Erro ao configurar AppUserModelID: {e}")

def main():
    try:
        configurar_pygame()
        
        icon = carregar_icone()
        
        if icon:
            pygame.display.set_icon(icon)
        pygame.display.set_caption("Generic Clicker Game")
        
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        
        game = Game(screen)
        game.run()
        
    except Exception as e:
        print(f"Erro fatal: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()