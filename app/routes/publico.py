"""
Rotas públicas (sem necessidade de login)
Para confirmação de recebimento e validação de PIN
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from app import db
from app.models import ValePallet, Empresa, Motorista
from datetime import datetime
from app.utils.whatsapp import enviar_whatsapp_recebimento_confirmado
from app.utils.auditoria import log_acao

publico_bp = Blueprint('publico', __name__, url_prefix='/publico')


@publico_bp.route('/confirmacao-recebimento', methods=['GET', 'POST'])
def confirmacao_recebimento():
    """
    Tela pública para confirmação de recebimento pelo destinatário
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
                # As propriedades cliente_nome, transportadora_nome e destinatario_nome
                # já são calculadas automaticamente pelo modelo
            else:
                flash('Nenhum vale encontrado com os dados informados.', 'warning')
    
    # Buscar empresas para os selects
    clientes = Empresa.query.join(Empresa.tipo).filter_by(nome='Cliente', ativo=True).all()
    transportadoras = Empresa.query.join(Empresa.tipo).filter_by(nome='Transportadora', ativo=True).all()
    
    return render_template('publico/confirmacao_recebimento.html',
                         clientes=clientes,
                         transportadoras=transportadoras,
                         vale=vale,
                         pin_encontrado=pin_encontrado,
                         now=datetime.now())


@publico_bp.route('/confirmar-entrega/<int:vale_id>', methods=['POST'])
def confirmar_entrega(vale_id):
    """
    Confirma a entrega do vale pallet
    Muda o status para 'entrega_realizada'
    """
    vale = ValePallet.query.get_or_404(vale_id)
    
    if vale.status == 'entrega_realizada':
        flash('Esta entrega já foi confirmada anteriormente.', 'info')
    else:
        vale.status = 'entrega_realizada'
        vale.data_confirmacao = datetime.utcnow()
        db.session.commit()
        
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
    
    return redirect(url_for('publico.confirmacao_recebimento'))


@publico_bp.route('/validacao-pin', methods=['GET', 'POST'])
def validacao_pin():
    """
    Tela pública para validação do PIN pelo motorista
    Verifica se o número do documento e PIN correspondem
    """
    resultado = None
    mensagem = None
    tipo_mensagem = None
    
    if request.method == 'POST':
        numero_documento = request.form.get('numero_documento', '').strip()
        pin = request.form.get('pin', '').strip()
        
        # Validar campos
        if not numero_documento or not pin:
            flash('Por favor, preencha todos os campos.', 'danger')
        else:
            # Debug: Log da tentativa de validação
            current_app.logger.info(f'Tentativa de validação - Doc: {numero_documento}, PIN: {pin}')
            
            # Buscar vale pallet
            vale = ValePallet.query.filter_by(
                numero_documento=numero_documento,
                pin=pin
            ).first()
            
            # Debug: Log do resultado da busca
            if vale:
                current_app.logger.info(f'Vale encontrado - ID: {vale.id}, Status: {vale.status}')
            else:
                current_app.logger.warning(f'Vale NÃO encontrado - Doc: {numero_documento}, PIN: {pin}')
                # Verificar se existe vale com esse documento
                vale_doc = ValePallet.query.filter_by(numero_documento=numero_documento).first()
                if vale_doc:
                    current_app.logger.warning(f'Vale existe mas PIN diferente. PIN correto: {vale_doc.pin}')
            
            if vale:
                # Aceitar validação se status for pendente_entrega ou entrega_realizada
                if vale.status in ['pendente_entrega', 'entrega_realizada']:
                    # Atualizar status para Entrega Concluída
                    status_anterior = vale.status
                    vale.status = 'entrega_concluida'
                    db.session.commit()
                    
                    # Registrar log
                    log_acao(
                        modulo='publico',
                        acao='validacao_pin_web',
                        descricao=f'PIN {pin} validado via web. Vale: {vale.numero_documento}. Status anterior: {status_anterior}',
                        operacao_sql='UPDATE',
                        tabela_afetada='vales_pallet'
                    )
                    
                    # Enviar WhatsApp para o motorista informando entrega concluída
                    try:
                        from app.utils.whatsapp import enviar_whatsapp_entrega_concluida
                        from app.models import Motorista
                        
                        # Buscar motorista (mais robusto que usar relacionamento)
                        if vale.motorista_id:
                            motorista = Motorista.query.get(vale.motorista_id)
                            if motorista and motorista.celular:
                                enviar_whatsapp_entrega_concluida(motorista, vale)
                    except Exception as e:
                        # Log do erro mas não interrompe o fluxo
                        current_app.logger.error(f'Erro ao enviar WhatsApp: {str(e)}')
                    
                    resultado = 'sucesso'
                    if status_anterior == 'pendente_entrega':
                        mensagem = 'Recebimento validado com sucesso! O destinatário ainda não confirmou, mas a entrega foi concluída.'
                    else:
                        mensagem = 'Recebimento realizado com sucesso! Entrega concluída.'
                    tipo_mensagem = 'success'
                elif vale.status == 'entrega_concluida':
                    resultado = 'sucesso'
                    mensagem = 'Esta entrega já foi validada anteriormente. Entrega concluída.'
                    tipo_mensagem = 'info'
                else:
                    resultado = 'erro'
                    mensagem = f'O documento foi encontrado, mas está com status: {vale.get_status_display()}. Não é possível validar.'
                    tipo_mensagem = 'warning'
            else:
                resultado = 'erro'
                mensagem = 'Documento e/ou PIN informado está incorreto. ATENÇÃO: Se esse processo não for concluído, os pallets mencionados poderão ser cobrados do responsável pela entrega!'
                tipo_mensagem = 'danger'
    
    return render_template('publico/validacao_pin.html',
                         resultado=resultado,
                         mensagem=mensagem,
                         tipo_mensagem=tipo_mensagem)


@publico_bp.route('/validar-vale/<int:vale_id>/<string:hash_validacao>')
def validar_vale_qrcode(vale_id, hash_validacao):
    """
    Página pública para validação de vale via QR Code
    Verifica autenticidade do documento impresso
    """
    from app.utils.qrcode_utils import validar_hash_vale
    
    # Buscar vale
    vale = ValePallet.query.get(vale_id)
    
    if not vale:
        return render_template(
            'publico/validar_vale_qrcode.html',
            valido=False,
            mensagem='Vale não encontrado no sistema.',
            vale=None
        )
    
    # Validar hash
    hash_valido = validar_hash_vale(
        vale.id,
        vale.numero_documento,
        vale.pin,
        vale.data_criacao,
        hash_validacao
    )
    
    if not hash_valido:
        return render_template(
            'publico/validar_vale_qrcode.html',
            valido=False,
            mensagem='Documento inválido! A assinatura digital não confere.',
            vale=None
        )
    
    # Verificar se está vencido
    vencido = vale.data_vencimento < datetime.now().date()
    
    # Calcular saldo
    saldo = vale.quantidade_pallets - vale.quantidade_devolvida
    
    # Registrar log de validação
    log_acao(
        modulo='vale_pallet',
        acao='validar_qrcode',
        descricao=f'Vale {vale.numero_documento} validado via QR Code',
        registro_id=vale.id,
        operacao_sql='SELECT',
        tabela_afetada='vales_pallet'
    )
    
    return render_template(
        'publico/validar_vale_qrcode.html',
        valido=True,
        mensagem='Documento autêntico! Assinatura digital verificada.',
        vale=vale,
        vencido=vencido,
        saldo=saldo
    )
