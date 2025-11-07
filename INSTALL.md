# Guia de Instalação Rápida

## 🚀 Instalação Rápida (Desenvolvimento)

### 1. Instalar Dependências

```bash
cd flask-argon-system
pip3 install -r requirements.txt
```

### 2. Configurar Banco de Dados (SQLite para testes)

O arquivo `.env` já está configurado para usar SQLite em desenvolvimento:

```bash
# Verificar o arquivo .env
cat .env
```

### 3. Inicializar o Banco de Dados

```bash
# Criar as tabelas no banco
python3 << EOF
from app import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
    print("Banco de dados criado com sucesso!")
EOF
```

### 4. Executar a Aplicação

```bash
python3 run.py
```

A aplicação estará disponível em: **http://localhost:5000**

### 5. Criar Primeiro Usuário

Acesse: **http://localhost:5000/auth/register**

Preencha o formulário com:
- Nome Completo: Seu nome
- Nome de Usuário: admin
- Email: admin@sistema.com
- Senha: admin123
- Confirmar Senha: admin123

### 6. Fazer Login

Acesse: **http://localhost:5000/auth/login**

Use as credenciais criadas no passo anterior.

---

## 🐘 Instalação com PostgreSQL (Produção)

### 1. Instalar PostgreSQL

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

**macOS:**
```bash
brew install postgresql
brew services start postgresql
```

### 2. Criar Banco de Dados

```bash
# Acessar o PostgreSQL
sudo -u postgres psql

# Criar banco e usuário
CREATE DATABASE flask_argon_db;
CREATE USER flask_user WITH PASSWORD 'senha_segura';
GRANT ALL PRIVILEGES ON DATABASE flask_argon_db TO flask_user;
\q
```

### 3. Configurar Variáveis de Ambiente

Edite o arquivo `.env`:

```env
FLASK_APP=run.py
FLASK_ENV=production
SECRET_KEY=gere-uma-chave-secreta-forte-aqui
DATABASE_URL=postgresql://flask_user:senha_segura@localhost:5432/flask_argon_db
```

### 4. Instalar Dependências

```bash
pip3 install -r requirements.txt
```

### 5. Executar Migrações

```bash
# Inicializar migrações
flask db init

# Criar migração inicial
flask db migrate -m "Initial migration"

# Aplicar migrações
flask db upgrade
```

### 6. Executar com Gunicorn

```bash
# Instalar Gunicorn
pip3 install gunicorn

# Executar
gunicorn -w 4 -b 0.0.0.0:8000 run:app
```

---

## 🔧 Solução de Problemas

### Erro: "No module named 'flask'"

```bash
pip3 install -r requirements.txt
```

### Erro: "Could not locate a Flask application"

```bash
export FLASK_APP=run.py
```

### Erro: "Database connection failed"

Verifique se o PostgreSQL está rodando:

```bash
sudo systemctl status postgresql
```

Verifique as credenciais no arquivo `.env`.

### Porta 5000 já está em uso

Altere a porta no arquivo `run.py` ou use:

```bash
PORT=8080 python3 run.py
```

---

## 📦 Estrutura de Arquivos Importantes

```
flask-argon-system/
├── run.py                    # Arquivo principal para executar
├── .env                      # Configurações (não commitar!)
├── requirements.txt          # Dependências Python
├── app/
│   ├── __init__.py          # Inicialização do Flask
│   ├── models.py            # Modelos do banco de dados
│   └── routes/              # Rotas da aplicação
└── README.md                # Documentação completa
```

---

## ✅ Checklist de Instalação

- [ ] Python 3.11+ instalado
- [ ] Dependências instaladas (`pip3 install -r requirements.txt`)
- [ ] Arquivo `.env` configurado
- [ ] Banco de dados criado
- [ ] Tabelas criadas (`db.create_all()` ou migrações)
- [ ] Aplicação rodando (`python3 run.py`)
- [ ] Primeiro usuário criado
- [ ] Login funcionando

---

## 🎯 Próximos Passos

1. Acesse o dashboard
2. Cadastre sua primeira empresa
3. Explore as funcionalidades
4. Personalize conforme necessário

---

## 📞 Precisa de Ajuda?

- Leia o `README.md` completo
- Verifique os logs de erro no terminal
- Consulte a documentação do Flask: https://flask.palletsprojects.com/
