from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from app.models import ValePallet, Empresa, TipoEmpresa
from sqlalchemy import func
from app.utils.auditoria import log_acesso_tela

bp = Blueprint('relatorios', __name__, url_prefix='/relatorios')


@bp.route('/movimentacao')
@login_required
def movimentacao():
    """Relatório de movimentação de pallets agrupado por destinatário"""
    log_acesso_tela('relatorios', 'Relatório de Movimentação')
    
    # Buscar tipo Destinatário
    tipo_destinatario = TipoEmpresa.query.filter_by(nome='Destinatário').first()
    
    if not tipo_destinatario:
        return render_template('relatorios/movimentacao.html', 
                             destinatarios=[], 
                             total_geral_pallets=0,
                             total_geral_vales=0)
    
    # Buscar todos os destinatários
    destinatarios_query = Empresa.query.filter_by(tipo_id=tipo_destinatario.id)
    
    # Filtrar por empresa do usuário se não for admin
    if current_user.empresa_id:
        # Usuário só vê destinatários da sua empresa ou que ele cadastrou
        destinatarios_query = destinatarios_query.filter(
            (Empresa.id == current_user.empresa_id) | 
            (Empresa.cadastrado_por_id == current_user.id)
        )
    
    destinatarios = destinatarios_query.all()
    
    # Montar dados do relatório
    dados_relatorio = []
    total_geral_pallets = 0
    total_geral_vales = 0
    
    for destinatario in destinatarios:
        # Buscar todos os vales deste destinatário
        vales = ValePallet.query.filter_by(destinatario_id=destinatario.id).order_by(ValePallet.data_criacao.desc()).all()
        
        if vales:
            # Calcular totais
            total_pallets = sum(vale.quantidade_pallets for vale in vales)
            total_vales = len(vales)
            
            dados_relatorio.append({
                'destinatario': destinatario,
                'vales': vales,
                'total_pallets': total_pallets,
                'total_vales': total_vales
            })
            
            total_geral_pallets += total_pallets
            total_geral_vales += total_vales
    
    return render_template('relatorios/movimentacao.html',
                         dados_relatorio=dados_relatorio,
                         total_geral_pallets=total_geral_pallets,
                         total_geral_vales=total_geral_vales)
