import sys, pygame, threading, math, io
from game_code.game import Game
from game_code.background import WIDTH, HEIGHT

def carregar_icone():
    try:
        from game_assets.game_assets_packed import load_image_raw
        icon_bytes = load_image_raw("icone.ico")
        try:
            from PIL import Image
            img = Image.open(io.BytesIO(icon_bytes))
            return pygame.image.fromstring(img.tobytes(), img.size, img.mode)
        except ImportError:
            return pygame.image.load(io.BytesIO(icon_bytes))
    except Exception:
        return None

def configurar_pygame():
    pygame.init()
    pygame.mixer.init()
    if sys.platform == 'win32':
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("GenericClickerGame.1.0")
        except Exception:
            pass

def show_loading_screen(screen, loading_done, angle, center):
    screen.fill((0, 0, 0))
    num_balls = 12
    radius = 20
    ball_color = (255, 255, 255)
    
    for i in range(num_balls):
        theta = 2 * math.pi * i / num_balls + angle
        x = int(center[0] + radius * math.cos(theta))
        y = int(center[1] + radius * math.sin(theta))
        pygame.draw.circle(screen, ball_color, (x, y), 5)
    
    return angle + 0.1

def main():
    try:
        configurar_pygame()
        icon = carregar_icone()
        if icon:
            pygame.display.set_icon(icon)
        pygame.display.set_caption("Generic Clicker Game")
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        
        loading_done = False
        game_instance = None
        game_loaded = False
        
        def carregar_jogo():
            nonlocal loading_done, game_instance, game_loaded
            try:
                game_instance = Game(screen)
                game_loaded = True
            except Exception as e:
                print("Erro ao carregar o jogo:", e)
                game_loaded = False
            finally:
                loading_done = True
        
        t = threading.Thread(target=carregar_jogo, daemon=True)
        t.start()
        
        clock = pygame.time.Clock()
        running = True
        angle = 0
        center = (WIDTH // 2, HEIGHT // 2)
        
        while running and not loading_done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    sys.exit()
            
            angle = show_loading_screen(screen, loading_done, angle, center)
            pygame.display.flip()
            clock.tick(60)
        
        if running and loading_done and game_loaded and game_instance:
            game_instance.run()
        else:
            if not game_loaded:
                print("Falha ao carregar o jogo")
            
    except Exception as e:
        print("Erro ao iniciar o jogo:", e)
    finally:
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()