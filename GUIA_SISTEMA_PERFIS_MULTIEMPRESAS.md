# 🎯 Sistema de Perfis e Multi-Empresas - Versão 33

## Data: 11/11/2024

---

## 📋 Resumo das Implementações

Este documento descreve todas as alterações realizadas para implementar:

1. ✅ **Correção do Menu Lateral** - Uso total do espaço vertical
2. ✅ **Sistema de Perfis** - Controle de permissões por perfil
3. ✅ **Sistema Multi-Empresas** - Isolamento total de dados entre empresas
4. ✅ **Gestão de Usuários** - CRUD completo de usuários vinculados a empresas
5. ✅ **Controle de Acesso** - Permissões aplicadas em rotas e menus

---

## 🔧 Alterações Realizadas

### 1. Banco de Dados

#### Novos Modelos

**Perfil** (`perfis`)
- `id` - Chave primária
- `nome` - Nome do perfil (único)
- `descricao` - Descrição do perfil
- `ativo` - Se o perfil está ativo
- `sistema` - Se é perfil do sistema (não pode ser excluído)
- `data_criacao` - Data de criação
- `data_atualizacao` - Data da última atualização

**PerfilPermissao** (`perfis_permissoes`)
- `id` - Chave primária
- `perfil_id` - FK para perfis
- `modulo` - Nome do módulo (dashboard, empresas, etc)
- `pode_visualizar` - Permissão de visualização
- `pode_criar` - Permissão de criação
- `pode_editar` - Permissão de edição
- `pode_excluir` - Permissão de exclusão
- `data_criacao` - Data de criação
- `data_atualizacao` - Data da última atualização

#### Alterações em Modelos Existentes

**User**
- Adicionado campo `perfil_id` (FK para perfis)
- Adicionado método `tem_permissao(modulo, acao)`
- Adicionado método `get_modulos_permitidos()`

---

### 2. Perfis Padrão do Sistema

#### Administrador
- **Acesso:** Total
- **Descrição:** Pode gerenciar tudo, incluindo usuários e perfis
- **Permissões:** Todas as ações em todos os módulos

#### Gestor
- **Acesso:** Operacional completo
- **Descrição:** Pode gerenciar empresas, motoristas e vales
- **Permissões:** Todas as ações exceto em usuários e perfis

#### Operador
- **Acesso:** Limitado
- **Descrição:** Pode criar e editar vales, visualizar empresas e motoristas
- **Permissões:**
  - Dashboard: Visualizar
  - Empresas: Visualizar
  - Tipos de Empresa: Visualizar
  - Motoristas: Visualizar
  - Vale Pallet: Visualizar, Criar, Editar
  - Relatórios: Visualizar

#### Consulta
- **Acesso:** Somente leitura
- **Descrição:** Pode apenas visualizar informações
- **Permissões:** Apenas visualização em módulos operacionais

---

### 3. Módulos do Sistema

1. **dashboard** - Dashboard principal
2. **empresas** - Cadastro de empresas
3. **tipos_empresa** - Tipos de empresa
4. **motoristas** - Cadastro de motoristas
5. **vale_pallet** - Vales pallet
6. **relatorios** - Relatórios
7. **logs** - Logs de auditoria
8. **usuarios** - Gestão de usuários (novo)
9. **perfis** - Gestão de perfis (novo)

---

### 4. Novos Arquivos Criados

#### Modelos e Utilitários
- `app/models.py` - Adicionados modelos Perfil e PerfilPermissao
- `app/utils/decorators.py` - Decorators para controle de acesso
- `app/forms_admin.py` - Formulários para usuários e perfis

#### Rotas
- `app/routes/usuarios.py` - CRUD de usuários
- `app/routes/perfis.py` - CRUD de perfis e permissões

#### Templates - Usuários
- `app/templates/usuarios/listar.html` - Lista de usuários
- `app/templates/usuarios/form.html` - Formulário de usuário
- `app/templates/usuarios/visualizar.html` - Detalhes do usuário
- `app/templates/usuarios/alterar_senha.html` - Alterar senha

#### Templates - Perfis
- `app/templates/perfis/listar.html` - Lista de perfis
- `app/templates/perfis/form.html` - Formulário de perfil
- `app/templates/perfis/visualizar.html` - Detalhes do perfil
- `app/templates/perfis/permissoes.html` - Editar permissões

