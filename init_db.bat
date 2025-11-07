@echo off
REM Script para inicializar o banco de dados no Windows
REM Uso: init_db.bat [comando]

if "%1"=="" goto help
if "%1"=="init" goto init
if "%1"=="reset" goto reset
if "%1"=="create-admin" goto create_admin
goto unknown

:init
echo Inicializando banco de dados...
python init_db.py init
goto end

:reset
echo Resetando banco de dados...
python init_db.py reset
goto end

:create_admin
echo Criando usuario administrador...
python init_db.py create-admin
goto end

:unknown
echo Comando desconhecido: %1
goto help

:help
echo.
echo Uso: init_db.bat [comando]
echo.
echo Comandos disponiveis:
echo   init          Inicializa o banco de dados (cria tabelas)
echo   reset         Remove e recria todas as tabelas (APAGA DADOS!)
echo   create-admin  Cria um novo usuario administrador
echo.
echo Exemplos:
echo   init_db.bat init
echo   init_db.bat create-admin
echo   init_db.bat reset
echo.
goto end

:end
