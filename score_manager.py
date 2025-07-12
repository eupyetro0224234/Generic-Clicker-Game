import os
import json
import time
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

class ScoreManager:
    def __init__(self, folder_name=".assets", filename="score.dat"):
        localappdata = os.getenv("LOCALAPPDATA") or "."
        self.folder_path = os.path.join(localappdata, folder_name)
        os.makedirs(self.folder_path, exist_ok=True)
        self.file_path = os.path.join(self.folder_path, filename)
        self.backup_path = os.path.join(self.folder_path, "old.json")
        self.encryption_key = b'justanotherkey12'  # 16 bytes chave AES
        
    def encrypt_data(self, data):
        try:
            json_data = json.dumps(data)
            data_bytes = json_data.encode('utf-8')
            
            iv = get_random_bytes(AES.block_size)
            cipher = AES.new(self.encryption_key, AES.MODE_CBC, iv)
            ct_bytes = cipher.encrypt(pad(data_bytes, AES.block_size))
            
            return iv + ct_bytes
        except Exception as e:
            print(f"Erro ao criptografar dados: {e}")
            return None

    def decrypt_data(self, encrypted_bytes):
        try:
            iv = encrypted_bytes[:AES.block_size]
            ct = encrypted_bytes[AES.block_size:]
            
            cipher = AES.new(self.encryption_key, AES.MODE_CBC, iv)
            pt = unpad(cipher.decrypt(ct), AES.block_size)
            return json.loads(pt.decode('utf-8'))
        except Exception as e:
            print(f"Erro ao descriptografar dados: {e}")
            return None

    def save_data(self, score: int, controls_visible: bool, achievements: list[str], upgrades: dict[str, int], mini_event_click_count: int):
        data_dict = {
            'score': score,
            'controls_visible': controls_visible,
            'achievements': achievements,
            'upgrades': upgrades,
            'mini_event_click_count': mini_event_click_count,
            'timestamp': int(time.time())
        }
        
        # Primeiro salva o backup (old.json)
        self.save_backup(score, controls_visible, achievements, upgrades, mini_event_click_count)
        
        # Depois salva o arquivo principal (score.dat)
        encrypted = self.encrypt_data(data_dict)
        if encrypted:
            try:
                # Salvamento atômico
                temp_path = self.file_path + ".tmp"
                with open(temp_path, "wb") as file:
                    file.write(encrypted)
                
                if os.path.exists(self.file_path):
                    os.replace(temp_path, self.file_path)
                else:
                    os.rename(temp_path, self.file_path)
                return True
            except Exception as e:
                print(f"Erro ao salvar score.dat: {e}")
                try:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                except:
                    pass
        return False
    
    def load_data(self):
        """SEMPRE carrega primeiro do old.json e depois sincroniza com score.dat"""
        # 1. Tenta carregar do backup (old.json)
        backup_data = self.load_backup()
        
        if backup_data:
            score, controls_visible, achievements, upgrades, mini_event_clicks = backup_data
            print("Dados carregados do backup old.json")
            
            # 2. Atualiza o score.dat com os dados do backup
            self.save_data(score, controls_visible, achievements, upgrades, mini_event_clicks)
            
            return score, controls_visible, achievements, upgrades, mini_event_clicks
        
        # 3. Se não tem backup, tenta carregar do score.dat (fallback)
        if os.path.isfile(self.file_path):
            try:
                with open(self.file_path, "rb") as file:
                    encrypted = file.read()
                data_dict = self.decrypt_data(encrypted)
                
                if data_dict:
                    return (
                        data_dict.get("score", 0),
                        data_dict.get("controls_visible", False),
                        data_dict.get("achievements", []),
                        data_dict.get("upgrades", {}),
                        data_dict.get("mini_event_click_count", 0)
                    )
            except Exception as e:
                print(f"Erro ao carregar score.dat: {e}")

        # 4. Se tudo falhar, retorna valores padrão
        print("Nenhum dado salvo encontrado, iniciando com valores padrão")
        return 0, False, [], {}, 0

    def save_backup(self, score: int, controls_visible: bool, achievements: list[str], upgrades: dict[str, int], mini_event_click_count: int):
        """Salva um backup não criptografado (old.json)"""
        data_dict = {
            'score': score,
            'controls_visible': controls_visible,
            'achievements': achievements,
            'upgrades': upgrades,
            'mini_event_click_count': mini_event_click_count,
            'timestamp': int(time.time()),
            'backup_note': 'Arquivo de backup principal. O jogo prioriza esses dados na inicialização.'
        }
        
        try:
            # Salvamento atômico
            temp_path = self.backup_path + ".tmp"
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(data_dict, f, ensure_ascii=False, indent=4)
            
            if os.path.exists(self.backup_path):
                os.replace(temp_path, self.backup_path)
            else:
                os.rename(temp_path, self.backup_path)
            return True
        except Exception as e:
            print(f"Erro ao salvar backup: {e}")
            try:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            except:
                pass
            return False

    def load_backup(self):
        """Carrega dados diretamente do backup old.json (prioridade máxima)"""
        if os.path.isfile(self.backup_path):
            try:
                with open(self.backup_path, "r", encoding="utf-8") as f:
                    data_dict = json.load(f)
                
                if not isinstance(data_dict, dict):
                    return None
                    
                return (
                    data_dict.get('score', 0),
                    data_dict.get('controls_visible', False),
                    data_dict.get('achievements', []),
                    data_dict.get('upgrades', {}),
                    data_dict.get('mini_event_click_count', 0)
                )
            except Exception as e:
                print(f"Erro ao carregar backup: {e}")
        return None