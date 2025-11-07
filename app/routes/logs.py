from flask import Blueprint, render_template, request
from flask_login import login_required
from app.models import LogAuditoria
from app.utils.auditoria import log_acesso_tela

bp = Blueprint('logs', __name__, url_prefix='/logs')


@bp.route('/')
@login_required
def listar():
    """Lista todos os logs de auditoria"""
    log_acesso_tela('logs', 'Logs de Auditoria')
    
    # Paginação
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    # Filtros
    modulo = request.args.get('modulo', '')
    acao = request.args.get('acao', '')
    usuario = request.args.get('usuario', '')
    
    # Query base
    query = LogAuditoria.query
    
    # Aplicar filtros
    if modulo:
        query = query.filter(LogAuditoria.modulo.like(f'%{modulo}%'))
    if acao:
        query = query.filter(LogAuditoria.acao.like(f'%{acao}%'))
    if usuario:
        query = query.filter(LogAuditoria.usuario_nome.like(f'%{usuario}%'))
    
    # Ordenar por data decrescente
    query = query.order_by(LogAuditoria.data_hora.desc())
    
    # Paginar
    logs_paginados = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('logs/listar.html',
                         logs=logs_paginados.items,
                         pagination=logs_paginados,
                         modulo=modulo,
                         acao=acao,
                         usuario=usuario)
