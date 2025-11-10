# 🚀 Deploy Completo no Ubuntu - Usuário Root

## 📋 Guia de Deploy para Produção

**Configuração:**
- **Usuário:** root
- **Pasta do Projeto:** /root/epallet-2025
- **Servidor:** Ubuntu 20.04+ ou 22.04+
- **Python:** 3.11
- **Servidor Web:** Nginx
- **WSGI:** Gunicorn
- **Gerenciador:** Systemd

---

## 📌 Pré-requisitos

- Servidor Ubuntu com acesso root
- Domínio configurado (ex: epallet.com.br)
- Subdomínio para motorista (ex: motorista.epallet.com.br)
- Credenciais WhatsGw API

---

## 1️⃣ Preparação do Servidor

### Atualizar Sistema

```bash
# Atualizar pacotes
apt update && apt upgrade -y

# Instalar ferramentas essenciais
apt install -y build-essential git curl wget vim nano software-properties-common
```

### Configurar Firewall

```bash
# Instalar UFW
apt install -y ufw

# Permitir SSH
ufw allow 22/tcp

# Permitir HTTP e HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Ativar firewall
ufw --force enable

# Verificar status
ufw status
```

---

## 2️⃣ Instalação de Dependências

### Instalar Python 3.11

```bash
# Adicionar repositório
add-apt-repository ppa:deadsnakes/ppa -y
apt update

# Instalar Python 3.11
apt install -y python3.11 python3.11-venv python3.11-dev

# Verificar instalação
python3.11 --version
```

### Instalar Nginx

```bash
# Instalar Nginx
apt install -y nginx

# Iniciar e habilitar
systemctl start nginx
systemctl enable nginx

# Verificar status
systemctl status nginx
```

### Instalar Ferramentas Adicionais

```bash
# Instalar pip
apt install -y python3-pip

# Instalar supervisor (opcional)
apt install -y supervisor

# Instalar certbot para SSL
apt install -y certbot python3-certbot-nginx
```

---

## 3️⃣ Configuração do Projeto

### Transferir Projeto para Servidor

**Opção 1: Via SCP (do seu computador)**

```bash
# No seu computador Windows/Linux
scp flask-argon-system-v20.zip root@seu-servidor:/root/
```

**Opção 2: Via Git**

```bash
cd /root
git clone https://seu-repositorio.git epallet-2025
```

**Opção 3: Upload Manual**

```bash
# Fazer upload via SFTP para /root/
# Depois extrair
cd /root
unzip flask-argon-system-v20.zip
mv flask-argon-system epallet-2025
```

### Configurar Ambiente Virtual

```bash
cd /root/epallet-2025

# Criar ambiente virtual
python3.11 -m venv venv

# Ativar ambiente virtual
source venv/bin/activate

# Atualizar pip
pip install --upgrade pip

# Instalar dependências
pip install -r requirements.txt

# Instalar Gunicorn
pip install gunicorn
```

### Criar Diretórios Necessários

```bash
cd /root/epallet-2025

# Criar diretórios
mkdir -p instance
mkdir -p logs
mkdir -p static/uploads

# Dar permissões
chmod 755 instance
chmod 755 logs
chmod 755 static/uploads
```

---

## 4️⃣ Configuração do Banco de Dados

### Opção 1: SQLite (Recomendado para Início)

#### 1. Configurar .env

```bash
cd /root/epallet-2025
nano .env
```

**Conteúdo do .env:**

```bash
# Flask
FLASK_APP=run.py
FLASK_ENV=production
SECRET_KEY=gere-uma-chave-secreta-aqui-use-comando-abaixo

# Banco de Dados (CAMINHO ABSOLUTO)
DATABASE_URL=sqlite:////root/epallet-2025/instance/epallet.db

# WhatsGw API
WHATSGW_APIKEY=sua-api-key-aqui
WHATSGW_PHONE_NUMBER=5511987654321

# Configurações
DEBUG=False
TESTING=False
```

**Gerar SECRET_KEY:**

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

#### 2. Inicializar Banco

```bash
cd /root/epallet-2025
source venv/bin/activate

# Inicializar banco de dados (criar tabelas)
python init_db.py init

# Criar usuário administrador
python init_db.py create-admin
```

**Nota:** O script `init_db.py` requer um comando:
- `init` - Cria as tabelas do banco
- `create-admin` - Cria usuário administrador
- `reset` - Apaga e recria tudo (cuidado!)

