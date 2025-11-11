# 📋 Análise e Planejamento - Sistema Multi-Empresas

## Data: 11/11/2024

---

## 🔍 Análise da Estrutura Atual

### Banco de Dados

**Modelo User (Atual):**
- ✅ Já possui `empresa_id` (FK para empresas)
- ❌ Não possui campo `perfil_id` (precisa adicionar)
- ✅ Método `pode_ver_empresa()` - base para multi-empresas
- ✅ Método `empresas_visiveis()` - base para multi-empresas

**Modelo Empresa (Atual):**
- ✅ Campo `criado_por_id` - rastreamento
- ✅ Relacionamento `usuarios_vinculados`
- ✅ Já estruturado para multi-empresas

**Modelo Motorista (Atual):**
- ✅ Campo `empresa_id` - vinculado a transportadora
- ✅ Campo `cadastrado_por_id` - rastreamento

**Modelo ValePallet (Atual):**
- ✅ Campo `criado_por_id` - rastreamento
- ✅ Relacionamentos com empresas (cliente, transportadora, destinatário)

**Modelos Faltantes:**
- ❌ **Perfil** - Não existe
- ❌ **PerfilPermissao** - Não existe

---

## 🎯 Problemas Identificados

### 1. Menu Lateral (Sidebar)

**Problema:** Espaço branco grande abaixo do último item do menu.

**Causa:** O container do menu tem `max-height: calc(100vh - 120px)` mas a lista `<ul>` não está ocupando todo o espaço disponível.

**Solução:**
```css
/* Fazer a lista ocupar todo o espaço disponível */
.navbar-collapse {
    display: flex !important;
    flex-direction: column !important;
    height: calc(100vh - 120px) !important;
}

.navbar-nav {
    flex: 1 !important;
    overflow-y: auto !important;
}
```

---

### 2. Sistema Não é Multi-Empresas

**Problemas:**
- Usuários podem ver dados de outras empresas
- Não há isolamento de dados
- Filtros não aplicam restrição por empresa

**Necessário:**
- Adicionar filtros em TODAS as queries
- Restringir acesso baseado em `empresa_id` do usuário
- Criar decorator para aplicar filtro automaticamente

---

### 3. Não Existe Sistema de Perfis

**Problemas:**
- Todos os usuários têm acesso a tudo
- Não há controle de permissões
- Não há como criar perfis customizados

**Necessário:**
- Criar modelo `Perfil`
- Criar modelo `PerfilPermissao`
- Adicionar campo `perfil_id` em User
- Criar CRUD de perfis
- Aplicar verificação de permissões nas rotas

---

### 4. Não Existe Gestão de Usuários

**Problemas:**
- Não há tela para criar usuários
- Não há como vincular usuários a empresas
- Não há como atribuir perfis

**Necessário:**
- Criar rota de gestão de usuários
- Criar formulário de usuário
- Criar template de listagem/criação/edição

---

## 🏗️ Arquitetura Proposta

### Novos Modelos

#### 1. Perfil
```python
class Perfil(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)
    descricao = db.Column(db.Text)
    ativo = db.Column(db.Boolean, default=True)
    sistema = db.Column(db.Boolean, default=False)  # Perfis do sistema não podem ser editados
    
    # Relacionamentos
    usuarios = db.relationship('User', backref='perfil', lazy='dynamic')
    permissoes = db.relationship('PerfilPermissao', backref='perfil', lazy='dynamic')
```

#### 2. PerfilPermissao
```python
class PerfilPermissao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    perfil_id = db.Column(db.Integer, db.ForeignKey('perfis.id'), nullable=False)
    
    # Permissões por módulo
    modulo = db.Column(db.String(50), nullable=False)  # empresas, motoristas, vale_pallet, etc
    
    # Ações permitidas
    pode_visualizar = db.Column(db.Boolean, default=False)
    pode_criar = db.Column(db.Boolean, default=False)
    pode_editar = db.Column(db.Boolean, default=False)
    pode_excluir = db.Column(db.Boolean, default=False)
```

