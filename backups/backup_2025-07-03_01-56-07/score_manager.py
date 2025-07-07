import os
import pygame

class ScoreManager:
    def __init__(self, folder_name=".assests", filename="score.dat", key=123):
        localappdata = os.getenv("LOCALAPPDATA")
        if not localappdata:
            raise EnvironmentError("Variável LOCALAPPDATA não encontrada no sistema.")

        self.folder_path = os.path.join(localappdata, folder_name)
        os.makedirs(self.folder_path, exist_ok=True)
        self.file_path = os.path.join(self.folder_path, filename)
        self.key = key  # chave XOR fixa para ofuscar

        self.controls_visible = False  # flag que vamos salvar/ler

    def _xor_encrypt(self, data: bytes) -> bytes:
        return bytes([b ^ self.key for b in data])

    def save_data(self, score: int, controls_visible: bool):
        # Salva score e flag no mesmo arquivo separado por pipe
        data_str = f"{score}|{int(controls_visible)}"
        data = data_str.encode("utf-8")
        encrypted = self._xor_encrypt(data)
        with open(self.file_path, "wb") as f:
            f.write(encrypted)

    def load_data(self):
        # retorna tuple (score, controls_visible)
        if not os.path.isfile(self.file_path):
            return 0, False
        try:
            with open(self.file_path, "rb") as f:
                encrypted = f.read()
            decrypted = self._xor_encrypt(encrypted).decode("utf-8")
            parts = decrypted.split("|")
            score = int(parts[0]) if len(parts) > 0 else 0
            controls_visible = bool(int(parts[1])) if len(parts) > 1 else False
            self.controls_visible = controls_visible
            return score, controls_visible
        except Exception:
            return 0, False

    def draw_score_box(self, screen, x, y, w, h):
        # Sombra
        shadow_color = (0, 0, 0, 50)
        shadow_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, shadow_color, (5, 5, w, h), border_radius=15)
        screen.blit(shadow_surf, (x, y))

        # Fundo pastel azul claro com cantos arredondados
        bg_color = (180, 210, 255)
        pygame.draw.rect(screen, bg_color, (x, y, w, h), border_radius=15)

        # Quadradinhos sutis (opcional)
        square_size = 12
        sq_surf = pygame.Surface((square_size, square_size), pygame.SRCALPHA)
        color1 = (200, 220, 255, 60)
        color2 = (170, 200, 250, 60)
        for i in range(0, w, square_size):
            for j in range(0, h, square_size):
                sq_surf.fill(color1 if (i//square_size + j//square_size) % 2 == 0 else color2)
                screen.blit(sq_surf, (x + i, y + j))
