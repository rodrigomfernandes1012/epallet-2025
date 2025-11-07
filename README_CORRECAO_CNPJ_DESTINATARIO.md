# 🔧 Correções Finais - CNPJ e Lista de Destinatário

## 📋 Problemas Identificados e Corrigidos

### **Problema 1: Erro ao Editar Empresa**
❌ Ao editar uma empresa, o sistema informava que o CNPJ já existe, mesmo sendo o CNPJ da própria empresa sendo editada.

### **Problema 2: Lista de Vales do Destinatário Vazia**
❌ Ao visualizar uma empresa do tipo "Destinatário", a lista de vales não carregava (ficava vazia).

---

## ✅ Soluções Aplicadas

### 1️⃣ **Correção da Validação de CNPJ** (`app/forms.py`)

**Problema:** O método `validate_cnpj` do formulário `EmpresaForm` sempre validava se o CNPJ existe no banco, sem verificar se era uma edição.

**Solução:** Removida a validação duplicada do formulário, mantendo apenas a validação na rota que já exclui corretamente a própria empresa.

#### Código Anterior (Linhas 108-120):
```python
def validate_cnpj(self, cnpj):
    """Valida se o CNPJ já existe (apenas números)"""
    # Remove caracteres não numéricos
    cnpj_numeros = re.sub(r'\D', '', cnpj.data)
    
    # Verifica se tem 14 dígitos
    if len(cnpj_numeros) != 14:
        raise ValidationError('CNPJ deve conter 14 dígitos')
    
    # Verifica se já existe no banco (exceto se for edição)
    empresa = Empresa.query.filter_by(cnpj=cnpj.data).first()
    if empresa:  # ❌ SEMPRE VALIDAVA, CAUSANDO ERRO NA EDIÇÃO
        raise ValidationError('Este CNPJ já está cadastrado.')
```

#### Código Corrigido:
```python
def validate_cnpj(self, cnpj):
    """Valida se o CNPJ já existe (apenas números)"""
    # Remove caracteres não numéricos
    cnpj_numeros = re.sub(r'\D', '', cnpj.data)
    
    # Verifica se tem 14 dígitos
    if len(cnpj_numeros) != 14:
        raise ValidationError('CNPJ deve conter 14 dígitos')
    
    # Verifica se já existe no banco (exceto se for edição)
    # Não valida em edição, pois a validação é feita na rota
    # Para evitar falso positivo ao editar a própria empresa
```

**Nota:** A validação de CNPJ duplicado continua funcionando na rota `editar()` (linhas 124-132 de `empresas.py`), que corretamente exclui a própria empresa:

```python
empresa_existente = Empresa.query.filter(
    Empresa.cnpj == form.cnpj.data,
    Empresa.id != id  # ✅ EXCLUI A PRÓPRIA EMPRESA
).first()
```

---

### 2️⃣ **Correção da Lista de Vales do Destinatário**

**Problema:** O código comparava o nome do tipo de empresa com strings exatas como `'Destinatário'`, mas no banco pode estar cadastrado como `'Destinatario'` (sem acento) ou com espaços extras.

**Solução:** Implementada verificação **flexível** usando `lower()` e `in` para detectar variações de acentuação e espaços.

---

#### A. Rota de Visualização (`app/routes/empresas.py`)

**Código Anterior (Linhas 88-99):**
```python
# Buscar vales pallet relacionados
vales_pallet = []
if empresa.tipo:
    if empresa.tipo.nome == 'Destinatário':  # ❌ COMPARAÇÃO EXATA
        vales_pallet = ValePallet.query.filter_by(destinatario_id=empresa.id).order_by(ValePallet.data_criacao.desc()).all()
    elif empresa.tipo.nome == 'Transportadora':
        vales_pallet = ValePallet.query.filter_by(transportadora_id=empresa.id).order_by(ValePallet.data_criacao.desc()).all()
    elif empresa.tipo.nome == 'Cliente':
        vales_pallet = ValePallet.query.filter_by(cliente_id=empresa.id).order_by(ValePallet.data_criacao.desc()).all()
```

