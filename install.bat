@echo off
REM Script para instalar dependencias no Windows

echo.
echo ========================================
echo   Instalacao do Sistema de Gestao
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

echo [1/4] Verificando versao do Python...
python --version
echo.

echo [2/4] Atualizando pip...
python -m pip install --upgrade pip
echo.

echo [3/4] Instalando dependencias...
pip install -r requirements.txt
echo.

echo [4/4] Verificando instalacao...
python -c "import flask; print('Flask instalado com sucesso!')"
echo.

echo ========================================
echo   Instalacao concluida!
echo ========================================
echo.
echo Proximos passos:
echo   1. Execute: init_db.bat init
echo   2. Execute: run.bat
echo.
pause
