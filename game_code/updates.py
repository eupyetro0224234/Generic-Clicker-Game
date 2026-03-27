import requests
import threading

VERSAO_ATUAL = "0.0.06.1"
URL_VERSAO = "https://raw.githack.com/eupyetro0224234/Generic-Clicker-Game/main/github_assets/version.txt"

# Variáveis globais para armazenar o resultado da verificação
_resultado_verificacao = None
_versao_online = None
_verificacao_concluida = False

def comparar_versoes(v1, v2):
    """Compara duas versões. Retorna: 1 se v1 > v2, -1 se v1 < v2, 0 se iguais"""
    try:
        partes_v1 = [int(x) for x in v1.split('.')]
        partes_v2 = [int(x) for x in v2.split('.')]
        
        # Preenche com zeros se necessário
        max_len = max(len(partes_v1), len(partes_v2))
        partes_v1 += [0] * (max_len - len(partes_v1))
        partes_v2 += [0] * (max_len - len(partes_v2))
        
        for p1, p2 in zip(partes_v1, partes_v2):
            if p1 > p2:
                return 1
            elif p1 < p2:
                return -1
        return 0
    except:
        return 0

def _checar_atualizacao_thread():
    """Função interna que executa a verificação em uma thread separada"""
    global _resultado_verificacao, _versao_online, _verificacao_concluida
    
    try:
        resp = requests.get(URL_VERSAO, timeout=3)
        resp.raise_for_status()
        versao_online = resp.text.strip()
        
        comparacao = comparar_versoes(VERSAO_ATUAL, versao_online)
        
        if comparacao > 0:
            # Versão atual é superior (versão de dev)
            _resultado_verificacao = "dev"
            _versao_online = versao_online
        elif comparacao < 0:
            # Versão online é superior (atualização disponível)
            _resultado_verificacao = True
            _versao_online = versao_online
        else:
            # Versões iguais
            _resultado_verificacao = False
            _versao_online = versao_online
    except Exception:
        _resultado_verificacao = False
        _versao_online = None
    finally:
        _verificacao_concluida = True

def checar_atualizacao_async():
    """Inicia a verificação de atualização em background"""
    global _verificacao_concluida
    _verificacao_concluida = False
    
    thread = threading.Thread(target=_checar_atualizacao_thread, daemon=True)
    thread.start()

def obter_resultado_verificacao():
    """Retorna o resultado da verificação se já estiver concluída"""
    global _resultado_verificacao, _versao_online, _verificacao_concluida
    
    if _verificacao_concluida:
        return _resultado_verificacao, _versao_online
    else:
        return None, None

def checar_atualizacao():
    """Versão síncrona (mantida por compatibilidade)"""
    try:
        resp = requests.get(URL_VERSAO, timeout=3)
        resp.raise_for_status()
        versao_online = resp.text.strip()
        
        comparacao = comparar_versoes(VERSAO_ATUAL, versao_online)
        
        if comparacao > 0:
            # Versão atual é superior (versão de dev)
            return "dev", versao_online
        elif comparacao < 0:
            # Versão online é superior (atualização disponível)
            return True, versao_online
        else:
            # Versões iguais
            return False, versao_online
    except Exception:
        return False, None