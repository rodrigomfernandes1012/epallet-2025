"""
Rotas para gerenciamento de tipos de empresa
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import TipoEmpresa
from app.forms import TipoEmpresaForm

bp = Blueprint('tipos_empresa', __name__, url_prefix='/tipos-empresa')


@bp.route('/')
@login_required
def listar():
    """Lista todos os tipos de empresa"""
    tipos = TipoEmpresa.query.order_by(TipoEmpresa.nome).all()
    return render_template('tipos_empresa/listar.html', tipos=tipos)


@bp.route('/novo', methods=['GET', 'POST'])
@login_required
def novo():
    """Cadastra um novo tipo de empresa"""
    form = TipoEmpresaForm()
    
    if form.validate_on_submit():
        # Verificar se já existe
        tipo_existente = TipoEmpresa.query.filter_by(nome=form.nome.data).first()
        if tipo_existente:
            flash('Já existe um tipo de empresa com este nome!', 'danger')
            return render_template('tipos_empresa/form.html', form=form, titulo='Novo Tipo de Empresa')
        
        # Criar novo tipo
        tipo = TipoEmpresa(
            nome=form.nome.data,
            descricao=form.descricao.data,
            ativo=form.ativo.data
        )
        
        db.session.add(tipo)
        db.session.commit()
        
        flash(f'Tipo de empresa "{tipo.nome}" cadastrado com sucesso!', 'success')
        return redirect(url_for('tipos_empresa.listar'))
    
    return render_template('tipos_empresa/form.html', form=form, titulo='Novo Tipo de Empresa')


@bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    """Edita um tipo de empresa"""
    tipo = TipoEmpresa.query.get_or_404(id)
    form = TipoEmpresaForm(obj=tipo)
    
    if form.validate_on_submit():
        # Verificar se o nome já existe (exceto para o próprio tipo)
        tipo_existente = TipoEmpresa.query.filter(
            TipoEmpresa.nome == form.nome.data,
            TipoEmpresa.id != id
        ).first()
        
        if tipo_existente:
            flash('Já existe um tipo de empresa com este nome!', 'danger')
            return render_template('tipos_empresa/form.html', form=form, tipo=tipo, titulo='Editar Tipo de Empresa')
        
        # Atualizar tipo
        tipo.nome = form.nome.data
        tipo.descricao = form.descricao.data
        tipo.ativo = form.ativo.data
        
        db.session.commit()
        
        flash(f'Tipo de empresa "{tipo.nome}" atualizado com sucesso!', 'success')
        return redirect(url_for('tipos_empresa.listar'))
    
    return render_template('tipos_empresa/form.html', form=form, tipo=tipo, titulo='Editar Tipo de Empresa')


@bp.route('/<int:id>/excluir', methods=['POST'])
@login_required
def excluir(id):
    """Exclui um tipo de empresa"""
    tipo = TipoEmpresa.query.get_or_404(id)
    
    # Verificar se há empresas usando este tipo
    if tipo.empresas.count() > 0:
        flash(f'Não é possível excluir o tipo "{tipo.nome}" pois existem empresas cadastradas com este tipo!', 'danger')
        return redirect(url_for('tipos_empresa.listar'))
    
    nome = tipo.nome
    db.session.delete(tipo)
    db.session.commit()
    
    flash(f'Tipo de empresa "{nome}" excluído com sucesso!', 'success')
    return redirect(url_for('tipos_empresa.listar'))
