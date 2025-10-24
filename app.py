import os
import sys
import pygame

# ---------------------------
# Função para compatibilidade com PyInstaller
# ---------------------------
def resource_path(relative_path):
    """Obtém caminho absoluto do recurso, mesmo dentro do executável PyInstaller."""
    try:
        base_path = sys._MEIPASS  # Caminho temporário usado pelo PyInstaller
    except AttributeError:
        base_path = os.path.abspath(".")  # Caminho normal (modo desenvolvimento)
    return os.path.join(base_path, relative_path)


# Ajusta import do código principal
sys.path.append(resource_path("game_code"))

from game_code.game import Game
from game_code.background import WIDTH, HEIGHT


# ---------------------------
# Função para carregar ícone
# ---------------------------
def carregar_icone():
    icon_path = resource_path(os.path.join("game_assets", "icone.ico"))

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
    except Exception:
        return None


# ---------------------------
# Configuração do Pygame
# ---------------------------
def configurar_pygame():
    pygame.init()
    pygame.mixer.init()
    if sys.platform == 'win32':
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("GenericClickerGame.1.0")
        except Exception:
            pass


# ---------------------------
# Função principal
# ---------------------------
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
        print("Erro ao iniciar o jogo:", e)
    finally:
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    main()