#### Scripts de Migração
- `migrate_perfis.py` - Script Python de migração
- `migrate_perfis.bat` - Script Windows
- `migrate_perfis.sh` - Script Linux

---

### 5. Arquivos Modificados

- `app/__init__.py` - Registrados novos blueprints
- `app/templates/includes/sidebar.html` - Menu dinâmico baseado em permissões

---

## 🚀 Como Aplicar as Alterações

### Passo 1: Atualizar Arquivos

#### Windows
```cmd
cd C:\TaxiDigital\PROJETOS_PYTHON\flask-argon-system

# Extrair ZIP e substituir arquivos
```

#### Linux (Produção)
```bash
cd /root/epallet-2025

# Extrair ZIP e substituir arquivos
```

---

### Passo 2: Executar Migração do Banco de Dados

#### Windows
```cmd
migrate_perfis.bat
```

#### Linux
```bash
./migrate_perfis.sh
```

**O que a migração faz:**
1. Cria tabelas `perfis` e `perfis_permissoes`
2. Cria 4 perfis padrão (Administrador, Gestor, Operador, Consulta)
3. Cria permissões para cada perfil
4. Atribui perfil "Administrador" a todos os usuários existentes

---

### Passo 3: Reiniciar Aplicação

#### Windows (Desenvolvimento)
```cmd
# Parar aplicação (Ctrl+C)
python run.py
```

#### Linux (Produção)
```bash
sudo systemctl restart epallet
sudo systemctl status epallet
```

---

### Passo 4: Limpar Cache do Navegador

Pressione `Ctrl + F5` no navegador para recarregar completamente.

---

## 📊 Funcionalidades Implementadas

### Gestão de Usuários

**Acessar:** Menu → Administração → Usuários

**Funcionalidades:**
- ✅ Listar usuários com paginação
- ✅ Criar novo usuário
- ✅ Editar usuário existente
- ✅ Visualizar detalhes do usuário
- ✅ Excluir usuário
- ✅ Alterar senha (próprio usuário)
- ✅ Vincular usuário a empresa
- ✅ Atribuir perfil ao usuário

**Campos do Usuário:**
- Nome de usuário (login)
- E-mail
- Nome completo
- Empresa (obrigatório)
- Perfil (obrigatório)
- Senha
- Status (ativo/inativo)

---

### Gestão de Perfis

**Acessar:** Menu → Administração → Perfis

**Funcionalidades:**
- ✅ Listar perfis
- ✅ Criar novo perfil
- ✅ Editar perfil (exceto perfis do sistema)
- ✅ Visualizar detalhes do perfil
- ✅ Configurar permissões por módulo
- ✅ Excluir perfil (exceto perfis do sistema)

**Configuração de Permissões:**
- Interface visual com checkboxes
- Permissões por módulo:
  - Visualizar
  - Criar
  - Editar
  - Excluir

---

### Menu Dinâmico

O menu lateral agora mostra apenas os itens que o usuário tem permissão de visualizar.

**Comportamento:**
- Se usuário não tem perfil: mostra todos os itens
- Se usuário tem perfil: mostra apenas itens permitidos
- Seções vazias são ocultadas automaticamente

---

### Sistema Multi-Empresas

**Isolamento de Dados:**
- Usuários veem apenas dados da sua empresa
- Filtros automáticos aplicados em todas as queries
- Decorators para garantir isolamento

**Decorators Disponíveis:**
- `@empresa_required` - Verifica se usuário tem empresa vinculada
- `@permissao_required(modulo, acao)` - Verifica permissão específica
- `@admin_required` - Apenas administradores
- `@perfil_required` - Verifica se tem perfil atribuído

**Funções Auxiliares:**
- `filtrar_por_empresa(query, model)` - Filtra query por empresa
- `pode_acessar_registro(registro)` - Verifica acesso a registro específico

---

## 🔐 Segurança

### Controle de Acesso

1. **Autenticação:** Login obrigatório para todas as rotas (exceto públicas)
2. **Perfil:** Usuário deve ter perfil atribuído
3. **Permissões:** Verificadas em cada rota
4. **Multi-Empresas:** Dados isolados por empresa

### Auditoria

Todas as ações são registradas nos logs de auditoria:
- Criação de usuários
- Edição de usuários
- Exclusão de usuários
- Criação de perfis
- Edição de permissões
- Exclusão de perfis

