# 🧪 Guia de Teste - WhatsApp para Motorista

## ✅ Correções Já Aplicadas

Todas as correções necessárias **já estão implementadas** no projeto v24:

### 1. **Relacionamento Motorista** (`app/models.py` linha 180)

```python
motorista = db.relationship('Motorista', backref='vales_pallet', lazy=True)
```

✅ **Resolvido:** Não haverá mais erro `AttributeError: 'ValePallet' object has no attribute 'motorista'`

### 2. **Busca Robusta** (`app/routes/publico.py` linha 136-137)

```python
if vale.motorista_id:
    motorista = Motorista.query.get(vale.motorista_id)
```

✅ **Resolvido:** Usa query direta em vez de relacionamento (mais robusto)

### 3. **Try/Except** (`app/routes/publico.py` linha 131-142)

```python
try:
    enviar_whatsapp_entrega_concluida(motorista, vale)
except Exception as e:
    current_app.logger.error(f'Erro ao enviar WhatsApp: {str(e)}')
```

✅ **Resolvido:** Não quebra o fluxo se WhatsApp falhar

### 4. **Logs Detalhados** (`app/utils/whatsapp.py` linha 185-193)

```python
current_app.logger.info(f'Enviando WhatsApp de entrega concluída para {motorista.nome}')
```

✅ **Resolvido:** Logs para debug e monitoramento

---

## 📋 Pré-requisitos para Teste

### 1. Configurar .env

```bash
cd /root/epallet-2025
nano .env
```

**Adicionar/Verificar:**

```bash
# WhatsGw API
WHATSGW_APIKEY=sua-api-key-aqui
WHATSGW_PHONE_NUMBER=5511987654321
```

