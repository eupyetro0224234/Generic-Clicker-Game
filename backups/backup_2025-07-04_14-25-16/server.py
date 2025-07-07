from flask import Flask, Response
from flask_socketio import SocketIO
import base64
import threading
import time
import pygame
import io

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# HTML embutido (sem arquivo .html)
html = """
<!DOCTYPE html>
<html>
<head>
    <title>Jogo Pygame no Navegador</title>
</head>
<body style="text-align:center; background:#222; color:#eee; font-family:sans-serif;">
    <h1>Jogo Pygame no Navegador (via localhost)</h1>
    <img id="game_frame" width="800" height="600" style="border:2px solid #fff;" />
    <p>Clique na imagem para enviar cliques para o servidor.</p>

    <script src="https://cdn.socket.io/4.6.1/socket.io.min.js"></script>
    <script>
        var socket = io();

        socket.on('frame', function(data) {
            document.getElementById('game_frame').src = 'data:image/png;base64,' + data.image;
        });

        document.getElementById('game_frame').addEventListener('click', function(event) {
            const rect = this.getBoundingClientRect();
            const x = event.clientX - rect.left;
            const y = event.clientY - rect.top;
            socket.emit('mouse_click', {x: x, y: y, button: 1});
        });
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return Response(html, mimetype='text/html')

# Variáveis globais do Pygame
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.Surface((WIDTH, HEIGHT))

# Exemplo: posição do círculo que será desenhado no frame
circle_pos = [WIDTH // 2, HEIGHT // 2]

def game_loop():
    """Loop que atualiza o jogo e envia frames para o cliente via socketio."""
    global circle_pos

    clock = pygame.time.Clock()
    while True:
        # Atualizar lógica simples: círculo se move lentamente para direita
        circle_pos[0] += 1
        if circle_pos[0] > WIDTH:
            circle_pos[0] = 0

        # Desenhar fundo preto
        screen.fill((0, 0, 0))

        # Desenhar círculo vermelho
        pygame.draw.circle(screen, (255, 0, 0), circle_pos, 40)

        # Converter Surface para PNG bytes em memória
        with io.BytesIO() as img_bytes:
            pygame.image.save(screen, img_bytes)
            img_bytes.seek(0)
            img_data = img_bytes.read()

        # Codificar imagem em base64 para enviar ao navegador
        b64_img = base64.b64encode(img_data).decode('ascii')

        # Enviar frame para todos clientes conectados
        socketio.emit('frame', {'image': b64_img})

        # 30 FPS
        clock.tick(30)

@socketio.on('mouse_click')
def handle_mouse_click(data):
    global circle_pos
    print(f"Mouse click recebido no servidor: {data}")
    # Exemplo: mover círculo para posição clicada
    circle_pos[0] = int(data['x'])
    circle_pos[1] = int(data['y'])

if __name__ == '__main__':
    # Rodar loop do jogo em thread separada
    threading.Thread(target=game_loop, daemon=True).start()
    socketio.run(app, host='0.0.0.0', port=5000)
