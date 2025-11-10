# 🚀 Solução Rápida - Nginx Warning e Systemd

## 📋 Problemas Identificados

### 1. ⚠️ Warning do Nginx (Não Crítico)

```
nginx: [warn] conflicting server name "epallet.com.br" on 0.0.0.0:80, ignored
```

**Causa:** Você tem duas configurações com o mesmo `server_name`.

**Solução:** Verificar e remover configurações duplicadas.

### 2. ❌ Serviço Systemd Não Existe

```
Unit epallet.service could not be found.
```

**Causa:** Você ainda não criou o arquivo de serviço systemd.

**Solução:** Criar o serviço agora.

---

## ✅ Solução Passo a Passo

### Passo 1: Resolver Warning do Nginx

#### 1.1 Verificar Configurações Duplicadas

```bash
# Listar todos os sites habilitados
ls -la /etc/nginx/sites-enabled/

# Ver conteúdo de cada um
cat /etc/nginx/sites-enabled/epallet
cat /etc/nginx/sites-enabled/default  # se existir
```

#### 1.2 Remover Configuração Padrão

```bash
# Remover default se existir
rm /etc/nginx/sites-enabled/default
```

#### 1.3 Verificar se Há Outros Arquivos

```bash
# Ver todos os arquivos de configuração
grep -r "server_name.*epallet" /etc/nginx/sites-enabled/
```

#### 1.4 Testar Novamente

```bash
nginx -t
```

**Deve mostrar:**
```
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

**Sem warnings!**

---

### Passo 2: Criar Serviço Systemd

#### 2.1 Criar Arquivo de Serviço

```bash
nano /etc/systemd/system/epallet.service
```

#### 2.2 Colar Esta Configuração

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

**Salvar:** `Ctrl+O`, Enter, `Ctrl+X`

#### 2.3 Recarregar Systemd

```bash
systemctl daemon-reload
```

#### 2.4 Habilitar Serviço

```bash
systemctl enable epallet
```

#### 2.5 Iniciar Serviço

```bash
systemctl start epallet
```

#### 2.6 Verificar Status

```bash
systemctl status epallet
```

**Deve mostrar:**
```
● epallet.service - Epallet Flask Application
   Loaded: loaded (/etc/systemd/system/epallet.service; enabled)
   Active: active (running) since ...
```

---

### Passo 3: Testar Tudo

#### 3.1 Verificar Gunicorn

```bash
# Ver se está rodando
ps aux | grep gunicorn

# Ver logs
journalctl -u epallet -n 50
```

#### 3.2 Verificar Porta 8000

```bash
netstat -tlnp | grep 8000
```

**Deve mostrar:**
```
tcp  0  0  127.0.0.1:8000  0.0.0.0:*  LISTEN  12345/gunicorn
```

#### 3.3 Testar Localmente

```bash
curl http://127.0.0.1:8000
```

**Deve retornar HTML da aplicação.**

#### 3.4 Testar via Nginx

```bash
curl http://localhost
```

#### 3.5 Testar via Domínio

```bash
curl http://app.epallet.com.br
```

---

## 🎯 Comandos Completos (Copie e Cole)

```bash
# 1. Remover configuração default
rm /etc/nginx/sites-enabled/default

# 2. Testar Nginx
nginx -t

# 3. Recarregar Nginx
systemctl reload nginx

# 4. Criar serviço systemd
cat > /etc/systemd/system/epallet.service << 'EOF'
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

StandardOutput=journal
StandardError=journal
SyslogIdentifier=epallet

[Install]
WantedBy=multi-user.target
EOF

# 5. Recarregar systemd
systemctl daemon-reload

# 6. Habilitar serviço
systemctl enable epallet

# 7. Iniciar serviço
systemctl start epallet

# 8. Verificar status
systemctl status epallet

# 9. Ver logs
journalctl -u epallet -n 50

# 10. Testar aplicação
curl http://127.0.0.1:8000
```

---

## 🔍 Verificações

### Verificar Nginx

```bash
# Status
systemctl status nginx

# Configuração
nginx -t

# Sites habilitados
ls -la /etc/nginx/sites-enabled/

# Logs
tail -f /var/log/nginx/error.log
```

### Verificar Gunicorn

```bash
# Status do serviço
systemctl status epallet

# Processos
ps aux | grep gunicorn

# Porta
netstat -tlnp | grep 8000

# Logs
journalctl -u epallet -f
```

### Verificar Aplicação

```bash
# Teste local
curl http://127.0.0.1:8000

