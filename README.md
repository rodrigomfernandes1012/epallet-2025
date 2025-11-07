# Sistema de Gestão - Flask com Argon Dashboard

Sistema web desenvolvido em Python/Flask com PostgreSQL para gerenciamento de usuários e empresas, utilizando o design visual do template Argon Dashboard.

## 📋 Características

- **Autenticação completa**: Login, registro e logout de usuários
- **Gerenciamento de usuários**: Cadastro e perfil de usuários
- **Gerenciamento de empresas**: CRUD completo (Criar, Ler, Atualizar, Deletar)
- **Design responsivo**: Interface moderna baseada no Argon Dashboard
- **Segurança**: Senhas criptografadas com Werkzeug, proteção CSRF
- **Banco de dados**: Suporte para PostgreSQL e SQLite

## 🚀 Tecnologias Utilizadas

- **Backend**: Python 3.11, Flask 3.0.0
- **Banco de Dados**: PostgreSQL (produção) / SQLite (desenvolvimento)
- **ORM**: SQLAlchemy 2.0.23
- **Autenticação**: Flask-Login 0.6.3
- **Formulários**: WTForms 3.1.1, Flask-WTF 1.2.1
- **Migrações**: Flask-Migrate 4.0.5
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Template**: Argon Dashboard (Creative Tim)

## 📁 Estrutura do Projeto

```
flask-argon-system/
├── app/
│   ├── __init__.py              # Inicialização da aplicação Flask
│   ├── models.py                # Modelos de banco de dados (User, Empresa)
│   ├── forms.py                 # Formulários WTForms
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py              # Rotas de autenticação
│   │   ├── main.py              # Rotas principais
│   │   └── empresas.py          # Rotas de empresas
│   ├── templates/
│   │   ├── layouts/
│   │   │   └── base.html        # Template base
│   │   ├── includes/
│   │   │   ├── sidebar.html     # Menu lateral
│   │   │   ├── navbar.html      # Barra superior
│   │   │   └── footer.html      # Rodapé
│   │   ├── auth/
│   │   │   ├── login.html       # Página de login
│   │   │   └── register.html    # Página de registro
│   │   ├── empresas/
│   │   │   ├── listar.html      # Listagem de empresas
│   │   │   ├── form.html        # Formulário de empresa
│   │   │   └── visualizar.html  # Detalhes da empresa
│   │   ├── dashboard.html       # Dashboard principal
│   │   └── profile.html         # Perfil do usuário
│   └── static/
│       ├── css/                 # Arquivos CSS do Argon Dashboard
│       ├── js/                  # Arquivos JavaScript
│       ├── fonts/               # Fontes
│       └── img/                 # Imagens
├── config/
│   ├── __init__.py
│   └── config.py                # Configurações da aplicação
├── run.py                       # Script principal para executar a aplicação
├── requirements.txt             # Dependências do projeto
├── .env.example                 # Exemplo de variáveis de ambiente
├── .gitignore                   # Arquivos ignorados pelo Git
└── README.md                    # Este arquivo

```

## 🔧 Instalação e Configuração

### Pré-requisitos

- Python 3.11 ou superior
- PostgreSQL 12 ou superior (para produção)
- pip (gerenciador de pacotes Python)

### Passo 1: Clonar o repositório

```bash
cd flask-argon-system
```

### Passo 2: Criar ambiente virtual

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### Passo 3: Instalar dependências

```bash
pip install -r requirements.txt
```

### Passo 4: Configurar variáveis de ambiente

Copie o arquivo `.env.example` para `.env` e configure as variáveis:

```bash
cp .env.example .env
```

Edite o arquivo `.env`:

```env
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=sua-chave-secreta-aqui-mude-em-producao
DATABASE_URL=postgresql://usuario:senha@localhost:5432/nome_banco
```

**Para desenvolvimento local com SQLite**, você pode usar:

```env
DATABASE_URL=sqlite:///app.db
```

### Passo 5: Criar o banco de dados

```bash
# Inicializar as migrações (apenas na primeira vez)
flask db init

# Criar a migração inicial
flask db migrate -m "Initial migration"

# Aplicar as migrações
flask db upgrade
```

### Passo 6: Executar a aplicação

```bash
python run.py
```

A aplicação estará disponível em `http://localhost:5000`

## 📊 Modelos de Dados

### User (Usuário)

- `id`: ID único do usuário
- `username`: Nome de usuário (único)
- `email`: Email do usuário (único)
- `nome_completo`: Nome completo do usuário
- `password_hash`: Senha criptografada
- `ativo`: Status do usuário (ativo/inativo)
- `data_criacao`: Data de criação do registro
- `data_atualizacao`: Data da última atualização

### Empresa

