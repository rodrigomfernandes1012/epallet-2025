# 🐧 Correção: Erro charset no Linux

## ❌ Erro

```
TypeError: 'charset' is an invalid keyword argument for Connection()
```

---

## 🔍 Causa

O PyMySQL no Linux não aceita o parâmetro `charset` em `connect_args` da mesma forma que no Windows.

---

## ✅ Solução Aplicada

### Arquivo Corrigido: `config/config.py`

**Antes:**
```python
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 10,
    'pool_recycle': 3600,
    'pool_pre_ping': True,
    'connect_args': {'charset': 'utf8mb4'}  # ❌ Causa erro no Linux
}
```

**Depois:**
```python
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 10,
    'pool_recycle': 3600,
    'pool_pre_ping': True
}
```

**O charset utf8mb4 já está configurado no MySQL via:**
- Tabelas criadas com `CHARSET=utf8mb4`
- DATABASE_URL pode incluir `?charset=utf8mb4` se necessário

---

## 🚀 Como Aplicar no Servidor

### Opção 1: Substituir Arquivo (Recomendado)

```bash
cd /root/epallet-2025

# Fazer backup
cp config/config.py config/config.py.bak

# Editar
nano config/config.py
```

**Remover a linha:**
```python
'connect_args': {'charset': 'utf8mb4'}
```

**Salvar:** `Ctrl+O`, `Enter`, `Ctrl+X`

### Opção 2: Comando Sed (Automático)

```bash
cd /root/epallet-2025

# Fazer backup
cp config/config.py config/config.py.bak

# Remover linha problemática
sed -i "/connect_args.*charset/d" config/config.py

# Verificar
cat config/config.py | grep -A5 "SQLALCHEMY_ENGINE_OPTIONS"
```

---

## 🧪 Testar

### 1. Testar Manualmente

```bash
cd /root/epallet-2025
source venv/bin/activate
python run.py
```

**Deve iniciar sem erros!**

### 2. Testar com Gunicorn

```bash
cd /root/epallet-2025
source venv/bin/activate
gunicorn --config gunicorn_config.py run:app
```

**Pressionar `Ctrl+C` para parar.**

### 3. Reiniciar Serviço

```bash
systemctl restart epallet
systemctl status epallet
```

**Deve mostrar:** `active (running)`

### 4. Verificar Logs

```bash
journalctl -u epallet -n 50
```

**Não deve ter erros de charset.**

---

## 🌐 Testar Aplicação

### 1. Acessar

```
http://seu-ip-ou-dominio
```

ou

```
http://app.epallet.com.br
```

### 2. Fazer Login

- Username: admin
- Senha: (sua senha)

### 3. Verificar Dashboard

Deve carregar sem erros!

---

## 💡 Por Que Isso Acontece?

### Windows vs Linux

| Aspecto | Windows | Linux |
|---------|---------|-------|
| **PyMySQL** | Aceita `charset` em `connect_args` | Não aceita |
| **Alternativa** | - | Configurar no MySQL ou na URL |

### Solução Correta

O charset deve ser configurado:

1. **No MySQL** (já feito no script SQL):
   ```sql
   CREATE TABLE ... CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
   ```

2. **Na DATABASE_URL** (opcional):
   ```bash
   DATABASE_URL=mysql://user:pass@host:3306/db?charset=utf8mb4
   ```

3. **Não em connect_args** (causa erro no Linux)

---

## ✅ Checklist

- [ ] Arquivo `config/config.py` editado
- [ ] Linha `connect_args` removida
- [ ] Arquivo salvo
- [ ] `python run.py` testado manualmente
- [ ] Gunicorn testado
- [ ] Serviço `epallet` reiniciado
- [ ] Status `active (running)`
- [ ] Logs sem erros
- [ ] Aplicação acessível
- [ ] Login funcionando
- [ ] Dashboard carregando

---

## 📞 Comandos Rápidos

```bash
# Editar config
nano /root/epallet-2025/config/config.py

# Testar
cd /root/epallet-2025
source venv/bin/activate
python run.py

# Reiniciar
systemctl restart epallet

# Ver logs
journalctl -u epallet -f

# Ver status
systemctl status epallet

# Testar conexão
curl http://127.0.0.1:8000
```

---

## ❌ Troubleshooting

### Erro: "Can't connect to MySQL"

**Verificar .env:**
```bash
cat /root/epallet-2025/.env | grep DATABASE_URL
```

**Deve ser:**
```
DATABASE_URL=mysql://epallet:Rodrigo%40101275@localhost:3306/epallet_db
```

### Erro: "Access denied"

**Verificar permissões:**
```bash
mysql -u root -p
```

```sql
GRANT ALL PRIVILEGES ON epallet_db.* TO 'epallet'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### Erro: "Unknown database"

**Criar banco:**
```bash
mysql -u root -p
```

```sql
CREATE DATABASE epallet_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

**Executar script:**
```bash
mysql -u epallet -p epallet_db < /root/epallet-2025/create_database_structure.sql
```

---

**Versão:** 29 (Charset Linux Corrigido)  
**Data:** 10/11/2024  
**Sistema:** Epallet - Gestão de Pallets

Problema do charset no Linux resolvido! 🐧✅
