@echo off
setlocal enabledelayedexpansion

:: Caminho do repositório
set "REPO_DIR=C:\Users\pyetr\OneDrive\Desktop\unitypy"

cd /d "%REPO_DIR%"

echo Atualizando repositório remoto...
git pull origin main

echo Removendo repositórios internos dos backups...
for /d %%F in (backups\*) do (
    if exist "%%F\.git" rd /s /q "%%F\.git"
)

echo Adicionando arquivos manualmente de cada subpasta de backup...
for /d %%F in (backups\*) do (
    git add "%%F\*"
)

:: Também adiciona arquivos de nível superior modificados, se desejar:
git add auto_commit.bat
git add *.py
git add requirements.txt

:: Mensagem de commit com data e hora
for /f "tokens=1-3 delims=/ " %%a in ('date /t') do (
    set dia=%%a
    set mes=%%b
    set ano=%%c
)
for /f "tokens=1-2 delims=: " %%a in ('time /t') do (
    set hora=%%a
    set minuto=%%b
)
set hora=!hora::=!
set commit_msg=Backup_!ano!-!mes!-!dia!_!hora!-!minuto!

git commit -m "!commit_msg!"
git push origin main

pause
