# 🪟 Guia de Instalação - Windows

## 📋 Pré-requisitos

### 1. Instalar Python

1. Baixe o Python 3.11 ou superior: https://www.python.org/downloads/
2. **IMPORTANTE**: Marque a opção "Add Python to PATH" durante a instalação
3. Verifique a instalação abrindo o CMD e digitando:
   ```cmd
   python --version
   ```

### 2. Instalar Git (Opcional)

- Baixe em: https://git-scm.com/download/win
- Útil para controle de versão

---

## 🚀 Instalação Rápida (Método 1 - Recomendado)

### Passo 1: Extrair o projeto

1. Extraia o arquivo `flask-argon-system.zip`
2. Abra a pasta extraída

### Passo 2: Executar configuração automática

1. Clique duas vezes em `setup.bat`
2. Aguarde a instalação das dependências
3. O banco de dados será criado automaticamente

### Passo 3: Executar o sistema

1. Clique duas vezes em `run.bat`
2. Acesse: http://localhost:5000

**Pronto! O sistema está rodando!**

---

## 🔧 Instalação Manual (Método 2)

### Passo 1: Abrir o Prompt de Comando

1. Pressione `Win + R`
2. Digite `cmd` e pressione Enter
3. Navegue até a pasta do projeto:
   ```cmd
   cd C:\caminho\para\flask-argon-system
   ```

### Passo 2: Criar ambiente virtual

```cmd
python -m venv venv
```

### Passo 3: Ativar ambiente virtual

```cmd
venv\Scripts\activate
```

Você verá `(venv)` no início da linha do prompt.

### Passo 4: Instalar dependências

```cmd
pip install -r requirements.txt
```

### Passo 5: Inicializar banco de dados

```cmd
python init_db.py init
```

### Passo 6: Executar o sistema

```cmd
python run.py
```

Acesse: http://localhost:5000

---

## 👤 Criar Primeiro Usuário

### Opção 1: Via Interface Web

1. Acesse: http://localhost:5000/auth/register
2. Preencha o formulário:
   - Nome Completo: Seu nome
   - Nome de Usuário: admin
   - Email: admin@sistema.com
   - Senha: admin123
   - Confirmar Senha: admin123
3. Clique em "Cadastrar"

### Opção 2: Via Script

```cmd
python init_db.py create-admin
```

Siga as instruções na tela.

---

## 📂 Estrutura de Arquivos

```
flask-argon-system/
├── setup.bat              # Configuração automática (Windows)
├── install.bat            # Instalar dependências (Windows)
├── run.bat                # Executar servidor (Windows)
├── init_db.bat            # Gerenciar banco de dados (Windows)
├── deploy.sh              # Script de deploy (Ubuntu)
├── run.py                 # Executar servidor (Python)
├── init_db.py             # Gerenciar banco de dados (Python)
├── requirements.txt       # Dependências
├── .env                   # Configurações
├── README.md              # Documentação completa
└── app/                   # Código da aplicação
```

---

## 🎯 Scripts Disponíveis (Windows)

### setup.bat
Configuração completa automática:
- Cria ambiente virtual
- Instala dependências
- Inicializa banco de dados

```cmd
setup.bat
```

### install.bat
Apenas instala as dependências:

```cmd
install.bat
```

### run.bat
Executa o servidor Flask:

```cmd
run.bat
```

### init_db.bat
Gerencia o banco de dados:

```cmd
init_db.bat init          # Criar tabelas
init_db.bat create-admin  # Criar usuário admin
init_db.bat reset         # Resetar banco (APAGA TUDO!)
```

---

## 🔄 Uso Diário

### Iniciar o sistema

**Método 1 (Simples):**
- Clique duas vezes em `run.bat`

**Método 2 (Manual):**
```cmd
cd C:\caminho\para\flask-argon-system
venv\Scripts\activate
python run.py
```

### Parar o sistema

- Pressione `Ctrl + C` no terminal
- Ou feche a janela do CMD

---

## 🗄️ Configuração do Banco de Dados

### SQLite (Padrão - Desenvolvimento)

Já está configurado no `.env`:
```env
DATABASE_URL=sqlite:///app.db
```

**Vantagens:**
- ✅ Não precisa instalar nada
- ✅ Perfeito para desenvolvimento
- ✅ Arquivo único (app.db)

**Desvantagens:**
- ❌ Não recomendado para produção
- ❌ Limitações de concorrência

### PostgreSQL (Recomendado para Produção)

#### 1. Instalar PostgreSQL

Baixe em: https://www.postgresql.org/download/windows/

Durante a instalação:
- Defina uma senha para o usuário `postgres`
- Anote a porta (padrão: 5432)

#### 2. Criar Banco de Dados

Abra o **pgAdmin** ou **SQL Shell (psql)**:

