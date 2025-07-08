import requests

VERSAO_ATUAL = "0.0.02"  # Mude aqui para a versão atual do seu jogo

URL_VERSAO = "https://raw.githubusercontent.com/eupyetro0224234/just-another-generic-clicker-game-but-with-references/main/version.txt
"  # Link raw para o version.txt no GitHub

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
        print(f"Erro ao verificar atualização: {e}")
        return False, None

if __name__ == "__main__":
    atualizou, versao = checar_atualizacao()
    if atualizou:
        print(f"Nova versão disponível: {versao} (Você está na {VERSAO_ATUAL})")
    else:
        print("Você já está usando a versão mais recente.")