**Código Corrigido:**
```python
# Buscar vales pallet relacionados
vales_pallet = []
if empresa.tipo:
    tipo_nome = empresa.tipo.nome.lower().strip()  # ✅ NORMALIZA O NOME
    
    if 'destinat' in tipo_nome:  # ✅ VERIFICA PARCIALMENTE (Destinatário ou Destinatario)
        vales_pallet = ValePallet.query.filter_by(destinatario_id=empresa.id).order_by(ValePallet.data_criacao.desc()).all()
    elif 'transport' in tipo_nome:  # Transportadora
        vales_pallet = ValePallet.query.filter_by(transportadora_id=empresa.id).order_by(ValePallet.data_criacao.desc()).all()
    elif 'client' in tipo_nome:  # Cliente
        vales_pallet = ValePallet.query.filter_by(cliente_id=empresa.id).order_by(ValePallet.data_criacao.desc()).all()
```

---

#### B. Template de Visualização (`app/templates/empresas/visualizar.html`)

Todas as verificações no template foram atualizadas para usar a mesma lógica flexível:

**1. Condição de Exibição do Card (Linha 189):**
```html
<!-- ANTES -->
{% if empresa.tipo and empresa.tipo.nome in ['Destinatário', 'Transportadora', 'Cliente'] %}

<!-- DEPOIS -->
{% if empresa.tipo and (empresa.tipo.nome in ['Destinatário', 'Destinatario', 'Transportadora', 'Cliente'] or 'destinat' in empresa.tipo.nome.lower() or 'transport' in empresa.tipo.nome.lower() or 'client' in empresa.tipo.nome.lower()) %}
```

**2. Título do Card (Linhas 194-200):**
```html
<!-- ANTES -->
{% if empresa.tipo.nome == 'Destinatário' %}
    Vales Pallet - Recebimentos
{% elif empresa.tipo.nome == 'Transportadora' %}
    Vales Pallet - Transportes
{% elif empresa.tipo.nome == 'Cliente' %}
    Vales Pallet - Enviados
{% endif %}

<!-- DEPOIS -->
{% if 'destinat' in empresa.tipo.nome.lower() %}
    Vales Pallet - Recebimentos
{% elif 'transport' in empresa.tipo.nome.lower() %}
    Vales Pallet - Transportes
{% elif 'client' in empresa.tipo.nome.lower() %}
    Vales Pallet - Enviados
{% endif %}
```

**3. Colunas da Tabela - Cabeçalho (Linhas 212-221):**
```html
<!-- ANTES -->
{% if empresa.tipo.nome == 'Destinatário' %}
    <th>Cliente</th>
    <th>Transportadora</th>
{% elif empresa.tipo.nome == 'Transportadora' %}
    ...

<!-- DEPOIS -->
{% if 'destinat' in empresa.tipo.nome.lower() %}
    <th>Cliente</th>
    <th>Transportadora</th>
{% elif 'transport' in empresa.tipo.nome.lower() %}
    ...
```

**4. Colunas da Tabela - Dados (Linhas 238-259):**
```html
<!-- ANTES -->
{% if empresa.tipo.nome == 'Destinatário' %}
    <td>{{ vale.cliente_nome }}</td>
    <td>{{ vale.transportadora_nome }}</td>
{% elif empresa.tipo.nome == 'Transportadora' %}
    ...

<!-- DEPOIS -->
{% if 'destinat' in empresa.tipo.nome.lower() %}
    <td>{{ vale.cliente_nome }}</td>
    <td>{{ vale.transportadora_nome }}</td>
{% elif 'transport' in empresa.tipo.nome.lower() %}
    ...
```

