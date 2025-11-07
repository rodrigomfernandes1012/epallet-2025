# 🐧 Guia de Deploy - Ubuntu/Linux

## 📋 Pré-requisitos

- Ubuntu 20.04 LTS ou superior
- Acesso SSH ao servidor
- Usuário com privilégios sudo
- Domínio apontando para o servidor (opcional, mas recomendado)

---

## 🚀 Deploy Automático (Recomendado)

### Passo 1: Copiar projeto para o servidor

```bash
# No seu computador local
scp flask-argon-system.tar.gz usuario@seu-servidor.com:~

# Ou use Git
ssh usuario@seu-servidor.com
git clone https://github.com/seu-usuario/flask-argon-system.git
cd flask-argon-system
```

### Passo 2: Executar script de deploy

```bash
chmod +x deploy.sh
./deploy.sh
```

O script irá:
- ✅ Atualizar o sistema
- ✅ Instalar Python, PostgreSQL, Nginx
- ✅ Criar ambiente virtual
- ✅ Instalar dependências
- ✅ Configurar PostgreSQL
- ✅ Inicializar banco de dados
- ✅ Criar serviço systemd
- ✅ Configurar inicialização automática

---

## 🔧 Deploy Manual

### 1. Atualizar Sistema

```bash
sudo apt update
sudo apt upgrade -y
```

### 2. Instalar Dependências

```bash
sudo apt install -y python3 python3-pip python3-venv \
    postgresql postgresql-contrib \
    nginx git
```

### 3. Configurar PostgreSQL

```bash
# Acessar PostgreSQL
sudo -u postgres psql

# Criar banco e usuário
CREATE DATABASE flask_argon_db;
CREATE USER flask_user WITH PASSWORD 'senha_segura_aqui';
GRANT ALL PRIVILEGES ON DATABASE flask_argon_db TO flask_user;
\q
```

### 4. Configurar Projeto

```bash
# Navegar para o projeto
cd /home/usuario/flask-argon-system

# Criar ambiente virtual
python3 -m venv venv

# Ativar ambiente virtual
source venv/bin/activate

# Instalar dependências
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn
```

### 5. Configurar Variáveis de Ambiente

Edite o arquivo `.env`:

```bash
nano .env
```

Configuração para produção:

```env
FLASK_ENV=production
SECRET_KEY=gere-uma-chave-forte-e-aleatoria-aqui
DATABASE_URL=postgresql://flask_user:senha_segura_aqui@localhost:5432/flask_argon_db
HOST=127.0.0.1
PORT=8000
```

**Gerar chave secreta:**
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 6. Inicializar Banco de Dados

```bash
python3 init_db.py init
python3 init_db.py create-admin
```

### 7. Testar Aplicação

```bash
python3 run.py
```

Acesse: http://seu-ip:5000

Se funcionar, pressione `Ctrl + C` e continue.

---

## 🔄 Configurar Gunicorn

### 1. Criar arquivo de configuração

```bash
nano gunicorn_config.py
```

Conteúdo:

```python
import multiprocessing

# Endereço e porta
bind = "127.0.0.1:8000"

# Número de workers (2-4 x CPU cores)
workers = multiprocessing.cpu_count() * 2 + 1

# Tipo de worker
worker_class = "sync"

# Timeout
timeout = 120

# Logs
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
loglevel = "info"

# Daemon
daemon = False
```

### 2. Criar diretório de logs

```bash
sudo mkdir -p /var/log/gunicorn
sudo chown -R $USER:$USER /var/log/gunicorn
```

### 3. Testar Gunicorn

```bash
source venv/bin/activate
gunicorn -c gunicorn_config.py run:app
```

---

## 🎯 Configurar Systemd (Serviço)

### 1. Criar arquivo de serviço

```bash
sudo nano /etc/systemd/system/flask-argon.service
```

Conteúdo:

```ini
[Unit]
Description=Flask Argon Dashboard
After=network.target

[Service]
Type=notify
User=usuario
Group=www-data
WorkingDirectory=/home/usuario/flask-argon-system
Environment="PATH=/home/usuario/flask-argon-system/venv/bin"
ExecStart=/home/usuario/flask-argon-system/venv/bin/gunicorn \
    -c gunicorn_config.py \
    run:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

**Importante:** Substitua `usuario` pelo seu usuário do sistema.

### 2. Habilitar e iniciar serviço

```bash
# Recarregar systemd
sudo systemctl daemon-reload

# Habilitar para iniciar no boot
sudo systemctl enable flask-argon

# Iniciar serviço
sudo systemctl start flask-argon

# Verificar status
sudo systemctl status flask-argon
```

### 3. Comandos úteis

```bash
# Ver status
sudo systemctl status flask-argon

# Reiniciar
sudo systemctl restart flask-argon

# Parar
sudo systemctl stop flask-argon

# Ver logs
sudo journalctl -u flask-argon -f
```

---

## 🌐 Configurar Nginx

### 1. Criar configuração do site

```bash
sudo nano /etc/nginx/sites-available/flask-argon
```

Conteúdo:

```nginx
server {
    listen 80;
    server_name seu-dominio.com www.seu-dominio.com;

    # Logs
    access_log /var/log/nginx/flask-argon-access.log;
    error_log /var/log/nginx/flask-argon-error.log;

    # Arquivos estáticos
    location /static {
        alias /home/usuario/flask-argon-system/app/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
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
    }

    # Segurança
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Tamanho máximo de upload
    client_max_body_size 10M;
}
```

### 2. Habilitar site

```bash
# Criar link simbólico
sudo ln -s /etc/nginx/sites-available/flask-argon /etc/nginx/sites-enabled/

