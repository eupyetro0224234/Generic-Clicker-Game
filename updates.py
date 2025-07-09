import requests

VERSAO_ATUAL = "0.0.02"

URL_VERSAO = "https://raw.githubusercontent.com/eupyetro0224234/just-another-generic-clicker-game-but-with-references/refs/heads/main/version.txt"

def checar_atualizacao():
    try:
        resp = requests.get(URL_VERSAO, timeout=5)
        resp.raise_for_status()
        versao_online = resp.text.strip()

        if versao_online != VERSAO_ATUAL:
            return True, versao_online
        else:
            return False, versao_online
    except Exception as e:
        return False, None
