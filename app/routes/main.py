from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models import User, Empresa, ValePallet, Motorista, TipoEmpresa, LogAuditoria
from app import db
from datetime import datetime, timedelta
from sqlalchemy import func

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    """Página inicial - redireciona para login ou dashboard"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))


@bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard principal do sistema"""
    from app.utils.auditoria import log_acesso_tela
    log_acesso_tela('dashboard', 'Dashboard Principal')
    
    # Estatísticas de empresas
    total_empresas = Empresa.query.count()
    empresas_ativas = Empresa.query.filter_by(ativa=True).count()
    
    # Empresas cadastradas este mês
    inicio_mes = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    empresas_mes = Empresa.query.filter(Empresa.data_criacao >= inicio_mes).count()
    
    # Estatísticas de vales pallet
    vales_pendentes = ValePallet.query.filter_by(status='pendente_entrega').count()
    vales_realizados = ValePallet.query.filter_by(status='entrega_realizada').count()
    vales_mes_atual = ValePallet.query.filter(ValePallet.data_criacao >= inicio_mes).count()
    
    # Total de pallets (soma de todos os vales)
    total_pallets_result = db.session.query(func.sum(ValePallet.quantidade_pallets)).scalar()
    total_pallets = total_pallets_result if total_pallets_result else 0
    
    # Estatísticas por tipo de empresa
    empresas_por_tipo = {}
    tipos = TipoEmpresa.query.all()
    for tipo in tipos:
        count = Empresa.query.filter_by(tipo_empresa_id=tipo.id).count()
        empresas_por_tipo[tipo.nome] = count
    
    # Total de motoristas
    total_motoristas = Motorista.query.count()
    
    # Logs de hoje
    hoje = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    logs_hoje = LogAuditoria.query.filter(LogAuditoria.data_hora >= hoje).count()
    
    # Vales recentes
    vales_recentes = ValePallet.query.order_by(ValePallet.data_criacao.desc()).limit(10).all()
    
    # Logs recentes
    logs_recentes = LogAuditoria.query.order_by(LogAuditoria.data_hora.desc()).limit(10).all()
    
    # Montar objeto de estatísticas
    stats = {
        'total_empresas': total_empresas,
        'empresas_ativas': empresas_ativas,
        'empresas_mes': empresas_mes,
        'vales_pendentes': vales_pendentes,
        'vales_realizados': vales_realizados,
        'vales_mes_atual': vales_mes_atual,
        'total_pallets': total_pallets,
        'empresas_por_tipo': empresas_por_tipo,
        'total_motoristas': total_motoristas,
        'logs_hoje': logs_hoje
    }
    
    return render_template('dashboard.html',
                         stats=stats,
                         vales_recentes=vales_recentes,
                         logs_recentes=logs_recentes)


@bp.route('/profile')
@login_required
def profile():
    """Página de perfil do usuário"""
    from app.utils.auditoria import log_acesso_tela
    log_acesso_tela('profile', 'Perfil do Usuário')
    
    return render_template('profile.html')
