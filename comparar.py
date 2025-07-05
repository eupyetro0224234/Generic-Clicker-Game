import os
from filecmp import cmp as filecmp

PASTA_BACKUPS = "backups"
IGNORAR = {'__pycache__', 'auto_commit.bat', '.gitignore'}
NOME_CHANGELOG = "CHANGELOG.txt"

def gerar_changelogs_sequenciais():
    backups = sorted([
        pasta for pasta in os.listdir(PASTA_BACKUPS)
        if os.path.isdir(os.path.join(PASTA_BACKUPS, pasta))
    ])

    for i in range(1, len(backups)):
        pasta_anterior = backups[i - 1]
        pasta_atual = backups[i]

        caminho_antigo = os.path.join(PASTA_BACKUPS, pasta_anterior)
        caminho_novo = os.path.join(PASTA_BACKUPS, pasta_atual)
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
            caminho_arquivo_antigo = os.path.join(caminho_antigo, nome)
            caminho_arquivo_novo = os.path.join(caminho_novo, nome)

            if os.path.exists(caminho_arquivo_antigo) and os.path.exists(caminho_arquivo_novo):
                if not filecmp(caminho_arquivo_antigo, caminho_arquivo_novo, shallow=False):
                    mudanças.append(f"- Arquivo alterado: {nome}")
            elif os.path.exists(caminho_arquivo_novo):
                mudanças.append(f"- Novo arquivo: {nome}")
            elif os.path.exists(caminho_arquivo_antigo):
                mudanças.append(f"- Arquivo removido: {nome}")

        if mudanças:
            with open(changelog_path, 'w', encoding='utf-8') as log:
                log.write(f"# Mudanças entre {pasta_anterior} → {pasta_atual}\n\n")
                log.write('\n'.join(mudanças))
            print(f"Changelog gerado: {changelog_path}")
        else:
            print(f"Nenhuma mudança entre {pasta_anterior} e {pasta_atual}.")

# Executar
if __name__ == '__main__':
    gerar_changelogs_sequenciais()
