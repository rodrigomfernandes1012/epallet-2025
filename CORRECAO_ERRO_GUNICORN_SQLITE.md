# 🔧 Correção - Erro Gunicorn com SQLite

## ❌ Erro Encontrado

```
sqlite3.OperationalError: unable to open database file
```

## 🔍 Causa do Problema

O Gunicorn não consegue criar ou acessar o arquivo do banco de dados SQLite porque:

1. **Diretório `instance/` não existe** ou não tem permissões adequadas
2. **Usuário incorreto** - Rodando como `root` mas o systemd vai rodar como usuário `epallet`
3. **Caminho relativo** - SQLite precisa de caminho absoluto em produção

---

## ✅ Solução Rápida (Para Testar Agora)

### 1. Criar Diretório e Dar Permissões

```bash
# Criar diretório instance
cd /root/epallet-2025
mkdir -p instance

# Dar permissões de escrita
chmod 755 instance

# Criar banco de dados
python init_db.py

# Verificar se foi criado
ls -la instance/
```

### 2. Testar Gunicorn Novamente

```bash
# Ativar ambiente virtual
source venv/bin/activate

# Testar Gunicorn
gunicorn --bind 127.0.0.1:8000 --workers 4 --timeout 60 run:app
```

**Deve funcionar agora!**

---

## 🎯 Solução Definitiva (Para Produção)

### Problema: Rodando como Root

Você está em `/root/epallet-2025` e rodando como `root`. Isso **não é recomendado** para produção.

### Solução Recomendada

#### 1. Criar Usuário Dedicado

```bash
# Criar usuário epallet
sudo adduser epallet

# Definir senha
# (seguir prompts)
```

#### 2. Mover Projeto para Usuário Epallet

```bash
# Copiar projeto para home do usuário epallet
sudo cp -r /root/epallet-2025 /home/epallet/flask-argon-system

# Dar permissões ao usuário epallet
sudo chown -R epallet:epallet /home/epallet/flask-argon-system

# Trocar para usuário epallet
su - epallet
```

#### 3. Configurar Projeto como Usuário Epallet

```bash
cd /home/epallet/flask-argon-system

# Criar ambiente virtual
python3.11 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Criar diretório instance
mkdir -p instance

# Inicializar banco
python init_db.py

# Testar Gunicorn
gunicorn --bind 127.0.0.1:8000 --workers 4 --timeout 60 run:app
```

---

## 📝 Alternativa: Usar Caminho Absoluto no .env

Se quiser continuar usando `/root/epallet-2025`, edite o `.env`:

### Antes (caminho relativo):
```bash
DATABASE_URL=sqlite:///instance/epallet.db
```

### Depois (caminho absoluto):
```bash
DATABASE_URL=sqlite:////root/epallet-2025/instance/epallet.db
```

**Nota:** São **4 barras** (`////`) - 3 do protocolo + 1 do caminho absoluto.

---

## 🔧 Configuração do Gunicorn para Produção

### Atualizar `gunicorn_config.py`

```python
import multiprocessing
import os

# Caminho base do projeto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

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
accesslog = os.path.join(BASE_DIR, "logs", "gunicorn_access.log")
errorlog = os.path.join(BASE_DIR, "logs", "gunicorn_error.log")
loglevel = "info"

# Process naming
proc_name = "epallet_gunicorn"

# Server mechanics
daemon = False
pidfile = os.path.join(BASE_DIR, "gunicorn.pid")

# Usuário e grupo (comentar se rodar como root)
# user = "epallet"
# group = "epallet"

# Preload app (melhora performance)
preload_app = True

# Chdir para diretório do projeto
chdir = BASE_DIR
```

---

## 🚀 Passo a Passo Completo (Recomendado)

### 1. Preparar Ambiente

```bash
# Como root
cd /root

# Criar usuário epallet
sudo adduser epallet

# Copiar projeto
sudo cp -r /root/epallet-2025 /home/epallet/flask-argon-system

# Dar permissões
sudo chown -R epallet:epallet /home/epallet/flask-argon-system
```

### 2. Configurar como Usuário Epallet

```bash
# Trocar para usuário epallet
su - epallet

# Ir para projeto
cd /home/epallet/flask-argon-system

# Criar ambiente virtual
python3.11 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Criar diretórios necessários
mkdir -p instance
mkdir -p logs

# Copiar .env de exemplo
cp .env.example .env

# Editar .env
nano .env
```

