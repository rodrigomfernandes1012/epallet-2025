#!/bin/bash
# Script de deploy para Ubuntu/Linux

set -e

echo ""
echo "========================================"
echo "  Deploy do Sistema de Gestão - Ubuntu"
echo "========================================"
echo ""

# Verificar se está rodando como root
if [ "$EUID" -eq 0 ]; then 
    echo "AVISO: Não execute este script como root!"
    echo "Execute como usuário normal."
    exit 1
fi

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "ERRO: Python3 não encontrado!"
    echo "Instalando Python3..."
    sudo apt update
    sudo apt install -y python3 python3-pip python3-venv
fi

echo "[1/8] Atualizando sistema..."
sudo apt update
sudo apt upgrade -y

echo ""
echo "[2/8] Instalando dependências do sistema..."
sudo apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib nginx

echo ""
echo "[3/8] Criando ambiente virtual..."
python3 -m venv venv

echo ""
echo "[4/8] Ativando ambiente virtual..."
source venv/bin/activate

echo ""
echo "[5/8] Instalando dependências Python..."
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

echo ""
echo "[6/8] Configurando PostgreSQL..."
read -p "Deseja configurar o PostgreSQL agora? (s/n): " config_pg

if [ "$config_pg" = "s" ]; then
    read -p "Nome do banco de dados: " db_name
    read -p "Nome do usuário: " db_user
    read -sp "Senha do usuário: " db_pass
    echo ""
    
    sudo -u postgres psql -c "CREATE DATABASE $db_name;"
    sudo -u postgres psql -c "CREATE USER $db_user WITH PASSWORD '$db_pass';"
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $db_name TO $db_user;"
    
    # Atualizar .env
    sed -i "s|DATABASE_URL=.*|DATABASE_URL=postgresql://$db_user:$db_pass@localhost:5432/$db_name|" .env
    
    echo "PostgreSQL configurado com sucesso!"
fi

echo ""
echo "[7/8] Inicializando banco de dados..."
python3 init_db.py init

echo ""
echo "[8/8] Criando serviço systemd..."
read -p "Deseja criar um serviço systemd? (s/n): " create_service

if [ "$create_service" = "s" ]; then
    CURRENT_DIR=$(pwd)
    USER=$(whoami)
    
    sudo tee /etc/systemd/system/flask-argon.service > /dev/null <<EOF
[Unit]
Description=Flask Argon Dashboard
After=network.target

[Service]
User=$USER
WorkingDirectory=$CURRENT_DIR
Environment="PATH=$CURRENT_DIR/venv/bin"
ExecStart=$CURRENT_DIR/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 run:app

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable flask-argon
    sudo systemctl start flask-argon
    
    echo "Serviço criado e iniciado!"
    echo "Comandos úteis:"
    echo "  sudo systemctl status flask-argon"
    echo "  sudo systemctl restart flask-argon"
    echo "  sudo systemctl stop flask-argon"
fi

echo ""
echo "========================================"
echo "  Deploy concluído!"
echo "========================================"
echo ""
echo "Próximos passos:"
echo "  1. Configure o Nginx como proxy reverso"
echo "  2. Configure SSL/TLS com Let's Encrypt"
echo "  3. Ajuste as configurações em .env"
echo ""
echo "Para testar localmente:"
echo "  source venv/bin/activate"
echo "  python3 run.py"
echo ""