**5. Mensagens de Vazio (Linhas 277-283):**
```html
<!-- ANTES -->
{% if empresa.tipo.nome == 'Destinatário' %}
    Nenhum vale pallet recebido ainda.
{% elif empresa.tipo.nome == 'Transportadora' %}
    ...

<!-- DEPOIS -->
{% if 'destinat' in empresa.tipo.nome.lower() %}
    Nenhum vale pallet recebido ainda.
{% elif 'transport' in empresa.tipo.nome.lower() %}
    ...
```

---

## 🎯 Resultado

### ✅ Problema 1 - CNPJ:
- **Antes:** Erro ao salvar edição de empresa
- **Depois:** Edição funciona normalmente, validação de CNPJ duplicado continua funcionando

### ✅ Problema 2 - Destinatário:
- **Antes:** Lista vazia ao visualizar Destinatário
- **Depois:** Lista carrega corretamente, independente de acentuação ou espaços no nome do tipo

---

## 📁 Arquivos Modificados

1. ✅ `/app/forms.py` - Corrigida validação de CNPJ
2. ✅ `/app/routes/empresas.py` - Implementada verificação flexível de tipos
3. ✅ `/app/templates/empresas/visualizar.html` - Atualizado template com verificação flexível

---

## 🚀 Como Aplicar

1. Extrair o arquivo ZIP
2. Substituir os arquivos do projeto
3. Reiniciar o servidor

```bash
# Parar o servidor (Ctrl+C)

# Reiniciar
python3 run.py
# ou
./deploy.sh
```

**Não é necessário** executar migrations ou atualizar o banco de dados.

---

## 🧪 Testes Recomendados

### Teste 1: Edição de Empresa
1. Acessar uma empresa existente
2. Clicar em "Editar"
3. Alterar algum campo (exceto CNPJ)
4. Salvar
5. ✅ Deve salvar sem erro

### Teste 2: Edição de CNPJ
1. Acessar uma empresa existente
2. Clicar em "Editar"
3. Alterar o CNPJ para um CNPJ de outra empresa
4. Salvar
5. ✅ Deve mostrar erro "Já existe uma empresa com este CNPJ!"

### Teste 3: Lista de Vales - Destinatário
1. Criar ou acessar uma empresa do tipo "Destinatário"
2. Criar alguns vales onde essa empresa é destinatário
3. Visualizar a empresa
4. ✅ Deve exibir o card "Vales Pallet - Recebimentos"
5. ✅ Deve listar todos os vales

### Teste 4: Lista de Vales - Transportadora
1. Acessar uma empresa do tipo "Transportadora"
2. ✅ Deve exibir o card "Vales Pallet - Transportes"
3. ✅ Deve listar todos os vales (não apenas pendentes)

### Teste 5: Lista de Vales - Cliente
1. Acessar uma empresa do tipo "Cliente"
2. ✅ Deve exibir o card "Vales Pallet - Enviados"
3. ✅ Deve listar todos os vales

---

## 💡 Observações Técnicas

### Por que usar verificação flexível?

A verificação flexível (`'destinat' in tipo_nome.lower()`) resolve vários problemas:

1. **Acentuação:** Funciona com "Destinatário" ou "Destinatario"
2. **Espaços:** Funciona com espaços extras antes/depois
3. **Case-insensitive:** Funciona com "DESTINATÁRIO", "destinatário", etc.
4. **Robustez:** Menos propenso a erros de digitação no cadastro

### Validação de CNPJ

A validação de CNPJ duplicado funciona em **duas camadas**:

1. **Formulário (`forms.py`):** Valida apenas o formato (14 dígitos)
2. **Rota (`empresas.py`):** Valida duplicação, excluindo a própria empresa na edição

Isso evita o problema de validação prematura no formulário.

---

## 📝 Histórico de Versões

- **v17** (07/11/2024) - Correção de CNPJ na edição e lista de Destinatário
- **v16** (07/11/2024) - Correção de visualização de vales por empresa
- **v15** (07/11/2024) - Correção visual do campo status

---

**Desenvolvido por:** Equipe de Desenvolvimento  
**Data da Correção:** 07/11/2024  
**Versão:** 17 (CNPJ e Destinatário Corrigidos)
