# 🚀 Guia Rápido - Inicialização do Banco de Dados

## ⚠️ IMPORTANTE

O script `init_db.py` **requer um comando**. Não execute apenas `python init_db.py`.

---

## 📋 Comandos Disponíveis

### 1️⃣ `init` - Inicializar Banco de Dados

Cria todas as tabelas no banco de dados.

```bash
cd /root/epallet-2025
source venv/bin/activate
python init_db.py init
```

**Saída esperada:**
```
✓ Banco de dados inicializado com sucesso!
✓ Tabelas criadas:
  - users
  - empresas
  - tipos_empresa
  - motoristas
  - vales_pallet
  - logs
```

---

### 2️⃣ `create-admin` - Criar Usuário Administrador

Cria um novo usuário administrador interativamente.

```bash
python init_db.py create-admin
```

**Prompts:**
```
Nome de usuário: admin
Email: admin@epallet.com.br
Senha: ********
Confirmar senha: ********

✓ Usuário administrador criado com sucesso!
  Username: admin
  Email: admin@epallet.com.br
```

---

### 3️⃣ `reset` - Resetar Banco de Dados

**⚠️ CUIDADO:** Apaga todos os dados e recria as tabelas.

```bash
python init_db.py reset
```

**Confirmação:**
```
ATENÇÃO: Esta operação irá APAGAR TODOS OS DADOS!
Tem certeza? (digite 'sim' para confirmar): sim

✓ Banco de dados resetado com sucesso!
```

---

## 🎯 Sequência Recomendada (Primeira Instalação)

### Passo 1: Criar Diretórios

```bash
cd /root/epallet-2025
mkdir -p instance logs
chmod 755 instance logs
```

### Passo 2: Ativar Ambiente Virtual

```bash
source venv/bin/activate
```

### Passo 3: Inicializar Banco

```bash
python init_db.py init
```

### Passo 4: Criar Administrador

```bash
python init_db.py create-admin
```

**Dados sugeridos:**
- **Username:** admin
- **Email:** admin@epallet.com.br
- **Senha:** (escolha uma senha forte)

### Passo 5: Verificar Criação

```bash
ls -la instance/
```

**Deve mostrar:**
```
-rw-r--r-- 1 root root 98304 Nov  7 15:30 epallet.db
```

### Passo 6: Popular Tipos de Empresa (Opcional)

```bash
python popular_tipos.py
```

**Cria os tipos padrão:**
- Cliente
- Transportadora
- Destinatário

---

## 🔍 Verificar Banco de Dados

### Verificar Tabelas

```bash
cd /root/epallet-2025
source venv/bin/activate
python3
```

**No Python:**

```python
from app import create_app, db
from app.models import User, Empresa, TipoEmpresa, Motorista, ValePallet

app = create_app()
app.app_context().push()

# Verificar usuários
users = User.query.all()
print(f"Total de usuários: {len(users)}")
for user in users:
    print(f"  - {user.username} ({user.email})")

# Verificar tipos de empresa
tipos = TipoEmpresa.query.all()
print(f"\nTotal de tipos: {len(tipos)}")
for tipo in tipos:
    print(f"  - {tipo.nome}")

exit()
```

---

## ❌ Erros Comuns

### Erro 1: "unable to open database file"

**Causa:** Diretório `instance/` não existe ou sem permissão.

**Solução:**
```bash
cd /root/epallet-2025
mkdir -p instance
chmod 755 instance
python init_db.py init
```

### Erro 2: "No module named 'app'"

**Causa:** Ambiente virtual não ativado ou dependências não instaladas.

**Solução:**
```bash
source venv/bin/activate
pip install -r requirements.txt
python init_db.py init
```

### Erro 3: "Uso: python3 init_db.py [comando]"

**Causa:** Comando não especificado.

**Solução:**
```bash
# Use um dos comandos: init, create-admin, ou reset
python init_db.py init
```

### Erro 4: "Table already exists"

**Causa:** Banco já foi inicializado.

**Solução:**
```bash
# Se quiser recriar (APAGA DADOS):
python init_db.py reset

# Ou apenas criar admin:
python init_db.py create-admin
```

---

## 🔧 Comandos de Manutenção

### Backup do Banco

```bash
# Criar backup
cp /root/epallet-2025/instance/epallet.db /root/backups/epallet_$(date +%Y%m%d_%H%M%S).db

# Verificar backup
ls -lh /root/backups/
```

### Restaurar Backup

```bash
# Parar serviço
systemctl stop epallet

# Restaurar
cp /root/backups/epallet_20241107_150000.db /root/epallet-2025/instance/epallet.db

# Iniciar serviço
systemctl start epallet
```

### Resetar e Recriar

```bash
# Parar serviço
systemctl stop epallet

# Fazer backup
cp /root/epallet-2025/instance/epallet.db /root/backups/epallet_backup_$(date +%Y%m%d_%H%M%S).db

# Resetar banco
cd /root/epallet-2025
source venv/bin/activate
python init_db.py reset

# Criar admin
python init_db.py create-admin

# Popular tipos
python popular_tipos.py

# Iniciar serviço
systemctl start epallet
```

---

## 📊 Estrutura do Banco

### Tabelas Criadas

| Tabela | Descrição |
|--------|-----------|
| `users` | Usuários do sistema |
| `empresas` | Empresas (clientes, transportadoras, destinatários) |
| `tipos_empresa` | Tipos de empresa |
| `motoristas` | Motoristas cadastrados |
| `vales_pallet` | Vales de pallet |
| `logs` | Logs de auditoria |

### Relacionamentos

```
users
  └─> vales_pallet (criado_por_id)
  └─> motoristas (cadastrado_por_id)
  └─> empresas (cadastrado_por_id)

tipos_empresa
  └─> empresas (tipo_id)

empresas
  └─> vales_pallet (cliente_id)
  └─> vales_pallet (transportadora_id)
  └─> vales_pallet (destinatario_id)
  └─> motoristas (empresa_id)

motoristas
  └─> vales_pallet (motorista_id)
```

---

## 🎯 Checklist de Inicialização

- [ ] Diretório `instance/` criado
- [ ] Permissões 755 aplicadas
- [ ] Ambiente virtual ativado
- [ ] Comando `python init_db.py init` executado
- [ ] Banco de dados criado (epallet.db)
- [ ] Usuário administrador criado
- [ ] Tipos de empresa populados (opcional)
- [ ] Banco verificado via Python
- [ ] Backup inicial criado

---

## 💡 Dicas

### 1. Sempre Ative o Ambiente Virtual

```bash
cd /root/epallet-2025
source venv/bin/activate
```

### 2. Use Caminho Absoluto no .env

```bash
DATABASE_URL=sqlite:////root/epallet-2025/instance/epallet.db
```

### 3. Faça Backup Antes de Resetar

```bash
cp instance/epallet.db backups/epallet_backup_$(date +%Y%m%d_%H%M%S).db
```

### 4. Verifique Permissões

```bash
ls -la instance/
chmod 644 instance/epallet.db
```

---

## 📞 Comandos Rápidos

```bash
# Inicializar banco
cd /root/epallet-2025 && source venv/bin/activate && python init_db.py init

# Criar admin
python init_db.py create-admin

# Popular tipos
python popular_tipos.py

# Verificar banco
ls -lh instance/epallet.db

# Fazer backup
cp instance/epallet.db /root/backups/epallet_$(date +%Y%m%d_%H%M%S).db
```

---

**Versão:** 21 (Deploy Root)  
**Data:** 07/11/2024  
**Sistema:** Epallet - Gestão de Pallets
