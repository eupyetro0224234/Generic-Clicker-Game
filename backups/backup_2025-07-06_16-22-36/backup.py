import os
import shutil
from datetime import datetime

def fazer_backup(pasta_origem, pasta_backup_root):
    """
    Faz backup da pasta_origem para pasta_backup_root/backup_YYYY-MM-DD_HH-MM-SS,
    copiando todos os arquivos e pastas, exceto a pasta 'backups' para evitar recursão.
    """

    agora = datetime.now()
    nome_pasta = agora.strftime("backup_%Y-%m-%d_%H-%M-%S")
    pasta_backup = os.path.join(pasta_backup_root, nome_pasta)

    os.makedirs(pasta_backup, exist_ok=False)

    def ignore_backups(dir, files):
        return ['backups'] if 'backups' in files else []

    shutil.copytree(pasta_origem, pasta_backup, dirs_exist_ok=True, ignore=ignore_backups)

    print(f"Backup criado em: {pasta_backup}")
    return pasta_backup
