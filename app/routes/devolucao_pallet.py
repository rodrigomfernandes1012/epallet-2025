"""
Rotas para Devolução de Pallets
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import DevolucaoPallet, DevolucaoBaixa, ValePallet, Empresa, Motorista
from app.forms_devolucao import (
    DevolucaoPalletForm, ValidarPinDevolucaoForm,
    ConfirmarDevolucaoForm, CancelarDevolucaoForm
)
from app.utils.decorators import permissao_required
from app.utils.auditoria import log_acao
from app.utils.devolucao_service import (
    gerar_pin_devolucao, calcular_saldo_disponivel,
    processar_baixa_fifo, enviar_email_devolucao,
    enviar_whatsapp_motorista, enviar_whatsapp_motorista_confirmacao,
    validar_pin_devolucao
)
from datetime import datetime
from sqlalchemy import func, or_

devolucao_pallet_bp = Blueprint('devolucao_pallet', __name__, url_prefix='/devolucao-pallet')


@devolucao_pallet_bp.route('/')
@login_required
@permissao_required('devolucao_pallet', 'visualizar')
def listar():
    """Lista todas as devoluções"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Filtros
    status_filtro = request.args.get('status', '')
    cliente_filtro = request.args.get('cliente', '', type=int)
    destinatario_filtro = request.args.get('destinatario', '', type=int)
    
    # Query base
    query = DevolucaoPallet.query
    
    # Aplicar filtros
    if status_filtro:
        query = query.filter_by(status=status_filtro)
    
    if cliente_filtro:
        query = query.filter_by(cliente_id=cliente_filtro)
    
    if destinatario_filtro:
        query = query.filter_by(destinatario_id=destinatario_filtro)
    
    # Ordenar por data de criação (mais recentes primeiro)
    query = query.order_by(DevolucaoPallet.criado_em.desc())
    
    # Paginar
    devolucoes = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Buscar empresas para filtros
    clientes = Empresa.query.join(Empresa.tipo_empresa_rel).filter(
        Empresa.tipo_empresa_rel.has(nome='Cliente'),
        Empresa.ativa == True
    ).order_by(Empresa.razao_social).all()
    
    destinatarios = Empresa.query.join(Empresa.tipo_empresa_rel).filter(
        Empresa.tipo_empresa_rel.has(nome='Destinatário'),
        Empresa.ativa == True
    ).order_by(Empresa.razao_social).all()
    
    # Registrar log
    log_acao(
        modulo='devolucao_pallet',
        acao='read',
        descricao='Listou devoluções de pallets'
    )
    
    return render_template(
        'devolucao_pallet/listar.html',
        devolucoes=devolucoes,
        clientes=clientes,
        destinatarios=destinatarios,
        status_filtro=status_filtro,
        cliente_filtro=cliente_filtro,
        destinatario_filtro=destinatario_filtro
    )


