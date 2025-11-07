"""
Rotas para gerenciamento de empresas
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Empresa, TipoEmpresa
from app.forms import EmpresaForm

bp = Blueprint('empresas', __name__, url_prefix='/empresas')


@bp.route('/')
@login_required
def listar():
    """Lista todas as empresas que o usuário pode ver"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Obter empresas visíveis para o usuário
    empresas_visiveis = current_user.empresas_visiveis()
    empresas_ids = [e.id for e in empresas_visiveis]
    
    empresas = Empresa.query.filter(Empresa.id.in_(empresas_ids)).order_by(
        Empresa.data_criacao.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('empresas/listar.html', empresas=empresas)


@bp.route('/nova', methods=['GET', 'POST'])
@login_required
def nova():
    """Cadastra uma nova empresa"""
    form = EmpresaForm()
    
    # Carregar tipos de empresa
    tipos = TipoEmpresa.query.filter_by(ativo=True).order_by(TipoEmpresa.nome).all()
    form.tipo_empresa_id.choices = [(0, 'Selecione um tipo')] + [
        (t.id, t.nome) for t in tipos
    ]
    
    if form.validate_on_submit():
        empresa = Empresa(
            razao_social=form.razao_social.data,
            nome_fantasia=form.nome_fantasia.data,
            cnpj=form.cnpj.data,
            tipo_empresa_id=form.tipo_empresa_id.data if form.tipo_empresa_id.data != 0 else None,
            inscricao_estadual=form.inscricao_estadual.data,
            inscricao_municipal=form.inscricao_municipal.data,
            cep=form.cep.data,
            logradouro=form.logradouro.data,
            numero=form.numero.data,
            complemento=form.complemento.data,
            bairro=form.bairro.data,
            cidade=form.cidade.data,
            estado=form.estado.data,
            telefone=form.telefone.data,
            celular=form.celular.data,
            email=form.email.data,
            site=form.site.data,
            ativa=form.ativa.data,
            criado_por_id=current_user.id
        )
        
        db.session.add(empresa)
        db.session.commit()
        
        flash(f'Empresa {empresa.razao_social} cadastrada com sucesso!', 'success')
        return redirect(url_for('empresas.listar'))
    
    return render_template('empresas/form.html', form=form, titulo='Nova Empresa')


@bp.route('/<int:id>')
@login_required
def visualizar(id):
    """Visualiza os detalhes de uma empresa"""
    from app.models import ValePallet
    
    empresa = Empresa.query.get_or_404(id)
    
    # Verificar se o usuário pode ver esta empresa
    if not current_user.pode_ver_empresa(id):
        flash('Você não tem permissão para visualizar esta empresa!', 'danger')
        return redirect(url_for('empresas.listar'))
    
    # Buscar vales pallet relacionados
    vales_pallet = []
    if empresa.tipo:
        tipo_nome = empresa.tipo.nome.lower().strip()
        
        if 'destinat' in tipo_nome:  # Destinatário ou Destinatario
            # Mostrar todos os vales onde a empresa é destinatário
            vales_pallet = ValePallet.query.filter_by(destinatario_id=empresa.id).order_by(ValePallet.data_criacao.desc()).all()
        elif 'transport' in tipo_nome:  # Transportadora
            # Mostrar todos os vales onde a empresa é transportadora
            vales_pallet = ValePallet.query.filter_by(transportadora_id=empresa.id).order_by(ValePallet.data_criacao.desc()).all()
        elif 'client' in tipo_nome:  # Cliente
            # Mostrar todos os vales onde a empresa é cliente
            vales_pallet = ValePallet.query.filter_by(cliente_id=empresa.id).order_by(ValePallet.data_criacao.desc()).all()
    
    return render_template('empresas/visualizar.html', empresa=empresa, vales_pallet=vales_pallet)


@bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    """Edita uma empresa"""
    empresa = Empresa.query.get_or_404(id)
    
    # Verificar se o usuário pode editar esta empresa
    if not current_user.pode_ver_empresa(id):
        flash('Você não tem permissão para editar esta empresa!', 'danger')
        return redirect(url_for('empresas.listar'))
    
    form = EmpresaForm(obj=empresa)
    
    # Carregar tipos de empresa
    tipos = TipoEmpresa.query.filter_by(ativo=True).order_by(TipoEmpresa.nome).all()
    form.tipo_empresa_id.choices = [(0, 'Selecione um tipo')] + [
        (t.id, t.nome) for t in tipos
    ]
    
    if form.validate_on_submit():
        # Verificar se o CNPJ já existe (exceto para a própria empresa)
        empresa_existente = Empresa.query.filter(
            Empresa.cnpj == form.cnpj.data,
            Empresa.id != id
        ).first()
        
        if empresa_existente:
            flash('Já existe uma empresa com este CNPJ!', 'danger')
            return render_template('empresas/form.html', form=form, empresa=empresa, titulo='Editar Empresa')
        
        # Atualizar empresa
        empresa.razao_social = form.razao_social.data
        empresa.nome_fantasia = form.nome_fantasia.data
        empresa.cnpj = form.cnpj.data
        empresa.tipo_empresa_id = form.tipo_empresa_id.data if form.tipo_empresa_id.data != 0 else None
        empresa.inscricao_estadual = form.inscricao_estadual.data
        empresa.inscricao_municipal = form.inscricao_municipal.data
        empresa.cep = form.cep.data
        empresa.logradouro = form.logradouro.data
        empresa.numero = form.numero.data
        empresa.complemento = form.complemento.data
        empresa.bairro = form.bairro.data
        empresa.cidade = form.cidade.data
        empresa.estado = form.estado.data
        empresa.telefone = form.telefone.data
        empresa.celular = form.celular.data
        empresa.email = form.email.data
        empresa.site = form.site.data
        empresa.ativa = form.ativa.data
        
        db.session.commit()
        
        flash(f'Empresa {empresa.razao_social} atualizada com sucesso!', 'success')
        return redirect(url_for('empresas.visualizar', id=empresa.id))
    
    # Preencher o valor atual do tipo de empresa
    if request.method == 'GET':
        form.tipo_empresa_id.data = empresa.tipo_empresa_id if empresa.tipo_empresa_id else 0
    
    return render_template('empresas/form.html', form=form, empresa=empresa, titulo='Editar Empresa')


@bp.route('/<int:id>/excluir', methods=['POST'])
@login_required
def excluir(id):
    """Exclui uma empresa"""
    empresa = Empresa.query.get_or_404(id)
    
    # Verificar se o usuário pode excluir esta empresa
    if empresa.criado_por_id != current_user.id:
        flash('Você não tem permissão para excluir esta empresa!', 'danger')
        return redirect(url_for('empresas.listar'))
    
    # Verificar se há usuários vinculados
    if empresa.usuarios_vinculados.count() > 0:
        flash(f'Não é possível excluir a empresa "{empresa.razao_social}" pois existem usuários vinculados a ela!', 'danger')
        return redirect(url_for('empresas.visualizar', id=id))
    
    # Verificar se há motoristas vinculados
    if empresa.motoristas.count() > 0:
        flash(f'Não é possível excluir a empresa "{empresa.razao_social}" pois existem motoristas vinculados a ela!', 'danger')
        return redirect(url_for('empresas.visualizar', id=id))
    
    razao_social = empresa.razao_social
    db.session.delete(empresa)
    db.session.commit()
    
    flash(f'Empresa {razao_social} excluída com sucesso!', 'success')
    return redirect(url_for('empresas.listar'))
