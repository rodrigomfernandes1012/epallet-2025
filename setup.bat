@echo off
REM Script completo de configuracao para Windows

echo.
echo ========================================
echo   Configuracao Completa do Sistema
echo ========================================
echo.

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao encontrado!
    echo.
    echo Por favor, instale o Python 3.11 ou superior:
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo [1/5] Criando ambiente virtual...
python -m venv venv
echo.

echo [2/5] Ativando ambiente virtual...
call venv\Scripts\activate.bat
echo.

echo [3/5] Atualizando pip...
python -m pip install --upgrade pip
echo.

echo [4/5] Instalando dependencias...
pip install -r requirements.txt
echo.

echo [5/5] Inicializando banco de dados...
python init_db.py init
echo.

echo ========================================
echo   Configuracao concluida!
echo ========================================
echo.
echo Para executar o sistema:
echo   1. Ative o ambiente virtual: venv\Scripts\activate
echo   2. Execute o servidor: python run.py
echo.
echo Ou simplesmente execute: run.bat
echo.
pause