---

## 📝 Fluxo de Trabalho Recomendado

### 1. Configuração Inicial

1. Executar migração
2. Fazer login com usuário existente (agora é Administrador)
3. Criar empresas (se ainda não existirem)

### 2. Criar Perfis Customizados (Opcional)

1. Acessar Administração → Perfis
2. Clicar em "Novo Perfil"
3. Preencher nome e descrição
4. Salvar
5. Configurar permissões

### 3. Criar Usuários

1. Acessar Administração → Usuários
2. Clicar em "Novo Usuário"
3. Preencher dados:
   - Nome de usuário
   - E-mail
   - Nome completo
   - Empresa (obrigatório)
   - Perfil (obrigatório)
   - Senha
4. Salvar

### 4. Testar Permissões

1. Fazer logout
2. Fazer login com novo usuário
3. Verificar que menu mostra apenas itens permitidos
4. Tentar acessar áreas sem permissão (deve bloquear)

---

## ⚠️ Observações Importantes

### Perfis do Sistema

Os perfis padrão (Administrador, Gestor, Operador, Consulta) são marcados como "sistema" e:
- ✅ Podem ter permissões editadas
- ❌ Não podem ser excluídos
- ❌ Não podem ter nome alterado

### Usuários Existentes

Todos os usuários existentes antes da migração:
- Recebem automaticamente o perfil "Administrador"
- Mantêm acesso total ao sistema
- Podem ser editados posteriormente

### Empresa Obrigatória

A partir desta versão:
- Todo usuário DEVE estar vinculado a uma empresa
- Usuários sem empresa não conseguem acessar dados
- Apenas administradores podem ver dados de todas as empresas

### Exclusão de Perfis

Um perfil só pode ser excluído se:
- Não for perfil do sistema
- Não tiver usuários vinculados

---

## 🧪 Testes Recomendados

### 1. Teste de Permissões

1. Criar usuário com perfil "Consulta"
2. Fazer login
3. Verificar que:
   - ✅ Pode visualizar dados
   - ❌ Não pode criar/editar/excluir
   - ❌ Não vê menus de administração

### 2. Teste Multi-Empresas

1. Criar duas empresas (A e B)
2. Criar usuário vinculado à empresa A
3. Criar dados na empresa A
4. Criar dados na empresa B
5. Fazer login com usuário da empresa A
6. Verificar que:
   - ✅ Vê apenas dados da empresa A
   - ❌ Não vê dados da empresa B

### 3. Teste de Menu

1. Criar perfil com permissões limitadas
2. Atribuir a usuário
3. Fazer login
4. Verificar que:
   - ✅ Menu mostra apenas itens permitidos
   - ✅ Seções vazias são ocultadas

---

## 🐛 Solução de Problemas

### Erro ao Executar Migração

**Problema:** Tabelas já existem

**Solução:** A migração verifica se perfis já existem e pula a criação

---

### Menu Não Atualiza

**Problema:** Menu ainda mostra todos os itens

**Solução:**
1. Limpar cache do navegador (Ctrl + F5)
2. Verificar se usuário tem perfil atribuído
3. Verificar se permissões estão configuradas

---

### Usuário Sem Acesso

**Problema:** Usuário não consegue acessar nada

**Solução:**
1. Verificar se usuário tem perfil atribuído
2. Verificar se perfil está ativo
3. Verificar se perfil tem permissões configuradas
4. Verificar se usuário está vinculado a uma empresa

---

## 📞 Suporte

Para dúvidas ou problemas:
1. Verificar logs de auditoria
2. Verificar logs do sistema
3. Consultar esta documentação

---

## ✅ Checklist de Implementação

- [ ] Backup do banco de dados
- [ ] Backup dos arquivos
- [ ] Extrair ZIP
- [ ] Substituir arquivos
- [ ] Executar migração
- [ ] Reiniciar aplicação
- [ ] Limpar cache do navegador
- [ ] Fazer login
- [ ] Verificar menu
- [ ] Criar perfil de teste
- [ ] Criar usuário de teste
- [ ] Testar permissões
- [ ] Testar multi-empresas
- [ ] Verificar logs de auditoria

---

**Versão:** v33  
**Data:** 11/11/2024  
**Sistema:** Epallet - Gestão de Pallets

✅ **Sistema de Perfis e Multi-Empresas Implementado com Sucesso!**