#### 3. Verificar Criação

```bash
ls -la instance/
```

**Deve mostrar:**
```
-rw-r--r-- 1 root root 98304 Nov  7 15:30 epallet.db
```

### Opção 2: PostgreSQL (Produção de Grande Porte)

#### 1. Instalar PostgreSQL

```bash
apt install -y postgresql postgresql-contrib

# Verificar status
systemctl status postgresql
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
cd /root/epallet-2025
source venv/bin/activate
pip install psycopg2-binary
```

#### 4. Atualizar .env

```bash
DATABASE_URL=postgresql://epallet_user:senha-super-segura@localhost/epallet_db
```

#### 5. Inicializar Banco

```bash
# Inicializar banco de dados
python init_db.py init

# Criar usuário administrador
python init_db.py create-admin
```

---

## 5️⃣ Configuração do Nginx

### 1. Criar Arquivo de Configuração

```bash
nano /etc/nginx/sites-available/epallet
```

**Conteúdo:**

```nginx
# Configuração para epallet.com.br
server {
    listen 80;
    server_name epallet.com.br www.epallet.com.br;

    # Logs
    access_log /var/log/nginx/epallet_access.log;
    error_log /var/log/nginx/epallet_error.log;

    # Arquivos estáticos
    location /static {
        alias /root/epallet-2025/app/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Uploads
    location /uploads {
        alias /root/epallet-2025/static/uploads;
        expires 30d;
    }

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
        
        # Buffers
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }

    # Tamanho máximo de upload
    client_max_body_size 50M;
}

# Configuração para motorista.epallet.com.br
server {
    listen 80;
    server_name motorista.epallet.com.br;

    # Logs
    access_log /var/log/nginx/motorista_access.log;
    error_log /var/log/nginx/motorista_error.log;

    # Arquivos estáticos
    location /static {
        alias /root/epallet-2025/app/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Proxy para Gunicorn (mesma aplicação)
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    client_max_body_size 50M;
}
```

### 2. Ativar Configuração

```bash
# Criar link simbólico
ln -s /etc/nginx/sites-available/epallet /etc/nginx/sites-enabled/

# Remover configuração padrão
rm /etc/nginx/sites-enabled/default

# Testar configuração
nginx -t

# Recarregar Nginx
systemctl reload nginx
```

---

## 6️⃣ Configuração do Gunicorn

### 1. Verificar gunicorn_config.py

O arquivo já está configurado no projeto. Verificar:

```bash
cat /root/epallet-2025/gunicorn_config.py
```

**Deve conter:**

```python
import multiprocessing
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

bind = "127.0.0.1:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
timeout = 120
graceful_timeout = 30
max_requests = 1000
max_requests_jitter = 50

accesslog = os.path.join(BASE_DIR, "logs", "gunicorn_access.log")
errorlog = os.path.join(BASE_DIR, "logs", "gunicorn_error.log")
loglevel = "info"

daemon = False
pidfile = os.path.join(BASE_DIR, "gunicorn.pid")
preload_app = True
chdir = BASE_DIR
```

### 2. Testar Gunicorn Manualmente

```bash
cd /root/epallet-2025
source venv/bin/activate
gunicorn --config gunicorn_config.py run:app
```

**Deve iniciar sem erros!**

Pressione `Ctrl+C` para parar.

---

## 7️⃣ Configuração do Systemd

### 1. Criar Arquivo de Serviço

```bash
nano /etc/systemd/system/epallet.service
```

**Conteúdo:**

```ini
[Unit]
Description=Epallet Flask Application
After=network.target

[Service]
Type=notify
User=root
Group=root
WorkingDirectory=/root/epallet-2025
Environment="PATH=/root/epallet-2025/venv/bin"
Environment="LANG=pt_BR.UTF-8"
Environment="LC_ALL=pt_BR.UTF-8"

ExecStart=/root/epallet-2025/venv/bin/gunicorn \
    --config /root/epallet-2025/gunicorn_config.py \
    run:app

ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=10

# Logs
StandardOutput=journal
StandardError=journal
SyslogIdentifier=epallet

[Install]
WantedBy=multi-user.target
```

### 2. Ativar e Iniciar Serviço

```bash
# Recarregar systemd
systemctl daemon-reload

# Ativar serviço (iniciar no boot)
systemctl enable epallet

# Iniciar serviço
systemctl start epallet

# Verificar status
systemctl status epallet
```

