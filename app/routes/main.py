from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models import User, Empresa, ValePallet, Motorista, TipoEmpresa, LogAuditoria, DevolucaoPallet
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
    hoje_datetime = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    logs_hoje = LogAuditoria.query.filter(LogAuditoria.data_hora >= hoje_datetime).count()
    
    # Vales recentes
    vales_recentes = ValePallet.query.order_by(ValePallet.data_criacao.desc()).limit(10).all()
    
    # Logs recentes
    logs_recentes = LogAuditoria.query.order_by(LogAuditoria.data_hora.desc()).limit(10).all()
    
    # ========== NOVOS CÁLCULOS DE VENCIMENTO ==========
    
    # Data de hoje
    hoje = datetime.now().date()
    
    # Calcular pallets não devolvidos (saldo > 0) por período de vencimento
    # Status válidos: entrega_realizada, entrega_concluida
    status_validos = ['entrega_realizada', 'entrega_concluida']
    
    # Pallets vencendo hoje
    pallets_vencendo_hoje = db.session.query(
        func.sum(ValePallet.quantidade_pallets - ValePallet.quantidade_devolvida)
    ).filter(
        ValePallet.status.in_(status_validos),
        ValePallet.data_vencimento == hoje,
        ValePallet.quantidade_pallets > ValePallet.quantidade_devolvida
    ).scalar() or 0
    
    # Pallets vencendo em 3 dias
    data_3_dias = hoje + timedelta(days=3)
    pallets_vencendo_3_dias = db.session.query(
        func.sum(ValePallet.quantidade_pallets - ValePallet.quantidade_devolvida)
    ).filter(
        ValePallet.status.in_(status_validos),
        ValePallet.data_vencimento > hoje,
        ValePallet.data_vencimento <= data_3_dias,
        ValePallet.quantidade_pallets > ValePallet.quantidade_devolvida
    ).scalar() or 0
    
    # Pallets vencendo em 7 dias
    data_7_dias = hoje + timedelta(days=7)
    pallets_vencendo_7_dias = db.session.query(
        func.sum(ValePallet.quantidade_pallets - ValePallet.quantidade_devolvida)
    ).filter(
        ValePallet.status.in_(status_validos),
        ValePallet.data_vencimento > data_3_dias,
        ValePallet.data_vencimento <= data_7_dias,
        ValePallet.quantidade_pallets > ValePallet.quantidade_devolvida
    ).scalar() or 0
    
    # Pallets vencendo em até 30 dias
    data_30_dias = hoje + timedelta(days=30)
    pallets_vencendo_30_dias = db.session.query(
        func.sum(ValePallet.quantidade_pallets - ValePallet.quantidade_devolvida)
    ).filter(
        ValePallet.status.in_(status_validos),
        ValePallet.data_vencimento > data_7_dias,
        ValePallet.data_vencimento <= data_30_dias,
        ValePallet.quantidade_pallets > ValePallet.quantidade_devolvida
    ).scalar() or 0
    
    # Pallets vencendo acima de 30 dias (30 a 60 dias)
    data_60_dias = hoje + timedelta(days=60)
    pallets_vencendo_acima_30_dias = db.session.query(
        func.sum(ValePallet.quantidade_pallets - ValePallet.quantidade_devolvida)
    ).filter(
        ValePallet.status.in_(status_validos),
        ValePallet.data_vencimento > data_30_dias,
        ValePallet.data_vencimento <= data_60_dias,
        ValePallet.quantidade_pallets > ValePallet.quantidade_devolvida
    ).scalar() or 0
    
    # Total de pallets a devolver (saldo > 0)
    total_pallets_devolver = db.session.query(
        func.sum(ValePallet.quantidade_pallets - ValePallet.quantidade_devolvida)
    ).filter(
        ValePallet.status.in_(status_validos),
        ValePallet.quantidade_pallets > ValePallet.quantidade_devolvida
    ).scalar() or 0
    
    # Pallets vencidos (acima de 30 dias)
    data_vencidos = hoje - timedelta(days=1)  # Vencidos = antes de hoje
    pallets_vencidos = db.session.query(
        func.sum(ValePallet.quantidade_pallets - ValePallet.quantidade_devolvida)
    ).filter(
        ValePallet.status.in_(status_validos),
        ValePallet.data_vencimento < hoje,
        ValePallet.quantidade_pallets > ValePallet.quantidade_devolvida
    ).scalar() or 0
    
    # Top 10 destinatários com mais pallets para devolução
    top_destinatarios = db.session.query(
        Empresa.razao_social,
        func.sum(ValePallet.quantidade_pallets - ValePallet.quantidade_devolvida).label('saldo')
    ).join(
        ValePallet, ValePallet.destinatario_id == Empresa.id
    ).filter(
        ValePallet.status.in_(status_validos),
        ValePallet.quantidade_pallets > ValePallet.quantidade_devolvida
    ).group_by(
        Empresa.id, Empresa.razao_social
    ).order_by(
        func.sum(ValePallet.quantidade_pallets - ValePallet.quantidade_devolvida).desc()
    ).limit(10).all()
    
    # ========== EVENTOS DO CALENDÁRIO ==========
    
    # Agendamentos de devolução (próximos 60 dias)
    data_fim_calendario = hoje + timedelta(days=60)
    agendamentos_raw = db.session.query(
        DevolucaoPallet.id,
        DevolucaoPallet.data_agendamento,
        DevolucaoPallet.quantidade_pallets,
        DevolucaoPallet.status,
        Empresa.razao_social.label('destinatario_nome'),
        Empresa.id.label('destinatario_id')
    ).join(
        Empresa, DevolucaoPallet.destinatario_id == Empresa.id
    ).filter(
        DevolucaoPallet.data_agendamento >= hoje,
        DevolucaoPallet.data_agendamento <= data_fim_calendario,
        DevolucaoPallet.status.in_(['agendado', 'coletado'])
    ).all()
    
    # Converter Row para dicionário (JSON serializável)
    agendamentos = [
        {
            'id': row.id,
            'data_agendamento': row.data_agendamento.strftime('%Y-%m-%d'),
            'quantidade_pallets': row.quantidade_pallets,
            'status': row.status,
            'destinatario_nome': row.destinatario_nome,
            'destinatario_id': row.destinatario_id
        }
        for row in agendamentos_raw
    ]
    
    # Vencimentos sem agendamento (próximos 60 dias)
    # Buscar vales que vencem mas não têm devolução agendada
    vencimentos_raw = db.session.query(
        ValePallet.id,
        ValePallet.data_vencimento,
        ValePallet.quantidade_pallets,
        ValePallet.quantidade_devolvida,
        Empresa.razao_social.label('destinatario_nome'),
        Empresa.id.label('destinatario_id')
    ).join(
        Empresa, ValePallet.destinatario_id == Empresa.id
    ).filter(
        ValePallet.status.in_(status_validos),
        ValePallet.data_vencimento >= hoje,
        ValePallet.data_vencimento <= data_fim_calendario,
        ValePallet.quantidade_pallets > ValePallet.quantidade_devolvida
    ).all()
    
    # Converter Row para dicionário (JSON serializável)
    vencimentos_sem_agendamento = [
        {
            'id': row.id,
            'data_vencimento': row.data_vencimento.strftime('%Y-%m-%d'),
            'quantidade_pallets': row.quantidade_pallets,
            'quantidade_devolvida': row.quantidade_devolvida,
            'destinatario_nome': row.destinatario_nome,
            'destinatario_id': row.destinatario_id
        }
        for row in vencimentos_raw
    ]
    
    # ========== FIM DOS NOVOS CÁLCULOS ==========
    
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
        'logs_hoje': logs_hoje,
        # Novos dados de vencimento
        'pallets_vencendo_hoje': int(pallets_vencendo_hoje),
        'pallets_vencendo_3_dias': int(pallets_vencendo_3_dias),
        'pallets_vencendo_7_dias': int(pallets_vencendo_7_dias),
        'pallets_vencendo_30_dias': int(pallets_vencendo_30_dias),
        'pallets_vencendo_acima_30_dias': int(pallets_vencendo_acima_30_dias),
        'pallets_vencidos': int(pallets_vencidos),
        'total_pallets_devolver': int(total_pallets_devolver)
    }
    
    return render_template('dashboard.html',
                         stats=stats,
                         vales_recentes=vales_recentes,
                         logs_recentes=logs_recentes,
                         top_destinatarios=top_destinatarios,
                         agendamentos=agendamentos,
                         vencimentos_sem_agendamento=vencimentos_sem_agendamento)


@bp.route('/profile')
@login_required
def profile():
    """Página de perfil do usuário"""
    from app.utils.auditoria import log_acesso_tela
    log_acesso_tela('profile', 'Perfil do Usuário')
    
    return render_template('profile.html')
