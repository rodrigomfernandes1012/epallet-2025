@echo off
echo ========================================
echo Migração: Sistema de Perfis
echo ========================================
echo.

REM Ativar ambiente virtual
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo ERRO: Ambiente virtual não encontrado!
    echo Execute setup.bat primeiro.
    pause
    exit /b 1
)

REM Executar migração
python migrate_perfis.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo Migração concluída com sucesso!
    echo ========================================
) else (
    echo.
    echo ========================================
    echo ERRO na migração!
    echo ========================================
)

echo.
pause