# Teste via Nginx
curl http://localhost

# Teste via domínio
curl http://app.epallet.com.br
```

---

## ❌ Erros Comuns

### Erro 1: Gunicorn não inicia

**Ver logs:**
```bash
journalctl -u epallet -n 100
```

**Possíveis causas:**
- Ambiente virtual não encontrado
- Erro no código Python
- Banco de dados não inicializado
- Porta 8000 já em uso

**Soluções:**
```bash
# Verificar venv
ls -la /root/epallet-2025/venv/

# Testar manualmente
cd /root/epallet-2025
source venv/bin/activate
gunicorn --config gunicorn_config.py run:app

# Verificar porta
netstat -tlnp | grep 8000
```

### Erro 2: "502 Bad Gateway"

**Causa:** Gunicorn não está rodando.

**Solução:**
```bash
systemctl restart epallet
systemctl status epallet
```

### Erro 3: "Permission denied"

**Causa:** Permissões incorretas.

**Solução:**
```bash
# Dar permissões ao diretório
chmod 755 /root/epallet-2025
chmod 755 /root/epallet-2025/instance
chmod 644 /root/epallet-2025/instance/epallet.db

# Reiniciar serviço
systemctl restart epallet
```

### Erro 4: "Module not found"

**Causa:** Dependências não instaladas.

**Solução:**
```bash
cd /root/epallet-2025
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
systemctl restart epallet
```

---

## 📊 Estrutura de Serviços

```
Nginx (porta 80/443)
    ↓ proxy_pass
Gunicorn (porta 8000)
    ↓ WSGI
Flask Application
    ↓
SQLite Database
```

---

## 🔧 Comandos de Manutenção

### Reiniciar Serviços

```bash
# Reiniciar Gunicorn
systemctl restart epallet

# Reiniciar Nginx
systemctl restart nginx

# Reiniciar ambos
systemctl restart epallet nginx
```

### Ver Logs

```bash
# Logs do Gunicorn (systemd)
journalctl -u epallet -f

# Logs do Gunicorn (arquivo)
tail -f /root/epallet-2025/logs/gunicorn_error.log

# Logs do Nginx
tail -f /var/log/nginx/epallet_error.log
```

### Parar/Iniciar

```bash
# Parar
systemctl stop epallet

# Iniciar
systemctl start epallet

# Status
systemctl status epallet
```

---

## ✅ Checklist

- [ ] Warning do Nginx resolvido
- [ ] Arquivo epallet.service criado
- [ ] Systemd recarregado
- [ ] Serviço habilitado
- [ ] Serviço iniciado
- [ ] Status "active (running)"
- [ ] Porta 8000 escutando
- [ ] Teste local funcionando
- [ ] Teste via Nginx funcionando
- [ ] Teste via domínio funcionando

---

## 🎯 Próximos Passos

Após resolver esses problemas:

1. ✅ Nginx funcionando
2. ✅ Gunicorn funcionando
3. ✅ Aplicação acessível via HTTP
4. ⏭️ Gerar certificados SSL

```bash
certbot --nginx -d app.epallet.com.br -d www.app.epallet.com.br -d motorista.epallet.com.br
```

---

## 💡 Dicas

### 1. Sempre Verifique os Logs

```bash
# Logs em tempo real
journalctl -u epallet -f

# Últimas 100 linhas
journalctl -u epallet -n 100

# Logs de hoje
journalctl -u epallet --since today
```

### 2. Teste Manualmente Primeiro

Antes de criar o serviço, sempre teste manualmente:

```bash
cd /root/epallet-2025
source venv/bin/activate
gunicorn --config gunicorn_config.py run:app
```

Se funcionar manualmente, vai funcionar no systemd.

### 3. Use systemctl status

```bash
systemctl status epallet
```

Mostra:
- Se está rodando
- PID do processo
- Últimas linhas de log
- Erros recentes

---

## 📞 Comandos Rápidos

```bash
# Ver status de tudo
systemctl status epallet nginx

# Reiniciar tudo
systemctl restart epallet nginx

# Ver logs em tempo real
journalctl -u epallet -f

# Testar aplicação
curl http://127.0.0.1:8000

# Verificar portas
netstat -tlnp | grep -E '80|443|8000'
```

---

**Versão:** 24 (Nginx + Systemd)  
**Data:** 07/11/2024  
**Sistema:** Epallet - Gestão de Pallets
