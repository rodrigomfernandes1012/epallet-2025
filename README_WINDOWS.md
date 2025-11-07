# 🪟 Sistema de Gestão Flask - Versão Windows

## 🎯 Início Rápido

### Para Desenvolvedores Windows

1. **Extrair o projeto**
2. **Executar `setup.bat`** (duplo clique)
3. **Executar `run.bat`** (duplo clique)
4. **Acessar**: http://localhost:5000

**Pronto! O sistema está rodando!**

---

## 📦 O que está incluído

### Scripts Windows (.bat)
- `setup.bat` - Configuração completa automática
- `install.bat` - Instalar apenas dependências
- `run.bat` - Executar o servidor
- `init_db.bat` - Gerenciar banco de dados

### Scripts Linux (.sh)
- `deploy.sh` - Deploy automático no Ubuntu
- `init_db.py` - Gerenciar banco (funciona em ambos)

### Documentação
- `README.md` - Documentação completa do projeto
- `INSTALL_WINDOWS.md` - Guia detalhado para Windows
- `DEPLOY_UBUNTU.md` - Guia de deploy para Ubuntu
- `README_WINDOWS.md` - Este arquivo (resumo Windows)

---

## 🚀 Desenvolvimento no Windows

### Primeira Execução

```cmd
# 1. Abrir a pasta do projeto no Explorer
# 2. Duplo clique em: setup.bat
# 3. Aguardar instalação
# 4. Duplo clique em: run.bat
```

### Execuções Seguintes

```cmd
# Apenas executar: run.bat
```

### Criar Usuário Admin

**Opção 1:** Acesse http://localhost:5000/auth/register

**Opção 2:** Execute `init_db.bat create-admin`

---

## 🐧 Deploy no Ubuntu (Produção)

### Preparar no Windows

1. Desenvolva e teste no Windows
2. Faça commit das alterações (Git)
3. Envie para o repositório

### Deploy no Servidor Ubuntu

```bash
# 1. Conectar ao servidor
ssh usuario@seu-servidor.com

# 2. Clonar ou copiar o projeto
git clone https://github.com/seu-usuario/flask-argon-system.git
cd flask-argon-system

# 3. Executar deploy automático
chmod +x deploy.sh
./deploy.sh
```

O script `deploy.sh` irá:
- ✅ Instalar todas as dependências
- ✅ Configurar PostgreSQL
- ✅ Configurar Nginx
- ✅ Criar serviço systemd
- ✅ Configurar SSL (opcional)

**Veja detalhes em:** `DEPLOY_UBUNTU.md`

---

## 🔄 Fluxo de Trabalho Recomendado

### 1. Desenvolvimento (Windows)

```cmd
# Ativar ambiente virtual
venv\Scripts\activate

# Fazer alterações no código
# ...

# Testar localmente
python run.py

# Commit das alterações
git add .
git commit -m "Descrição das alterações"
git push
```

### 2. Deploy (Ubuntu)

```bash
# No servidor
cd flask-argon-system
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart flask-argon
```

---

## 📁 Estrutura de Arquivos

```
flask-argon-system/
│
├── 🪟 WINDOWS
│   ├── setup.bat              # Configuração completa
│   ├── install.bat            # Instalar dependências
│   ├── run.bat                # Executar servidor
│   ├── init_db.bat            # Gerenciar banco
│   ├── INSTALL_WINDOWS.md     # Guia Windows
│   └── README_WINDOWS.md      # Este arquivo
│
├── 🐧 UBUNTU/LINUX
│   ├── deploy.sh              # Deploy automático
│   ├── gunicorn_config.py     # Configuração Gunicorn
│   └── DEPLOY_UBUNTU.md       # Guia Ubuntu
│
├── 🐍 PYTHON
│   ├── run.py                 # Executar servidor
│   ├── init_db.py             # Gerenciar banco
│   ├── requirements.txt       # Dependências
│   ├── config/                # Configurações
│   └── app/                   # Código da aplicação
│
└── 📚 DOCUMENTAÇÃO
    ├── README.md              # Documentação completa
    ├── INSTALL.md             # Guia de instalação
    └── .env.example           # Exemplo de configuração
```

---

## 🗄️ Banco de Dados

### Windows (Desenvolvimento)
- **SQLite** (padrão) - Já configurado
- Arquivo: `app.db`
- Sem instalação necessária

