@echo off
setlocal enabledelayedexpansion

:: Diretório do repositório
set "REPO_DIR=C:\Users\pyetr\OneDrive\Desktop\unitypy"

cd /d "%REPO_DIR%"

echo Atualizando repositório remoto...
git pull origin main

echo Adicionando arquivos da pasta backups...
git add backups/

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
