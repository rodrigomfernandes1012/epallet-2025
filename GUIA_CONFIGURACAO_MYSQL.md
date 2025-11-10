# 🗄️ Guia Completo - Configuração MySQL

## 📋 Mudanças Implementadas

O projeto foi refatorado para usar **MySQL** ao invés de SQLite:

✅ **Driver MySQL** adicionado ao `requirements.txt`  
✅ **Configuração padrão** alterada para MySQL  
✅ **Pool de conexões** configurado  
✅ **Charset UTF-8** configurado  
✅ **Script de migração** criado  

---

## 🚀 Instalação e Configuração

### Passo 1: Instalar MySQL no Ubuntu

```bash
# Atualizar repositórios
apt update

# Instalar MySQL Server
apt install -y mysql-server

# Verificar status
systemctl status mysql

# Iniciar MySQL (se não estiver rodando)
systemctl start mysql

# Habilitar para iniciar no boot
systemctl enable mysql
```

---

### Passo 2: Configurar MySQL

#### 2.1 Executar Configuração Segura

```bash
mysql_secure_installation
```

**Respostas sugeridas:**
- **VALIDATE PASSWORD:** `N` (não, para facilitar)
- **Remove anonymous users:** `Y` (sim)
- **Disallow root login remotely:** `Y` (sim)
- **Remove test database:** `Y` (sim)
- **Reload privilege tables:** `Y` (sim)

#### 2.2 Definir Senha do Root

```bash
# Acessar MySQL
mysql

# Dentro do MySQL
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'senha_root_segura';
FLUSH PRIVILEGES;
EXIT;
```

---

### Passo 3: Criar Banco de Dados e Usuário

```bash
# Acessar MySQL como root
mysql -u root -p
# Digite a senha definida acima
```

**Dentro do MySQL:**

```sql
-- Criar banco de dados
CREATE DATABASE epallet_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Criar usuário
CREATE USER 'epallet_user'@'localhost' IDENTIFIED BY 'senha_super_segura_aqui';

-- Conceder permissões
GRANT ALL PRIVILEGES ON epallet_db.* TO 'epallet_user'@'localhost';

-- Aplicar mudanças
FLUSH PRIVILEGES;

-- Verificar
SHOW DATABASES;
SELECT user, host FROM mysql.user WHERE user = 'epallet_user';

-- Sair
EXIT;
```

---

### Passo 4: Instalar Dependências Python

```bash
cd /root/epallet-2025

# Ativar ambiente virtual
source venv/bin/activate

# Instalar dependências do sistema para mysqlclient
apt install -y python3-dev default-libmysqlclient-dev build-essential pkg-config

# Instalar dependências Python
pip install -r requirements.txt
```

**Se houver erro ao instalar mysqlclient:**

```bash
# Alternativa: usar PyMySQL
pip uninstall mysqlclient
pip install PyMySQL

# Adicionar no início do run.py:
# import pymysql
# pymysql.install_as_MySQLdb()
```

---

### Passo 5: Configurar .env

```bash
nano /root/epallet-2025/.env
```

**Atualizar DATABASE_URL:**

```bash
# ============================================
# Banco de Dados - MySQL
# ============================================

# Formato: mysql://usuario:senha@host:porta/nome_banco
DATABASE_URL=mysql://epallet_user:senha_super_segura_aqui@localhost:3306/epallet_db
```

**Exemplo completo do .env:**

```bash
# Flask
FLASK_APP=run.py
FLASK_ENV=production
SECRET_KEY=gere-chave-com-comando-abaixo
DEBUG=False
TESTING=False

# Banco de Dados - MySQL
DATABASE_URL=mysql://epallet_user:senha_super_segura_aqui@localhost:3306/epallet_db

# WhatsGw API
WHATSGW_APIKEY=sua-api-key
WHATSGW_PHONE_NUMBER=5511987654321
```

**Gerar SECRET_KEY:**

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

---

### Passo 6: Inicializar Banco de Dados

#### Opção A: Banco Novo (sem dados anteriores)

```bash
cd /root/epallet-2025
source venv/bin/activate

# Inicializar banco
python init_db.py init

# Criar admin
python init_db.py create-admin

# Popular tipos de empresa
python popular_tipos.py
```

