"""
Rotas para gerenciamento de motoristas
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Motorista, Empresa, TipoEmpresa
from app.forms import MotoristaForm

bp = Blueprint('motoristas', __name__, url_prefix='/motoristas')


@bp.route('/')
@login_required
def listar():
    """Lista todos os motoristas que o usuário pode ver"""
    # Motoristas das empresas que o usuário pode ver
    empresas_visiveis = current_user.empresas_visiveis()
    empresas_ids = [e.id for e in empresas_visiveis]
    
    motoristas = Motorista.query.filter(
        Motorista.empresa_id.in_(empresas_ids)
    ).order_by(Motorista.nome).all()
    
    return render_template('motoristas/listar.html', motoristas=motoristas)


@bp.route('/novo', methods=['GET', 'POST'])
@login_required
def novo():
    """Cadastra um novo motorista"""
    form = MotoristaForm()
    
    # Carregar apenas transportadoras que o usuário pode ver
    empresas_visiveis = current_user.empresas_visiveis()
    tipo_transportadora = TipoEmpresa.query.filter_by(nome='Transportadora').first()
    
    if tipo_transportadora:
        transportadoras = [e for e in empresas_visiveis if e.tipo_empresa_id == tipo_transportadora.id]
    else:
        transportadoras = empresas_visiveis
    
    form.empresa_id.choices = [(0, 'Selecione uma transportadora')] + [
        (e.id, e.razao_social) for e in transportadoras
    ]
    
    if form.validate_on_submit():
        # Verificar se a empresa é uma transportadora
        empresa = Empresa.query.get(form.empresa_id.data)
        if not empresa:
            flash('Transportadora não encontrada!', 'danger')
            return render_template('motoristas/form.html', form=form, titulo='Novo Motorista')
        
        # Verificar se o usuário pode cadastrar motorista nesta empresa
        if not current_user.pode_ver_empresa(empresa.id):
            flash('Você não tem permissão para cadastrar motorista nesta empresa!', 'danger')
            return redirect(url_for('motoristas.listar'))
        
        # Criar novo motorista
        motorista = Motorista(
            nome=form.nome.data,
            cpf=form.cpf.data,
            placa_caminhao=form.placa_caminhao.data,
            empresa_id=form.empresa_id.data,
            telefone=form.telefone.data,
            celular=form.celular.data,
            email=form.email.data,
            ativo=form.ativo.data,
            cadastrado_por_id=current_user.id
        )
        
        db.session.add(motorista)
        db.session.commit()
        
        flash(f'Motorista "{motorista.nome}" cadastrado com sucesso!', 'success')
        return redirect(url_for('motoristas.listar'))
    
    return render_template('motoristas/form.html', form=form, titulo='Novo Motorista')


@bp.route('/<int:id>')
@login_required
def visualizar(id):
    """Visualiza os detalhes de um motorista"""
    motorista = Motorista.query.get_or_404(id)
    
    # Verificar se o usuário pode ver este motorista
    if not current_user.pode_ver_empresa(motorista.empresa_id):
        flash('Você não tem permissão para visualizar este motorista!', 'danger')
        return redirect(url_for('motoristas.listar'))
    
    return render_template('motoristas/visualizar.html', motorista=motorista)


@bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    """Edita um motorista"""
    motorista = Motorista.query.get_or_404(id)
    
    # Verificar se o usuário pode editar este motorista
    if not current_user.pode_ver_empresa(motorista.empresa_id):
        flash('Você não tem permissão para editar este motorista!', 'danger')
        return redirect(url_for('motoristas.listar'))
    
    form = MotoristaForm(obj=motorista)
    
    # Carregar apenas transportadoras que o usuário pode ver
    empresas_visiveis = current_user.empresas_visiveis()
    tipo_transportadora = TipoEmpresa.query.filter_by(nome='Transportadora').first()
    
    if tipo_transportadora:
        transportadoras = [e for e in empresas_visiveis if e.tipo_empresa_id == tipo_transportadora.id]
    else:
        transportadoras = empresas_visiveis
    
    form.empresa_id.choices = [(0, 'Selecione uma transportadora')] + [
        (e.id, e.razao_social) for e in transportadoras
    ]
    
    if form.validate_on_submit():
        # Verificar se o CPF já existe (exceto para o próprio motorista)
        motorista_existente = Motorista.query.filter(
            Motorista.cpf == form.cpf.data,
            Motorista.id != id
        ).first()
        
        if motorista_existente:
            flash('Já existe um motorista com este CPF!', 'danger')
            return render_template('motoristas/form.html', form=form, motorista=motorista, titulo='Editar Motorista')
        
        # Atualizar motorista
        motorista.nome = form.nome.data
        motorista.cpf = form.cpf.data
        motorista.placa_caminhao = form.placa_caminhao.data
        motorista.empresa_id = form.empresa_id.data
        motorista.telefone = form.telefone.data
        motorista.celular = form.celular.data
        motorista.email = form.email.data
        motorista.ativo = form.ativo.data
        
        db.session.commit()
        
        flash(f'Motorista "{motorista.nome}" atualizado com sucesso!', 'success')
        return redirect(url_for('motoristas.visualizar', id=motorista.id))
    
    return render_template('motoristas/form.html', form=form, motorista=motorista, titulo='Editar Motorista')


@bp.route('/<int:id>/excluir', methods=['POST'])
@login_required
def excluir(id):
    """Exclui um motorista"""
    motorista = Motorista.query.get_or_404(id)
    
    # Verificar se o usuário pode excluir este motorista
    if not current_user.pode_ver_empresa(motorista.empresa_id):
        flash('Você não tem permissão para excluir este motorista!', 'danger')
        return redirect(url_for('motoristas.listar'))
    
    nome = motorista.nome
    db.session.delete(motorista)
    db.session.commit()
    
    flash(f'Motorista "{nome}" excluído com sucesso!', 'success')
    return redirect(url_for('motoristas.listar'))
