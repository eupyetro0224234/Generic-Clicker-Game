import os
from filecmp import cmp as filecmp

IGNORAR = {'__pycache__', 'auto_commit.bat', '.gitignore'}
NOME_CHANGELOG = "CHANGELOG_DIFF.txt"

def comparar_com_backup_anterior(pasta_backups):
    backups = sorted([
        p for p in os.listdir(pasta_backups)
        if os.path.isdir(os.path.join(pasta_backups, p))
    ])

    if len(backups) < 2:
        return  # nada a comparar

    anterior = backups[-2]
    atual = backups[-1]

    caminho_antigo = os.path.join(pasta_backups, anterior)
    caminho_novo = os.path.join(pasta_backups, atual)
    changelog_path = os.path.join(caminho_novo, NOME_CHANGELOG)

    mudanças = []

    arquivos_antigos = {
        os.path.relpath(os.path.join(root, nome), caminho_antigo)
        for root, _, files in os.walk(caminho_antigo)
        for nome in files
        if nome not in IGNORAR and not any(ign in root for ign in IGNORAR)
    }

    arquivos_novos = {
        os.path.relpath(os.path.join(root, nome), caminho_novo)
        for root, _, files in os.walk(caminho_novo)
        for nome in files
        if nome not in IGNORAR and not any(ign in root for ign in IGNORAR)
    }

    todos_arquivos = arquivos_antigos | arquivos_novos

    for nome in sorted(todos_arquivos):
        ant = os.path.join(caminho_antigo, nome)
        nov = os.path.join(caminho_novo, nome)

        if os.path.exists(ant) and os.path.exists(nov):
            if not filecmp(ant, nov, shallow=False):
                mudanças.append(f"- Arquivo alterado: {nome}")
        elif os.path.exists(nov):
            mudanças.append(f"- Novo arquivo: {nome}")
        elif os.path.exists(ant):
            mudanças.append(f"- Arquivo removido: {nome}")

    if mudanças:
        with open(changelog_path, 'w', encoding='utf-8') as f:
            f.write(f"# Mudanças entre {anterior} → {atual}\n\n")
            f.write('\n'.join(mudanças))
        print(f"Changelog gerado: {changelog_path}")
    else:
        print(f"Nenhuma mudança detectada entre {anterior} e {atual}.")