- `id`: ID único da empresa
- `razao_social`: Razão social (obrigatório)
- `nome_fantasia`: Nome fantasia
- `cnpj`: CNPJ (único, obrigatório)
- `inscricao_estadual`: Inscrição estadual
- `inscricao_municipal`: Inscrição municipal
- `cep`: CEP
- `logradouro`: Endereço
- `numero`: Número
- `complemento`: Complemento
- `bairro`: Bairro
- `cidade`: Cidade
- `estado`: Estado (UF)
- `telefone`: Telefone
- `celular`: Celular
- `email`: Email
- `site`: Website
- `ativa`: Status da empresa (ativa/inativa)
- `data_criacao`: Data de criação do registro
- `data_atualizacao`: Data da última atualização
- `usuario_id`: ID do usuário que cadastrou

## 🔐 Funcionalidades de Autenticação

### Registro de Usuário

- Validação de campos obrigatórios
- Verificação de usuário e email únicos
- Confirmação de senha
- Criptografia de senha com Werkzeug

### Login

- Login com usuário ou email
- Opção "Lembrar-me"
- Proteção contra CSRF
- Redirecionamento após login

### Logout

- Encerramento seguro da sessão
- Redirecionamento para página de login

## 📦 Funcionalidades de Empresas

### Listar Empresas

- Visualização em tabela com paginação
- Exibição de informações principais
- Badges de status (Ativa/Inativa)
- Ações: Visualizar, Editar, Excluir

### Cadastrar Empresa

- Formulário completo com validação
- Campos organizados por seções:
  - Informações da Empresa
  - Endereço
  - Contato
- Validação de CNPJ único
- Validação de email

### Visualizar Empresa

- Exibição de todos os dados da empresa
- Informações do sistema (data de cadastro, última atualização, usuário)
- Botões de ação (Editar, Voltar)

### Editar Empresa

- Formulário pré-preenchido
- Mesmas validações do cadastro
- Atualização da data de modificação

### Excluir Empresa

- Confirmação antes da exclusão
- Exclusão permanente do registro

## 🎨 Interface do Usuário

### Dashboard

- Cards com estatísticas:
  - Total de Usuários
  - Total de Empresas
  - Empresas Ativas
  - Empresas Inativas
- Tabela de empresas recentes
- Menu lateral com navegação
- Barra superior com busca e perfil

### Design Responsivo

- Layout adaptável para desktop, tablet e mobile
- Menu lateral retrátil
- Tabelas responsivas com scroll horizontal

## 🔒 Segurança

- **Senhas criptografadas**: Uso de Werkzeug para hash de senhas
- **Proteção CSRF**: Tokens CSRF em todos os formulários
- **Autenticação obrigatória**: Rotas protegidas com `@login_required`
- **Validação de entrada**: WTForms para validação de dados
- **SQL Injection**: Proteção via SQLAlchemy ORM

## 🚀 Deploy em Produção

### Configurações Recomendadas

1. **Servidor WSGI**: Use Gunicorn ou uWSGI

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 run:app
```

2. **Proxy Reverso**: Configure Nginx ou Apache

3. **Banco de Dados**: Use PostgreSQL em produção

4. **Variáveis de Ambiente**: Configure corretamente o `.env`

```env
FLASK_ENV=production
SECRET_KEY=chave-secreta-forte-e-aleatoria
DATABASE_URL=postgresql://usuario:senha@host:5432/banco
```

5. **HTTPS**: Configure certificado SSL/TLS

### Exemplo de Configuração Nginx

```nginx
server {
    listen 80;
    server_name seu-dominio.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /static {
        alias /caminho/para/flask-argon-system/app/static;
    }
}
```

## 📝 Credenciais de Teste

Após a instalação, você pode criar um usuário de teste:

```bash
python
>>> from app import create_app, db
>>> from app.models import User
>>> app = create_app()
>>> with app.app_context():
...     user = User(username='admin', email='admin@sistema.com', nome_completo='Administrador')
...     user.set_password('admin123')
...     db.session.add(user)
...     db.session.commit()
```

**Credenciais:**
- Usuário: `admin`
- Senha: `admin123`

## 🛠️ Desenvolvimento

### Adicionar novas rotas

1. Crie um novo arquivo em `app/routes/`
2. Registre o Blueprint em `app/__init__.py`

### Adicionar novos modelos

1. Adicione o modelo em `app/models.py`
2. Crie uma migração: `flask db migrate -m "Descrição"`
3. Aplique a migração: `flask db upgrade`

### Personalizar templates

- Templates base: `app/templates/layouts/`
- Componentes: `app/templates/includes/`
- Páginas específicas: `app/templates/[modulo]/`

## 📄 Licença

Este projeto utiliza o template Argon Dashboard da Creative Tim, que possui licença MIT.

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para:

1. Fazer fork do projeto
2. Criar uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abrir um Pull Request

## 📞 Suporte

Para dúvidas ou problemas, abra uma issue no repositório do projeto.

## 🎯 Roadmap

- [ ] Implementar recuperação de senha
- [ ] Adicionar upload de logo da empresa
- [ ] Implementar relatórios em PDF
- [ ] Adicionar filtros e busca avançada
- [ ] Implementar API REST
- [ ] Adicionar testes automatizados
- [ ] Implementar logs de auditoria
- [ ] Adicionar dashboard com gráficos

---

Desenvolvido com ❤️ usando Flask e Argon Dashboard
