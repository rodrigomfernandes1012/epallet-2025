# 🔧 Correção - Erro SSL do Nginx

## ❌ Erro Encontrado

```
nginx: [emerg] cannot load certificate "/etc/letsencrypt/live/app.epallet.com.br/fullchain.pem": 
BIO_new_file() failed (SSL: error:80000002:system library::No such file or directory)
nginx: configuration file /etc/nginx/nginx.conf test failed
```

---

## 🔍 Causa do Problema

O arquivo de configuração do Nginx está tentando carregar certificados SSL que **ainda não existem**. Isso acontece quando:

1. Você configurou o SSL manualmente no Nginx
2. Mas ainda não executou o Certbot para gerar os certificados

---

## ✅ Solução Rápida

### Passo 1: Criar Configuração Nginx SEM SSL

```bash
# Remover configuração atual
rm /etc/nginx/sites-enabled/epallet

# Criar nova configuração (sem SSL)
nano /etc/nginx/sites-available/epallet
```

**Cole esta configuração (HTTP apenas):**

```nginx
# Configuração para app.epallet.com.br (HTTP)
server {
    listen 80;
    server_name app.epallet.com.br www.app.epallet.com.br;

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
        
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    client_max_body_size 50M;
}

# Configuração para motorista.epallet.com.br (HTTP)
server {
    listen 80;
    server_name motorista.epallet.com.br;

    access_log /var/log/nginx/motorista_access.log;
    error_log /var/log/nginx/motorista_error.log;

    location /static {
        alias /root/epallet-2025/app/static;
        expires 30d;
    }

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

### Passo 2: Ativar Configuração

```bash
# Criar link simbólico
ln -s /etc/nginx/sites-available/epallet /etc/nginx/sites-enabled/

# Testar configuração
nginx -t
```

**Deve mostrar:**
```
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

### Passo 3: Recarregar Nginx

```bash
systemctl reload nginx
```

### Passo 4: Verificar se Gunicorn está Rodando

```bash
systemctl status epallet
```

**Se não estiver rodando:**
```bash
systemctl start epallet
```

### Passo 5: Testar HTTP

```bash
# Testar localmente
curl http://localhost

# Testar via domínio
curl http://app.epallet.com.br
```

### Passo 6: Gerar Certificados SSL com Certbot

```bash
# Executar Certbot (ele vai modificar a configuração automaticamente)
certbot --nginx -d app.epallet.com.br -d www.app.epallet.com.br -d motorista.epallet.com.br
```

**Prompts do Certbot:**
1. **Email:** Informe seu email
2. **Termos:** Digite `Y` para aceitar
3. **Compartilhar email:** Digite `N`
4. **Redirecionar HTTP para HTTPS:** Digite `2` (recomendado)

**O Certbot vai:**
- Gerar os certificados
- Modificar automaticamente o arquivo do Nginx
- Adicionar as configurações SSL
- Configurar redirecionamento HTTP → HTTPS

### Passo 7: Verificar SSL

```bash
# Testar configuração
nginx -t

# Recarregar Nginx
systemctl reload nginx

# Testar HTTPS
curl -I https://app.epallet.com.br
```

---

## 🎯 Resumo dos Comandos

```bash
# 1. Remover configuração antiga
rm /etc/nginx/sites-enabled/epallet

# 2. Criar nova configuração sem SSL
nano /etc/nginx/sites-available/epallet
# (colar configuração acima)

# 3. Ativar
ln -s /etc/nginx/sites-available/epallet /etc/nginx/sites-enabled/

# 4. Testar
nginx -t

# 5. Recarregar
systemctl reload nginx

# 6. Verificar Gunicorn
systemctl status epallet

# 7. Gerar SSL
certbot --nginx -d app.epallet.com.br -d www.app.epallet.com.br -d motorista.epallet.com.br

# 8. Verificar
curl -I https://app.epallet.com.br
```

---

## 🔍 Verificações

### Verificar DNS

Antes de gerar certificados, verifique se os domínios estão apontando para o servidor:

```bash
# Verificar DNS
nslookup app.epallet.com.br
nslookup motorista.epallet.com.br
```

**Deve mostrar o IP do seu servidor.**

### Verificar Firewall

```bash
# Verificar portas abertas
ufw status

# Se necessário, abrir portas
ufw allow 80/tcp
ufw allow 443/tcp
```

### Verificar Nginx

```bash
# Status
systemctl status nginx

# Logs de erro
tail -f /var/log/nginx/error.log

# Logs de acesso
tail -f /var/log/nginx/epallet_access.log
```

---

## ❌ Erros Comuns

### Erro 1: "nginx: [emerg] bind() to 0.0.0.0:80 failed"

**Causa:** Outra aplicação está usando a porta 80.

