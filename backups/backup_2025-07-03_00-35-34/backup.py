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
