#!/bin/bash

echo "========================================"
echo "Migração: Sistema de Perfis"
echo "========================================"
echo ""

# Ativar ambiente virtual
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    echo "ERRO: Ambiente virtual não encontrado!"
    echo "Execute o script de instalação primeiro."
    exit 1
fi

# Executar migração
python3 migrate_perfis.py

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "Migração concluída com sucesso!"
    echo "========================================"
else
    echo ""
    echo "========================================"
    echo "ERRO na migração!"
    echo "========================================"
    exit 1
fi
