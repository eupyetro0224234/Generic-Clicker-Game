import os

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

    def save_score(self, score: int):
        data = str(score).encode("utf-8")
        encrypted = self._xor_encrypt(data)
        with open(self.file_path, "wb") as f:
            f.write(encrypted)

    def load_score(self) -> int:
        if not os.path.isfile(self.file_path):
            return 0
        try:
            with open(self.file_path, "rb") as f:
                encrypted = f.read()
            decrypted = self._xor_encrypt(encrypted)
            return int(decrypted.decode("utf-8"))
        except Exception:
            return 0
