@echo off
REM Script de Migração do Banco de Dados - Windows
REM Adiciona coluna motorista_id na tabela vales_pallet

echo ============================================================
echo MIGRACAO DO BANCO DE DADOS
echo ============================================================
echo.

REM Verificar se o ambiente virtual existe
if exist "env\Scripts\activate.bat" (
    echo Ativando ambiente virtual...
    call env\Scripts\activate.bat
) else if exist "venv\Scripts\activate.bat" (
    echo Ativando ambiente virtual...
    call venv\Scripts\activate.bat
) else (
    echo AVISO: Ambiente virtual nao encontrado
    echo Usando Python global...
)

echo.
echo Executando migracao...
echo.

python migrate_db.py

echo.
echo ============================================================
echo.
pause