**Como obter:**
- Acesse [https://app.whatsgw.com.br](https://app.whatsgw.com.br)
- Faça login
- Copie sua API Key
- Copie o número do telefone conectado

### 2. Reiniciar Aplicação

```bash
systemctl restart epallet
```

### 3. Verificar Logs

```bash
# Ver logs em tempo real
journalctl -u epallet -f
```

---

## 🧪 Cenários de Teste

### Cenário 1: Teste Completo (Fluxo Normal)

#### Passo 1: Criar Vale Pallet

1. Acesse o sistema: `https://app.epallet.com.br`
2. Faça login
3. Vá em "Vales Pallet" → "Novo Vale"
4. Preencha:
   - Cliente
   - Transportadora
   - Destinatário
   - **Motorista** (importante!)
   - Quantidade de pallets
   - Número do documento

5. Clique em "Salvar"

**Resultado esperado:**
- Vale criado com sucesso
- Motorista recebe WhatsApp com instruções

#### Passo 2: Confirmar Recebimento (Destinatário)

1. Acesse: `https://app.epallet.com.br/publico/confirmacao-recebimento`
2. Informe o número do documento
3. Clique em "Confirmar Recebimento"

**Resultado esperado:**
- Status muda para "Entrega Realizada"
- Motorista recebe WhatsApp com PIN

#### Passo 3: Validar PIN (Motorista)

1. Acesse: `https://motorista.epallet.com.br/publico/validacao-pin`
2. Informe:
   - Número do documento
   - PIN (recebido por WhatsApp)
3. Clique em "Validar"

**Resultado esperado:**
- ✅ Status muda para "Entrega Concluída"
- ✅ **Motorista recebe WhatsApp:** `"Sr.(a) [Nome], a nota "[Documento]", foi registrado entrega concluida em nosso sistema."`
- ✅ Nenhum erro no log

---

### Cenário 2: Teste de Erro (Motorista sem Celular)

#### Passo 1: Criar Motorista sem Celular

1. Vá em "Motoristas" → "Novo Motorista"
2. Preencha nome, CPF, etc.
3. **Deixe o campo "Celular" vazio**
4. Salve

#### Passo 2: Criar Vale com Este Motorista

1. Crie um vale pallet
2. Selecione o motorista sem celular
3. Salve

#### Passo 3: Validar PIN

1. Confirme recebimento
2. Valide PIN

**Resultado esperado:**
- ✅ Validação funciona normalmente
- ⚠️ WhatsApp não é enviado (motorista sem celular)
- ✅ Log registra: `"Motorista [Nome] não tem celular cadastrado"`
- ✅ **Nenhum erro quebra o sistema**

---

### Cenário 3: Teste de Erro (API Key Inválida)

#### Passo 1: Configurar API Key Inválida

```bash
nano /root/epallet-2025/.env
```

**Alterar temporariamente:**
```bash
WHATSGW_APIKEY=chave-invalida-teste
```

#### Passo 2: Reiniciar e Testar

```bash
systemctl restart epallet
```

#### Passo 3: Validar PIN

1. Confirme recebimento
2. Valide PIN

**Resultado esperado:**
- ✅ Validação funciona normalmente
- ❌ WhatsApp não é enviado (API key inválida)
- ✅ Log registra erro de API
- ✅ **Sistema não quebra**

#### Passo 4: Restaurar API Key

```bash
nano /root/epallet-2025/.env
# Restaurar API key correta
systemctl restart epallet
```

---

## 🔍 Como Verificar se Funcionou

### 1. Verificar Logs da Aplicação

```bash
# Ver logs em tempo real
journalctl -u epallet -f

# Buscar logs de WhatsApp
journalctl -u epallet | grep -i whatsapp

# Últimas 100 linhas
journalctl -u epallet -n 100
```

**O que procurar:**

✅ **Sucesso:**
```
Enviando WhatsApp de entrega concluída para João Silva (5511987654321)
WhatsApp enviado com sucesso para João Silva
```

❌ **Erro:**
```
Erro ao enviar WhatsApp: ...
Motorista João Silva não tem celular cadastrado
WHATSGW_APIKEY não configurado no .env
```

### 2. Verificar Logs do Gunicorn

```bash
tail -f /root/epallet-2025/logs/gunicorn_error.log
```

### 3. Verificar Banco de Dados

```bash
cd /root/epallet-2025
source venv/bin/activate
python3
```

**No Python:**

```python
from app import create_app, db
from app.models import ValePallet, Motorista

app = create_app()
app.app_context().push()

# Buscar último vale
vale = ValePallet.query.order_by(ValePallet.id.desc()).first()

print(f"Vale: {vale.numero_documento}")
print(f"Status: {vale.status}")
print(f"Motorista ID: {vale.motorista_id}")

# Verificar motorista
if vale.motorista_id:
    motorista = Motorista.query.get(vale.motorista_id)
    print(f"Motorista: {motorista.nome}")
    print(f"Celular: {motorista.celular}")
else:
    print("Sem motorista associado")

exit()
```

### 4. Verificar Celular do Motorista

O motorista deve receber WhatsApp com:

```
Sr.(a) João Silva, a nota "NF-12345", foi registrado entrega concluida em nosso sistema.
```

---

## ❌ Troubleshooting

### Problema 1: WhatsApp não chega

**Possíveis causas:**

1. **API Key inválida**
   ```bash
   # Verificar .env
   cat /root/epallet-2025/.env | grep WHATSGW
   ```

2. **Número de telefone incorreto**
   ```bash
   # Verificar formato: 5511987654321
   # Deve ter 13 dígitos (55 + DDD + 9 dígitos)
   ```

3. **Motorista sem celular**
   ```bash
   # Verificar no banco
   # (ver script Python acima)
   ```

4. **Serviço WhatsGw fora do ar**
   ```bash
   # Testar API manualmente
   curl -X POST https://app.whatsgw.com.br/api/WhatsGw/Send \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer SUA_API_KEY" \
     -d '{
       "apikey": "SUA_API_KEY",
       "phone_number": "5511987654321",
       "contact_phone_number": "5511987654321",
       "message_type": "text",
       "message_body": "Teste"
     }'
   ```

### Problema 2: Erro AttributeError

**Se ainda aparecer:**

```bash
# Verificar se o relacionamento está no modelo
grep -n "motorista = db.relationship" /root/epallet-2025/app/models.py

# Deve mostrar:
# 180:    motorista = db.relationship('Motorista', backref='vales_pallet', lazy=True)
```

**Se não estiver:**

```bash
# Adicionar manualmente
nano /root/epallet-2025/app/models.py
# Adicionar após a linha 179 (motorista_id):
# motorista = db.relationship('Motorista', backref='vales_pallet', lazy=True)

# Reiniciar
systemctl restart epallet
```

### Problema 3: Logs não aparecem

**Verificar nível de log:**

```bash
# Ver configuração
cat /root/epallet-2025/config/config.py | grep -i log

# Deve ter:
# LOG_LEVEL = 'INFO'
```

**Forçar logs:**

```bash
# Ver todos os logs
journalctl -u epallet --since "1 hour ago"

# Ver apenas erros
journalctl -u epallet -p err
```

---

## 📊 Checklist de Validação

### Configuração

- [ ] WHATSGW_APIKEY configurado no .env
- [ ] WHATSGW_PHONE_NUMBER configurado no .env
- [ ] API Key válida (testada manualmente)
- [ ] Número de telefone no formato correto

### Código

- [ ] Relacionamento motorista existe no modelo (linha 180)
- [ ] Busca robusta implementada (publico.py linha 136)
- [ ] Try/except implementado (publico.py linha 131)
- [ ] Logs implementados (whatsapp.py linha 185)
- [ ] Webhook também envia WhatsApp (webhook.py linha 186)

### Testes

- [ ] Teste completo (fluxo normal) - WhatsApp chega
- [ ] Teste sem celular - Sistema não quebra
- [ ] Teste com API key inválida - Sistema não quebra
- [ ] Logs aparecem corretamente
- [ ] Nenhum erro AttributeError

---

## 📞 Comandos Rápidos

```bash
# Ver logs em tempo real
journalctl -u epallet -f

# Buscar logs de WhatsApp
journalctl -u epallet | grep -i whatsapp

# Ver configuração
cat /root/epallet-2025/.env | grep WHATSGW

# Reiniciar aplicação
systemctl restart epallet

# Testar aplicação
curl http://127.0.0.1:8000

# Ver último vale criado
cd /root/epallet-2025 && source venv/bin/activate && python3 -c "from app import create_app, db; from app.models import ValePallet; app = create_app(); app.app_context().push(); vale = ValePallet.query.order_by(ValePallet.id.desc()).first(); print(f'Vale: {vale.numero_documento}, Status: {vale.status}, Motorista ID: {vale.motorista_id}')"
```

---

## 🎯 Resultado Esperado

Após seguir este guia:

✅ **WhatsApp é enviado** quando motorista valida PIN  
✅ **Nenhum erro** AttributeError  
✅ **Sistema não quebra** mesmo com erros de WhatsApp  
✅ **Logs detalhados** para debug  
✅ **Funciona via web** (motorista.epallet.com.br)  
✅ **Funciona via WhatsApp** (webhook)  

---

**Versão:** 24 (WhatsApp Validado)  
**Data:** 07/11/2024  
**Sistema:** Epallet - Gestão de Pallets
