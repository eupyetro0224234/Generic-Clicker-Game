import os
import pygame

class ScoreManager:
    def __init__(self, folder_name=".assests", filename="score.dat", key=123):
        localappdata = os.getenv("LOCALAPPDATA")
        if not localappdata:
            raise EnvironmentError("Variável LOCALAPPDATA não encontrada.")
        self.folder_path = os.path.join(localappdata, folder_name)
        os.makedirs(self.folder_path, exist_ok=True)
        self.file_path = os.path.join(self.folder_path, filename)
        self.key = key

    def _xor_encrypt(self, data: bytes) -> bytes:
        return bytes(b ^ self.key for b in data)

    def save_data(self, score: int, controls_visible: bool, achievements: list[str], upgrades: list[str]):
        ach_str = ",".join(achievements)
        upg_str = ",".join(upgrades)
        data_str = f"{score}|{int(controls_visible)}|{ach_str}|{upg_str}"
        encrypted = self._xor_encrypt(data_str.encode("utf-8"))
        with open(self.file_path, "wb") as f:
            f.write(encrypted)

    def load_data(self):
        if not os.path.isfile(self.file_path):
            return 0, False, [], []

        try:
            with open(self.file_path, "rb") as f:
                encrypted = f.read()
            decrypted = self._xor_encrypt(encrypted).decode("utf-8")
            parts = decrypted.split("|")
            score = int(parts[0]) if parts[0].isdigit() else 0
            controls_visible = bool(int(parts[1])) if parts[1].isdigit() else False
            achievements = parts[2].split(",") if len(parts) > 2 and parts[2] else []
            upgrades = parts[3].split(",") if len(parts) > 3 and parts[3] else []
            return score, controls_visible, achievements, upgrades
        except:
            return 0, False, [], []

    def draw_score_box(self, screen, x, y, w, h):
        rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(screen, (255, 192, 203), rect, border_radius=12)
        shadow = pygame.Rect(x+4, y+4, w, h)
        pygame.draw.rect(screen, (200, 160, 180), shadow, border_radius=12)
