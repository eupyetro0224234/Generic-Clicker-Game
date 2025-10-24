import requests

VERSAO_ATUAL = "0.0.05"

URL_VERSAO = "https://raw.githack.com/eupyetro0224234/Generic-Clicker-Game/main/github_assets/version.txt"

def checar_atualizacao():
    try:
        resp = requests.get(URL_VERSAO, timeout=5)
        resp.raise_for_status()
        versao_online = resp.text.strip()

        if versao_online != VERSAO_ATUAL:
            return True, versao_online
        else:
            return False, versao_online
    except Exception:
        return False, None
