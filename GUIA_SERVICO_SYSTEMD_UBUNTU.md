# 🚀 Guia Completo: Configurar Epallet como Serviço no Ubuntu

## 📋 O Que Vamos Fazer

Configurar o projeto Epallet para rodar como **serviço systemd** no Ubuntu, garantindo:

✅ Inicia automaticamente quando o servidor reinicia  
✅ Reinicia automaticamente se travar  
✅ Gerenciamento fácil com comandos systemctl  
✅ Logs centralizados no journalctl  
✅ Execução em background  

---

## 🎯 Passo a Passo Completo

### Passo 1: Criar Arquivo de Serviço

```bash
sudo nano /etc/systemd/system/epallet.service
```

**Copiar e colar este conteúdo:**

```ini
[Unit]
Description=Epallet Flask Application - Sistema de Gestão de Pallets
Documentation=https://github.com/seu-usuario/epallet
After=network.target mysql.service
Wants=mysql.service

[Service]
Type=notify
User=root
Group=root
WorkingDirectory=/root/epallet-2025
Environment="PATH=/root/epallet-2025/venv/bin"
Environment="LANG=pt_BR.UTF-8"
Environment="LC_ALL=pt_BR.UTF-8"

# Comando para iniciar a aplicação
ExecStart=/root/epallet-2025/venv/bin/gunicorn \
    --config /root/epallet-2025/gunicorn_config.py \
    run:app

# Comando para recarregar (reload graceful)
ExecReload=/bin/kill -s HUP $MAINPID

# Configurações de processo
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

# Reiniciar automaticamente
Restart=always
RestartSec=10

# Logs
StandardOutput=journal
StandardError=journal
SyslogIdentifier=epallet

[Install]
WantedBy=multi-user.target
```

**Salvar:** `Ctrl+O`, `Enter`, `Ctrl+X`

---

### Passo 2: Recarregar Systemd

```bash
sudo systemctl daemon-reload
```

**Isso carrega o novo arquivo de serviço.**

---

### Passo 3: Habilitar Auto-Start

```bash
sudo systemctl enable epallet
```

**Saída esperada:**
```
Created symlink /etc/systemd/system/multi-user.target.wants/epallet.service → /etc/systemd/system/epallet.service.
```

✅ Agora o serviço inicia automaticamente no boot!

---

### Passo 4: Iniciar o Serviço

```bash
sudo systemctl start epallet
```

---

### Passo 5: Verificar Status

```bash
sudo systemctl status epallet
```

**Saída esperada:**

```
● epallet.service - Epallet Flask Application - Sistema de Gestão de Pallets
     Loaded: loaded (/etc/systemd/system/epallet.service; enabled; vendor preset: enabled)
     Active: active (running) since Sun 2024-11-10 18:30:00 -03; 5s ago
   Main PID: 12345 (gunicorn)
      Tasks: 5 (limit: 4915)
     Memory: 120.0M
        CPU: 2.5s
     CGroup: /system.slice/epallet.service
             ├─12345 /root/epallet-2025/venv/bin/python3 /root/epallet-2025/venv/bin/gunicorn...
             ├─12346 /root/epallet-2025/venv/bin/python3 /root/epallet-2025/venv/bin/gunicorn...
             ├─12347 /root/epallet-2025/venv/bin/python3 /root/epallet-2025/venv/bin/gunicorn...
             └─12348 /root/epallet-2025/venv/bin/python3 /root/epallet-2025/venv/bin/gunicorn...

Nov 10 18:30:00 servidor systemd[1]: Started Epallet Flask Application.
Nov 10 18:30:01 servidor gunicorn[12345]: [INFO] Starting gunicorn 21.2.0
Nov 10 18:30:01 servidor gunicorn[12345]: [INFO] Listening at: http://127.0.0.1:8000
Nov 10 18:30:01 servidor gunicorn[12345]: [INFO] Using worker: sync
Nov 10 18:30:01 servidor gunicorn[12346]: [INFO] Booting worker with pid: 12346
```

✅ **Status:** `active (running)` - Tudo funcionando!

---

## 📞 Comandos de Gerenciamento

### Comandos Básicos

```bash
# Iniciar serviço
sudo systemctl start epallet

# Parar serviço
sudo systemctl stop epallet

# Reiniciar serviço
sudo systemctl restart epallet

# Recarregar configuração (sem downtime)
sudo systemctl reload epallet

# Ver status
sudo systemctl status epallet

# Habilitar auto-start
sudo systemctl enable epallet

# Desabilitar auto-start
sudo systemctl disable epallet
```

### Ver Logs

```bash
# Ver últimas 50 linhas
sudo journalctl -u epallet -n 50

# Ver logs em tempo real
sudo journalctl -u epallet -f

# Ver logs de hoje
sudo journalctl -u epallet --since today

# Ver logs com prioridade (erros)
sudo journalctl -u epallet -p err

# Ver logs entre datas
sudo journalctl -u epallet --since "2024-11-10 00:00:00" --until "2024-11-10 23:59:59"
```

### Verificar se Está Rodando

```bash
# Método 1: systemctl
sudo systemctl is-active epallet

# Método 2: ps
ps aux | grep gunicorn

# Método 3: netstat
sudo netstat -tlnp | grep 8000

# Método 4: curl
curl http://127.0.0.1:8000
```

---

## 🔧 Configuração Avançada

### Arquivo gunicorn_config.py

Certifique-se de que existe em `/root/epallet-2025/gunicorn_config.py`:

