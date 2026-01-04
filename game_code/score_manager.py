import os, json, time, pytz
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from datetime import datetime

class ScoreManager:
    def __init__(self, folder_name="genericclickergame", filename="score.dat"):
        appdata = os.getenv("APPDATA") or "."
        self.folder_path = os.path.join(appdata, folder_name)
        os.makedirs(self.folder_path, exist_ok=True)
        self.file_path = os.path.join(self.folder_path, filename)
        self.encryption_key = b'justanotherkey12'
        
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

    def save_data(self, score: int, controls_visible: bool, achievements, 
                 upgrades: dict[str, int], mini_event_click_count: int, 
                 trabalhador_limit_enabled: bool = True, eventos_participados: dict = None,
                 total_play_time: int = 0, last_timestamp: int = None, max_score: int = None,
                 total_score_earned: int = 0, mini_event1_total: int = 0, mini_event2_total: int = 0,
                 normal_clicks: int = 0, first_join_date: str = None, streak_data: dict = None,
                 is_reset: bool = False, mini_event1_session: int = 0, mini_event2_session: int = 0,
                 offline_time_bank: int = 0):
        
        if eventos_participados is None:
            eventos_participados = {}
            
        if last_timestamp is None:
            last_timestamp = int(time.time())
            
        if streak_data is None:
            streak_data = {"current_streak": 0, "last_login_date": None, "max_streak": 0}
                
        existing_max_score = 0
        existing_total_score_earned = 0
        existing_mini_event1_total = 0
        existing_mini_event2_total = 0
        existing_normal_clicks = 0
        existing_first_join_date = None
        existing_streak_data = {"current_streak": 0, "last_login_date": None, "max_streak": 0}
        existing_mini_event1_session = 0
        existing_mini_event2_session = 0
        
        if os.path.exists(self.file_path):
            try:
                existing_data = self.load_data()
                if existing_data:
                    if len(existing_data) > 10:
                        existing_max_score = existing_data[10]
                    elif existing_data:
                        existing_max_score = existing_data[0] if existing_data[0] > existing_max_score else existing_max_score
                    
                    if len(existing_data) > 11:
                        existing_total_score_earned = existing_data[11]
                    if len(existing_data) > 12:
                        existing_mini_event1_total = existing_data[12]
                    if len(existing_data) > 13:
                        existing_mini_event2_total = existing_data[13]
                    if len(existing_data) > 14:
                        existing_normal_clicks = existing_data[14]
                    if len(existing_data) > 15:
                        existing_first_join_date = existing_data[15]
                    if len(existing_data) > 16:
                        existing_streak_data = existing_data[16]
                    if len(existing_data) > 17:
                        existing_mini_event1_session = existing_data[17]
                    if len(existing_data) > 18:
                        existing_mini_event2_session = existing_data[18]
                    
                    if normal_clicks == 0 and len(existing_data) > 14:
                        normal_clicks = existing_data[14]
                    if mini_event_click_count == 0 and len(existing_data) > 4:
                        mini_event_click_count = existing_data[4]
            except:
                pass
        
        if max_score is None:
            max_score = max(score, existing_max_score)
        else:
            max_score = max(score, max_score, existing_max_score)
            
        if total_score_earned == 0:
            total_score_earned = existing_total_score_earned
        
        if is_reset:
            mini_event1_total = existing_mini_event1_total
            mini_event2_total = existing_mini_event2_total
            mini_event1_session = 0
            mini_event2_session = 0
        else:
            if mini_event1_total == 0:
                mini_event1_total = existing_mini_event1_total
            if mini_event2_total == 0:
                mini_event2_total = existing_mini_event2_total
            if mini_event1_session == 0:
                mini_event1_session = existing_mini_event1_session
            if mini_event2_session == 0:
                mini_event2_session = existing_mini_event2_session
            
        if existing_first_join_date:
            first_join_date = existing_first_join_date
        elif first_join_date is None:
            tz_brasilia = pytz.timezone('America/Sao_Paulo')
            first_join_date = datetime.now(tz_brasilia).strftime("%d/%m/%Y - %H:%M")
                
        if streak_data["current_streak"] == 0:
            streak_data = existing_streak_data
            
        if total_play_time == 0 and os.path.exists(self.file_path):
            try:
                existing_data = self.load_data()
                if existing_data and len(existing_data) > 8:
                    total_play_time = existing_data[8]
            except:
                pass
            
        data_dict = {
            'score': score,
            'controls_visible': controls_visible,
            'achievements': achievements,
            'upgrades': upgrades,
            'mini_event_click_count': mini_event_click_count,
            'trabalhadores': [],
            'trabalhador_limit_enabled': trabalhador_limit_enabled,
            'eventos_participados': eventos_participados,
            'total_play_time': total_play_time,
            'last_timestamp': last_timestamp,
            'timestamp': int(time.time()),
            'max_score': max_score,
            'total_score_earned': total_score_earned,
            'mini_event1_total': mini_event1_total,
            'mini_event2_total': mini_event2_total,
            'normal_clicks': normal_clicks,
            'first_join_date': first_join_date,
            'streak_data': streak_data,
            'mini_event1_session': mini_event1_session,
            'mini_event2_session': mini_event2_session,
            'offline_time_bank': offline_time_bank
        }

        encrypted = self.encrypt_data(data_dict)
        if encrypted:
            try:
                temp_path = self.file_path + ".tmp"
                with open(temp_path, "wb") as file:
                    file.write(encrypted)
                
                if os.path.exists(self.file_path):
                    os.replace(temp_path, self.file_path)
                else:
                    os.rename(temp_path, self.file_path)
                return True
            except Exception as e:
                try:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                except:
                    pass
        return False

    def load_data(self):
        if os.path.isfile(self.file_path):
            try:
                with open(self.file_path, "rb") as file:
                    encrypted = file.read()
                data_dict = self.decrypt_data(encrypted)
                
                if data_dict:
                    max_score = data_dict.get("max_score", data_dict.get("score", 0))
                    total_score_earned = data_dict.get("total_score_earned", max_score)
                    mini_event1_total = data_dict.get("mini_event1_total", 0)
                    mini_event2_total = data_dict.get("mini_event2_total", 0)
                    normal_clicks = data_dict.get("normal_clicks", 0)
                    first_join_date = data_dict.get("first_join_date")
                    streak_data = data_dict.get("streak_data", {"current_streak": 0, "last_login_date": None, "max_streak": 0})
                    mini_event1_session = data_dict.get("mini_event1_session", 0)
                    mini_event2_session = data_dict.get("mini_event2_session", 0)
                    offline_time_bank = data_dict.get("offline_time_bank", 0)
                    
                    achievements = data_dict.get("achievements", {})
                    
                    if not first_join_date:
                        tz_brasilia = pytz.timezone('America/Sao_Paulo')
                        first_join_date = datetime.now(tz_brasilia).strftime("%d/%m/%Y - %H:%M")
                    
                    return (
                        data_dict.get("score", 0),
                        data_dict.get("controls_visible", False),
                        achievements,
                        data_dict.get("upgrades", {}),
                        data_dict.get("mini_event_click_count", 0),
                        [],
                        data_dict.get("trabalhador_limit_enabled", True),
                        data_dict.get("eventos_participados", {}),
                        data_dict.get("total_play_time", 0),
                        data_dict.get("last_timestamp", None),
                        max_score,
                        total_score_earned,
                        mini_event1_total,
                        mini_event2_total,
                        normal_clicks,
                        first_join_date,
                        streak_data,
                        mini_event1_session,
                        mini_event2_session,
                        offline_time_bank
                    )
            except Exception:
                pass

        tz_brasilia = pytz.timezone('America/Sao_Paulo')
        first_join_date = datetime.now(tz_brasilia).strftime("%d/%m/%Y - %H:%M")
        streak_data = {"current_streak": 0, "last_login_date": None, "max_streak": 0}
        
        return 0, False, {}, {}, 0, [], True, {}, 0, None, 0, 0, 0, 0, 0, first_join_date, streak_data, 0, 0, 0