### 3. Configurar .env

```bash
# Flask
FLASK_APP=run.py
FLASK_ENV=production
SECRET_KEY=sua-chave-secreta-aqui

# Banco de Dados (caminho absoluto)
DATABASE_URL=sqlite:////home/epallet/flask-argon-system/instance/epallet.db

# WhatsGw API
WHATSGW_APIKEY=sua-api-key-aqui
WHATSGW_PHONE_NUMBER=5511987654321

# Configurações
DEBUG=False
TESTING=False
```

### 4. Inicializar Banco

```bash
python init_db.py
```

### 5. Testar Gunicorn

```bash
gunicorn --bind 127.0.0.1:8000 --workers 4 --timeout 60 run:app
```

### 6. Configurar Systemd

```bash
# Voltar para root
exit

# Criar serviço
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

### 7. Ativar Serviço

```bash
# Recarregar systemd
sudo systemctl daemon-reload

# Ativar serviço
sudo systemctl enable epallet

# Iniciar serviço
sudo systemctl start epallet

# Verificar status
sudo systemctl status epallet
```

---

## 🔍 Verificações

### Verificar Permissões

```bash
ls -la /home/epallet/flask-argon-system/instance/
```

**Deve mostrar:**
```
drwxr-xr-x 2 epallet epallet 4096 Nov  7 15:30 .
-rw-r--r-- 1 epallet epallet 98304 Nov  7 15:30 epallet.db
```

### Verificar Banco de Dados

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

### Verificar Logs do Gunicorn

```bash
tail -f /home/epallet/flask-argon-system/logs/gunicorn_error.log
```

---

## 📊 Checklist de Correção

- [ ] Diretório `instance/` criado
- [ ] Permissões corretas no diretório
- [ ] Banco de dados inicializado
- [ ] `.env` configurado com caminho correto
- [ ] Gunicorn testado manualmente
- [ ] Usuário `epallet` criado (produção)
- [ ] Projeto movido para `/home/epallet/`
- [ ] Permissões ajustadas
- [ ] Serviço systemd configurado
- [ ] Serviço iniciado e funcionando

---

## 🐛 Troubleshooting

### Erro persiste após criar diretório

```bash
# Verificar se o diretório existe
ls -la instance/

# Verificar permissões
stat instance/

# Dar permissões completas (temporário para teste)
chmod 777 instance/

# Testar novamente
gunicorn --bind 127.0.0.1:8000 --workers 1 --timeout 60 run:app
```

### Erro "Permission denied"

```bash
# Verificar quem é o dono
ls -la instance/

# Mudar dono para usuário atual
sudo chown -R $USER:$USER instance/

# Ou para usuário epallet
sudo chown -R epallet:epallet instance/
```

### Banco não é criado

```bash
# Executar init_db.py manualmente
python init_db.py

# Se der erro, verificar .env
cat .env | grep DATABASE

# Testar conexão
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all(); print('OK')"
```

---

## 💡 Dicas

### 1. Use Caminho Absoluto em Produção

Sempre use caminho absoluto no `.env` para evitar problemas:

```bash
DATABASE_URL=sqlite:////home/epallet/flask-argon-system/instance/epallet.db
```

### 2. Não Rode como Root

Criar usuário dedicado é mais seguro:
- Isola a aplicação
- Limita danos em caso de invasão
- Segue boas práticas de segurança

### 3. Verifique Logs

Sempre verifique os logs para identificar problemas:

```bash
# Logs do Gunicorn
tail -f logs/gunicorn_error.log

# Logs do systemd
sudo journalctl -u epallet -f
```

### 4. Teste Antes de Configurar Systemd

Sempre teste o Gunicorn manualmente antes de criar o serviço:

```bash
gunicorn --bind 127.0.0.1:8000 --workers 1 --timeout 60 run:app
```

---

## 📞 Suporte

Se o erro persistir:

1. Verificar logs: `tail -f logs/gunicorn_error.log`
2. Verificar permissões: `ls -la instance/`
3. Verificar .env: `cat .env | grep DATABASE`
4. Testar conexão: `python init_db.py`

---

**Versão:** 20 (Correção Gunicorn SQLite)  
**Data:** 07/11/2024  
**Sistema:** Epallet - Gestão de Pallets