```python
import multiprocessing
import os

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
graceful_timeout = 30
keepalive = 5

# Logging
accesslog = "/root/epallet-2025/logs/gunicorn_access.log"
errorlog = "/root/epallet-2025/logs/gunicorn_error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "epallet"

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (se necessário)
# keyfile = "/path/to/key.pem"
# certfile = "/path/to/cert.pem"
```

### Criar Diretório de Logs

```bash
mkdir -p /root/epallet-2025/logs
chmod 755 /root/epallet-2025/logs
```

---

## 🧪 Testar Configuração

### 1. Testar Gunicorn Manualmente

```bash
cd /root/epallet-2025
source venv/bin/activate
gunicorn --config gunicorn_config.py run:app
```

**Pressionar `Ctrl+C` para parar.**

Se funcionar, o serviço também vai funcionar!

### 2. Testar Serviço

```bash
# Parar
sudo systemctl stop epallet

# Iniciar
sudo systemctl start epallet

# Ver status
sudo systemctl status epallet

# Ver logs
sudo journalctl -u epallet -n 20
```

### 3. Testar Auto-Restart

```bash
# Pegar PID do processo
sudo systemctl status epallet | grep "Main PID"

# Matar processo (simular crash)
sudo kill -9 <PID>

# Aguardar 10 segundos e verificar
sleep 10
sudo systemctl status epallet
```

**Deve reiniciar automaticamente!** ✅

### 4. Testar Reboot

```bash
# Reiniciar servidor
sudo reboot

# Após reiniciar, verificar
sudo systemctl status epallet
```

**Deve estar rodando automaticamente!** ✅

---

## 🔍 Troubleshooting

### Erro: "Failed to start epallet.service"

**Ver detalhes:**
```bash
sudo journalctl -u epallet -n 50
```

**Causas comuns:**
1. Caminho errado no WorkingDirectory
2. Gunicorn não instalado no venv
3. Erro no arquivo run.py
4. Banco de dados inacessível

**Solução:**
```bash
# Testar manualmente
cd /root/epallet-2025
source venv/bin/activate
python run.py
```

### Erro: "Connection refused"

**Verificar se está rodando:**
```bash
sudo systemctl status epallet
sudo netstat -tlnp | grep 8000
```

**Verificar logs:**
```bash
sudo journalctl -u epallet -n 50
```

### Erro: "Access denied" (MySQL)

**Verificar .env:**
```bash
cat /root/epallet-2025/.env | grep DATABASE_URL
```

**Deve ser:**
```
DATABASE_URL=mysql://epallet:Rodrigo%40101275@localhost:3306/epallet_db
```

### Serviço Não Inicia no Boot

**Verificar se está habilitado:**
```bash
sudo systemctl is-enabled epallet
```

**Se não estiver, habilitar:**
```bash
sudo systemctl enable epallet
```

---

## 📊 Monitoramento

### Ver Uso de Recursos

```bash
# CPU e Memória
sudo systemctl status epallet

# Detalhado
sudo ps aux | grep gunicorn

# Top
sudo top -p $(pgrep -d',' -f gunicorn)
```

### Ver Conexões Ativas

```bash
sudo netstat -an | grep 8000 | grep ESTABLISHED | wc -l
```

### Ver Logs de Acesso

```bash
tail -f /root/epallet-2025/logs/gunicorn_access.log
```

### Ver Logs de Erro

```bash
tail -f /root/epallet-2025/logs/gunicorn_error.log
```

---

## 🔄 Atualizar Aplicação

Quando fizer alterações no código:

```bash
# 1. Ir para o diretório
cd /root/epallet-2025

# 2. Ativar venv (se precisar instalar dependências)
source venv/bin/activate

# 3. Atualizar código (git pull ou upload)
# ...

# 4. Instalar dependências (se necessário)
pip install -r requirements.txt

# 5. Reiniciar serviço
sudo systemctl restart epallet

# 6. Verificar
sudo systemctl status epallet
sudo journalctl -u epallet -n 20
```

---

## ✅ Checklist Final

- [ ] Arquivo `/etc/systemd/system/epallet.service` criado
- [ ] `systemctl daemon-reload` executado
- [ ] `systemctl enable epallet` executado
- [ ] `systemctl start epallet` executado
- [ ] Status `active (running)`
- [ ] Logs sem erros
- [ ] Aplicação acessível via navegador
- [ ] Auto-restart testado
- [ ] Reboot testado
- [ ] Nginx configurado (se aplicável)

---

## 🎯 Resultado Final

Após seguir este guia:

✅ **Serviço rodando** em background  
✅ **Auto-start** no boot  
✅ **Auto-restart** em caso de falha  
✅ **Logs centralizados** no journalctl  
✅ **Gerenciamento fácil** com systemctl  
✅ **Pronto para produção**  

---

## 📞 Comandos Rápidos

```bash
# Ver tudo de uma vez
sudo systemctl status epallet && \
sudo journalctl -u epallet -n 10 && \
curl -I http://127.0.0.1:8000

# Reiniciar e ver logs
sudo systemctl restart epallet && \
sleep 2 && \
sudo journalctl -u epallet -n 20

# Parar, limpar logs, iniciar
sudo systemctl stop epallet && \
sudo journalctl --vacuum-time=1s && \
sudo systemctl start epallet && \
sudo systemctl status epallet
```

---

**Versão:** 30 (Serviço Systemd)  
**Data:** 10/11/2024  
**Sistema:** Epallet - Gestão de Pallets  
**Plataforma:** Ubuntu 20.04+ com systemd

Seu projeto agora roda como um serviço profissional! 🚀