**Solução:**
```bash
# Ver o que está usando a porta 80
netstat -tlnp | grep :80

# Se for Apache
systemctl stop apache2
systemctl disable apache2

# Reiniciar Nginx
systemctl restart nginx
```

### Erro 2: Certbot falha com "Connection refused"

**Causa:** Nginx não está rodando ou firewall bloqueando.

**Solução:**
```bash
# Verificar Nginx
systemctl status nginx

# Verificar firewall
ufw status

# Permitir HTTP/HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Tentar novamente
certbot --nginx -d app.epallet.com.br -d motorista.epallet.com.br
```

### Erro 3: "Domain not found"

**Causa:** DNS não está configurado corretamente.

**Solução:**
```bash
# Verificar DNS
nslookup app.epallet.com.br

# Aguardar propagação DNS (pode levar até 48h)
# Ou configurar DNS corretamente no seu provedor
```

### Erro 4: "502 Bad Gateway"

**Causa:** Gunicorn não está rodando.

**Solução:**
```bash
# Verificar Gunicorn
systemctl status epallet

# Ver logs
journalctl -u epallet -n 50

# Reiniciar
systemctl restart epallet
```

---

## 📝 Configuração Final (Após Certbot)

Após executar o Certbot, seu arquivo `/etc/nginx/sites-available/epallet` terá algo assim:

```nginx
server {
    server_name app.epallet.com.br www.app.epallet.com.br;

    # ... configurações ...

    listen 443 ssl; # managed by Certbot
    ssl_certificate /etc/letsencrypt/live/app.epallet.com.br/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/app.epallet.com.br/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot
}

server {
    if ($host = www.app.epallet.com.br) {
        return 301 https://$host$request_uri;
    } # managed by Certbot

    if ($host = app.epallet.com.br) {
        return 301 https://$host$request_uri;
    } # managed by Certbot

    listen 80;
    server_name app.epallet.com.br www.app.epallet.com.br;
    return 404; # managed by Certbot
}
```

**Não edite as linhas com `# managed by Certbot`!**

---

## 🔄 Renovação Automática

### Configurar Cron Job

```bash
# Editar crontab
crontab -e
```

**Adicionar linha:**
```
0 3 * * * certbot renew --quiet --post-hook "systemctl reload nginx"
```

### Testar Renovação

```bash
# Testar renovação (não renova de verdade)
certbot renew --dry-run
```

**Deve mostrar:**
```
Congratulations, all simulated renewals succeeded
```

---

## ✅ Checklist

- [ ] Configuração Nginx criada (sem SSL)
- [ ] Link simbólico criado
- [ ] `nginx -t` passou
- [ ] Nginx recarregado
- [ ] Gunicorn rodando
- [ ] HTTP funcionando
- [ ] DNS configurado e propagado
- [ ] Firewall com portas 80 e 443 abertas
- [ ] Certbot executado com sucesso
- [ ] HTTPS funcionando
- [ ] Renovação automática configurada
- [ ] Renovação testada

---

## 🎯 Teste Final

```bash
# Testar HTTP (deve redirecionar para HTTPS)
curl -I http://app.epallet.com.br

# Testar HTTPS
curl -I https://app.epallet.com.br

# Testar motorista
curl -I https://motorista.epallet.com.br

# Ver certificado
echo | openssl s_client -servername app.epallet.com.br -connect app.epallet.com.br:443 2>/dev/null | openssl x509 -noout -dates
```

---

## 💡 Dicas

### 1. Sempre Configure HTTP Primeiro

Nunca configure SSL manualmente. Deixe o Certbot fazer isso:
1. Configure Nginx com HTTP
2. Execute Certbot
3. Certbot adiciona SSL automaticamente

### 2. Verifique DNS Antes

```bash
nslookup app.epallet.com.br
nslookup motorista.epallet.com.br
```

### 3. Teste Passo a Passo

```bash
# 1. Nginx funciona?
nginx -t

# 2. Gunicorn funciona?
systemctl status epallet

# 3. HTTP funciona?
curl http://localhost

# 4. DNS funciona?
nslookup app.epallet.com.br

# 5. Certbot pode ser executado?
certbot --nginx -d app.epallet.com.br
```

---

## 📞 Comandos Rápidos

```bash
# Ver logs do Nginx
tail -f /var/log/nginx/error.log

# Ver logs do Gunicorn
journalctl -u epallet -f

# Recarregar Nginx
systemctl reload nginx

# Reiniciar Gunicorn
systemctl restart epallet

# Testar SSL
curl -I https://app.epallet.com.br

# Renovar certificados
certbot renew
```

---

**Versão:** 23 (Correção SSL)  
**Data:** 07/11/2024  
**Sistema:** Epallet - Gestão de Pallets
