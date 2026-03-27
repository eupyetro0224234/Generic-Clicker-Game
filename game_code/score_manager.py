import sys, os, json
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from datetime import datetime
from game_code.key_provider import get_key


class ScoreManager:
    DEFAULT_DATA = {
        "version": 1,
        "score": 0,
        "controls_visible": False,
        "achievements": {},
        "upgrades": {},
        "mini_event_click_count": 0,
        "trabalhadores": [],
        "trabalhador_limit_enabled": True,
        "trabalhador_time_enabled": True,
        "eventos_participados": {},
        "total_play_time": 0,
        "last_timestamp": None,
        "max_score": 0,
        "total_score_earned": 0,
        "mini_event1_total": 0,
        "mini_event2_total": 0,
        "normal_clicks": 0,
        "first_join_date": None,
        "streak_data": {
            "current_streak": 0,
            "last_login_date": None,
            "max_streak": 0
        },
        "mini_event1_session": 0,
        "mini_event2_session": 0,
        "offline_time_bank": 0,
        "auto_compra_ativa": False,
        "image_viewed": False,
        "show_full_score": False
    }

    def __init__(self, folder_name="genericclickergame", filename="score.dat"):
        self.encryption_key = get_key(machine_bound=True)
        appdata = os.getenv("APPDATA") or "."
        self.folder_path = os.path.join(appdata, folder_name)
        os.makedirs(self.folder_path, exist_ok=True)
        self.file_path = os.path.join(self.folder_path, filename)

    def backup_save(self):
        if os.path.exists(self.file_path):
            try:
                os.replace(self.file_path, self.file_path + ".bak")
            except:
                pass

    def encrypt_data(self, data):
        try:
            json_data = json.dumps(data)
            data_bytes = json_data.encode('utf-8')
            iv = get_random_bytes(AES.block_size)
            cipher = AES.new(self.encryption_key, AES.MODE_CBC, iv)
            ct_bytes = cipher.encrypt(pad(data_bytes, AES.block_size))
            return iv + ct_bytes
        except Exception as e:
            return None

    def decrypt_data(self, encrypted_bytes):
        try:
            iv = encrypted_bytes[:AES.block_size]
            ct = encrypted_bytes[AES.block_size:]
            cipher = AES.new(self.encryption_key, AES.MODE_CBC, iv)
            pt = unpad(cipher.decrypt(ct), AES.block_size)
            return json.loads(pt.decode('utf-8'))
        except Exception as e:
            return None

    def load_data(self):
        if not os.path.exists(self.file_path):
            return self.DEFAULT_DATA.copy()
        try:
            with open(self.file_path, "rb") as f:
                encrypted = f.read()
            data_dict = self.decrypt_data(encrypted)
            if not data_dict:
                return None
            for k, v in self.DEFAULT_DATA.items():
                if k not in data_dict:
                    data_dict[k] = v
            return data_dict
        except Exception as e:
            return None

    def save_data(self, data_dict):
        for k, v in self.DEFAULT_DATA.items():
            if k not in data_dict:
                data_dict[k] = v
        try:
            self.backup_save()
            encrypted = self.encrypt_data(data_dict)
            if not encrypted:
                return False
            with open(self.file_path, "wb") as f:
                f.write(encrypted)
            return True
        except Exception as e:
            return False