**Deve mostrar:**
```
● epallet.service - Epallet Flask Application
   Loaded: loaded (/etc/systemd/system/epallet.service; enabled)
   Active: active (running) since ...
```

### 3. Comandos Úteis

```bash
# Parar serviço
systemctl stop epallet

# Reiniciar serviço
systemctl restart epallet

# Ver logs
journalctl -u epallet -f

# Ver logs das últimas 100 linhas
journalctl -u epallet -n 100

# Ver logs de hoje
journalctl -u epallet --since today
```

---

## 8️⃣ Configuração de SSL/HTTPS

### 1. Instalar Certbot

```bash
apt install -y certbot python3-certbot-nginx
```

### 2. Obter Certificado SSL

```bash
# Para epallet.com.br e motorista.epallet.com.br
certbot --nginx -d epallet.com.br -d www.epallet.com.br -d motorista.epallet.com.br
```

**Seguir prompts:**
- Informar email
- Aceitar termos
- Escolher opção 2 (redirecionar HTTP para HTTPS)

### 3. Renovação Automática

```bash
# Testar renovação
certbot renew --dry-run

# Adicionar cron job para renovação automática
crontab -e
```

**Adicionar linha:**
```
0 3 * * * certbot renew --quiet --post-hook "systemctl reload nginx"
```

### 4. Verificar Configuração

```bash
# Verificar certificado
certbot certificates

# Testar HTTPS
curl -I https://epallet.com.br
```

---

## 9️⃣ Testes e Validação

### 1. Testar Aplicação

```bash
# Verificar se Gunicorn está rodando
systemctl status epallet

# Verificar se Nginx está rodando
systemctl status nginx

# Testar localmente
curl http://127.0.0.1:8000

# Testar via Nginx
curl http://localhost

# Testar via domínio
curl http://epallet.com.br
```

### 2. Testar Rotas Públicas

```bash
# Testar confirmação de recebimento
curl http://epallet.com.br/publico/confirmacao-recebimento

# Testar validação de PIN
curl http://motorista.epallet.com.br/publico/validacao-pin
```

### 3. Verificar Logs

```bash
# Logs do Gunicorn
tail -f /root/epallet-2025/logs/gunicorn_error.log

# Logs do Nginx
tail -f /var/log/nginx/epallet_error.log

# Logs do systemd
journalctl -u epallet -f
```

---

## 🔟 Manutenção e Monitoramento

### Backup do Banco de Dados

#### SQLite

```bash
# Criar script de backup
nano /root/backup_epallet.sh
```

**Conteúdo:**

```bash
#!/bin/bash

# Diretórios
BACKUP_DIR="/root/backups"
DB_FILE="/root/epallet-2025/instance/epallet.db"
DATE=$(date +%Y%m%d_%H%M%S)

# Criar diretório de backup
mkdir -p $BACKUP_DIR

# Fazer backup
cp $DB_FILE $BACKUP_DIR/epallet_$DATE.db

# Manter apenas últimos 30 backups
ls -t $BACKUP_DIR/epallet_*.db | tail -n +31 | xargs -r rm

echo "Backup concluído: epallet_$DATE.db"
```

**Dar permissão e agendar:**

```bash
# Dar permissão
chmod +x /root/backup_epallet.sh

# Testar
/root/backup_epallet.sh

# Agendar backup diário às 3h
crontab -e
```

**Adicionar:**
```
0 3 * * * /root/backup_epallet.sh >> /root/backup.log 2>&1
```

#### PostgreSQL

```bash
# Criar script de backup
nano /root/backup_epallet_pg.sh
```

**Conteúdo:**

```bash
#!/bin/bash

BACKUP_DIR="/root/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="epallet_db"
DB_USER="epallet_user"

mkdir -p $BACKUP_DIR

# Backup
PGPASSWORD="senha-super-segura" pg_dump -U $DB_USER $DB_NAME > $BACKUP_DIR/epallet_$DATE.sql

# Comprimir
gzip $BACKUP_DIR/epallet_$DATE.sql

# Manter últimos 30
ls -t $BACKUP_DIR/epallet_*.sql.gz | tail -n +31 | xargs -r rm

echo "Backup concluído: epallet_$DATE.sql.gz"
```

### Monitoramento de Logs

```bash
# Ver logs em tempo real
journalctl -u epallet -f

# Ver erros do Nginx
tail -f /var/log/nginx/epallet_error.log

# Ver erros do Gunicorn
tail -f /root/epallet-2025/logs/gunicorn_error.log
```

