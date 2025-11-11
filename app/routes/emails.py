"""
Rotas para Consulta de Emails Enviados
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import EmailEnviado, ValePallet, Empresa
from app.utils.decorators import permissao_required
from app.utils.email_service import reenviar_email

emails_bp = Blueprint('emails', __name__, url_prefix='/emails')


@emails_bp.route('/listar', methods=['GET'])
@login_required
@permissao_required('emails', 'visualizar')
def listar():
    """Lista emails enviados com filtros"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Filtros
    status = request.args.get('status', '')
    empresa_id = request.args.get('empresa_id', '', type=int)
    data_inicio = request.args.get('data_inicio', '')
    data_fim = request.args.get('data_fim', '')
    
    # Query base
    query = EmailEnviado.query
    
    # Aplicar filtros
    if status:
        query = query.filter_by(status=status)
    
    if empresa_id:
        # Filtrar por empresa destinatária
        query = query.join(ValePallet).filter(ValePallet.destinatario_id == empresa_id)
    
    if data_inicio:
        from datetime import datetime
        data_inicio_dt = datetime.strptime(data_inicio, '%Y-%m-%d')
        query = query.filter(EmailEnviado.data_envio >= data_inicio_dt)
    
    if data_fim:
        from datetime import datetime
        data_fim_dt = datetime.strptime(data_fim, '%Y-%m-%d')
        data_fim_dt = data_fim_dt.replace(hour=23, minute=59, second=59)
        query = query.filter(EmailEnviado.data_envio <= data_fim_dt)
    
    # Se não for administrador, filtrar por empresa
    if current_user.empresa_id:
        if not (current_user.perfil_rel and current_user.perfil_rel.nome == 'Administrador'):
            query = query.join(ValePallet).filter(
                (ValePallet.destinatario_id == current_user.empresa_id) |
                (ValePallet.cliente_id == current_user.empresa_id) |
                (ValePallet.transportadora_id == current_user.empresa_id)
            )
    
    # Ordenar e paginar
    emails = query.order_by(EmailEnviado.data_envio.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Buscar empresas para filtro
    if current_user.perfil_rel and current_user.perfil_rel.nome == 'Administrador':
        empresas = Empresa.query.filter_by(ativa=True).order_by(Empresa.razao_social).all()
    else:
        empresas = Empresa.query.filter_by(id=current_user.empresa_id).all() if current_user.empresa_id else []
    
    return render_template('emails/listar.html', 
                         emails=emails, 
                         empresas=empresas,
                         status_atual=status,
                         empresa_id_atual=empresa_id,
                         data_inicio=data_inicio,
                         data_fim=data_fim)


@emails_bp.route('/visualizar/<int:id>', methods=['GET'])
@login_required
@permissao_required('emails', 'visualizar')
def visualizar(id):
    """Visualiza detalhes de um email enviado"""
    email = EmailEnviado.query.get_or_404(id)
    
    # Verificar permissão
    if current_user.empresa_id:
        if not (current_user.perfil_rel and current_user.perfil_rel.nome == 'Administrador'):
            vale = email.vale_pallet
            if (vale.destinatario_id != current_user.empresa_id and 
                vale.cliente_id != current_user.empresa_id and 
                vale.transportadora_id != current_user.empresa_id):
                flash('Você não tem permissão para visualizar este email.', 'danger')
                return redirect(url_for('emails.listar'))
    
    return render_template('emails/visualizar.html', email=email)


@emails_bp.route('/reenviar/<int:id>', methods=['POST'])
@login_required
@permissao_required('emails', 'criar')
def reenviar(id):
    """Reenvia um email"""
    email = EmailEnviado.query.get_or_404(id)
    
    # Verificar permissão
    if current_user.empresa_id:
        if not (current_user.perfil_rel and current_user.perfil_rel.nome == 'Administrador'):
            vale = email.vale_pallet
            if (vale.destinatario_id != current_user.empresa_id and 
                vale.cliente_id != current_user.empresa_id and 
                vale.transportadora_id != current_user.empresa_id):
                flash('Você não tem permissão para reenviar este email.', 'danger')
                return redirect(url_for('emails.listar'))
    
    resultado = reenviar_email(id, current_user.id)
    
    if resultado['sucesso']:
        flash(resultado['mensagem'], 'success')
    else:
        flash(resultado['mensagem'], 'danger')
    
    return redirect(url_for('emails.visualizar', id=id))
