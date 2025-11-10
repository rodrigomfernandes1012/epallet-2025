# 🪟 Guia Completo - Windows + MySQL na Nuvem

## 📋 Cenário

- **Desenvolvimento:** Windows (local)
- **Banco de Dados:** MySQL na nuvem (Linux)
- **Usuário MySQL:** epallet
- **Senha MySQL:** Rodrigo@101275
- **Banco:** epallet_db

---

## 🚀 Passo a Passo Completo

### Passo 1: Criar Estrutura do Banco de Dados

#### 1.1 Conectar ao MySQL na Nuvem

**Opção A: Via terminal Windows (MySQL Client)**

```cmd
mysql -h SEU_IP_OU_DOMINIO -u epallet -p epallet_db
```

Quando solicitar a senha, digite: `Rodrigo@101275`

**Opção B: Via SSH + MySQL**

```cmd
ssh root@SEU_IP_OU_DOMINIO
mysql -u epallet -p epallet_db
```

#### 1.2 Executar Script SQL

**Método 1: Copiar e Colar (Recomendado)**

1. Abrir o arquivo `create_database_structure.sql`
2. Copiar todo o conteúdo
3. Colar no terminal MySQL
4. Pressionar Enter

**Método 2: Executar via Arquivo**

```bash
# No servidor Linux (via SSH)
mysql -u epallet -p epallet_db < /caminho/para/create_database_structure.sql
```

**Método 3: Via MySQL Workbench**

1. Abrir MySQL Workbench
2. Conectar ao servidor MySQL na nuvem
3. Abrir o arquivo `create_database_structure.sql`
4. Clicar em "Execute" (⚡)

#### 1.3 Verificar Criação

```sql
-- Listar tabelas
SHOW TABLES;

-- Deve mostrar:
-- +---------------------------+
-- | Tables_in_epallet_db      |
-- +---------------------------+
-- | empresas                  |
-- | logs_auditoria            |
-- | motoristas                |
-- | tipos_empresa             |
-- | users                     |
-- | vales_pallet              |
-- +---------------------------+

-- Verificar tipos de empresa
SELECT * FROM tipos_empresa;

-- Deve mostrar:
-- +----+----------------+----------------------------------+-------+
-- | id | nome           | descricao                        | ativo |
-- +----+----------------+----------------------------------+-------+
-- |  1 | Cliente        | Empresa que envia pallets        |     1 |
-- |  2 | Transportadora | Empresa responsável pelo transporte |  1 |
-- |  3 | Destinatário   | Empresa que recebe pallets       |     1 |
-- +----+----------------+----------------------------------+-------+
```

---

### Passo 2: Configurar .env no Windows

#### 2.1 Copiar Arquivo de Exemplo

```cmd
cd C:\TaxiDigital\PROJETOS_PYTHON\flask-argon-system
copy .env.windows .env
```

#### 2.2 Editar .env

Abrir o arquivo `.env` com Notepad++ ou VS Code e editar:

```bash
# Flask
FLASK_APP=run.py
FLASK_ENV=development
DEBUG=True
SECRET_KEY=cole-aqui-a-chave-gerada-abaixo

# Banco de Dados - MySQL na Nuvem
# SUBSTITUA 'SEU_IP_OU_DOMINIO' pelo IP/domínio real
DATABASE_URL=mysql://epallet:Rodrigo@101275@192.168.1.100:3306/epallet_db

# WhatsGw API
WHATSGW_APIKEY=sua-api-key-aqui
WHATSGW_PHONE_NUMBER=5511987654321
```

**Exemplos de DATABASE_URL:**

```bash
# Se o MySQL está em um servidor com IP 192.168.1.100
DATABASE_URL=mysql://epallet:Rodrigo@101275@192.168.1.100:3306/epallet_db

# Se o MySQL está em um domínio
DATABASE_URL=mysql://epallet:Rodrigo@101275@mysql.seudominio.com:3306/epallet_db

# Se o MySQL está na mesma máquina Windows (localhost)
DATABASE_URL=mysql://epallet:Rodrigo@101275@localhost:3306/epallet_db
```

#### 2.3 Gerar SECRET_KEY

```cmd
python -c "import secrets; print(secrets.token_hex(32))"
```

**Exemplo de saída:**
```
a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2
```