# Remover site padrão (opcional)
sudo rm /etc/nginx/sites-enabled/default

# Testar configuração
sudo nginx -t

# Reiniciar Nginx
sudo systemctl restart nginx
```

---

## 🔒 Configurar SSL/TLS (HTTPS)

### Usando Let's Encrypt (Gratuito)

```bash
# Instalar Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obter certificado
sudo certbot --nginx -d seu-dominio.com -d www.seu-dominio.com

# Renovação automática já está configurada
# Testar renovação:
sudo certbot renew --dry-run
```

O Certbot irá:
- ✅ Obter certificado SSL
- ✅ Configurar Nginx automaticamente
- ✅ Redirecionar HTTP para HTTPS
- ✅ Configurar renovação automática

---

## 🔥 Configurar Firewall

```bash
# Habilitar UFW
sudo ufw enable

# Permitir SSH
sudo ufw allow OpenSSH

# Permitir HTTP e HTTPS
sudo ufw allow 'Nginx Full'

# Verificar status
sudo ufw status
```

---

## 📊 Monitoramento

### Ver logs da aplicação

```bash
# Logs do systemd
sudo journalctl -u flask-argon -f

# Logs do Gunicorn
tail -f /var/log/gunicorn/error.log
tail -f /var/log/gunicorn/access.log

# Logs do Nginx
tail -f /var/log/nginx/flask-argon-error.log
tail -f /var/log/nginx/flask-argon-access.log
```

### Monitorar recursos

```bash
# CPU e memória
htop

# Espaço em disco
df -h

# Processos Python
ps aux | grep python
```

---

## 🔄 Atualizar Aplicação

```bash
# Parar serviço
sudo systemctl stop flask-argon

# Navegar para o projeto
cd /home/usuario/flask-argon-system

# Fazer backup do banco (se PostgreSQL)
pg_dump -U flask_user flask_argon_db > backup_$(date +%Y%m%d).sql

# Atualizar código (Git)
git pull origin main

# Ativar ambiente virtual
source venv/bin/activate

# Atualizar dependências
pip install -r requirements.txt

# Aplicar migrações (se houver)
# flask db upgrade

# Reiniciar serviço
sudo systemctl start flask-argon

# Verificar status
sudo systemctl status flask-argon
```

---

## 🗄️ Backup e Restauração

### Backup do Banco de Dados

```bash
# Backup manual
pg_dump -U flask_user flask_argon_db > backup.sql

# Backup automático diário
sudo crontab -e

# Adicionar linha:
0 2 * * * pg_dump -U flask_user flask_argon_db > /home/usuario/backups/db_$(date +\%Y\%m\%d).sql
```

### Restaurar Backup

```bash
# Restaurar banco
psql -U flask_user flask_argon_db < backup.sql
```

---

## 🚨 Solução de Problemas

### Serviço não inicia

```bash
# Ver logs detalhados
sudo journalctl -u flask-argon -n 50 --no-pager

# Verificar permissões
ls -la /home/usuario/flask-argon-system

# Testar manualmente
cd /home/usuario/flask-argon-system
source venv/bin/activate
gunicorn -c gunicorn_config.py run:app
```

### Erro 502 Bad Gateway (Nginx)

```bash
# Verificar se Gunicorn está rodando
sudo systemctl status flask-argon

# Verificar logs do Nginx
sudo tail -f /var/log/nginx/flask-argon-error.log

# Reiniciar serviços
sudo systemctl restart flask-argon
sudo systemctl restart nginx
```

### Erro de conexão com PostgreSQL

```bash
# Verificar se PostgreSQL está rodando
sudo systemctl status postgresql

# Testar conexão
psql -U flask_user -d flask_argon_db -h localhost

# Verificar .env
cat .env | grep DATABASE_URL
```

### Permissões de arquivo

```bash
# Ajustar permissões
sudo chown -R usuario:www-data /home/usuario/flask-argon-system
sudo chmod -R 755 /home/usuario/flask-argon-system
```

---

## ✅ Checklist de Deploy

- [ ] Servidor Ubuntu atualizado
- [ ] Python 3.11+ instalado
- [ ] PostgreSQL instalado e configurado
- [ ] Nginx instalado
- [ ] Projeto copiado para o servidor
- [ ] Ambiente virtual criado
- [ ] Dependências instaladas
- [ ] `.env` configurado para produção
- [ ] Banco de dados inicializado
- [ ] Usuário admin criado
- [ ] Serviço systemd configurado
- [ ] Nginx configurado
- [ ] SSL/TLS configurado (Let's Encrypt)
- [ ] Firewall configurado
- [ ] Backup automático configurado
- [ ] Aplicação acessível via domínio

---

## 📈 Otimizações de Produção

### 1. Configurar cache de arquivos estáticos

No Nginx:
```nginx
location /static {
    alias /home/usuario/flask-argon-system/app/static;
    expires 30d;
    add_header Cache-Control "public, immutable";
}
```

### 2. Compressão Gzip

No Nginx:
```nginx
gzip on;
gzip_vary on;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
```

### 3. Limitar taxa de requisições

No Nginx:
```nginx
limit_req_zone $binary_remote_addr zone=one:10m rate=10r/s;

location / {
    limit_req zone=one burst=20;
    # ... resto da configuração
}
```

---

## 📞 Suporte

Para problemas específicos do Ubuntu:
- Documentação do Ubuntu: https://help.ubuntu.com/
- Documentação do Nginx: https://nginx.org/en/docs/
- Documentação do PostgreSQL: https://www.postgresql.org/docs/

---

**Sistema pronto para produção no Ubuntu! 🚀**