@devolucao_pallet_bp.route('/novo', methods=['GET', 'POST'])
@login_required
@permissao_required('devolucao_pallet', 'criar')
def novo():
    """Cria uma nova devolução"""
    form = DevolucaoPalletForm()
    
    if form.validate_on_submit():
        try:
            # Gerar PIN único
            pin = gerar_pin_devolucao()
            
            # Criar devolução
            devolucao = DevolucaoPallet(
                cliente_id=form.cliente_id.data,
                destinatario_id=form.destinatario_id.data,
                transportadora_id=form.transportadora_id.data,
                motorista_id=form.motorista_id.data if form.motorista_id.data != 0 else None,
                quantidade_pallets=form.quantidade_pallets.data,
                data_agendamento=form.data_agendamento.data,
                pin_devolucao=pin,
                observacoes=form.observacoes.data,
                status='agendado',
                criado_por_id=current_user.id
            )
            
            db.session.add(devolucao)
            db.session.commit()
            
            # Enviar email para destinatário
            resultado_email = enviar_email_devolucao(devolucao.id, current_user.id)
            
            # Enviar WhatsApp para motorista informando agendamento
            resultado_whatsapp = None
            if devolucao.motorista_id:
                print(f"[DEBUG] Enviando WhatsApp para motorista ID: {devolucao.motorista_id}")
                from app.utils.devolucao_service import enviar_whatsapp_agendamento_motorista
                resultado_whatsapp = enviar_whatsapp_agendamento_motorista(devolucao.id)
                print(f"[DEBUG] Resultado WhatsApp: {resultado_whatsapp}")
            else:
                print("[DEBUG] Motorista não selecionado, WhatsApp não será enviado")
            
            # Mensagem de sucesso
            mensagem = f'Devolução agendada com sucesso!'
            
            if resultado_email['sucesso']:
                mensagem += f' {resultado_email["emails_enviados"]} email(s) enviado(s).'
            else:
                mensagem += f' Aviso: {resultado_email["mensagem"]}'
            
            if resultado_whatsapp:
                if resultado_whatsapp['sucesso']:
                    mensagem += ' WhatsApp de agendamento enviado ao motorista.'
                else:
                    mensagem += f' Aviso WhatsApp: {resultado_whatsapp["mensagem"]}'
            
            flash(mensagem, 'success')
            
            # Registrar log
            log_acao(
                modulo='devolucao_pallet',
                acao='create',
                descricao=f'Criou devolução #{devolucao.id} - {devolucao.quantidade_pallets} pallets'
            )
            
            return redirect(url_for('devolucao_pallet.visualizar', id=devolucao.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar devolução: {str(e)}', 'danger')
            
            # Registrar log de erro
            log_acao(
                modulo='devolucao_pallet',
                acao='create',
                descricao=f'Erro ao criar devolução: {str(e)}'
            )
    
    return render_template('devolucao_pallet/form.html', form=form, titulo='Nova Devolução')


@devolucao_pallet_bp.route('/<int:id>')
@login_required
@permissao_required('devolucao_pallet', 'visualizar')
def visualizar(id):
    """Visualiza uma devolução"""
    devolucao = DevolucaoPallet.query.get_or_404(id)
    
    # Buscar baixas relacionadas
    baixas = DevolucaoBaixa.query.filter_by(devolucao_id=id).all()
    
    # Registrar log
    log_acao(
        modulo='devolucao_pallet',
        acao='read',
        descricao=f'Visualizou devolução #{id}'
    )
    
    return render_template(
        'devolucao_pallet/visualizar.html',
        devolucao=devolucao,
        baixas=baixas
    )


@devolucao_pallet_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@permissao_required('devolucao_pallet', 'editar')
def editar(id):
    """Edita uma devolução"""
    devolucao = DevolucaoPallet.query.get_or_404(id)
    
    # Só pode editar se estiver agendada
    if devolucao.status != 'agendado':
        flash('Não é possível editar uma devolução que não está agendada', 'warning')
        return redirect(url_for('devolucao_pallet.visualizar', id=id))
    
    form = DevolucaoPalletForm(obj=devolucao)
    
    if form.validate_on_submit():
        try:
            # Verificar se motorista foi atribuído agora
            motorista_anterior = devolucao.motorista_id
            motorista_novo = form.motorista_id.data if form.motorista_id.data != 0 else None
            motorista_atribuido = (motorista_anterior is None and motorista_novo is not None)
            
            devolucao.cliente_id = form.cliente_id.data
            devolucao.destinatario_id = form.destinatario_id.data
            devolucao.transportadora_id = form.transportadora_id.data
            devolucao.motorista_id = motorista_novo
            devolucao.quantidade_pallets = form.quantidade_pallets.data
            devolucao.data_agendamento = form.data_agendamento.data
            devolucao.observacoes = form.observacoes.data
            
            db.session.commit()
            
            # Enviar WhatsApp se motorista foi atribuído agora
            if motorista_atribuido:
                from app.utils.devolucao_service import enviar_whatsapp_agendamento_motorista
                resultado_whatsapp = enviar_whatsapp_agendamento_motorista(devolucao.id)
                if resultado_whatsapp['sucesso']:
                    flash('WhatsApp de agendamento enviado ao motorista.', 'info')
            
            flash('Devolução atualizada com sucesso!', 'success')
            
            # Registrar log
            log_acao(
                modulo='devolucao_pallet',
                acao='update',
                descricao=f'Editou devolução #{id}'
            )
            
            return redirect(url_for('devolucao_pallet.visualizar', id=id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar devolução: {str(e)}', 'danger')
            
            # Registrar log de erro
            log_acao(
                modulo='devolucao_pallet',
                acao='update',
                descricao=f'Erro ao editar devolução #{id}: {str(e)}'
            )
    
    # Preencher form com dados atuais
    if request.method == 'GET':
        form.cliente_id.data = devolucao.cliente_id
        form.destinatario_id.data = devolucao.destinatario_id
        form.transportadora_id.data = devolucao.transportadora_id
        form.motorista_id.data = devolucao.motorista_id or 0
        form.quantidade_pallets.data = devolucao.quantidade_pallets
        form.data_agendamento.data = devolucao.data_agendamento
        form.observacoes.data = devolucao.observacoes
    
    return render_template(
        'devolucao_pallet/form.html',
        form=form,
        titulo='Editar Devolução',
        devolucao=devolucao
    )


@devolucao_pallet_bp.route('/validar-pin', methods=['GET', 'POST'])
def validar_pin():
    """Validar PIN de devolução (acesso público para motoristas)"""
    form = ValidarPinDevolucaoForm()
    
    if form.validate_on_submit():
        pin = form.pin_devolucao.data
        
        resultado = validar_pin_devolucao(pin)
        
        if resultado['sucesso']:
            flash(resultado['mensagem'], 'success')
            return redirect(url_for('devolucao_pallet.validar_pin_sucesso', devolucao_id=resultado['devolucao_id']))
        else:
            flash(resultado['mensagem'], 'danger')
    
    return render_template('devolucao_pallet/validar_pin.html', form=form)


@devolucao_pallet_bp.route('/validar-pin/sucesso/<int:devolucao_id>')
def validar_pin_sucesso(devolucao_id):
    """Tela de sucesso após validar PIN"""
    devolucao = DevolucaoPallet.query.get_or_404(devolucao_id)
    
    return render_template('devolucao_pallet/validar_pin_sucesso.html', devolucao=devolucao)


@devolucao_pallet_bp.route('/<int:id>/confirmar', methods=['GET', 'POST'])
@login_required
@permissao_required('devolucao_pallet', 'editar')
def confirmar(id):
    """Confirmar devolução (processar baixa FIFO)"""
    devolucao = DevolucaoPallet.query.get_or_404(id)
    
    # Só pode confirmar se estiver coletada
    if devolucao.status != 'coletado':
        flash('Não é possível confirmar uma devolução que não foi coletada', 'warning')
        return redirect(url_for('devolucao_pallet.visualizar', id=id))
    
    form = ConfirmarDevolucaoForm()
    
    if form.validate_on_submit():
        try:
            # Processar baixa FIFO
            resultado = processar_baixa_fifo(id)
            
            if resultado['sucesso']:
                # Atualizar observações se fornecidas
                if form.observacoes.data:
                    if devolucao.observacoes:
                        devolucao.observacoes += f"\n\nConfirmação: {form.observacoes.data}"
                    else:
                        devolucao.observacoes = f"Confirmação: {form.observacoes.data}"
                    db.session.commit()
                
                flash(f'Devolução confirmada com sucesso! {resultado["mensagem"]}', 'success')
                
                # Registrar log
                log_acao(
                    modulo='devolucao_pallet',
                    acao='update',
                    descricao=f'Confirmou devolução #{id} - Baixa FIFO processada'
                )
                
                return redirect(url_for('devolucao_pallet.visualizar', id=id))
            else:
                flash(f'Erro ao confirmar devolução: {resultado["mensagem"]}', 'danger')
                
        except Exception as e:
            flash(f'Erro ao confirmar devolução: {str(e)}', 'danger')
            
            # Registrar log de erro
            log_acao(
                modulo='devolucao_pallet',
                acao='update',
                descricao=f'Erro ao confirmar devolução #{id}: {str(e)}'
            )
    
    return render_template('devolucao_pallet/confirmar.html', form=form, devolucao=devolucao)


@devolucao_pallet_bp.route('/<int:id>/cancelar', methods=['GET', 'POST'])
@login_required
@permissao_required('devolucao_pallet', 'editar')
def cancelar(id):
    """Cancelar devolução"""
    devolucao = DevolucaoPallet.query.get_or_404(id)
    
    # Só pode cancelar se não estiver finalizada
    if devolucao.status in ['finalizado', 'cancelado']:
        flash(f'Não é possível cancelar uma devolução {devolucao.get_status_display()}', 'warning')
        return redirect(url_for('devolucao_pallet.visualizar', id=id))
    
    form = CancelarDevolucaoForm()
    
    if form.validate_on_submit():
        try:
            devolucao.status = 'cancelado'
            devolucao.motivo_cancelamento = form.motivo_cancelamento.data
            
            db.session.commit()
            
            flash('Devolução cancelada com sucesso!', 'success')
            
            # Registrar log
            log_acao(
                modulo='devolucao_pallet',
                acao='update',
                descricao=f'Cancelou devolução #{id}'
            )
            
            return redirect(url_for('devolucao_pallet.visualizar', id=id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao cancelar devolução: {str(e)}', 'danger')
            
            # Registrar log de erro
            log_acao(
                modulo='devolucao_pallet',
                acao='update',
                descricao=f'Erro ao cancelar devolução #{id}: {str(e)}'
            )
    
    return render_template('devolucao_pallet/cancelar.html', form=form, devolucao=devolucao)


@devolucao_pallet_bp.route('/<int:id>/reenviar-notificacoes', methods=['POST'])
@login_required
@permissao_required('devolucao_pallet', 'editar')
def reenviar_notificacoes(id):
    """Reenviar email e WhatsApp"""
    devolucao = DevolucaoPallet.query.get_or_404(id)
    
    try:
        # Reenviar email
        resultado_email = enviar_email_devolucao(id, current_user.id)
        
        # Reenviar WhatsApp
        resultado_whatsapp = None
        if devolucao.motorista_id:
            resultado_whatsapp = enviar_whatsapp_motorista(id)
        
        # Mensagem
        mensagem = 'Notificações reenviadas!'
        
        if resultado_email['sucesso']:
            mensagem += f' {resultado_email["emails_enviados"]} email(s) enviado(s).'
        
        if resultado_whatsapp and resultado_whatsapp['sucesso']:
            mensagem += ' WhatsApp enviado.'
        
        flash(mensagem, 'success')
        
        # Registrar log
        log_acao(
            modulo='devolucao_pallet',
            acao='update',
            descricao=f'Reenviou notificações da devolução #{id}'
        )
        
    except Exception as e:
        flash(f'Erro ao reenviar notificações: {str(e)}', 'danger')
    
    return redirect(url_for('devolucao_pallet.visualizar', id=id))


@devolucao_pallet_bp.route('/api/saldo/<int:cliente_id>/<int:destinatario_id>')
@login_required
def api_saldo(cliente_id, destinatario_id):
    """API para consultar saldo disponível"""
    try:
        saldo = calcular_saldo_disponivel(cliente_id, destinatario_id)
        return jsonify({'sucesso': True, 'saldo': saldo})
    except Exception as e:
        return jsonify({'sucesso': False, 'mensagem': str(e)}), 400
