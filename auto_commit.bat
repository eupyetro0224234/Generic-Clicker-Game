@echo off
setlocal enabledelayedexpansion

:: Configurar o diretório do repositório local (ajuste conforme seu caminho)
set "REPO_DIR=C:\Users\pyetr\OneDrive\Desktop\unitypy"

cd /d "%REPO_DIR%"

:menu
cls
echo ------------------------------------
echo [1] Fazer backup com data/hora (como subpasta) e enviar pro GitHub
echo [0] Sair
echo ------------------------------------
set /p escolha=Escolha uma opcao:

if "%escolha%"=="1" goto backup
if "%escolha%"=="0" exit
goto menu

:backup

:: Criar arquivo excluir.tmp antes para listar o que não copiar
(
    echo .git\
    echo backup_
    echo auto_commit.bat
    echo backup_push.bat
    echo excluir.tmp
) > excluir.tmp

:: Gerar nome de pasta com data e hora
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
set pasta=backup_!ano!-!mes!-!dia!_!hora!-!minuto!

:: Verificar se pasta existe, se sim acrescenta sufixo numérico
set /a contador=1
:verifica_pasta
if exist "!pasta!" (
    set pasta=backup_!ano!-!mes!-!dia!_!hora!-!minuto!_!contador!
    set /a contador+=1
    goto verifica_pasta
)

:: Criar pasta do backup
mkdir "!pasta!"

:: Copiar todos os arquivos da raiz para a nova pasta, excluindo o que foi listado
xcopy * "!pasta!\" /E /I /Y /EXCLUDE:excluir.tmp

:: Adicionar mudanças ao git e commitar com mensagem de backup
git add .
git commit -m "Backup automático: !pasta!"
git push origin main

del excluir.tmp

pause
goto menu