#### Opção B: Migrar do SQLite

```bash
cd /root/epallet-2025
source venv/bin/activate

# Primeiro, inicializar estrutura do MySQL
python init_db.py init

# Depois, migrar dados do SQLite
python migrate_sqlite_to_mysql.py instance/epallet.db

# Verificar migração
mysql -u epallet_user -p epallet_db -e "SELECT COUNT(*) FROM users; SELECT COUNT(*) FROM vales_pallet;"
```

---

### Passo 7: Testar Conexão

```bash
cd /root/epallet-2025
source venv/bin/activate
python3
```

**No Python:**

```python
from app import create_app, db
from app.models import User

app = create_app()
app.app_context().push()

# Testar conexão
print("Testando conexão com MySQL...")
users = User.query.all()
print(f"Total de usuários: {len(users)}")

# Verificar banco
print(f"Banco: {db.engine.url}")

exit()
```

**Deve mostrar:**
```
Testando conexão com MySQL...
Total de usuários: 1
Banco: mysql://epallet_user:***@localhost:3306/epallet_db
```

---

### Passo 8: Reiniciar Aplicação

```bash
# Reiniciar serviço
systemctl restart epallet

# Verificar status
systemctl status epallet

# Ver logs
journalctl -u epallet -n 50
```

---

## 🔍 Verificações

### Verificar MySQL Rodando

```bash
# Status do serviço
systemctl status mysql

# Processos
ps aux | grep mysql

# Porta 3306
netstat -tlnp | grep 3306
```

### Verificar Banco de Dados

```bash
# Listar bancos
mysql -u root -p -e "SHOW DATABASES;"

# Ver tabelas
mysql -u epallet_user -p epallet_db -e "SHOW TABLES;"

# Contar registros
mysql -u epallet_user -p epallet_db -e "
SELECT 
    'users' as tabela, COUNT(*) as total FROM users
UNION ALL
SELECT 'empresas', COUNT(*) FROM empresas
UNION ALL
SELECT 'motoristas', COUNT(*) FROM motoristas
UNION ALL
SELECT 'vales_pallet', COUNT(*) FROM vales_pallet;
"
```

### Verificar Configuração da Aplicação

```bash
# Ver DATABASE_URL
cat /root/epallet-2025/.env | grep DATABASE_URL

# Testar conexão
cd /root/epallet-2025 && source venv/bin/activate && python3 -c "from app import create_app, db; app = create_app(); app.app_context().push(); print(f'Conectado: {db.engine.url}')"
```

---

## 🔧 Manutenção

### Backup do Banco de Dados

```bash
# Criar script de backup
nano /root/backup_mysql.sh
```

**Conteúdo:**

```bash
#!/bin/bash

# Configurações
BACKUP_DIR="/root/backups/mysql"
DB_NAME="epallet_db"
DB_USER="epallet_user"
DB_PASS="senha_super_segura_aqui"
DATE=$(date +%Y%m%d_%H%M%S)

# Criar diretório
mkdir -p $BACKUP_DIR

# Fazer backup
mysqldump -u $DB_USER -p$DB_PASS $DB_NAME > $BACKUP_DIR/epallet_$DATE.sql

# Comprimir
gzip $BACKUP_DIR/epallet_$DATE.sql

# Manter apenas últimos 30 backups
ls -t $BACKUP_DIR/epallet_*.sql.gz | tail -n +31 | xargs -r rm

echo "Backup concluído: epallet_$DATE.sql.gz"
```

**Dar permissão e agendar:**

```bash
# Permissão
chmod +x /root/backup_mysql.sh

# Testar
/root/backup_mysql.sh

# Agendar backup diário às 3h
crontab -e
# Adicionar: 0 3 * * * /root/backup_mysql.sh >> /root/backup.log 2>&1
```

### Restaurar Backup

```bash
# Descompactar
gunzip /root/backups/mysql/epallet_20241107_030000.sql.gz

# Restaurar
mysql -u epallet_user -p epallet_db < /root/backups/mysql/epallet_20241107_030000.sql

# Reiniciar aplicação
systemctl restart epallet
```

