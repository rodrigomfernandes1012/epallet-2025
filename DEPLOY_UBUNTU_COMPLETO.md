# 🚀 Guia Completo de Deploy - Sistema Epallet no Ubuntu

## 📋 Índice

1. [Pré-requisitos](#pré-requisitos)
2. [Preparação do Servidor](#preparação-do-servidor)
3. [Instalação de Dependências](#instalação-de-dependências)
4. [Configuração do Projeto](#configuração-do-projeto)
5. [Configuração do Banco de Dados](#configuração-do-banco-de-dados)
6. [Configuração do Nginx](#configuração-do-nginx)
7. [Configuração do Gunicorn](#configuração-do-gunicorn)
8. [Configuração do Systemd](#configuração-do-systemd)
9. [Configuração de SSL/HTTPS](#configuração-de-sslhttps)
10. [Testes e Validação](#testes-e-validação)
11. [Manutenção e Monitoramento](#manutenção-e-monitoramento)
12. [Troubleshooting](#troubleshooting)

---

## 🖥️ Pré-requisitos

### Servidor Ubuntu
- **Sistema Operacional:** Ubuntu 20.04 LTS ou superior
- **RAM:** Mínimo 2GB (recomendado 4GB)
- **Disco:** Mínimo 20GB
- **Acesso:** SSH com usuário sudo

### Domínio e DNS
- Domínio registrado (ex: `epallet.com.br`)
- Subdomínios configurados:
  - `app.epallet.com.br` (aplicação principal)
  - `motorista.epallet.com.br` (área do motorista)

### Credenciais Necessárias
- API WhatsGw (para notificações)
- Chave secreta para sessões Flask

---

## 🔧 Preparação do Servidor

### 1. Atualizar Sistema

```bash
sudo apt update
sudo apt upgrade -y
```

### 2. Criar Usuário para a Aplicação

```bash
# Criar usuário
sudo adduser epallet

# Adicionar ao grupo sudo (opcional)
sudo usermod -aG sudo epallet

# Trocar para o usuário
su - epallet
```

### 3. Configurar Firewall

```bash
# Permitir SSH
sudo ufw allow OpenSSH

# Permitir HTTP e HTTPS
sudo ufw allow 'Nginx Full'

# Ativar firewall
sudo ufw enable

# Verificar status
sudo ufw status
```

---

## 📦 Instalação de Dependências

### 1. Instalar Python 3.11

```bash
# Adicionar repositório
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update

# Instalar Python 3.11
sudo apt install python3.11 python3.11-venv python3.11-dev -y

# Verificar instalação
python3.11 --version
```

### 2. Instalar Nginx

```bash
sudo apt install nginx -y

# Verificar status
sudo systemctl status nginx

# Iniciar se não estiver rodando
sudo systemctl start nginx
sudo systemctl enable nginx
```

### 3. Instalar Supervisor (opcional, para gerenciamento de processos)

```bash
sudo apt install supervisor -y
sudo systemctl enable supervisor
sudo systemctl start supervisor
```

### 4. Instalar Git

```bash
sudo apt install git -y
git --version
```

---

## ⚙️ Configuração do Projeto

### 1. Clonar ou Transferir Projeto

#### Opção A: Via Git (se tiver repositório)
```bash
cd /home/epallet
git clone https://github.com/seu-usuario/flask-argon-system.git
cd flask-argon-system
```

#### Opção B: Via SCP/SFTP
```bash
# No seu computador local
scp flask-argon-system-v18.zip epallet@SEU_SERVIDOR_IP:/home/epallet/

# No servidor
cd /home/epallet
unzip flask-argon-system-v18.zip
cd flask-argon-system
```

### 2. Criar Ambiente Virtual

```bash
cd /home/epallet/flask-argon-system

# Criar ambiente virtual com Python 3.11
python3.11 -m venv venv

# Ativar ambiente virtual
source venv/bin/activate

# Verificar Python do ambiente
which python
python --version  # Deve mostrar Python 3.11.x
```

### 3. Instalar Dependências Python

```bash
# Atualizar pip
pip install --upgrade pip

# Instalar dependências
pip install -r requirements.txt

# Verificar instalação
pip list
```

### 4. Configurar Variáveis de Ambiente

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar arquivo .env
nano .env
```

**Conteúdo do arquivo `.env`:**

```bash
# Flask
FLASK_APP=run.py
FLASK_ENV=production
SECRET_KEY=sua-chave-secreta-super-segura-aqui-min-32-caracteres

# Banco de Dados
DATABASE_URL=sqlite:///instance/epallet.db
# Para PostgreSQL:
# DATABASE_URL=postgresql://usuario:senha@localhost/epallet_db

# WhatsGw API
WHATSGW_APIKEY=sua-api-key-aqui
WHATSGW_PHONE_NUMBER=5511987654321

# Configurações do Sistema
DEBUG=False
TESTING=False
```

**Gerar SECRET_KEY segura:**

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

---

## 🗄️ Configuração do Banco de Dados

### Opção 1: SQLite (Desenvolvimento/Pequeno Porte)

```bash
# Criar diretório instance
mkdir -p instance

# Inicializar banco de dados
python init_db.py

# Verificar criação
ls -la instance/
```

### Opção 2: PostgreSQL (Produção/Grande Porte)

#### 1. Instalar PostgreSQL

```bash
sudo apt install postgresql postgresql-contrib -y

# Verificar status
sudo systemctl status postgresql
```

#### 2. Criar Banco e Usuário

```bash
# Acessar PostgreSQL
sudo -u postgres psql

# Dentro do PostgreSQL
CREATE DATABASE epallet_db;
CREATE USER epallet_user WITH PASSWORD 'senha-super-segura';
GRANT ALL PRIVILEGES ON DATABASE epallet_db TO epallet_user;
\q
```

#### 3. Instalar Adaptador Python

```bash
source venv/bin/activate
pip install psycopg2-binary
```

#### 4. Atualizar .env

```bash
DATABASE_URL=postgresql://epallet_user:senha-super-segura@localhost/epallet_db
```

#### 5. Inicializar Banco

```bash
python init_db.py
```

---

## 🌐 Configuração do Nginx

### 1. Criar Arquivo de Configuração

```bash
sudo nano /etc/nginx/sites-available/epallet
```

**Conteúdo do arquivo:**

```nginx
# Redirecionar HTTP para HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name app.epallet.com.br motorista.epallet.com.br;
    
    # Redirecionar para HTTPS
    return 301 https://$server_name$request_uri;
}

# Servidor HTTPS Principal
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name app.epallet.com.br motorista.epallet.com.br;
    
    # Certificados SSL (serão configurados depois)
    ssl_certificate /etc/letsencrypt/live/app.epallet.com.br/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/app.epallet.com.br/privkey.pem;
    
    # Configurações SSL
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # Logs
    access_log /var/log/nginx/epallet_access.log;
    error_log /var/log/nginx/epallet_error.log;
    
    # Tamanho máximo de upload
    client_max_body_size 10M;
    
    # Proxy para Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Arquivos estáticos
    location /static {
        alias /home/epallet/flask-argon-system/app/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Favicon
    location /favicon.ico {
        alias /home/epallet/flask-argon-system/app/static/img/favicon.ico;
        access_log off;
        log_not_found off;
    }
}
```

### 2. Ativar Configuração

```bash
# Criar link simbólico
sudo ln -s /etc/nginx/sites-available/epallet /etc/nginx/sites-enabled/

# Remover configuração padrão
sudo rm /etc/nginx/sites-enabled/default

# Testar configuração
sudo nginx -t

# Se OK, recarregar Nginx
sudo systemctl reload nginx
```

---

## 🦄 Configuração do Gunicorn

### 1. Testar Gunicorn Manualmente

```bash
cd /home/epallet/flask-argon-system
source venv/bin/activate

# Testar
gunicorn --bind 127.0.0.1:8000 --workers 4 --timeout 60 run:app

# Se funcionar, pressione Ctrl+C para parar
```

### 2. Criar Arquivo de Configuração

```bash
nano /home/epallet/flask-argon-system/gunicorn_config.py
```

**Conteúdo:**

```python
import multiprocessing

# Bind
bind = "127.0.0.1:8000"

# Workers
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50

# Timeouts
timeout = 60
keepalive = 5
graceful_timeout = 30

# Logging
accesslog = "/home/epallet/flask-argon-system/logs/gunicorn_access.log"
errorlog = "/home/epallet/flask-argon-system/logs/gunicorn_error.log"
loglevel = "info"

# Process naming
proc_name = "epallet_gunicorn"

# Server mechanics
daemon = False
pidfile = "/home/epallet/flask-argon-system/gunicorn.pid"
user = "epallet"
group = "epallet"
```

### 3. Criar Diretório de Logs

```bash
mkdir -p /home/epallet/flask-argon-system/logs
```

---

## 🔄 Configuração do Systemd

### 1. Criar Serviço Systemd

```bash
sudo nano /etc/systemd/system/epallet.service
```

**Conteúdo:**

```ini
[Unit]
Description=Epallet Flask Application
After=network.target

[Service]
Type=notify
User=epallet
Group=epallet
WorkingDirectory=/home/epallet/flask-argon-system
Environment="PATH=/home/epallet/flask-argon-system/venv/bin"
ExecStart=/home/epallet/flask-argon-system/venv/bin/gunicorn \
    --config /home/epallet/flask-argon-system/gunicorn_config.py \
    run:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 2. Ativar e Iniciar Serviço

```bash
# Recarregar systemd
sudo systemctl daemon-reload

# Ativar serviço (iniciar automaticamente no boot)
sudo systemctl enable epallet

# Iniciar serviço
sudo systemctl start epallet

# Verificar status
sudo systemctl status epallet

# Ver logs
sudo journalctl -u epallet -f
```

### 3. Comandos Úteis

```bash
# Parar serviço
sudo systemctl stop epallet

# Reiniciar serviço
sudo systemctl restart epallet

# Recarregar (sem downtime)
sudo systemctl reload epallet

# Ver logs das últimas 100 linhas
sudo journalctl -u epallet -n 100

# Ver logs em tempo real
sudo journalctl -u epallet -f
```

---

## 🔒 Configuração de SSL/HTTPS

### 1. Instalar Certbot

```bash
sudo apt install certbot python3-certbot-nginx -y
```

### 2. Obter Certificado SSL

```bash
# Para ambos os domínios
sudo certbot --nginx -d app.epallet.com.br -d motorista.epallet.com.br

# Seguir instruções:
# - Informar email
# - Aceitar termos
# - Escolher redirecionar HTTP para HTTPS (opção 2)
```

### 3. Testar Renovação Automática

```bash
# Testar renovação (dry-run)
sudo certbot renew --dry-run

# Certbot cria automaticamente um cron job para renovação
```

### 4. Verificar Certificado

```bash
# Ver certificados instalados
sudo certbot certificates

# Testar HTTPS
curl -I https://app.epallet.com.br
```

---

## ✅ Testes e Validação

### 1. Testar Aplicação

```bash
# Verificar se está rodando
curl http://localhost:8000

# Testar via domínio
curl https://app.epallet.com.br
```

### 2. Testar Banco de Dados

```bash
cd /home/epallet/flask-argon-system
source venv/bin/activate
python

# No Python
>>> from app import create_app, db
>>> from app.models import User
>>> app = create_app()
>>> app.app_context().push()
>>> users = User.query.all()
>>> print(f"Total de usuários: {len(users)}")
>>> exit()
```

### 3. Criar Usuário Admin

```bash
cd /home/epallet/flask-argon-system
source venv/bin/activate
python

# No Python
>>> from app import create_app, db
>>> from app.models import User
>>> app = create_app()
>>> app.app_context().push()
>>> admin = User(username='admin', email='admin@epallet.com.br', nome_completo='Administrador', is_admin=True)
>>> admin.set_password('senha-segura-aqui')
>>> db.session.add(admin)
>>> db.session.commit()
>>> print("Usuário admin criado!")
>>> exit()
```

### 4. Testar WhatsApp

```bash
cd /home/epallet/flask-argon-system
source venv/bin/activate
python

# No Python
>>> from app.utils.whatsapp import enviar_whatsapp
>>> resultado = enviar_whatsapp('5511987654321', 'Teste do sistema Epallet')
>>> print(resultado)
>>> exit()
```

---

## 🔧 Manutenção e Monitoramento

### 1. Backup do Banco de Dados

#### SQLite:
```bash
# Backup manual
cp /home/epallet/flask-argon-system/instance/epallet.db /home/epallet/backups/epallet_$(date +%Y%m%d_%H%M%S).db

# Script de backup automático
nano /home/epallet/backup_db.sh
```

**Conteúdo do script:**

```bash
#!/bin/bash
BACKUP_DIR="/home/epallet/backups"
DB_FILE="/home/epallet/flask-argon-system/instance/epallet.db"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
cp $DB_FILE $BACKUP_DIR/epallet_$DATE.db

# Manter apenas últimos 30 backups
ls -t $BACKUP_DIR/epallet_*.db | tail -n +31 | xargs rm -f

echo "Backup realizado: epallet_$DATE.db"
```

```bash
# Tornar executável
chmod +x /home/epallet/backup_db.sh

# Adicionar ao crontab (diário às 3h)
crontab -e

# Adicionar linha:
0 3 * * * /home/epallet/backup_db.sh >> /home/epallet/backup.log 2>&1
```

#### PostgreSQL:
```bash
# Backup manual
pg_dump -U epallet_user epallet_db > /home/epallet/backups/epallet_$(date +%Y%m%d_%H%M%S).sql

# Script automático
nano /home/epallet/backup_pg.sh
```

**Conteúdo:**

```bash
#!/bin/bash
BACKUP_DIR="/home/epallet/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
pg_dump -U epallet_user epallet_db > $BACKUP_DIR/epallet_$DATE.sql

# Comprimir
gzip $BACKUP_DIR/epallet_$DATE.sql

# Manter apenas últimos 30 backups
ls -t $BACKUP_DIR/epallet_*.sql.gz | tail -n +31 | xargs rm -f

echo "Backup realizado: epallet_$DATE.sql.gz"
```

### 2. Monitoramento de Logs

```bash
# Ver logs do Gunicorn
tail -f /home/epallet/flask-argon-system/logs/gunicorn_error.log

# Ver logs do Nginx
sudo tail -f /var/log/nginx/epallet_error.log

# Ver logs do sistema
sudo journalctl -u epallet -f
```

### 3. Atualização da Aplicação

```bash
# Parar serviço
sudo systemctl stop epallet

# Fazer backup
cp -r /home/epallet/flask-argon-system /home/epallet/flask-argon-system_backup_$(date +%Y%m%d)

# Atualizar código (via git ou upload)
cd /home/epallet/flask-argon-system
git pull origin main
# ou
# scp novo-arquivo.zip epallet@servidor:/home/epallet/

# Ativar ambiente virtual
source venv/bin/activate

# Atualizar dependências
pip install -r requirements.txt

# Executar migrations (se houver)
# python migrate_db.py

# Reiniciar serviço
sudo systemctl start epallet

# Verificar status
sudo systemctl status epallet
```

---

## 🐛 Troubleshooting

### Problema 1: Serviço não inicia

```bash
# Ver logs detalhados
sudo journalctl -u epallet -n 100 --no-pager

# Verificar permissões
ls -la /home/epallet/flask-argon-system/

# Testar manualmente
cd /home/epallet/flask-argon-system
source venv/bin/activate
gunicorn --bind 127.0.0.1:8000 run:app
```

### Problema 2: Erro 502 Bad Gateway

```bash
# Verificar se Gunicorn está rodando
sudo systemctl status epallet

# Verificar porta
sudo netstat -tulpn | grep 8000

# Ver logs do Nginx
sudo tail -f /var/log/nginx/epallet_error.log
```

### Problema 3: Banco de dados não conecta

```bash
# Verificar arquivo .env
cat /home/epallet/flask-argon-system/.env | grep DATABASE

# Testar conexão PostgreSQL
psql -U epallet_user -d epallet_db -h localhost

# Verificar permissões SQLite
ls -la /home/epallet/flask-argon-system/instance/
```

### Problema 4: WhatsApp não envia

```bash
# Verificar variáveis de ambiente
cat /home/epallet/flask-argon-system/.env | grep WHATSGW

# Testar API manualmente
cd /home/epallet/flask-argon-system
source venv/bin/activate
python

# No Python
>>> from app.utils.whatsapp import enviar_whatsapp
>>> resultado = enviar_whatsapp('5511987654321', 'Teste')
>>> print(resultado)
```

### Problema 5: Certificado SSL expirado

```bash
# Verificar validade
sudo certbot certificates

# Renovar manualmente
sudo certbot renew

# Reiniciar Nginx
sudo systemctl reload nginx
```

---

## 📊 Checklist de Deploy

- [ ] Servidor Ubuntu atualizado
- [ ] Firewall configurado
- [ ] Python 3.11 instalado
- [ ] Nginx instalado e configurado
- [ ] Projeto transferido para servidor
- [ ] Ambiente virtual criado
- [ ] Dependências instaladas
- [ ] Arquivo .env configurado
- [ ] Banco de dados inicializado
- [ ] Gunicorn testado
- [ ] Serviço systemd criado e ativo
- [ ] Certificado SSL instalado
- [ ] Domínios apontando corretamente
- [ ] Aplicação acessível via HTTPS
- [ ] Usuário admin criado
- [ ] WhatsApp testado
- [ ] Backup automático configurado
- [ ] Logs sendo gerados corretamente

---

## 📞 Suporte

Em caso de dúvidas ou problemas:

1. Verificar logs: `sudo journalctl -u epallet -f`
2. Consultar documentação do projeto
3. Entrar em contato com a equipe de desenvolvimento

---

**Versão:** 18 (Deploy Completo)  
**Data:** 07/11/2024  
**Sistema:** Epallet - Gestão de Pallets
