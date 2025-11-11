"""
Rotas para gestão de perfis e permissões
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Perfil, PerfilPermissao
from app.forms_admin import PerfilForm
from app.utils.decorators import permissao_required, admin_required
from app.utils.auditoria import log_acao

perfis_bp = Blueprint('perfis', __name__, url_prefix='/perfis')

# Módulos disponíveis no sistema
MODULOS_SISTEMA = [
    {'id': 'dashboard', 'nome': 'Dashboard'},
    {'id': 'empresas', 'nome': 'Empresas'},
    {'id': 'tipos_empresa', 'nome': 'Tipos de Empresa'},
    {'id': 'motoristas', 'nome': 'Motoristas'},
    {'id': 'vale_pallet', 'nome': 'Vale Pallet'},
    {'id': 'relatorios', 'nome': 'Relatórios'},
    {'id': 'logs', 'nome': 'Logs de Auditoria'},
    {'id': 'usuarios', 'nome': 'Usuários'},
    {'id': 'perfis', 'nome': 'Perfis'},
]


@perfis_bp.route('/')
@login_required
@permissao_required('perfis', 'visualizar')
def listar():
    """Lista todos os perfis"""
    perfis = Perfil.query.order_by(Perfil.nome).all()
    
    log_acao(
        modulo='perfis',
        acao='read',
        descricao='Listou perfis'
    )
    
    return render_template('perfis/listar.html', perfis=perfis)


@perfis_bp.route('/novo', methods=['GET', 'POST'])
@login_required
@permissao_required('perfis', 'criar')
def novo():
    """Cria novo perfil"""
    form = PerfilForm()
    
    if form.validate_on_submit():
        try:
            # Criar novo perfil
            perfil = Perfil(
                nome=form.nome.data,
                descricao=form.descricao.data,
                ativo=form.ativo.data,
                sistema=False  # Perfis criados manualmente não são do sistema
            )
            
            db.session.add(perfil)
            db.session.flush()  # Para obter o ID
            
            # Criar permissões padrão (todas desabilitadas)
            for modulo in MODULOS_SISTEMA:
                permissao = PerfilPermissao(
                    perfil_id=perfil.id,
                    modulo=modulo['id'],
                    pode_visualizar=False,
                    pode_criar=False,
                    pode_editar=False,
                    pode_excluir=False
                )
                db.session.add(permissao)
            
            db.session.commit()
            
            log_acao(
                modulo='perfis',
                acao='create',
                descricao=f'Criou perfil: {perfil.nome}',
                operacao_sql='INSERT',
                tabela_afetada='perfis',
                registro_id=perfil.id,
                dados_novos={
                    'nome': perfil.nome,
                    'descricao': perfil.descricao,
                    'ativo': perfil.ativo
                }
            )
            
            flash(f'Perfil {perfil.nome} criado com sucesso!', 'success')
            return redirect(url_for('perfis.editar_permissoes', id=perfil.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar perfil: {str(e)}', 'danger')
            log_acao(
                modulo='perfis',
                acao='create',
                descricao=f'Erro ao criar perfil: {str(e)}',
                sucesso=False,
                mensagem_erro=str(e)
            )
    
    return render_template('perfis/form.html', form=form, titulo='Novo Perfil')


@perfis_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@permissao_required('perfis', 'editar')
def editar(id):
    """Edita perfil existente"""
    perfil = Perfil.query.get_or_404(id)
    
    # Não permitir editar perfis do sistema
    if perfil.sistema:
        flash('Perfis do sistema não podem ser editados.', 'warning')
        return redirect(url_for('perfis.listar'))
    
    form = PerfilForm(perfil_id=perfil.id, obj=perfil)
    
    if form.validate_on_submit():
        try:
            dados_anteriores = {
                'nome': perfil.nome,
                'descricao': perfil.descricao,
                'ativo': perfil.ativo
            }
            
            # Atualizar dados
            perfil.nome = form.nome.data
            perfil.descricao = form.descricao.data
            perfil.ativo = form.ativo.data
            
            db.session.commit()
            
            log_acao(
                modulo='perfis',
                acao='update',
                descricao=f'Editou perfil: {perfil.nome}',
                operacao_sql='UPDATE',
                tabela_afetada='perfis',
                registro_id=perfil.id,
                dados_anteriores=dados_anteriores,
                dados_novos={
                    'nome': perfil.nome,
                    'descricao': perfil.descricao,
                    'ativo': perfil.ativo
                }
            )
            
            flash(f'Perfil {perfil.nome} atualizado com sucesso!', 'success')
            return redirect(url_for('perfis.listar'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar perfil: {str(e)}', 'danger')
            log_acao(
                modulo='perfis',
                acao='update',
                descricao=f'Erro ao editar perfil: {str(e)}',
                sucesso=False,
                mensagem_erro=str(e)
            )
    
    return render_template('perfis/form.html', form=form, perfil=perfil, titulo='Editar Perfil')


@perfis_bp.route('/<int:id>/permissoes', methods=['GET', 'POST'])
@login_required
@permissao_required('perfis', 'editar')
def editar_permissoes(id):
    """Edita permissões do perfil"""
    perfil = Perfil.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            # Processar permissões enviadas
            for modulo in MODULOS_SISTEMA:
                modulo_id = modulo['id']
                
                # Buscar ou criar permissão
                permissao = PerfilPermissao.query.filter_by(
                    perfil_id=perfil.id,
                    modulo=modulo_id
                ).first()
                
                if not permissao:
                    permissao = PerfilPermissao(
                        perfil_id=perfil.id,
                        modulo=modulo_id
                    )
                    db.session.add(permissao)
                
                # Atualizar permissões
                permissao.pode_visualizar = request.form.get(f'{modulo_id}_visualizar') == 'on'
                permissao.pode_criar = request.form.get(f'{modulo_id}_criar') == 'on'
                permissao.pode_editar = request.form.get(f'{modulo_id}_editar') == 'on'
                permissao.pode_excluir = request.form.get(f'{modulo_id}_excluir') == 'on'
            
            db.session.commit()
            
            log_acao(
                modulo='perfis',
                acao='update',
                descricao=f'Atualizou permissões do perfil: {perfil.nome}',
                operacao_sql='UPDATE',
                tabela_afetada='perfis_permissoes',
                registro_id=perfil.id
            )
            
            flash(f'Permissões do perfil {perfil.nome} atualizadas com sucesso!', 'success')
            return redirect(url_for('perfis.listar'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar permissões: {str(e)}', 'danger')
            log_acao(
                modulo='perfis',
                acao='update',
                descricao=f'Erro ao atualizar permissões: {str(e)}',
                sucesso=False,
                mensagem_erro=str(e)
            )
    
    # Buscar permissões atuais
    permissoes = {}
    for modulo in MODULOS_SISTEMA:
        perm = PerfilPermissao.query.filter_by(
            perfil_id=perfil.id,
            modulo=modulo['id']
        ).first()
        
        permissoes[modulo['id']] = {
            'visualizar': perm.pode_visualizar if perm else False,
            'criar': perm.pode_criar if perm else False,
            'editar': perm.pode_editar if perm else False,
            'excluir': perm.pode_excluir if perm else False,
        }
    
    return render_template('perfis/permissoes.html', 
                         perfil=perfil, 
                         modulos=MODULOS_SISTEMA,
                         permissoes=permissoes)


@perfis_bp.route('/<int:id>/visualizar')
@login_required
@permissao_required('perfis', 'visualizar')
def visualizar(id):
    """Visualiza detalhes do perfil"""
    perfil = Perfil.query.get_or_404(id)
    
    # Buscar permissões
    permissoes = {}
    for modulo in MODULOS_SISTEMA:
        perm = PerfilPermissao.query.filter_by(
            perfil_id=perfil.id,
            modulo=modulo['id']
        ).first()
        
        permissoes[modulo['id']] = {
            'nome': modulo['nome'],
            'visualizar': perm.pode_visualizar if perm else False,
            'criar': perm.pode_criar if perm else False,
            'editar': perm.pode_editar if perm else False,
            'excluir': perm.pode_excluir if perm else False,
        }
    
    log_acao(
        modulo='perfis',
        acao='read',
        descricao=f'Visualizou perfil: {perfil.nome}',
        registro_id=perfil.id
    )
    
    return render_template('perfis/visualizar.html', perfil=perfil, permissoes=permissoes)


@perfis_bp.route('/<int:id>/excluir', methods=['POST'])
@login_required
@permissao_required('perfis', 'excluir')
def excluir(id):
    """Exclui perfil"""
    perfil = Perfil.query.get_or_404(id)
    
    # Não permitir excluir perfis do sistema
    if perfil.sistema:
        flash('Perfis do sistema não podem ser excluídos.', 'danger')
        return redirect(url_for('perfis.listar'))
    
    # Verificar se há usuários vinculados
    if perfil.usuarios.count() > 0:
        flash(f'Não é possível excluir o perfil {perfil.nome} pois há {perfil.usuarios.count()} usuário(s) vinculado(s).', 'danger')
        return redirect(url_for('perfis.listar'))
    
    try:
        dados_perfil = {
            'nome': perfil.nome,
            'descricao': perfil.descricao,
            'ativo': perfil.ativo
        }
        
        db.session.delete(perfil)
        db.session.commit()
        
        log_acao(
            modulo='perfis',
            acao='delete',
            descricao=f'Excluiu perfil: {dados_perfil["nome"]}',
            operacao_sql='DELETE',
            tabela_afetada='perfis',
            registro_id=id,
            dados_anteriores=dados_perfil
        )
        
        flash('Perfil excluído com sucesso!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir perfil: {str(e)}', 'danger')
        log_acao(
            modulo='perfis',
            acao='delete',
            descricao=f'Erro ao excluir perfil: {str(e)}',
            sucesso=False,
            mensagem_erro=str(e)
        )
    
    return redirect(url_for('perfis.listar'))
