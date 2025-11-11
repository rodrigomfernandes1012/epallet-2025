# 🔒 Guia Completo: Configurar HTTPS com Let's Encrypt

## 📋 O Que Vamos Fazer

Configurar **HTTPS** (SSL/TLS) gratuito usando **Let's Encrypt** para a aplicação Epallet.

**Benefícios:**
✅ Conexão segura e criptografada  
✅ Certificado SSL gratuito  
✅ Renovação automática  
✅ Confiança do navegador (cadeado verde)  
✅ Melhor SEO  
✅ Obrigatório para produção  

---

## 📝 Pré-requisitos

Antes de começar, você precisa:

- [ ] **Domínio configurado** apontando para o IP do servidor
  - Exemplo: `app.epallet.com.br` → `74.50.123.210`
  - Exemplo: `motorista.epallet.com.br` → `74.50.123.210`

- [ ] **Nginx funcionando** na porta 80 (HTTP)
  - Testar: `curl http://seu-dominio`

- [ ] **Firewall liberado** para portas 80 e 443
  - Porta 80: HTTP (necessária para validação)
  - Porta 443: HTTPS

- [ ] **Aplicação funcionando** com HTTP

---

## 🚀 Passo a Passo Completo

### Passo 1: Verificar DNS

```bash
# Verificar se o domínio aponta para o IP correto
nslookup app.epallet.com.br
nslookup motorista.epallet.com.br
```

**Deve mostrar o IP do seu servidor!**

Se não mostrar, aguarde a propagação do DNS (pode levar até 48h).

---

### Passo 2: Instalar Certbot

```bash
# Atualizar pacotes
sudo apt update

# Instalar Certbot e plugin Nginx
sudo apt install -y certbot python3-certbot-nginx
```

**Verificar instalação:**
```bash
certbot --version
```

**Deve mostrar:**
```
certbot 1.x.x
```

---

### Passo 3: Atualizar Configuração do Nginx

Antes de gerar o certificado, precisamos configurar os domínios no Nginx.

```bash
sudo nano /etc/nginx/sites-available/epallet
```

**Substituir TODO o conteúdo por:**

```nginx
# Servidor principal - app.epallet.com.br
server {
    listen 80;
    server_name app.epallet.com.br www.app.epallet.com.br;

    access_log /var/log/nginx/epallet_access.log;
    error_log /var/log/nginx/epallet_error.log;

    # Arquivos estáticos
    location /static {
        alias /root/epallet-2025/app/static;
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
        
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    client_max_body_size 50M;
}

# Servidor motorista - motorista.epallet.com.br
server {
    listen 80;
    server_name motorista.epallet.com.br;

    access_log /var/log/nginx/motorista_access.log;
    error_log /var/log/nginx/motorista_error.log;

    # Arquivos estáticos
    location /static {
        alias /root/epallet-2025/app/static;
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
        
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    client_max_body_size 50M;
}
```

**Salvar:** `Ctrl+O`, `Enter`, `Ctrl+X`

---

### Passo 4: Testar e Recarregar Nginx

```bash
# Testar configuração
sudo nginx -t

# Recarregar
sudo systemctl reload nginx
```

**Deve mostrar:**
```
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

---

### Passo 5: Liberar Firewall

```bash
# Verificar status
sudo ufw status

# Se estiver ativo, liberar portas
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Verificar
sudo ufw status
```

**Deve mostrar:**
```
80/tcp                     ALLOW       Anywhere
443/tcp                    ALLOW       Anywhere
```

---

### Passo 6: Gerar Certificado SSL

**Opção 1: Certificado para Ambos os Domínios (Recomendado)**

```bash
sudo certbot --nginx -d app.epallet.com.br -d www.app.epallet.com.br -d motorista.epallet.com.br
```

**Opção 2: Certificado Apenas para App**

```bash
sudo certbot --nginx -d app.epallet.com.br -d www.app.epallet.com.br
```

**Durante a execução, o Certbot vai perguntar:**

1. **Email:** Digite seu email (para avisos de expiração)
   ```
   Enter email address: seu@email.com
   ```

2. **Termos de Serviço:** Digite `Y` (aceitar)
   ```
   (A)gree/(C)ancel: A
   ```

3. **Compartilhar email:** Digite `N` (não compartilhar)
   ```
   (Y)es/(N)o: N
   ```

4. **Redirecionar HTTP para HTTPS:** Digite `2` (redirecionar)
   ```
   1: No redirect
   2: Redirect - Make all requests redirect to secure HTTPS access
   Select: 2
   ```

**Aguardar...**

**Sucesso!**
```
Congratulations! You have successfully enabled HTTPS on https://app.epallet.com.br and https://motorista.epallet.com.br
```

✅ **Certificado instalado!**

---

### Passo 7: Verificar Configuração

```bash
# Ver configuração atualizada
sudo cat /etc/nginx/sites-available/epallet
```

**O Certbot adicionou automaticamente:**
- Bloco `server` na porta 443 (HTTPS)
- Certificados SSL
- Redirecionamento HTTP → HTTPS

---

### Passo 8: Testar HTTPS

**No navegador, acessar:**
```
https://app.epallet.com.br
```

**Deve mostrar:**
- ✅ Cadeado verde na barra de endereço
- ✅ Certificado válido
- ✅ Conexão segura

**Testar redirecionamento:**
```
http://app.epallet.com.br
```

**Deve redirecionar automaticamente para:**
```
https://app.epallet.com.br
```

---

## 🔄 Renovação Automática

O Certbot configura renovação automática via **cron** ou **systemd timer**.

### Verificar Timer de Renovação

```bash
sudo systemctl status certbot.timer
```

**Deve mostrar:**
```
● certbot.timer - Run certbot twice daily
     Loaded: loaded
     Active: active (waiting)
