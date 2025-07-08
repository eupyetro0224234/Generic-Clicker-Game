# score_manager.py (mantendo a criptografia)
import os
import json
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

class ScoreManager:
    def __init__(self, folder_name=".assets", filename="score.dat"):
        localappdata = os.getenv("LOCALAPPDATA")
        if not localappdata:
            raise EnvironmentError("Variável LOCALAPPDATA não encontrada.")
        
        self.folder_path = os.path.join(localappdata, folder_name)
        os.makedirs(self.folder_path, exist_ok=True)
        self.file_path = os.path.join(self.folder_path, filename)
        
        # Chave fixa
        self.encryption_key = b'justanotherkey12'  # 16 bytes para AES-128
        
    def encrypt_data(self, data):
        """Criptografa os dados usando AES-128 em modo CBC"""
        try:
            json_data = json.dumps(data)
            data_bytes = json_data.encode('utf-8')
            
            iv = get_random_bytes(AES.block_size)
            cipher = AES.new(self.encryption_key, AES.MODE_CBC, iv)
            ct_bytes = cipher.encrypt(pad(data_bytes, AES.block_size))
            
            encrypted_data = base64.b64encode(iv + ct_bytes).decode('utf-8')
            return encrypted_data
        except Exception as e:
            print(f"Erro ao criptografar dados: {e}")
            return None

    def decrypt_data(self, encrypted_data):
        """Descriptografa dados usando AES-128 em modo CBC"""
        try:
            data = base64.b64decode(encrypted_data)
            iv = data[:AES.block_size]
            ct = data[AES.block_size:]
            
            cipher = AES.new(self.encryption_key, AES.MODE_CBC, iv)
            pt = unpad(cipher.decrypt(ct), AES.block_size)
            return json.loads(pt.decode('utf-8'))
        except Exception as e:
            print(f"Erro ao descriptografar dados: {e}")
            return None

    def save_data(self, score: int, controls_visible: bool, achievements: list[str], upgrades: dict[str, int], last_mini_event_click_time: int):
        """Salva todos os dados em um único arquivo criptografado"""
        data_dict = {
            'score': score,
            'controls_visible': controls_visible,
            'achievements': achievements,
            'upgrades': upgrades,  # Agora incluindo os upgrades aqui
            'last_mini_event_click_time': last_mini_event_click_time
        }
        
        encrypted = self.encrypt_data(data_dict)
        if encrypted:
            with open(self.file_path, "w") as file:
                file.write(encrypted)

    def load_data(self):
        """Carrega todos os dados de um único arquivo criptografado"""
        if not os.path.isfile(self.file_path):
            return 0, False, [], {}, 0

        try:
            with open(self.file_path, "r") as file:
                encrypted = file.read()
            data_dict = self.decrypt_data(encrypted)
            
            if not data_dict:
                return 0, False, [], {}, 0
            
            # Extrai todos os valores incluindo upgrades
            score = data_dict.get("score", 0)
            controls_visible = data_dict.get("controls_visible", False)
            achievements = data_dict.get("achievements", [])
            upgrades = data_dict.get("upgrades", {})  # Carrega os upgrades
            last_mini_event_click_time = data_dict.get("last_mini_event_click_time", 0)

            return score, controls_visible, achievements, upgrades, last_mini_event_click_time
        except Exception as e:
            print("Erro ao carregar dados:", e)
            return 0, False, [], {}, 0