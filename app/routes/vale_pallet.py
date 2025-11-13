"""
Rotas para gerenciamento de Vale Pallet
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import ValePallet, Empresa, TipoEmpresa, Motorista
from app.forms import ValePalletForm
from app.utils.whatsapp import enviar_whatsapp_vale_criado

bp = Blueprint('vale_pallet', __name__, url_prefix='/vale-pallet')


@bp.route('/')
@login_required
def listar():
    """Lista todos os vales pallet que o usuário pode ver (com filtros)"""
    from datetime import datetime
    
    page = request.args.get('page', 1, type=int)
    per_page = 15  # 15 vales por página
    
    # Filtros
    status_filtro = request.args.get('status', '')
    destinatario_filtro = request.args.get('destinatario', '', type=int)
    data_vencimento_inicio = request.args.get('data_vencimento_inicio', '')
    data_vencimento_fim = request.args.get('data_vencimento_fim', '')
    
    # Vales das empresas que o usuário pode ver
    empresas_visiveis = current_user.empresas_visiveis()
    empresas_ids = [e.id for e in empresas_visiveis]
    
    # Query base
    query = ValePallet.query.filter(
        (ValePallet.cliente_id.in_(empresas_ids)) |
        (ValePallet.transportadora_id.in_(empresas_ids)) |
        (ValePallet.destinatario_id.in_(empresas_ids))
    )
    
    # Aplicar filtro de status
    if status_filtro:
        query = query.filter(ValePallet.status == status_filtro)
    
    # Aplicar filtro de destinatário
    if destinatario_filtro:
        query = query.filter(ValePallet.destinatario_id == destinatario_filtro)
    
    # Aplicar filtro de data de vencimento (início)
    if data_vencimento_inicio:
        try:
            data_inicio = datetime.strptime(data_vencimento_inicio, '%Y-%m-%d').date()
            query = query.filter(ValePallet.data_vencimento >= data_inicio)
        except ValueError:
            pass
    
    # Aplicar filtro de data de vencimento (fim)
    if data_vencimento_fim:
        try:
            data_fim = datetime.strptime(data_vencimento_fim, '%Y-%m-%d').date()
            query = query.filter(ValePallet.data_vencimento <= data_fim)
        except ValueError:
            pass
    
    # Ordenar e paginar
    vales = query.order_by(ValePallet.data_criacao.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Buscar destinatários para o filtro
    tipo_destinatario = TipoEmpresa.query.filter_by(nome='Destinatário').first()
    destinatarios = []
    if tipo_destinatario:
        destinatarios = [e for e in empresas_visiveis if e.tipo_empresa_id == tipo_destinatario.id]
    else:
        destinatarios = empresas_visiveis
    
    # Status disponíveis
    status_opcoes = [
        ('pendente_entrega', 'Pendente de Entrega'),
        ('entrega_realizada', 'Entrega Realizada'),
        ('entrega_concluida', 'Entrega Concluída'),
        ('cancelado', 'Cancelado')
    ]
    
    return render_template('vale_pallet/listar.html',
                          vales=vales,
                          destinatarios=destinatarios,
                          status_opcoes=status_opcoes,
                          status_filtro=status_filtro,
                          destinatario_filtro=destinatario_filtro,
                          data_vencimento_inicio=data_vencimento_inicio,
                          data_vencimento_fim=data_vencimento_fim)


@bp.route('/novo', methods=['GET', 'POST'])
@login_required
def novo():
    """Cadastra um novo vale pallet"""
    form = ValePalletForm()
    
    # Carregar empresas que o usuário pode ver, separadas por tipo
    empresas_visiveis = current_user.empresas_visiveis()
    
    tipo_cliente = TipoEmpresa.query.filter_by(nome='Cliente').first()
    tipo_transportadora = TipoEmpresa.query.filter_by(nome='Transportadora').first()
    tipo_destinatario = TipoEmpresa.query.filter_by(nome='Destinatário').first()
    
    # Filtrar empresas por tipo
    clientes = [e for e in empresas_visiveis if tipo_cliente and e.tipo_empresa_id == tipo_cliente.id]
    transportadoras = [e for e in empresas_visiveis if tipo_transportadora and e.tipo_empresa_id == tipo_transportadora.id]
    destinatarios = [e for e in empresas_visiveis if tipo_destinatario and e.tipo_empresa_id == tipo_destinatario.id]
    
    # Se não houver tipos cadastrados, mostrar todas as empresas
    if not tipo_cliente:
        clientes = empresas_visiveis
    if not tipo_transportadora:
        transportadoras = empresas_visiveis
    if not tipo_destinatario:
        destinatarios = empresas_visiveis
    
    form.cliente_id.choices = [(0, 'Selecione um cliente')] + [
        (e.id, e.razao_social) for e in clientes
    ]
    form.transportadora_id.choices = [(0, 'Selecione uma transportadora')] + [
        (e.id, e.razao_social) for e in transportadoras
    ]
    form.destinatario_id.choices = [(0, 'Selecione um destinatário')] + [
        (e.id, e.razao_social) for e in destinatarios
    ]
    
    # Carregar motoristas ativos
    motoristas = Motorista.query.filter_by(ativo=True).all()
    form.motorista_id.choices = [(0, 'Selecione um motorista (opcional)')] + [
        (m.id, f"{m.nome} - {m.placa_caminhao}") for m in motoristas
    ]
    
    if form.validate_on_submit():
        # Verificar se as empresas existem e o usuário pode vê-las
        cliente = Empresa.query.get(form.cliente_id.data)
        transportadora = Empresa.query.get(form.transportadora_id.data)
        destinatario = Empresa.query.get(form.destinatario_id.data)
        
        if not cliente or not transportadora or not destinatario:
            flash('Uma ou mais empresas selecionadas não foram encontradas!', 'danger')
            return render_template('vale_pallet/form.html', form=form, titulo='Novo Vale Pallet')
        
        if not (current_user.pode_ver_empresa(cliente.id) and 
                current_user.pode_ver_empresa(transportadora.id) and 
                current_user.pode_ver_empresa(destinatario.id)):
            flash('Você não tem permissão para criar vale pallet com uma ou mais empresas selecionadas!', 'danger')
            return redirect(url_for('vale_pallet.listar'))
        
        # Gerar PIN único
        pin = ValePallet.gerar_pin()
        
        # Criar novo vale pallet
        vale = ValePallet(
            cliente_id=form.cliente_id.data,
            transportadora_id=form.transportadora_id.data,
            destinatario_id=form.destinatario_id.data,
            motorista_id=form.motorista_id.data if form.motorista_id.data != 0 else None,
            quantidade_pallets=int(form.quantidade_pallets.data),
            numero_documento=form.numero_documento.data,
            data_vencimento=form.data_vencimento.data,
            pin=pin,
            status='pendente_entrega',
            criado_por_id=current_user.id
        )
        
        db.session.add(vale)
        db.session.commit()
        
        # Enviar email para o destinatário
        from app.utils.email_service import enviar_email_vale_pallet
        resultado_email = enviar_email_vale_pallet(vale.id, current_user.id)
        
        # Enviar WhatsApp para o motorista (se selecionado)
        mensagem_sucesso = 'Vale Pallet criado com sucesso!'
        
        if resultado_email['sucesso']:
            mensagem_sucesso += f'. {resultado_email["emails_enviados"]} email(s) enviado(s)'
        else:
            mensagem_sucesso += f'. Aviso: {resultado_email["mensagem"]}'
        
        if vale.motorista_id:
            motorista = Motorista.query.get(vale.motorista_id)
            if motorista and motorista.celular:
                enviado = enviar_whatsapp_vale_criado(motorista, vale)
                if enviado:
                    mensagem_sucesso += '. WhatsApp enviado para o motorista'
                else:
                    mensagem_sucesso += '. Erro ao enviar WhatsApp para o motorista'
            else:
                mensagem_sucesso += '. Motorista sem celular cadastrado'
        
        flash(mensagem_sucesso, 'success' if resultado_email['sucesso'] else 'warning')
        
        return redirect(url_for('vale_pallet.visualizar', id=vale.id))
    
    return render_template('vale_pallet/form.html', form=form, titulo='Novo Vale Pallet')


@bp.route('/<int:id>')
@login_required
def visualizar(id):
    """Visualiza os detalhes de um vale pallet"""
    vale = ValePallet.query.get_or_404(id)
    
    # Verificar se o usuário pode ver este vale
    if not (current_user.pode_ver_empresa(vale.cliente_id) or 
            current_user.pode_ver_empresa(vale.transportadora_id) or 
            current_user.pode_ver_empresa(vale.destinatario_id)):
        flash('Você não tem permissão para visualizar este vale pallet!', 'danger')
        return redirect(url_for('vale_pallet.listar'))
    
    return render_template('vale_pallet/visualizar.html', vale=vale)


@bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    """Edita um vale pallet"""
    vale = ValePallet.query.get_or_404(id)
    
    # Verificar se o usuário pode editar este vale
    if not (current_user.pode_ver_empresa(vale.cliente_id) or 
            current_user.pode_ver_empresa(vale.transportadora_id) or 
            current_user.pode_ver_empresa(vale.destinatario_id)):
        flash('Você não tem permissão para editar este vale pallet!', 'danger')
        return redirect(url_for('vale_pallet.listar'))
    
    form = ValePalletForm(obj=vale)
    
    # Carregar empresas que o usuário pode ver, separadas por tipo
    empresas_visiveis = current_user.empresas_visiveis()
    
    tipo_cliente = TipoEmpresa.query.filter_by(nome='Cliente').first()
    tipo_transportadora = TipoEmpresa.query.filter_by(nome='Transportadora').first()
    tipo_destinatario = TipoEmpresa.query.filter_by(nome='Destinatário').first()
    
    # Filtrar empresas por tipo
    clientes = [e for e in empresas_visiveis if tipo_cliente and e.tipo_empresa_id == tipo_cliente.id]
    transportadoras = [e for e in empresas_visiveis if tipo_transportadora and e.tipo_empresa_id == tipo_transportadora.id]
    destinatarios = [e for e in empresas_visiveis if tipo_destinatario and e.tipo_empresa_id == tipo_destinatario.id]
    
    # Se não houver tipos cadastrados, mostrar todas as empresas
    if not tipo_cliente:
        clientes = empresas_visiveis
    if not tipo_transportadora:
        transportadoras = empresas_visiveis
    if not tipo_destinatario:
        destinatarios = empresas_visiveis
    
    form.cliente_id.choices = [(0, 'Selecione um cliente')] + [
        (e.id, e.razao_social) for e in clientes
    ]
    form.transportadora_id.choices = [(0, 'Selecione uma transportadora')] + [
        (e.id, e.razao_social) for e in transportadoras
    ]
    form.destinatario_id.choices = [(0, 'Selecione um destinatário')] + [
        (e.id, e.razao_social) for e in destinatarios
    ]
    
    if form.validate_on_submit():
        # Atualizar vale pallet (mantém o PIN original)
        vale.cliente_id = form.cliente_id.data
        vale.transportadora_id = form.transportadora_id.data
        vale.destinatario_id = form.destinatario_id.data
        vale.quantidade_pallets = int(form.quantidade_pallets.data)
        vale.numero_documento = form.numero_documento.data
        vale.data_vencimento = form.data_vencimento.data
        
        db.session.commit()
        
        flash(f'Vale Pallet atualizado com sucesso!', 'success')
        return redirect(url_for('vale_pallet.visualizar', id=vale.id))
    
    # Preencher os valores atuais
    if request.method == 'GET':
        form.cliente_id.data = vale.cliente_id
        form.transportadora_id.data = vale.transportadora_id
        form.destinatario_id.data = vale.destinatario_id
        form.quantidade_pallets.data = str(vale.quantidade_pallets)
        form.data_vencimento.data = vale.data_vencimento
    
    return render_template('vale_pallet/form.html', form=form, vale=vale, titulo='Editar Vale Pallet')


@bp.route('/<int:id>/cancelar', methods=['POST'])
@login_required
def cancelar(id):
    """Cancela um vale pallet"""
    vale = ValePallet.query.get_or_404(id)
    
    # Verificar se o usuário pode cancelar este vale
    if not (current_user.pode_ver_empresa(vale.cliente_id) or 
            current_user.pode_ver_empresa(vale.transportadora_id) or 
            current_user.pode_ver_empresa(vale.destinatario_id)):
        flash('Você não tem permissão para cancelar este vale pallet!', 'danger')
        return redirect(url_for('vale_pallet.listar'))
    
    vale.status = 'cancelado'
    db.session.commit()
    
    flash(f'Vale Pallet cancelado com sucesso!', 'success')
    return redirect(url_for('vale_pallet.visualizar', id=vale.id))


@bp.route('/<int:id>/finalizar', methods=['POST'])
@login_required
def finalizar(id):
    """Finaliza um vale pallet"""
    vale = ValePallet.query.get_or_404(id)
    
    # Verificar se o usuário pode finalizar este vale
    if not (current_user.pode_ver_empresa(vale.cliente_id) or 
            current_user.pode_ver_empresa(vale.transportadora_id) or 
            current_user.pode_ver_empresa(vale.destinatario_id)):
        flash('Você não tem permissão para finalizar este vale pallet!', 'danger')
        return redirect(url_for('vale_pallet.listar'))
    
    vale.status = 'finalizado'
    db.session.commit()
    
    flash(f'Vale Pallet finalizado com sucesso!', 'success')
    return redirect(url_for('vale_pallet.visualizar', id=vale.id))


@bp.route('/buscar-pin', methods=['GET', 'POST'])
@login_required
def buscar_pin():
    """Busca um vale pallet pelo PIN"""
    vale = None
    pin = request.args.get('pin') or request.form.get('pin')
    
    if pin:
        vale = ValePallet.query.filter_by(pin=pin).first()
        
        if vale:
            # Verificar se o usuário pode ver este vale
            if not (current_user.pode_ver_empresa(vale.cliente_id) or 
                    current_user.pode_ver_empresa(vale.transportadora_id) or 
                    current_user.pode_ver_empresa(vale.destinatario_id)):
                flash('Você não tem permissão para visualizar este vale pallet!', 'danger')
                return redirect(url_for('vale_pallet.buscar_pin'))
            
            return redirect(url_for('vale_pallet.visualizar', id=vale.id))
        else:
            flash(f'Vale Pallet com PIN "{pin}" não encontrado!', 'warning')
    
    return render_template('vale_pallet/buscar_pin.html')