### Atualizar Aplicação

```bash
# Parar serviço
systemctl stop epallet

# Fazer backup
/root/backup_epallet.sh

# Atualizar código
cd /root/epallet-2025
# (copiar novos arquivos ou git pull)

# Ativar venv
source venv/bin/activate

# Atualizar dependências (se necessário)
pip install -r requirements.txt

# Reiniciar serviço
systemctl start epallet

# Verificar status
systemctl status epallet
```

---

## 🔧 Troubleshooting

### Problema 1: Gunicorn não inicia

```bash
# Ver logs detalhados
journalctl -u epallet -n 100

# Testar manualmente
cd /root/epallet-2025
source venv/bin/activate
gunicorn --config gunicorn_config.py run:app
```

### Problema 2: Erro 502 Bad Gateway

```bash
# Verificar se Gunicorn está rodando
systemctl status epallet

# Verificar se está escutando na porta 8000
netstat -tlnp | grep 8000

# Reiniciar serviços
systemctl restart epallet
systemctl restart nginx
```

### Problema 3: Erro de Permissão no Banco

```bash
# Verificar permissões
ls -la /root/epallet-2025/instance/

# Dar permissões
chmod 755 /root/epallet-2025/instance
chmod 644 /root/epallet-2025/instance/epallet.db
```

### Problema 4: WhatsApp não envia

```bash
# Verificar .env
cat /root/epallet-2025/.env | grep WHATSGW

# Ver logs
tail -f /root/epallet-2025/logs/gunicorn_error.log | grep -i whatsapp
```

### Problema 5: SSL não funciona

```bash
# Verificar certificados
certbot certificates

# Renovar manualmente
certbot renew

# Verificar configuração Nginx
nginx -t

# Recarregar Nginx
systemctl reload nginx
```

---

## ✅ Checklist Final

### Servidor
- [ ] Ubuntu atualizado
- [ ] Firewall configurado (UFW)
- [ ] Python 3.11 instalado
- [ ] Nginx instalado e rodando

### Projeto
- [ ] Projeto em /root/epallet-2025
- [ ] Ambiente virtual criado
- [ ] Dependências instaladas
- [ ] Diretórios criados (instance, logs)

### Banco de Dados
- [ ] .env configurado com caminho absoluto
- [ ] Banco inicializado
- [ ] Dados de teste criados

### Gunicorn
- [ ] gunicorn_config.py configurado
- [ ] Testado manualmente
- [ ] Logs funcionando

### Systemd
- [ ] Serviço criado
- [ ] Serviço habilitado
- [ ] Serviço rodando

### Nginx
- [ ] Configuração criada
- [ ] Sites habilitados
- [ ] Nginx recarregado
- [ ] Testes HTTP funcionando

### SSL
- [ ] Certbot instalado
- [ ] Certificados obtidos
- [ ] HTTPS funcionando
- [ ] Renovação automática configurada

### Backup
- [ ] Script de backup criado
- [ ] Backup agendado no cron
- [ ] Testado manualmente

### Testes
- [ ] Aplicação acessível via HTTP
- [ ] Aplicação acessível via HTTPS
- [ ] Rotas públicas funcionando
- [ ] WhatsApp funcionando
- [ ] Logs sendo gerados

---

## 📞 Comandos Rápidos

```bash
# Ver status de tudo
systemctl status epallet nginx

# Reiniciar tudo
systemctl restart epallet nginx

# Ver logs em tempo real
journalctl -u epallet -f

# Fazer backup
/root/backup_epallet.sh

# Atualizar SSL
certbot renew

# Verificar portas
netstat -tlnp | grep -E '80|443|8000'
```

---

## 🎯 Estrutura Final

```
/root/epallet-2025/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes/
│   ├── templates/
│   ├── static/
│   └── utils/
├── config/
├── instance/
│   └── epallet.db
├── logs/
│   ├── gunicorn_access.log
│   └── gunicorn_error.log
├── venv/
├── .env
├── gunicorn_config.py
├── requirements.txt
└── run.py

/root/backups/
├── epallet_20241107_030000.db
├── epallet_20241106_030000.db
└── ...
```

---

**Versão:** 21 (Deploy Root)  
**Data:** 07/11/2024  
**Sistema:** Epallet - Gestão de Pallets  
**Configuração:** root + /root/epallet-2025
