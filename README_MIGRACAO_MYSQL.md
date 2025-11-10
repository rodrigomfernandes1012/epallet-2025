# 🔄 Migração para MySQL - Resumo Completo

## 📋 O Que Mudou

O projeto **Epallet** foi refatorado para usar **MySQL** ao invés de SQLite.

---

## ✅ Arquivos Modificados

### 1. `requirements.txt`

**Adicionado:**
```
mysqlclient==2.2.0
```

### 2. `config/config.py`

**Antes:**
```python
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
```

**Depois:**
```python
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql://epallet_user:epallet_pass@localhost:3306/epallet_db'
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 10,
    'pool_recycle': 3600,
    'pool_pre_ping': True,
    'connect_args': {'charset': 'utf8mb4'}
}
```

### 3. `.env.example`

**Antes:**
```bash
DATABASE_URL=postgresql://usuario:senha@localhost:5432/nome_banco
```

**Depois:**
```bash
DATABASE_URL=mysql://epallet_user:senha_segura@localhost:3306/epallet_db
```

---

## 📁 Arquivos Criados

### 1. `migrate_sqlite_to_mysql.py`

Script para migrar dados do SQLite para MySQL.

**Uso:**
```bash
python migrate_sqlite_to_mysql.py instance/epallet.db
```

### 2. `GUIA_CONFIGURACAO_MYSQL.md`

Guia completo com:
- Instalação do MySQL
- Configuração do banco
- Criação de usuário
- Migração de dados
- Backup e manutenção
- Troubleshooting

---

## 🚀 Como Aplicar (Instalação Nova)

### Passo 1: Instalar MySQL

```bash
apt update
apt install -y mysql-server
systemctl start mysql
systemctl enable mysql
```

### Passo 2: Configurar MySQL

```bash
mysql_secure_installation

# Acessar MySQL
mysql -u root -p
```

**No MySQL:**
```sql
CREATE DATABASE epallet_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'epallet_user'@'localhost' IDENTIFIED BY 'senha_super_segura';
GRANT ALL PRIVILEGES ON epallet_db.* TO 'epallet_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### Passo 3: Instalar Dependências

```bash
cd /root/epallet-2025

# Dependências do sistema
apt install -y python3-dev default-libmysqlclient-dev build-essential pkg-config

# Ativar venv
source venv/bin/activate

# Instalar dependências Python
pip install -r requirements.txt
```

### Passo 4: Configurar .env

```bash
nano /root/epallet-2025/.env
```

**Adicionar:**
```bash
DATABASE_URL=mysql://epallet_user:senha_super_segura@localhost:3306/epallet_db
```

### Passo 5: Inicializar Banco

```bash
cd /root/epallet-2025
source venv/bin/activate

python init_db.py init
python init_db.py create-admin
python popular_tipos.py
```

### Passo 6: Reiniciar Aplicação

```bash
systemctl restart epallet
systemctl status epallet
```

---

## 🔄 Como Migrar (de SQLite para MySQL)

### Passo 1: Fazer Backup do SQLite

```bash
cp /root/epallet-2025/instance/epallet.db /root/backups/epallet_sqlite_$(date +%Y%m%d).db
```

### Passo 2: Instalar e Configurar MySQL

(Seguir passos 1-4 acima)

### Passo 3: Inicializar Estrutura MySQL

```bash
cd /root/epallet-2025
source venv/bin/activate

python init_db.py init
```

### Passo 4: Migrar Dados

```bash
python migrate_sqlite_to_mysql.py instance/epallet.db
```

**O script vai:**
- ✅ Conectar ao SQLite
- ✅ Conectar ao MySQL
- ✅ Listar tabelas
- ✅ Copiar todos os dados
- ✅ Exibir progresso

### Passo 5: Verificar Migração

```bash
# Ver total de registros
mysql -u epallet_user -p epallet_db -e "
SELECT 'users' as tabela, COUNT(*) as total FROM users
UNION ALL SELECT 'vales_pallet', COUNT(*) FROM vales_pallet;
"
```

### Passo 6: Reiniciar Aplicação

```bash
systemctl restart epallet
```

---

## 🔍 Verificações

### Verificar MySQL

```bash
# Status
systemctl status mysql

# Porta
netstat -tlnp | grep 3306

# Bancos
mysql -u root -p -e "SHOW DATABASES;"
```

### Verificar Aplicação

```bash
# Logs
journalctl -u epallet -n 50

# Testar conexão
cd /root/epallet-2025 && source venv/bin/activate && python3 -c "from app import create_app, db; app = create_app(); app.app_context().push(); print(f'Conectado: {db.engine.url}')"