### Otimizar Banco de Dados

```bash
# Analisar tabelas
mysql -u epallet_user -p epallet_db -e "ANALYZE TABLE users, empresas, motoristas, vales_pallet, logs;"

# Otimizar tabelas
mysql -u epallet_user -p epallet_db -e "OPTIMIZE TABLE users, empresas, motoristas, vales_pallet, logs;"
```

---

## ❌ Troubleshooting

### Erro: "Can't connect to MySQL server"

**Solução:**

```bash
# Verificar se MySQL está rodando
systemctl status mysql

# Iniciar MySQL
systemctl start mysql

# Ver logs
journalctl -u mysql -n 50
```

### Erro: "Access denied for user"

**Solução:**

```bash
# Verificar usuário e senha no .env
cat /root/epallet-2025/.env | grep DATABASE_URL

# Recriar usuário
mysql -u root -p
DROP USER 'epallet_user'@'localhost';
CREATE USER 'epallet_user'@'localhost' IDENTIFIED BY 'nova_senha';
GRANT ALL PRIVILEGES ON epallet_db.* TO 'epallet_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;

# Atualizar .env
nano /root/epallet-2025/.env
# Alterar DATABASE_URL com nova senha

# Reiniciar aplicação
systemctl restart epallet
```

### Erro: "Unknown database 'epallet_db'"

**Solução:**

```bash
# Criar banco
mysql -u root -p -e "CREATE DATABASE epallet_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# Inicializar
cd /root/epallet-2025 && source venv/bin/activate && python init_db.py init
```

### Erro: "mysqlclient installation failed"

**Solução:**

```bash
# Instalar dependências
apt install -y python3-dev default-libmysqlclient-dev build-essential pkg-config

# Tentar novamente
pip install mysqlclient

# Se ainda falhar, usar PyMySQL
pip install PyMySQL

# Adicionar no run.py (antes de criar app):
# import pymysql
# pymysql.install_as_MySQLdb()
```

---

## 📊 Comparação: SQLite vs MySQL

| Recurso | SQLite | MySQL |
|---------|--------|-------|
| **Performance** | Boa para poucos usuários | Excelente para muitos usuários |
| **Concorrência** | Limitada | Alta |
| **Escalabilidade** | Baixa | Alta |
| **Backup** | Copiar arquivo | Dump SQL |
| **Replicação** | Não | Sim |
| **Usuários simultâneos** | ~10 | Milhares |
| **Tamanho máximo** | ~140 TB | ~64 TB por tabela |
| **Ideal para** | Desenvolvimento | Produção |

---

## ✅ Checklist de Migração

- [ ] MySQL instalado e rodando
- [ ] Banco de dados criado
- [ ] Usuário criado com permissões
- [ ] Dependências Python instaladas
- [ ] .env configurado com DATABASE_URL
- [ ] Banco inicializado ou migrado
- [ ] Conexão testada
- [ ] Aplicação reiniciada
- [ ] Backup configurado
- [ ] Logs verificados

---

## 🎯 Vantagens do MySQL

✅ **Melhor performance** com múltiplos usuários  
✅ **Maior confiabilidade** em produção  
✅ **Suporte a transações** complexas  
✅ **Replicação** para alta disponibilidade  
✅ **Backup** mais robusto  
✅ **Escalabilidade** horizontal  
✅ **Monitoramento** avançado  

---

## 📞 Comandos Rápidos

```bash
# Ver status MySQL
systemctl status mysql

# Acessar MySQL
mysql -u epallet_user -p epallet_db

# Ver tabelas
mysql -u epallet_user -p epallet_db -e "SHOW TABLES;"

# Contar registros
mysql -u epallet_user -p epallet_db -e "SELECT COUNT(*) FROM vales_pallet;"

# Fazer backup
mysqldump -u epallet_user -p epallet_db > backup.sql

# Restaurar backup
mysql -u epallet_user -p epallet_db < backup.sql

# Reiniciar aplicação
systemctl restart epallet

# Ver logs
journalctl -u epallet -f
```

---

**Versão:** 25 (MySQL)  
**Data:** 07/11/2024  
**Sistema:** Epallet - Gestão de Pallets
