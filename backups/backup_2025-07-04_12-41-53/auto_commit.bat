@echo off
setlocal enabledelayedexpansion

set "REPO_DIR=C:\Users\pyetr\OneDrive\Desktop\unitypy"
cd /d "%REPO_DIR%"

echo Atualizando repositório remoto...
git pull origin main

echo Removendo repositórios internos dos backups...
for /d %%F in (backups\*) do (
    if exist "%%F\.git" (
        rmdir /s /q "%%F\.git"
    )
)

if exist ".gitmodules" (
    del /f /q ".gitmodules"
)

git rm --cached -r backups >nul 2>&1

echo Adicionando todos os arquivos dos backups...
git add backups/*

:: Gerar mensagem de commit com data e hora
for /f "tokens=1-3 delims=/" %%a in ('date /t') do (
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