#### 3. Atualização do User
```python
class User(UserMixin, db.Model):
    # ... campos existentes ...
    
    # Novo campo
    perfil_id = db.Column(db.Integer, db.ForeignKey('perfis.id'))
    
    # Novos métodos
    def tem_permissao(self, modulo, acao):
        """Verifica se o usuário tem permissão para uma ação"""
        if not self.perfil:
            return False
        
        permissao = PerfilPermissao.query.filter_by(
            perfil_id=self.perfil_id,
            modulo=modulo
        ).first()
        
        if not permissao:
            return False
        
        if acao == 'visualizar':
            return permissao.pode_visualizar
        elif acao == 'criar':
            return permissao.pode_criar
        elif acao == 'editar':
            return permissao.pode_editar
        elif acao == 'excluir':
            return permissao.pode_excluir
        
        return False
```

---

## 📊 Perfis Padrão do Sistema

### 1. Administrador
- Acesso total a todos os módulos
- Pode criar/editar/excluir tudo
- Pode gerenciar usuários e perfis

### 2. Gestor
- Acesso a todos os módulos da sua empresa
- Pode criar/editar/excluir registros da sua empresa
- Pode visualizar relatórios

### 3. Operador
- Acesso limitado aos módulos operacionais
- Pode criar/editar vales pallet
- Pode visualizar empresas e motoristas
- Não pode excluir

### 4. Consulta
- Apenas visualização
- Não pode criar/editar/excluir
- Pode visualizar relatórios

---

## 🔐 Módulos de Permissão

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

## 🛠️ Implementação - Fases

### Fase 1: Corrigir Menu Lateral ✅
- Ajustar CSS do sidebar
- Testar em diferentes resoluções

### Fase 2: Criar Modelos de Perfil
- Criar modelo `Perfil`
- Criar modelo `PerfilPermissao`
- Atualizar modelo `User`

### Fase 3: Multi-Empresas
- Criar decorator `@empresa_required`
- Aplicar filtros em todas as queries
- Atualizar rotas existentes

### Fase 4: CRUD de Perfis
- Criar rotas de perfis
- Criar formulários
- Criar templates

### Fase 5: CRUD de Usuários
- Criar rotas de usuários
- Criar formulários
- Criar templates

### Fase 6: Aplicar Permissões
- Criar decorator `@permissao_required`
- Aplicar em todas as rotas
- Atualizar menu lateral (mostrar apenas itens permitidos)

### Fase 7: Migração e Testes
- Script de migração do banco
- Popular perfis padrão
- Atribuir perfil aos usuários existentes
- Testes completos

---

## 📝 Notas Importantes

1. **Compatibilidade:** Manter compatibilidade com usuários existentes
2. **Migração:** Criar script para atribuir perfil "Administrador" aos usuários atuais
3. **Segurança:** Validar permissões em TODAS as rotas
4. **UX:** Menu deve mostrar apenas itens que o usuário tem permissão
5. **Performance:** Cachear permissões para evitar queries repetidas

---

## ✅ Checklist de Implementação

- [ ] Corrigir CSS do menu lateral
- [ ] Criar modelo Perfil
- [ ] Criar modelo PerfilPermissao
- [ ] Atualizar modelo User
- [ ] Criar decorator @empresa_required
- [ ] Criar decorator @permissao_required
- [ ] Criar CRUD de perfis
- [ ] Criar CRUD de usuários
- [ ] Aplicar filtros multi-empresas em todas as rotas
- [ ] Aplicar verificação de permissões em todas as rotas
- [ ] Atualizar menu lateral com permissões
- [ ] Criar script de migração
- [ ] Popular perfis padrão
- [ ] Testes completos

---

**Próximo Passo:** Começar implementação pela correção do menu lateral.
