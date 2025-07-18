import os
import pygame
import sys
from game import Game
from background import WIDTH, HEIGHT  # Movido para o topo do arquivo

def carregar_icone():
    """Carrega o ícone do jogo com fallbacks para diferentes métodos"""
    icon_path = os.path.join(os.getenv("LOCALAPPDATA") or ".", ".assets", "icone.ico")
    if not os.path.exists(icon_path):
        return None  # Retorna None se o ícone não existir

    try:
        # Tenta carregar usando PIL para melhor qualidade
        try:
            from PIL import Image
            img = Image.open(icon_path)
            icon = pygame.image.fromstring(img.tobytes(), img.size, img.mode)
            return icon
        except ImportError:
            # Fallback para pygame se PIL não estiver disponível
            icon = pygame.image.load(icon_path)
            return icon
    except Exception as e:
        print(f"Erro ao carregar ícone: {e}")
        return None

def configurar_pygame():
    """Configurações iniciais do pygame"""
    pygame.init()
    pygame.mixer.init()  # Inicializa o mixer de áudio
    
    # Configuração para Windows para evitar duplicação na barra de tarefas
    if sys.platform == 'win32':
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("GenericClickerGame.1.0")
        except Exception as e:
            print(f"Erro ao configurar AppUserModelID: {e}")

def main():
    try:
        configurar_pygame()
        
        # Carrega o ícone antes de criar a janela
        icon = carregar_icone()
        
        # Configuração da tela - IMPORTANTE: definir o ícone ANTES de criar a janela
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