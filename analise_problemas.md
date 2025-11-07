# Análise de Problemas - Campo Status em Vales Pallet

## Problema Identificado

O campo `status` está aparecendo em branco na lista de vales Pallet.

## Análise Detalhada

### 1. Modelo ValePallet (models.py)

**Linha 187:** O campo `status` está corretamente definido:
```python
status = db.Column(db.String(30), default='pendente_entrega', nullable=False)
```

**Valores possíveis:**
- `pendente_entrega` (padrão)
- `entrega_realizada`
- `entrega_concluida`
- `cancelado`

**Métodos auxiliares:**
- `get_status_display()` - Retorna o nome do status em português
- `get_status_badge_class()` - Retorna a classe CSS para o badge

### 2. Rotas (vale_pallet.py)

**Problema encontrado:**
- Na rota `/listar` (linha 16-28): A query está correta e retorna os vales
- Na rota `/novo` (linha 93-102): O vale é criado SEM definir explicitamente o status (confia no default do banco)
- Na rota `/cancelar` (linha 223): Define `status = 'cancelado'`
- Na rota `/finalizar` (linha 243): Define `status = 'finalizado'` ⚠️ **ERRO: valor não existe no mapeamento!**

**Problemas identificados:**
1. O status `'finalizado'` não existe no mapeamento de `get_status_display()` e `get_status_badge_class()`
2. Ao criar um novo vale, o status não é explicitamente definido (depende do default do banco)
3. Se o banco não foi criado corretamente ou migrado, o default pode não estar funcionando

### 3. Templates

**listar.html (linha 59):**
```html
<span class="badge badge-sm {{ vale.get_status_badge_class() }}">{{ vale.get_status_display() }}</span>
```
✅ Está correto - usa os métodos do modelo

**listar.html (linha 68):**
```html
{% if vale.status == 'ativo' %}
```
⚠️ **ERRO: o status 'ativo' não existe!** Deveria ser `'pendente_entrega'` ou outro status válido

**visualizar.html (linha 14):**
```html
{% if vale.status == 'ativo' %}
```
⚠️ **ERRO: o status 'ativo' não existe!**

**visualizar.html (linha 38):**
```html
<div class="alert alert-{{ 'warning' if vale.status == 'pendente_entrega' else ('success' if vale.status == 'entrega_realizada' else 'secondary') }}">
```
✅ Está correto - usa os status válidos

**visualizar.html (linha 48):**
```html
{% if vale.status == 'pendente_entrega' %}
```
✅ Está correto

## Problemas Encontrados - Resumo

1. **Status 'ativo' inexistente**: Templates verificam `vale.status == 'ativo'` mas esse valor não existe
2. **Status 'finalizado' inexistente no mapeamento**: A rota `finalizar` define `status = 'finalizado'` mas esse valor não está mapeado em `get_status_display()` e `get_status_badge_class()`
3. **Falta de inicialização explícita**: Ao criar um vale, o status não é definido explicitamente no código Python

## Soluções Necessárias

### 1. Corrigir o modelo (models.py)

Adicionar o status 'finalizado' nos métodos de mapeamento:

```python
def get_status_display(self):
    """Retorna o nome do status em português"""
    status_map = {
        'pendente_entrega': 'Pendente de Entrega',
        'entrega_realizada': 'Entrega Realizada',
        'entrega_concluida': 'Entrega Concluída',
        'finalizado': 'Finalizado',  # ADICIONAR
        'cancelado': 'Cancelado'
    }
    return status_map.get(self.status, self.status)

def get_status_badge_class(self):
    """Retorna a classe CSS para o badge de status"""
    status_class = {
        'pendente_entrega': 'badge-warning',
        'entrega_realizada': 'badge-success',
        'entrega_concluida': 'badge-primary',
        'finalizado': 'badge-info',  # ADICIONAR
        'cancelado': 'badge-danger'
    }
    return status_class.get(self.status, 'badge-secondary')
```

### 2. Corrigir as rotas (vale_pallet.py)

Definir explicitamente o status ao criar um vale:

```python
# Linha 93-102
vale = ValePallet(
    cliente_id=form.cliente_id.data,
    transportadora_id=form.transportadora_id.data,
    destinatario_id=form.destinatario_id.data,
    motorista_id=form.motorista_id.data if form.motorista_id.data != 0 else None,
    quantidade_pallets=int(form.quantidade_pallets.data),
    numero_documento=form.numero_documento.data,
    pin=pin,
    status='pendente_entrega',  # ADICIONAR EXPLICITAMENTE
    criado_por_id=current_user.id
)
```

### 3. Corrigir os templates

**listar.html (linha 68):**
```html
{% if vale.status == 'pendente_entrega' %}
```

**visualizar.html (linha 14):**
```html
{% if vale.status == 'pendente_entrega' %}
```

## Causa Raiz do Problema

O campo `status` aparece em branco porque:

1. **Inconsistência nos templates**: Os templates verificam `vale.status == 'ativo'`, que nunca será verdadeiro
2. **Status não mapeado**: O status 'finalizado' existe no código mas não está mapeado nos métodos de exibição
3. **Possível problema no banco**: Se o banco foi criado sem o default ou se há registros antigos sem status

## Arquivos a Corrigir

1. `/app/models.py` - Adicionar 'finalizado' nos mapeamentos
2. `/app/routes/vale_pallet.py` - Definir status explicitamente ao criar
3. `/app/templates/vale_pallet/listar.html` - Corrigir verificação de status
4. `/app/templates/vale_pallet/visualizar.html` - Corrigir verificação de status