Copiar e colar no `.env` no campo `SECRET_KEY`.

---

### Passo 3: Instalar Dependências Python

#### 3.1 Ativar Ambiente Virtual

```cmd
cd C:\TaxiDigital\PROJETOS_PYTHON\flask-argon-system
env\Scripts\activate
```

#### 3.2 Instalar mysqlclient

**Opção A: Via pip (pode dar erro no Windows)**

```cmd
pip install mysqlclient
```

**Se der erro, usar Opção B:**

**Opção B: Usar PyMySQL (mais fácil no Windows)**

```cmd
pip install PyMySQL
```

Depois, editar o arquivo `run.py` e adicionar no início (antes de importar o app):

```python
# No início do arquivo run.py, adicionar:
import pymysql
pymysql.install_as_MySQLdb()

# Depois continua o código normal:
from app import create_app
# ...
```

#### 3.3 Instalar Outras Dependências

```cmd
pip install -r requirements.txt
```

---

### Passo 4: Criar Usuário Administrador

#### 4.1 Executar Script

```cmd
python init_db.py create-admin
```

#### 4.2 Preencher Dados

```
Username: admin
Email: admin@epallet.com.br
Senha: (escolha uma senha forte)
Nome Completo: Administrador do Sistema
```

#### 4.3 Verificar Criação

```sql
-- No MySQL
SELECT id, username, email, nome_completo, ativo FROM users;
```

---

### Passo 5: Testar Aplicação

#### 5.1 Iniciar Servidor

```cmd
python run.py
```

**Deve mostrar:**
```
 * Serving Flask app 'run.py'
 * Debug mode: on
WARNING: This is a development server.
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
```

#### 5.2 Acessar no Navegador

```
http://127.0.0.1:5000
```

#### 5.3 Fazer Login

- **Username:** admin
- **Senha:** (a que você definiu)

---

## 🔍 Verificações

### Verificar Conexão com MySQL

```cmd
python
```

**No Python:**

```python
from app import create_app, db
from app.models import User, TipoEmpresa

app = create_app()
app.app_context().push()

# Testar conexão
print("Testando conexão com MySQL...")
print(f"Banco: {db.engine.url}")

# Verificar tipos de empresa
tipos = TipoEmpresa.query.all()
print(f"\nTipos de empresa: {len(tipos)}")
for tipo in tipos:
    print(f"  - {tipo.nome}")

# Verificar usuários
users = User.query.all()
print(f"\nUsuários: {len(users)}")
for user in users:
    print(f"  - {user.username} ({user.email})")

exit()
```

**Deve mostrar:**
```
Testando conexão com MySQL...
Banco: mysql://epallet:***@192.168.1.100:3306/epallet_db

Tipos de empresa: 3
  - Cliente
  - Transportadora
  - Destinatário

Usuários: 1
  - admin (admin@epallet.com.br)
```

---

## ❌ Troubleshooting

### Erro: "Can't connect to MySQL server"

**Causa:** Não consegue conectar ao servidor MySQL.

**Soluções:**

1. **Verificar IP/Domínio no .env**
   ```cmd
   type .env | findstr DATABASE_URL
   ```

2. **Verificar se MySQL está rodando no servidor**
   ```bash
   # Via SSH no servidor
   systemctl status mysql
   ```

3. **Verificar firewall (porta 3306)**
   ```bash
   # No servidor Linux
   ufw status
   ufw allow 3306/tcp
   ```

4. **Testar conexão**
   ```cmd
   mysql -h SEU_IP -u epallet -p
   ```

---

### Erro: "Access denied for user 'epallet'@'IP'"

**Causa:** Usuário não tem permissão para conectar remotamente.

**Solução:**

```bash
# No servidor MySQL (via SSH)
mysql -u root -p
```

**No MySQL:**

```sql
-- Permitir conexão remota
GRANT ALL PRIVILEGES ON epallet_db.* TO 'epallet'@'%' IDENTIFIED BY 'Rodrigo@101275';
FLUSH PRIVILEGES;

-- Verificar
SELECT user, host FROM mysql.user WHERE user = 'epallet';

EXIT;
```

**Editar configuração do MySQL:**

```bash
nano /etc/mysql/mysql.conf.d/mysqld.cnf
```

**Alterar:**
```
# De:
bind-address = 127.0.0.1

# Para:
bind-address = 0.0.0.0
```

