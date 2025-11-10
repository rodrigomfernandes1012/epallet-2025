# 🚀 Guia Rápido: Executar Script SQL no MySQL

## ❌ Problema

A tabela `logs_auditoria` está com estrutura incorreta ou incompleta no MySQL, causando o erro:

```
Unknown column 'logs_auditoria.ip_origem' in 'field list'
```

---

## ✅ Solução

Executar o script SQL corrigido no servidor MySQL.

---

## 📋 Passo a Passo

### Opção 1: Via SSH (Recomendado)

#### 1. Conectar ao Servidor

```bash
ssh usuario@74.50.123.210
```

#### 2. Fazer Upload do Script

**No seu Windows, enviar o arquivo via SCP:**

```cmd
scp create_database_structure.sql usuario@74.50.123.210:/tmp/
```

#### 3. Executar no Servidor

```bash
mysql -u epallet -p epallet_db < /tmp/create_database_structure.sql
# Senha: Rodrigo@101275
```

---

### Opção 2: Via MySQL Workbench (Mais Fácil)

#### 1. Abrir MySQL Workbench

#### 2. Conectar ao Servidor

- Host: `74.50.123.210`
- Port: `3306`
- Username: `epallet`
- Password: `Rodrigo@101275`
- Default Schema: `epallet_db`

#### 3. Abrir o Script

- File → Open SQL Script
- Selecionar: `create_database_structure.sql`

#### 4. Executar

- Clicar no ícone de raio ⚡ (Execute)
- Ou pressionar `Ctrl+Shift+Enter`

#### 5. Verificar

```sql
SHOW TABLES;
DESCRIBE logs_auditoria;
```

---

### Opção 3: Via Linha de Comando MySQL (Direto)

#### 1. Conectar ao MySQL

```bash
mysql -h 74.50.123.210 -u epallet -p epallet_db
# Senha: Rodrigo@101275
```

#### 2. Limpar Tabelas Antigas (se existirem)

```sql
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS logs_auditoria;
DROP TABLE IF EXISTS vales_pallet;
DROP TABLE IF EXISTS motoristas;
DROP TABLE IF EXISTS empresas;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS tipos_empresa;

SET FOREIGN_KEY_CHECKS = 1;
```

#### 3. Copiar e Colar o Script SQL Completo

**Abrir o arquivo `create_database_structure.sql` no Notepad, copiar TODO o conteúdo e colar no terminal MySQL.**

#### 4. Verificar

```sql
SHOW TABLES;

SELECT 
    TABLE_NAME as 'Tabela',
    TABLE_ROWS as 'Registros'
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'epallet_db'
ORDER BY TABLE_NAME;

DESCRIBE logs_auditoria;
```

**Deve mostrar:**

```
+-------------------+
| Tabela            |
+-------------------+
| empresas          |
| logs_auditoria    |
| motoristas        |
| tipos_empresa     |
| users             |
| vales_pallet      |
+-------------------+
```

---

## 🧪 Testar no Windows

### 1. Testar Conexão

```cmd
python
```

**No Python:**

```python
import pymysql
pymysql.install_as_MySQLdb()

from app import create_app, db
app = create_app()
app.app_context().push()

# Testar query
from app.models import LogAuditoria
count = LogAuditoria.query.count()
print(f"Logs no banco: {count}")

exit()
```

**Deve funcionar sem erros!**

### 2. Rodar Aplicação

```cmd
python run.py
```

### 3. Acessar

```
http://127.0.0.1:5000
```

**Fazer login e verificar dashboard.**

---

## ✅ Checklist

- [ ] Script SQL atualizado (com `ip_origem`)
- [ ] Conectado ao MySQL no servidor
- [ ] Tabelas antigas removidas
- [ ] Script SQL executado
- [ ] 6 tabelas criadas
- [ ] 3 tipos de empresa inseridos
- [ ] Estrutura de `logs_auditoria` correta
- [ ] Teste no Windows OK
- [ ] Aplicação rodando sem erros

---

## 📊 Estrutura Correta da Tabela logs_auditoria

```sql
CREATE TABLE logs_auditoria (
    id INT AUTO_INCREMENT PRIMARY KEY,
    modulo VARCHAR(100) NOT NULL,
    acao VARCHAR(50) NOT NULL,
    descricao TEXT NOT NULL,
    operacao_sql VARCHAR(20),
    tabela_afetada VARCHAR(100),
    registro_id INT,
    dados_anteriores TEXT,
    dados_novos TEXT,
    usuario_id INT,
    usuario_nome VARCHAR(150),
    ip_origem VARCHAR(45) NOT NULL,  -- ✅ CORRIGIDO!
    user_agent VARCHAR(500),
    sucesso BOOLEAN NOT NULL DEFAULT TRUE,
    mensagem_erro TEXT,
    data_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_modulo (modulo),
    INDEX idx_acao (acao),
    INDEX idx_usuario (usuario_id),
    INDEX idx_data_hora (data_hora),
    INDEX idx_sucesso (sucesso),
    INDEX idx_tabela (tabela_afetada),
    FOREIGN KEY (usuario_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Colunas principais:**
- ✅ `ip_origem` (não `ip_address`)
- ✅ `user_agent` VARCHAR(500) (não TEXT)
- ✅ Sem coluna `tempo_execucao`

---

## ❌ Troubleshooting

### Erro: "Access denied"

**Solução:**

```sql
-- No MySQL como root
GRANT ALL PRIVILEGES ON epallet_db.* TO 'epallet'@'%';
FLUSH PRIVILEGES;
```

### Erro: "Can't connect"

**Verificar:**
1. Firewall liberado na porta 3306
2. MySQL configurado para aceitar conexões remotas
3. IP correto no .env

### Erro: "Table already exists"

**Solução:**

```sql
DROP TABLE IF EXISTS logs_auditoria;
-- Depois executar o CREATE TABLE novamente
```

---

## 📞 Comandos Rápidos

```bash
# Conectar
mysql -h 74.50.123.210 -u epallet -p epallet_db

# Limpar tudo
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS logs_auditoria, vales_pallet, motoristas, empresas, users, tipos_empresa;
SET FOREIGN_KEY_CHECKS = 1;

# Executar script
SOURCE /tmp/create_database_structure.sql;

# Verificar
SHOW TABLES;
DESCRIBE logs_auditoria;

# Sair
EXIT;
```

---

**Versão:** 28 (Script SQL Corrigido)  
**Data:** 10/11/2024  
**Sistema:** Epallet - Gestão de Pallets

Execute o script SQL e teste novamente! 🚀
