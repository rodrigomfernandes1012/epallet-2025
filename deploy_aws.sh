#!/bin/bash

##############################################################################
# Script de Deploy Automático - Epallet System
# Para Ubuntu 22.04 LTS em AWS
##############################################################################

set -e  # Parar em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funções auxiliares
print_header() {
    echo -e "\n${BLUE}============================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}============================================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Verificar se está rodando como root
if [ "$EUID" -eq 0 ]; then
    print_error "Não execute este script como root!"
    print_info "Execute como usuário normal: ./deploy_aws.sh"
    exit 1
fi

print_header "DEPLOY AUTOMÁTICO - EPALLET SYSTEM"

# Solicitar informações
print_info "Por favor, forneça as seguintes informações:"
echo ""

read -p "Domínio (ex: epallet.com.br): " DOMAIN
read -p "Email para SSL (Let's Encrypt): " EMAIL
read -p "Senha do PostgreSQL: " -s DB_PASSWORD
echo ""
read -p "WhatsGw API Key: " WHATSGW_APIKEY
read -p "WhatsGw Phone Number (ex: 5511945480370): " WHATSGW_PHONE

echo ""
print_warning "Confirme as informações:"
echo "Domínio: $DOMAIN"
echo "Email: $EMAIL"
echo "WhatsGw Phone: $WHATSGW_PHONE"
echo ""
read -p "Continuar? (s/n): " CONFIRM

if [ "$CONFIRM" != "s" ] && [ "$CONFIRM" != "S" ]; then
    print_error "Deploy cancelado pelo usuário"
    exit 1
fi

##############################################################################
# 1. ATUALIZAR SISTEMA
##############################################################################

print_header "1. Atualizando Sistema"

sudo apt update
sudo apt upgrade -y

print_success "Sistema atualizado"

##############################################################################
# 2. INSTALAR DEPENDÊNCIAS
##############################################################################

print_header "2. Instalando Dependências"

# Python
sudo apt install -y python3.11 python3.11-venv python3-pip
sudo apt install -y build-essential libpq-dev
sudo apt install -y git curl wget unzip

# PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Nginx
sudo apt install -y nginx

# Certbot
sudo apt install -y certbot python3-certbot-nginx

print_success "Dependências instaladas"

##############################################################################
# 3. CONFIGURAR POSTGRESQL
##############################################################################

print_header "3. Configurando PostgreSQL"

# Criar banco e usuário
sudo -u postgres psql <<EOF
CREATE DATABASE epallet_db;
CREATE USER epallet_user WITH PASSWORD '$DB_PASSWORD';
ALTER ROLE epallet_user SET client_encoding TO 'utf8';
ALTER ROLE epallet_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE epallet_user SET timezone TO 'America/Sao_Paulo';
GRANT ALL PRIVILEGES ON DATABASE epallet_db TO epallet_user;
EOF

# Configurar acesso
sudo bash -c "echo 'local   epallet_db      epallet_user                            md5' >> /etc/postgresql/14/main/pg_hba.conf"

# Reiniciar PostgreSQL
sudo systemctl restart postgresql
sudo systemctl enable postgresql

print_success "PostgreSQL configurado"

##############################################################################
# 4. CONFIGURAR APLICAÇÃO
##############################################################################

print_header "4. Configurando Aplicação"

# Criar diretório
sudo mkdir -p /var/www/epallet
sudo chown -R $USER:$USER /var/www/epallet

# Copiar arquivos (assumindo que o script está na pasta do projeto)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cp -r $SCRIPT_DIR/* /var/www/epallet/

cd /var/www/epallet

# Criar ambiente virtual
python3.11 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn psycopg2-binary

# Gerar SECRET_KEY
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")

# Criar .env
cat > .env <<EOF
FLASK_APP=run.py
FLASK_ENV=production
SECRET_KEY=$SECRET_KEY
DATABASE_URL=postgresql://epallet_user:$DB_PASSWORD@localhost:5432/epallet_db

# Configurações WhatsGw para WhatsApp
WHATSGW_APIKEY=$WHATSGW_APIKEY
WHATSGW_PHONE_NUMBER=$WHATSGW_PHONE
EOF

# Inicializar banco
python3 init_db.py init <<EOF
n
EOF

python3 popular_tipos.py

print_success "Aplicação configurada"

##############################################################################
# 5. CONFIGURAR GUNICORN
##############################################################################

print_header "5. Configurando Gunicorn"

# Criar diretórios de log
sudo mkdir -p /var/log/epallet
sudo mkdir -p /var/run/epallet
sudo chown -R $USER:$USER /var/log/epallet
sudo chown -R $USER:$USER /var/run/epallet

# Criar serviço systemd
sudo tee /etc/systemd/system/epallet.service > /dev/null <<EOF
[Unit]
Description=Epallet Flask Application
After=network.target postgresql.service

[Service]
Type=notify
User=$USER
Group=$USER
WorkingDirectory=/var/www/epallet
Environment="PATH=/var/www/epallet/venv/bin"
ExecStart=/var/www/epallet/venv/bin/gunicorn -c gunicorn_config.py run:app
ExecReload=/bin/kill -s HUP \$MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Ativar e iniciar serviço
sudo systemctl daemon-reload
sudo systemctl enable epallet
sudo systemctl start epallet

print_success "Gunicorn configurado"

##############################################################################
# 6. CONFIGURAR NGINX
##############################################################################

print_header "6. Configurando Nginx"

# Criar configuração do site
sudo tee /etc/nginx/sites-available/epallet > /dev/null <<EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN motorista.$DOMAIN;

    # Logs
    access_log /var/log/nginx/epallet_access.log;
    error_log /var/log/nginx/epallet_error.log;

    # Tamanho máximo de upload
    client_max_body_size 10M;

    # Arquivos estáticos
    location /static {
        alias /var/www/epallet/app/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Proxy para Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Buffering
        proxy_buffering off;
        proxy_request_buffering off;
    }

    # Webhook WhatsApp (sem timeout)
    location /webhook {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Sem timeout para webhook
        proxy_read_timeout 300s;
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
    }
}
EOF

