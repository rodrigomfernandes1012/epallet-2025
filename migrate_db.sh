#!/bin/bash
# Script de Migração do Banco de Dados - Linux
# Adiciona coluna motorista_id na tabela vales_pallet

echo "============================================================"
echo "MIGRAÇÃO DO BANCO DE DADOS"
echo "============================================================"
echo ""

# Verificar se o ambiente virtual existe
if [ -d "venv" ]; then
    echo "Ativando ambiente virtual..."
    source venv/bin/activate
elif [ -d "env" ]; then
    echo "Ativando ambiente virtual..."
    source env/bin/activate
else
    echo "AVISO: Ambiente virtual não encontrado"
    echo "Usando Python global..."
fi

echo ""
echo "Executando migração..."
echo ""

python3 migrate_db.py

echo ""
echo "============================================================"
echo ""
