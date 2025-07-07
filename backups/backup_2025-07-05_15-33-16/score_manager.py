import os
import pygame
import json

class ScoreManager:
    def __init__(self, folder_name=".assests", filename="score.dat", key=123):
        localappdata = os.getenv("LOCALAPPDATA")
        if not localappdata:
            raise EnvironmentError("Variável LOCALAPPDATA não encontrada no sistema.")

        self.folder_path = os.path.join(localappdata, folder_name)
        os.makedirs(self.folder_path, exist_ok=True)
        self.file_path = os.path.join(self.folder_path, filename)
        self.key = key  # chave XOR fixa para ofuscar

    def _xor_encrypt(self, data: bytes) -> bytes:
        return bytes([b ^ self.key for b in data])

    def save_data(self, score: int, controls_visible: bool, achievements: list[str] = None):
        if achievements is None:
            achievements = []
        # Salva em JSON e depois encripta
        data_dict = {
            "score": score,
            "controls_visible": int(controls_visible),
            "achievements": achievements
        }
        json_str = json.dumps(data_dict)
        data = json_str.encode("utf-8")
        encrypted = self._xor_encrypt(data)
        with open(self.file_path, "wb") as f:
            f.write(encrypted)

    def load_data(self):
        if not os.path.isfile(self.file_path):
            return 0, False, []
        try:
            with open(self.file_path, "rb") as f:
                encrypted = f.read()
            decrypted = self._xor_encrypt(encrypted).decode("utf-8")
            data_dict = json.loads(decrypted)
            score = data_dict.get("score", 0)
            controls_visible = bool(data_dict.get("controls_visible", 0))
            achievements = data_dict.get("achievements", [])
            return score, controls_visible, achievements
        except Exception:
            return 0, False, []

    def draw_score_box(self, screen, x, y, w, h):
        # Aqui pode desenhar fundo e sombra do score box, seu código atual ou novo
        pygame.draw.rect(screen, (255, 182, 193), (x, y, w, h), border_radius=12)  # rosa claro de fundo
        pygame.draw.rect(screen, (255, 105, 180), (x, y, w, h), 2, border_radius=12)  # borda rosa forte