# Ativar site
sudo ln -sf /etc/nginx/sites-available/epallet /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Testar configuração
sudo nginx -t

# Reiniciar Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx

print_success "Nginx configurado"

##############################################################################
# 7. CONFIGURAR SSL
##############################################################################

print_header "7. Configurando SSL (HTTPS)"

# Obter certificado SSL
sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN -d motorista.$DOMAIN --non-interactive --agree-tos --email $EMAIL --redirect

print_success "SSL configurado"

##############################################################################
# 8. CONFIGURAR BACKUP AUTOMÁTICO
##############################################################################

print_header "8. Configurando Backup Automático"

# Criar diretório de backup
sudo mkdir -p /var/backups/epallet
sudo chown $USER:$USER /var/backups/epallet

# Adicionar cron job
(crontab -l 2>/dev/null; echo "0 3 * * * sudo -u postgres pg_dump epallet_db > /var/backups/epallet/backup_\$(date +\%Y\%m\%d).sql") | crontab -
(crontab -l 2>/dev/null; echo "0 4 * * * find /var/backups/epallet -name 'backup_*.sql' -mtime +30 -delete") | crontab -

print_success "Backup automático configurado"

##############################################################################
# 9. VERIFICAÇÕES FINAIS
##############################################################################

print_header "9. Verificações Finais"

# Verificar serviços
print_info "Verificando serviços..."

if systemctl is-active --quiet epallet; then
    print_success "Epallet: Rodando"
else
    print_error "Epallet: Não está rodando"
fi

if systemctl is-active --quiet nginx; then
    print_success "Nginx: Rodando"
else
    print_error "Nginx: Não está rodando"
fi

if systemctl is-active --quiet postgresql; then
    print_success "PostgreSQL: Rodando"
else
    print_error "PostgreSQL: Não está rodando"
fi

# Testar webhook
print_info "Testando webhook..."
WEBHOOK_TEST=$(curl -s https://$DOMAIN/webhook/test)
if echo "$WEBHOOK_TEST" | grep -q "ok"; then
    print_success "Webhook: Funcionando"
else
    print_warning "Webhook: Verifique manualmente"
fi

##############################################################################
# 10. INFORMAÇÕES FINAIS
##############################################################################

print_header "DEPLOY CONCLUÍDO COM SUCESSO!"

echo ""
print_success "Sistema instalado e configurado!"
echo ""
print_info "URLs de acesso:"
echo "  • Sistema: https://$DOMAIN"
echo "  • Motorista: https://motorista.$DOMAIN"
echo "  • Webhook: https://$DOMAIN/webhook/whatsapp"
echo ""
print_info "Credenciais do banco:"
echo "  • Banco: epallet_db"
echo "  • Usuário: epallet_user"
echo "  • Senha: $DB_PASSWORD"
echo ""
print_info "Comandos úteis:"
echo "  • Ver logs: sudo journalctl -u epallet -f"
echo "  • Reiniciar: sudo systemctl restart epallet"
echo "  • Status: sudo systemctl status epallet"
echo ""
print_warning "PRÓXIMOS PASSOS:"
echo "  1. Configure o webhook no WhatsGw:"
echo "     URL: https://$DOMAIN/webhook/whatsapp"
echo "  2. Crie um usuário admin no sistema"
echo "  3. Faça backup do arquivo .env"
echo ""
print_success "Deploy finalizado! 🚀"
echo ""
