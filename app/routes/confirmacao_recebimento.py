"""
Rotas para confirmação de recebimento de Vale Pallet (área autenticada)
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from app import db
from app.models import ValePallet, Empresa, Motorista
from datetime import datetime
from app.utils.whatsapp import enviar_whatsapp_recebimento_confirmado
from app.utils.auditoria import log_acao

confirmacao_bp = Blueprint('confirmacao', __name__, url_prefix='/confirmacao-recebimento')


@confirmacao_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    """
    Tela autenticada para confirmação de recebimento pelo destinatário
    Busca por cliente, transportadora e número do documento
    """
    vale = None
    pin_encontrado = None
    
    if request.method == 'POST':
        cliente_id = request.form.get('cliente_id')
        transportadora_id = request.form.get('transportadora_id')
        numero_documento = request.form.get('numero_documento')
        
        # Validar campos
        if not cliente_id or not transportadora_id or not numero_documento:
            flash('Por favor, preencha todos os campos.', 'danger')
        else:
            # Buscar vale pallet
            vale = ValePallet.query.filter_by(
                cliente_id=cliente_id,
                transportadora_id=transportadora_id,
                numero_documento=numero_documento
            ).first()
            
            if vale:
                pin_encontrado = vale.pin
                
                # Log de consulta
                log_acao(
                    modulo='confirmacao',
                    acao='consulta_vale',
                    descricao=f'Usuário {current_user.username} consultou vale {numero_documento}',
                    operacao_sql='SELECT',
                    tabela_afetada='vales_pallet'
                )
            else:
                flash('Nenhum vale encontrado com os dados informados.', 'warning')
    
    # Buscar empresas para os selects
    clientes = Empresa.query.join(Empresa.tipo).filter_by(nome='Cliente', ativo=True).all()
    transportadoras = Empresa.query.join(Empresa.tipo).filter_by(nome='Transportadora', ativo=True).all()
    
    return render_template('confirmacao_recebimento/index.html',
                         clientes=clientes,
                         transportadoras=transportadoras,
                         vale=vale,
                         pin_encontrado=pin_encontrado,
                         now=datetime.now())


@confirmacao_bp.route('/confirmar/<int:vale_id>', methods=['POST'])
@login_required
def confirmar(vale_id):
    """
    Confirma a entrega do vale pallet
    Muda o status para 'entrega_realizada'
    """
    vale = ValePallet.query.get_or_404(vale_id)
    
    if vale.status == 'entrega_realizada':
        flash('Esta entrega já foi confirmada anteriormente.', 'info')
    elif vale.status == 'entrega_concluida':
        flash('Esta entrega já foi concluída (PIN validado pelo motorista).', 'info')
    else:
        status_anterior = vale.status
        vale.status = 'entrega_realizada'
        vale.data_confirmacao = datetime.utcnow()
        db.session.commit()
        
        # Registrar log
        log_acao(
            modulo='confirmacao',
            acao='confirmar_entrega',
            descricao=f'Usuário {current_user.username} confirmou entrega do vale {vale.numero_documento}. Status anterior: {status_anterior}',
            operacao_sql='UPDATE',
            tabela_afetada='vales_pallet',
            registro_id=vale.id
        )
        
        # Enviar WhatsApp para o motorista (se houver motorista vinculado)
        if vale.motorista_id:
            motorista = Motorista.query.get(vale.motorista_id)
            if motorista and motorista.celular:
                enviado = enviar_whatsapp_recebimento_confirmado(motorista, vale)
                if enviado:
                    flash('Entrega confirmada com sucesso! WhatsApp enviado para o motorista.', 'success')
                else:
                    flash('Entrega confirmada com sucesso! Erro ao enviar WhatsApp para o motorista.', 'warning')
            else:
                flash('Entrega confirmada com sucesso!', 'success')
        else:
            flash('Entrega confirmada com sucesso!', 'success')
    
    return redirect(url_for('confirmacao.index'))