### Ubuntu (Produção)
- **PostgreSQL** (recomendado)
- Configurado automaticamente pelo `deploy.sh`
- Alta performance e confiabilidade

---

## 🔧 Comandos Úteis

### Windows

```cmd
# Ativar ambiente virtual
venv\Scripts\activate

# Desativar ambiente virtual
deactivate

# Instalar nova dependência
pip install nome-pacote
pip freeze > requirements.txt

# Resetar banco de dados
init_db.bat reset

# Criar usuário admin
init_db.bat create-admin
```

### Ubuntu

```bash
# Ver status do serviço
sudo systemctl status flask-argon

# Reiniciar serviço
sudo systemctl restart flask-argon

# Ver logs
sudo journalctl -u flask-argon -f

# Atualizar aplicação
git pull
sudo systemctl restart flask-argon
```

---

## 🌐 Acessar o Sistema

### Desenvolvimento (Windows)
- Local: http://localhost:5000
- Na rede: http://SEU-IP:5000

### Produção (Ubuntu)
- HTTP: http://seu-dominio.com
- HTTPS: https://seu-dominio.com

---

## 🔐 Segurança

### Desenvolvimento
- ✅ Senhas criptografadas
- ✅ Proteção CSRF
- ✅ Validação de formulários
- ⚠️ Debug mode ativo (apenas local)

### Produção
- ✅ Todas as proteções de desenvolvimento
- ✅ HTTPS/SSL obrigatório
- ✅ Firewall configurado
- ✅ Debug mode desativado
- ✅ Senhas fortes no banco

---

## 📝 Configuração (.env)

### Windows (Desenvolvimento)

```env
FLASK_ENV=development
SECRET_KEY=dev-secret-key
DATABASE_URL=sqlite:///app.db
HOST=127.0.0.1
PORT=5000
```

### Ubuntu (Produção)

```env
FLASK_ENV=production
SECRET_KEY=chave-forte-gerada-aleatoriamente
DATABASE_URL=postgresql://user:pass@localhost:5432/db
HOST=127.0.0.1
PORT=8000
```

---

## 🐛 Problemas Comuns

### Windows

**"python não é reconhecido"**
- Reinstale Python marcando "Add to PATH"

**"Porta 5000 em uso"**
- Feche outros programas ou altere a porta no `.env`

**"pip não funciona"**
- Execute: `python -m pip install --upgrade pip`

### Ubuntu

**"Erro 502 Bad Gateway"**
- Verifique: `sudo systemctl status flask-argon`
- Reinicie: `sudo systemctl restart flask-argon`

**"Erro de conexão com banco"**
- Verifique PostgreSQL: `sudo systemctl status postgresql`
- Verifique `.env`: `cat .env | grep DATABASE_URL`

---

## 📚 Documentação Completa

- **README.md** - Documentação técnica completa
- **INSTALL_WINDOWS.md** - Guia detalhado Windows
- **DEPLOY_UBUNTU.md** - Guia completo de deploy
- **INSTALL.md** - Guia geral de instalação

---

## ✅ Checklist

### Windows (Desenvolvimento)
- [ ] Python 3.11+ instalado
- [ ] Projeto extraído
- [ ] Executado `setup.bat`
- [ ] Sistema rodando em http://localhost:5000
- [ ] Usuário criado e login funcionando

### Ubuntu (Produção)
- [ ] Servidor Ubuntu configurado
- [ ] Projeto copiado para servidor
- [ ] Executado `deploy.sh`
- [ ] PostgreSQL configurado
- [ ] Nginx configurado
- [ ] SSL/HTTPS configurado
- [ ] Sistema acessível pelo domínio

---

## 🎓 Próximos Passos

1. **Desenvolva no Windows** usando SQLite
2. **Teste localmente** com `run.bat`
3. **Faça commits** das alterações
4. **Deploy no Ubuntu** com `deploy.sh`
5. **Configure domínio** e SSL
6. **Sistema em produção!** 🚀

---

## 📞 Suporte

- **Windows**: Veja `INSTALL_WINDOWS.md`
- **Ubuntu**: Veja `DEPLOY_UBUNTU.md`
- **Geral**: Veja `README.md`

---

**Desenvolvido para funcionar perfeitamente em Windows e Ubuntu! 💻🐧**
