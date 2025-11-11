"""
Decorators para controle de acesso e permissões
"""
from functools import wraps
from flask import flash, redirect, url_for, abort
from flask_login import current_user


def perfil_required(f):
    """
    Decorator que verifica se o usuário tem um perfil atribuído
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Você precisa estar autenticado para acessar esta página.', 'warning')
            return redirect(url_for('auth.login'))
        
        if not current_user.perfil_id:
            flash('Seu usuário não possui um perfil atribuído. Entre em contato com o administrador.', 'danger')
            return redirect(url_for('main.dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function


def permissao_required(modulo, acao='visualizar'):
    """
    Decorator que verifica se o usuário tem permissão para uma ação em um módulo
    
    Args:
        modulo: Nome do módulo (ex: 'empresas', 'vale_pallet')
        acao: Tipo de ação (visualizar, criar, editar, excluir)
    
    Exemplo:
        @permissao_required('empresas', 'criar')
        def nova_empresa():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Você precisa estar autenticado para acessar esta página.', 'warning')
                return redirect(url_for('auth.login'))
            
            if not current_user.perfil_id:
                flash('Seu usuário não possui um perfil atribuído. Entre em contato com o administrador.', 'danger')
                return redirect(url_for('main.dashboard'))
            
            if not current_user.tem_permissao(modulo, acao):
                flash(f'Você não tem permissão para {acao} em {modulo}.', 'danger')
                return redirect(url_for('main.dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def empresa_required(f):
    """
    Decorator que verifica se o usuário está vinculado a uma empresa
    Necessário para sistema multi-empresas
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Você precisa estar autenticado para acessar esta página.', 'warning')
            return redirect(url_for('auth.login'))
        
        if not current_user.empresa_id:
            flash('Seu usuário não está vinculado a nenhuma empresa. Entre em contato com o administrador.', 'danger')
            return redirect(url_for('main.dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """
    Decorator que verifica se o usuário tem perfil de administrador
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Você precisa estar autenticado para acessar esta página.', 'warning')
            return redirect(url_for('auth.login'))
        
        if not current_user.perfil_id:
            flash('Seu usuário não possui um perfil atribuído.', 'danger')
            return redirect(url_for('main.dashboard'))
        
        # Verifica se o perfil é "Administrador"
        from app.models import Perfil
        perfil = Perfil.query.get(current_user.perfil_id)
        if not perfil or perfil.nome != 'Administrador':
            flash('Você não tem permissão para acessar esta área.', 'danger')
            return redirect(url_for('main.dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function


def filtrar_por_empresa(query, model):
    """
    Função auxiliar para filtrar queries por empresa do usuário
    Aplica isolamento multi-empresas
    
    Args:
        query: Query do SQLAlchemy
        model: Modelo que possui empresa_id
    
    Returns:
        Query filtrada pela empresa do usuário
    
    Exemplo:
        query = Motorista.query
        query = filtrar_por_empresa(query, Motorista)
        motoristas = query.all()
    """
    if not current_user.is_authenticated:
        return query.filter_by(id=None)  # Retorna query vazia
    
    if not current_user.empresa_id:
        return query.filter_by(id=None)  # Retorna query vazia
    
    # Filtra pela empresa do usuário
    return query.filter_by(empresa_id=current_user.empresa_id)


def pode_acessar_registro(registro):
    """
    Verifica se o usuário pode acessar um registro específico
    Baseado na empresa vinculada
    
    Args:
        registro: Objeto do modelo que possui empresa_id
    
    Returns:
        True se pode acessar, False caso contrário
    """
    if not current_user.is_authenticated:
        return False
    
    if not current_user.empresa_id:
        return False
    
    # Verifica se o registro pertence à empresa do usuário
    if hasattr(registro, 'empresa_id'):
        return registro.empresa_id == current_user.empresa_id
    
    # Se não tem empresa_id, verifica se foi criado pelo usuário
    if hasattr(registro, 'criado_por_id'):
        return registro.criado_por_id == current_user.id
    
    return False