**Reiniciar MySQL:**
```bash
systemctl restart mysql
```

---

### Erro: "No module named 'MySQLdb'"

**Causa:** mysqlclient não instalado ou falhou.

**Solução: Usar PyMySQL**

```cmd
pip install PyMySQL
```

**Editar `run.py`:**

```python
# Adicionar no início do arquivo
import pymysql
pymysql.install_as_MySQLdb()

# Resto do código...
from app import create_app
# ...
```

---

### Erro: "Unknown database 'epallet_db'"

**Causa:** Banco não foi criado.

**Solução:**

```bash
# No servidor MySQL
mysql -u root -p
```

```sql
CREATE DATABASE epallet_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

Depois executar o script SQL novamente.

---

## 📊 Estrutura Criada

### Tabelas

| Tabela | Descrição | Registros Iniciais |
|--------|-----------|-------------------|
| `tipos_empresa` | Tipos de empresa | 3 (Cliente, Transportadora, Destinatário) |
| `users` | Usuários do sistema | 0 (criar com init_db.py) |
| `empresas` | Empresas cadastradas | 0 |
| `motoristas` | Motoristas cadastrados | 0 |
| `vales_pallet` | Vales de pallet | 0 |
| `logs_auditoria` | Logs de auditoria | 0 |

### Relacionamentos

```
users
  ├─> empresas (criado_por_id)
  ├─> motoristas (cadastrado_por_id)
  └─> vales_pallet (criado_por_id)

empresas
  ├─> tipos_empresa (tipo_empresa_id)
  ├─> motoristas (empresa_id)
  ├─> vales_pallet (cliente_id)
  ├─> vales_pallet (transportadora_id)
  └─> vales_pallet (destinatario_id)

motoristas
  └─> vales_pallet (motorista_id)
```

---

## 🔧 Comandos Úteis

### Windows

```cmd
# Ativar ambiente virtual
env\Scripts\activate

# Desativar ambiente virtual
deactivate

# Executar aplicação
python run.py

# Criar admin
python init_db.py create-admin

# Testar conexão
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); print(db.engine.url)"
```

### MySQL (via SSH no servidor)

```bash
# Conectar ao MySQL
mysql -u epallet -p epallet_db

# Ver tabelas
SHOW TABLES;

# Ver estrutura de uma tabela
DESCRIBE users;

# Contar registros
SELECT COUNT(*) FROM users;

# Fazer backup
mysqldump -u epallet -p epallet_db > backup.sql

# Restaurar backup
mysql -u epallet -p epallet_db < backup.sql
```

---

## ✅ Checklist

- [ ] MySQL rodando no servidor Linux
- [ ] Porta 3306 aberta no firewall
- [ ] Usuário 'epallet' com permissão remota
- [ ] Script SQL executado com sucesso
- [ ] Tabelas criadas (6 tabelas)
- [ ] Tipos de empresa inseridos (3 registros)
- [ ] Arquivo .env configurado no Windows
- [ ] DATABASE_URL com IP/domínio correto
- [ ] SECRET_KEY gerada
- [ ] PyMySQL instalado (ou mysqlclient)
- [ ] Ambiente virtual ativado
- [ ] Dependências instaladas
- [ ] Usuário admin criado
- [ ] Aplicação rodando
- [ ] Login funcionando

---

## 📄 Arquivos Importantes

1. **create_database_structure.sql** - Script SQL completo
2. **.env.windows** - Exemplo de configuração
3. **.env** - Sua configuração (criar a partir do .env.windows)
4. **run.py** - Arquivo principal da aplicação
5. **init_db.py** - Script para criar admin

---

## 🎯 Próximos Passos

Após concluir este guia:

1. ✅ Banco de dados criado e funcionando
2. ✅ Aplicação rodando no Windows
3. ✅ Conectada ao MySQL na nuvem
4. ⏭️ Começar a usar o sistema
5. ⏭️ Cadastrar empresas
6. ⏭️ Cadastrar motoristas
7. ⏭️ Criar vales pallet

---

**Versão:** 26 (Windows + MySQL Nuvem)  
**Data:** 10/11/2024  
**Sistema:** Epallet - Gestão de Pallets

Tudo pronto para desenvolvimento no Windows com banco MySQL na nuvem! 🎉
