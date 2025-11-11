"""
Rotas para gestão de usuários
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import User, Empresa, Perfil
from app.forms_admin import UsuarioForm, AlterarSenhaForm
from app.utils.decorators import permissao_required, admin_required
from app.utils.auditoria import registrar_log

usuarios_bp = Blueprint('usuarios', __name__, url_prefix='/usuarios')


@usuarios_bp.route('/')
@login_required
@permissao_required('usuarios', 'visualizar')
def listar():
    """Lista todos os usuários"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Filtrar por empresa do usuário logado (multi-empresas)
    if current_user.empresa_id:
        # Usuário vê apenas usuários da sua empresa
        usuarios_query = User.query.filter_by(empresa_id=current_user.empresa_id)
    else:
        # Admin sem empresa vê todos
        usuarios_query = User.query
    
    usuarios = usuarios_query.order_by(User.nome_completo).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    registrar_log(
        modulo='usuarios',
        acao='read',
        descricao=f'Listou usuários - Página {page}',
        usuario_id=current_user.id,
        usuario_nome=current_user.nome_completo
    )
    
    return render_template('usuarios/listar.html', usuarios=usuarios)


@usuarios_bp.route('/novo', methods=['GET', 'POST'])
@login_required
@permissao_required('usuarios', 'criar')
def novo():
    """Cria novo usuário"""
    form = UsuarioForm()
    
    if form.validate_on_submit():
        try:
            # Criar novo usuário
            usuario = User(
                username=form.username.data,
                email=form.email.data,
                nome_completo=form.nome_completo.data,
                empresa_id=form.empresa_id.data,
                perfil_id=form.perfil_id.data,
                ativo=form.ativo.data
            )
            
            # Definir senha
            usuario.set_password(form.password.data)
            
            db.session.add(usuario)
            db.session.commit()
            
            registrar_log(
                modulo='usuarios',
                acao='create',
                descricao=f'Criou usuário: {usuario.username} - {usuario.nome_completo}',
                usuario_id=current_user.id,
                usuario_nome=current_user.nome_completo,
                operacao_sql='INSERT',
                tabela_afetada='users',
                registro_id=usuario.id,
                dados_novos={
                    'username': usuario.username,
                    'email': usuario.email,
                    'nome_completo': usuario.nome_completo,
                    'empresa_id': usuario.empresa_id,
                    'perfil_id': usuario.perfil_id
                }
            )
            
            flash(f'Usuário {usuario.username} criado com sucesso!', 'success')
            return redirect(url_for('usuarios.listar'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar usuário: {str(e)}', 'danger')
            registrar_log(
                modulo='usuarios',
                acao='create',
                descricao=f'Erro ao criar usuário: {str(e)}',
                usuario_id=current_user.id,
                usuario_nome=current_user.nome_completo,
                sucesso=False,
                mensagem_erro=str(e)
            )
    
    return render_template('usuarios/form.html', form=form, titulo='Novo Usuário')


@usuarios_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@permissao_required('usuarios', 'editar')
def editar(id):
    """Edita usuário existente"""
    usuario = User.query.get_or_404(id)
    
    # Verificar se pode editar (multi-empresas)
    if current_user.empresa_id and usuario.empresa_id != current_user.empresa_id:
        flash('Você não tem permissão para editar este usuário.', 'danger')
        return redirect(url_for('usuarios.listar'))
    
    form = UsuarioForm(user_id=usuario.id, obj=usuario)
    
    if form.validate_on_submit():
        try:
            dados_anteriores = {
                'username': usuario.username,
                'email': usuario.email,
                'nome_completo': usuario.nome_completo,
                'empresa_id': usuario.empresa_id,
                'perfil_id': usuario.perfil_id,
                'ativo': usuario.ativo
            }
            
            # Atualizar dados
            usuario.username = form.username.data
            usuario.email = form.email.data
            usuario.nome_completo = form.nome_completo.data
            usuario.empresa_id = form.empresa_id.data
            usuario.perfil_id = form.perfil_id.data
            usuario.ativo = form.ativo.data
            
            # Atualizar senha se fornecida
            if form.password.data:
                usuario.set_password(form.password.data)
            
            db.session.commit()
            
            registrar_log(
                modulo='usuarios',
                acao='update',
                descricao=f'Editou usuário: {usuario.username} - {usuario.nome_completo}',
                usuario_id=current_user.id,
                usuario_nome=current_user.nome_completo,
                operacao_sql='UPDATE',
                tabela_afetada='users',
                registro_id=usuario.id,
                dados_anteriores=dados_anteriores,
                dados_novos={
                    'username': usuario.username,
                    'email': usuario.email,
                    'nome_completo': usuario.nome_completo,
                    'empresa_id': usuario.empresa_id,
                    'perfil_id': usuario.perfil_id,
                    'ativo': usuario.ativo
                }
            )
            
            flash(f'Usuário {usuario.username} atualizado com sucesso!', 'success')
            return redirect(url_for('usuarios.listar'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar usuário: {str(e)}', 'danger')
            registrar_log(
                modulo='usuarios',
                acao='update',
                descricao=f'Erro ao editar usuário: {str(e)}',
                usuario_id=current_user.id,
                usuario_nome=current_user.nome_completo,
                sucesso=False,
                mensagem_erro=str(e)
            )
    
    return render_template('usuarios/form.html', form=form, usuario=usuario, titulo='Editar Usuário')


@usuarios_bp.route('/<int:id>/visualizar')
@login_required
@permissao_required('usuarios', 'visualizar')
def visualizar(id):
    """Visualiza detalhes do usuário"""
    usuario = User.query.get_or_404(id)
    
    # Verificar se pode visualizar (multi-empresas)
    if current_user.empresa_id and usuario.empresa_id != current_user.empresa_id:
        flash('Você não tem permissão para visualizar este usuário.', 'danger')
        return redirect(url_for('usuarios.listar'))
    
    registrar_log(
        modulo='usuarios',
        acao='read',
        descricao=f'Visualizou usuário: {usuario.username}',
        usuario_id=current_user.id,
        usuario_nome=current_user.nome_completo,
        registro_id=usuario.id
    )
    
    return render_template('usuarios/visualizar.html', usuario=usuario)


@usuarios_bp.route('/<int:id>/excluir', methods=['POST'])
@login_required
@permissao_required('usuarios', 'excluir')
def excluir(id):
    """Exclui usuário"""
    usuario = User.query.get_or_404(id)
    
    # Verificar se pode excluir (multi-empresas)
    if current_user.empresa_id and usuario.empresa_id != current_user.empresa_id:
        flash('Você não tem permissão para excluir este usuário.', 'danger')
        return redirect(url_for('usuarios.listar'))
    
    # Não permitir excluir a si mesmo
    if usuario.id == current_user.id:
        flash('Você não pode excluir seu próprio usuário.', 'danger')
        return redirect(url_for('usuarios.listar'))
    
    try:
        dados_usuario = {
            'username': usuario.username,
            'email': usuario.email,
            'nome_completo': usuario.nome_completo,
            'empresa_id': usuario.empresa_id,
            'perfil_id': usuario.perfil_id
        }
        
        db.session.delete(usuario)
        db.session.commit()
        
        registrar_log(
            modulo='usuarios',
            acao='delete',
            descricao=f'Excluiu usuário: {dados_usuario["username"]} - {dados_usuario["nome_completo"]}',
            usuario_id=current_user.id,
            usuario_nome=current_user.nome_completo,
            operacao_sql='DELETE',
            tabela_afetada='users',
            registro_id=id,
            dados_anteriores=dados_usuario
        )
        
        flash('Usuário excluído com sucesso!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir usuário: {str(e)}', 'danger')
        registrar_log(
            modulo='usuarios',
            acao='delete',
            descricao=f'Erro ao excluir usuário: {str(e)}',
            usuario_id=current_user.id,
            usuario_nome=current_user.nome_completo,
            sucesso=False,
            mensagem_erro=str(e)
        )
    
    return redirect(url_for('usuarios.listar'))


@usuarios_bp.route('/alterar-senha', methods=['GET', 'POST'])
@login_required
def alterar_senha():
    """Permite usuário alterar sua própria senha"""
    form = AlterarSenhaForm()
    
    if form.validate_on_submit():
        # Verificar senha atual
        if not current_user.check_password(form.senha_atual.data):
            flash('Senha atual incorreta.', 'danger')
            return render_template('usuarios/alterar_senha.html', form=form)
        
        try:
            # Atualizar senha
            current_user.set_password(form.nova_senha.data)
            db.session.commit()
            
            registrar_log(
                modulo='usuarios',
                acao='update',
                descricao='Alterou sua própria senha',
                usuario_id=current_user.id,
                usuario_nome=current_user.nome_completo,
                operacao_sql='UPDATE',
                tabela_afetada='users',
                registro_id=current_user.id
            )
            
            flash('Senha alterada com sucesso!', 'success')
            return redirect(url_for('main.dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao alterar senha: {str(e)}', 'danger')
            registrar_log(
                modulo='usuarios',
                acao='update',
                descricao=f'Erro ao alterar senha: {str(e)}',
                usuario_id=current_user.id,
                usuario_nome=current_user.nome_completo,
                sucesso=False,
                mensagem_erro=str(e)
            )
    
    return render_template('usuarios/alterar_senha.html', form=form)
