import os
import shutil
from datetime import datetime

def fazer_backup(pasta_origem, pasta_backup_root):
    # Cria nome da pasta backup com data e hora
    agora = datetime.now()
    nome_pasta = agora.strftime("backup_%Y-%m-%d_%H-%M-%S")
    pasta_backup = os.path.join(pasta_backup_root, nome_pasta)

    # Cria pasta backup
    os.makedirs(pasta_backup, exist_ok=False)

    # Copia arquivos e pastas de pasta_origem para pasta_backup,
    # ignorando a pasta de backups para evitar cópia cíclica
    def ignore_backups(dir, files):
        return ['backups'] if 'backups' in files else []

    shutil.copytree(pasta_origem, pasta_backup, dirs_exist_ok=True, ignore=ignore_backups)

    print(f"Backup criado em: {pasta_backup}")
    return pasta_backup

def main():
    # Define os caminhos
    pasta_do_projeto = os.path.dirname(os.path.abspath(__file__))
    pasta_de_backups = r"C:\Users\pyetr\OneDrive\Desktop\backups"

    # Faz backup no início do app
    fazer_backup(pasta_do_projeto, pasta_de_backups)

    # Aqui começa o código real do seu app
    print("App iniciado!")
    # Coloque seu código principal aqui

    # Simulação de app rodando (para demo)
    while True:
        cmd = input("Digite 'sair' para fechar: ")
        if cmd.strip().lower() == 'sair':
            break

if __name__ == "__main__":
    main()