```sql
CREATE DATABASE flask_argon_db;
CREATE USER flask_user WITH PASSWORD 'senha_segura';
GRANT ALL PRIVILEGES ON DATABASE flask_argon_db TO flask_user;
```

#### 3. Atualizar .env

Edite o arquivo `.env`:

```env
DATABASE_URL=postgresql://flask_user:senha_segura@localhost:5432/flask_argon_db
```

#### 4. Inicializar Banco

```cmd
python init_db.py init
```

---

## 🌐 Acessar de Outros Dispositivos na Rede

### 1. Descobrir seu IP local

```cmd
ipconfig
```

Procure por "Endereço IPv4" (ex: 192.168.1.100)

### 2. Permitir no Firewall

1. Abra "Firewall do Windows"
2. Clique em "Configurações Avançadas"
3. Clique em "Regras de Entrada"
4. Clique em "Nova Regra"
5. Selecione "Porta" → Próximo
6. Digite "5000" → Próximo
7. Selecione "Permitir conexão" → Próximo
8. Marque todas as opções → Próximo
9. Dê um nome (ex: "Flask Server") → Concluir

### 3. Editar run.py

Altere a linha:
```python
host = os.environ.get('HOST', '0.0.0.0')
```

### 4. Acessar de outros dispositivos

No navegador de outro dispositivo na mesma rede:
```
http://192.168.1.100:5000
```

---

## 🐛 Solução de Problemas

### "python não é reconhecido como comando"

**Solução:**
1. Reinstale o Python
2. Marque "Add Python to PATH"
3. Ou adicione manualmente ao PATH:
   - Painel de Controle → Sistema → Configurações Avançadas
   - Variáveis de Ambiente → PATH
   - Adicione: `C:\Python311\` e `C:\Python311\Scripts\`

### "pip não é reconhecido como comando"

**Solução:**
```cmd
python -m pip install --upgrade pip
```

### "Porta 5000 já está em uso"

**Solução 1:** Feche outros programas usando a porta

**Solução 2:** Altere a porta no `.env`:
```env
PORT=8080
```

### "Erro ao conectar ao banco de dados"

**Solução:**
1. Verifique se o PostgreSQL está rodando
2. Verifique as credenciais no `.env`
3. Use SQLite para testes:
   ```env
   DATABASE_URL=sqlite:///app.db
   ```

### "ModuleNotFoundError: No module named 'flask'"

**Solução:**
```cmd
pip install -r requirements.txt
```

### Ambiente virtual não ativa

**Solução:**
```cmd
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
venv\Scripts\activate
```

---

## 📝 Variáveis de Ambiente (.env)

Edite o arquivo `.env` para configurar:

```env
# Modo de execução
FLASK_ENV=development          # development ou production

# Chave secreta (MUDE EM PRODUÇÃO!)
SECRET_KEY=sua-chave-secreta-aqui

# Banco de dados
DATABASE_URL=sqlite:///app.db  # SQLite (desenvolvimento)
# DATABASE_URL=postgresql://user:pass@localhost:5432/db  # PostgreSQL

# Porta do servidor
PORT=5000

# Host
HOST=127.0.0.1                 # Apenas local
# HOST=0.0.0.0                 # Acessível na rede
```

---

## 🚀 Deploy no Ubuntu (Produção)

Quando estiver pronto para publicar no Ubuntu:

1. Copie o projeto para o servidor Ubuntu
2. Execute o script de deploy:
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

O script irá:
- ✅ Instalar dependências do sistema
- ✅ Configurar PostgreSQL
- ✅ Criar ambiente virtual
- ✅ Instalar Gunicorn
- ✅ Criar serviço systemd
- ✅ Configurar para iniciar automaticamente

Veja mais detalhes em: `DEPLOY_UBUNTU.md`

---

## ✅ Checklist de Instalação

- [ ] Python 3.11+ instalado
- [ ] Python adicionado ao PATH
- [ ] Projeto extraído
- [ ] Executado `setup.bat` ou instalação manual
- [ ] Banco de dados inicializado
- [ ] Primeiro usuário criado
- [ ] Sistema rodando em http://localhost:5000
- [ ] Login funcionando

---

## 📞 Precisa de Ajuda?

1. Verifique o `README.md` para documentação completa
2. Veja os logs de erro no terminal
3. Consulte a documentação do Flask: https://flask.palletsprojects.com/

---

## 🎓 Dicas para Desenvolvedores

### Ativar ambiente virtual sempre

Antes de trabalhar no projeto:
```cmd
cd C:\caminho\para\flask-argon-system
venv\Scripts\activate
```

### Instalar novas dependências

```cmd
pip install nome-do-pacote
pip freeze > requirements.txt
```

### Desativar ambiente virtual

```cmd
deactivate
```

### Resetar banco de dados

```cmd
python init_db.py reset
```

---

**Desenvolvido com ❤️ para Windows e Ubuntu**