```

### Testar Renovação Manualmente

```bash
sudo certbot renew --dry-run
```

**Deve mostrar:**
```
Congratulations, all simulated renewals succeeded
```

✅ **Renovação automática funcionando!**

---

## 📊 Verificar Certificados

### Listar Certificados

```bash
sudo certbot certificates
```

**Mostra:**
- Domínios cobertos
- Data de expiração
- Caminho dos certificados

### Verificar Expiração

```bash
echo | openssl s_client -servername app.epallet.com.br -connect app.epallet.com.br:443 2>/dev/null | openssl x509 -noout -dates
```

**Mostra:**
```
notBefore=Nov 10 00:00:00 2024 GMT
notAfter=Feb 08 23:59:59 2025 GMT
```

---

## 🔧 Configuração Avançada

### Forçar HTTPS em Todo o Site

Editar `/etc/nginx/sites-available/epallet` e adicionar no bloco `server` porta 443:

```nginx
# Adicionar dentro do bloco server { ... } porta 443
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

Isso força navegadores a sempre usarem HTTPS.

### Melhorar Segurança SSL

```bash
sudo nano /etc/nginx/sites-available/epallet
```

**Adicionar no bloco `server` porta 443:**

```nginx
# SSL Configuration
ssl_protocols TLSv1.2 TLSv1.3;
ssl_prefer_server_ciphers on;
ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 10m;
```

**Testar e recarregar:**
```bash
sudo nginx -t
sudo systemctl reload nginx
```

---

## 🧪 Testar Segurança SSL

### Teste Online

Acessar:
```
https://www.ssllabs.com/ssltest/analyze.html?d=app.epallet.com.br
```

**Objetivo:** Nota **A** ou **A+**

### Teste Local

```bash
curl -I https://app.epallet.com.br
```

**Deve mostrar:**
```
HTTP/2 200
server: nginx
strict-transport-security: max-age=31536000
```

---

## ❌ Troubleshooting

### Erro: "Domain not found"

**Causa:** DNS não configurado ou não propagado.

**Solução:**
```bash
nslookup app.epallet.com.br
```

Se não mostrar o IP, aguardar propagação ou verificar configuração DNS.

### Erro: "Connection refused"

**Causa:** Firewall bloqueando porta 80 ou 443.

**Solução:**
```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw reload
```

### Erro: "Too many failed authorizations"

**Causa:** Muitas tentativas falhadas (limite do Let's Encrypt).

**Solução:** Aguardar 1 hora e tentar novamente.

### Erro: "Certificate has expired"

**Causa:** Renovação automática falhou.

**Solução:**
```bash
# Renovar manualmente
sudo certbot renew

# Verificar timer
sudo systemctl status certbot.timer

# Habilitar timer (se desabilitado)
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

### Erro: "Mixed content" (conteúdo misto)

**Causa:** Página HTTPS carregando recursos HTTP.

**Solução:** Verificar se todos os recursos (CSS, JS, imagens) usam HTTPS ou caminhos relativos.

---

## 🔄 Renovar Certificado Manualmente

```bash
# Renovar todos os certificados
sudo certbot renew

# Renovar certificado específico
sudo certbot renew --cert-name app.epallet.com.br

# Forçar renovação (mesmo não expirado)
sudo certbot renew --force-renewal
```

---

## 🗑️ Remover Certificado

```bash
# Listar certificados
sudo certbot certificates

# Deletar certificado específico
sudo certbot delete --cert-name app.epallet.com.br
```

---

## ✅ Checklist Final

- [ ] DNS configurado apontando para o IP
- [ ] Certbot instalado
- [ ] Nginx configurado com domínios
- [ ] Firewall liberado (portas 80 e 443)
- [ ] Certificado SSL gerado
- [ ] HTTPS funcionando
- [ ] Redirecionamento HTTP → HTTPS ativo
- [ ] Renovação automática configurada
- [ ] Teste de renovação OK
- [ ] Teste de segurança SSL OK (Nota A)

---

## 🎯 Resultado Final

Após seguir este guia:

✅ **HTTPS ativo** com certificado válido  
✅ **Conexão segura** (cadeado verde)  
✅ **Renovação automática** configurada  
✅ **Redirecionamento HTTP → HTTPS**  
✅ **Segurança SSL** otimizada  
✅ **Pronto para produção**  

---

## 📞 Comandos Rápidos

```bash
# Gerar certificado
sudo certbot --nginx -d app.epallet.com.br -d motorista.epallet.com.br

# Renovar certificados
sudo certbot renew

# Testar renovação
sudo certbot renew --dry-run

# Listar certificados
sudo certbot certificates

# Ver logs
sudo tail -f /var/log/letsencrypt/letsencrypt.log

# Verificar timer
sudo systemctl status certbot.timer

# Testar HTTPS
curl -I https://app.epallet.com.br
```

---

**Versão:** 31 (HTTPS Let's Encrypt)  
**Data:** 10/11/2024  
**Sistema:** Epallet - Gestão de Pallets  
**Certificado:** Let's Encrypt (Gratuito, 90 dias, renovação automática)

Sua aplicação agora está segura com HTTPS! 🔒✅