# Acessar aplicação
curl http://127.0.0.1:8000
```

---

## 📊 Vantagens do MySQL

| Vantagem | Descrição |
|----------|-----------|
| **Performance** | Melhor com múltiplos usuários simultâneos |
| **Escalabilidade** | Suporta milhares de conexões |
| **Confiabilidade** | Mais robusto para produção |
| **Backup** | Ferramentas profissionais (mysqldump) |
| **Replicação** | Suporte nativo para alta disponibilidade |
| **Monitoramento** | Ferramentas avançadas disponíveis |

---

## ⚙️ Configurações Adicionadas

### Pool de Conexões

```python
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 10,           # 10 conexões no pool
    'pool_recycle': 3600,      # Reciclar conexões a cada 1h
    'pool_pre_ping': True,     # Verificar conexão antes de usar
    'connect_args': {
        'charset': 'utf8mb4'   # Suporte completo a UTF-8
    }
}
```

**Benefícios:**
- ✅ Reutiliza conexões (mais rápido)
- ✅ Evita conexões mortas
- ✅ Suporte a emojis e caracteres especiais

---

## 🔧 Manutenção

### Backup Automático

```bash
# Criar script
nano /root/backup_mysql.sh
```

**Conteúdo:**
```bash
#!/bin/bash
BACKUP_DIR="/root/backups/mysql"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR
mysqldump -u epallet_user -psenha_super_segura epallet_db | gzip > $BACKUP_DIR/epallet_$DATE.sql.gz
ls -t $BACKUP_DIR/epallet_*.sql.gz | tail -n +31 | xargs -r rm
```

**Agendar:**
```bash
chmod +x /root/backup_mysql.sh
crontab -e
# Adicionar: 0 3 * * * /root/backup_mysql.sh
```

### Otimização

```bash
# Analisar tabelas
mysql -u epallet_user -p epallet_db -e "ANALYZE TABLE users, vales_pallet;"

# Otimizar tabelas
mysql -u epallet_user -p epallet_db -e "OPTIMIZE TABLE users, vales_pallet;"
```

---

## ❌ Troubleshooting

### Erro: "Can't connect to MySQL"

```bash
systemctl start mysql
systemctl status mysql
```

### Erro: "Access denied"

```bash
# Verificar .env
cat /root/epallet-2025/.env | grep DATABASE_URL

# Recriar usuário
mysql -u root -p
DROP USER 'epallet_user'@'localhost';
CREATE USER 'epallet_user'@'localhost' IDENTIFIED BY 'nova_senha';
GRANT ALL PRIVILEGES ON epallet_db.* TO 'epallet_user'@'localhost';
FLUSH PRIVILEGES;
```

### Erro: "mysqlclient install failed"

```bash
# Instalar dependências
apt install -y python3-dev default-libmysqlclient-dev build-essential

# Ou usar PyMySQL
pip install PyMySQL
# Adicionar no run.py: import pymysql; pymysql.install_as_MySQLdb()
```

---

## 📄 Documentação Incluída

1. **GUIA_CONFIGURACAO_MYSQL.md** ⭐ - Guia completo (NOVO)
2. **README_MIGRACAO_MYSQL.md** ⭐ - Este arquivo (NOVO)
3. **migrate_sqlite_to_mysql.py** ⭐ - Script de migração (NOVO)
4. **requirements.txt** - Atualizado com mysqlclient
5. **config/config.py** - Atualizado para MySQL
6. **.env.example** - Atualizado com exemplo MySQL

---

## ✅ Checklist

### Instalação Nova
- [ ] MySQL instalado
- [ ] Banco criado
- [ ] Usuário criado
- [ ] Dependências instaladas
- [ ] .env configurado
- [ ] Banco inicializado
- [ ] Aplicação reiniciada

### Migração do SQLite
- [ ] Backup do SQLite feito
- [ ] MySQL instalado e configurado
- [ ] Estrutura MySQL criada
- [ ] Script de migração executado
- [ ] Dados verificados
- [ ] Aplicação reiniciada
- [ ] Backup automático configurado

---

## 📞 Comandos Rápidos

```bash
# Instalar MySQL
apt install -y mysql-server

# Criar banco e usuário
mysql -u root -p < /root/epallet-2025/setup_mysql.sql

# Instalar dependências
cd /root/epallet-2025 && source venv/bin/activate && pip install -r requirements.txt

# Inicializar banco
python init_db.py init

# Migrar do SQLite
python migrate_sqlite_to_mysql.py instance/epallet.db

# Reiniciar aplicação
systemctl restart epallet

# Ver logs
journalctl -u epallet -f
```

---

**Versão:** 25 (MySQL)  
**Data:** 07/11/2024  
**Sistema:** Epallet - Gestão de Pallets

**Projeto refatorado para MySQL com sucesso!** 🎉
