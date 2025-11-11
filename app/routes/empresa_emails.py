"""
Rotas para Gestão de Emails por Empresa
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Empresa, EmpresaEmail
from app.forms_empresa_email import EmpresaEmailForm
from app.utils.decorators import permissao_required
from app.utils.auditoria import log_acao

empresa_emails_bp = Blueprint('empresa_emails', __name__, url_prefix='/empresa_emails')


@empresa_emails_bp.route('/gerenciar/<int:empresa_id>', methods=['GET'])
@login_required
@permissao_required('empresa_emails', 'visualizar')
def gerenciar(empresa_id):
    """Gerenciar emails de uma empresa"""
    empresa = Empresa.query.get_or_404(empresa_id)
    
    # Verificar se usuário pode acessar esta empresa
    if current_user.empresa_id and current_user.empresa_id != empresa_id:
        # Se não for administrador, só pode acessar sua própria empresa
        if not (current_user.perfil_rel and current_user.perfil_rel.nome == 'Administrador'):
            flash('Você não tem permissão para acessar esta empresa.', 'danger')
            return redirect(url_for('empresas.listar'))
    
    emails = EmpresaEmail.query.filter_by(empresa_id=empresa_id).order_by(EmpresaEmail.email).all()
    
    log_acao(
        modulo='empresa_emails',
        acao='read',
        descricao=f'Acessou gestão de emails da empresa: {empresa.razao_social}',
        registro_id=empresa_id
    )
    
    return render_template('empresa_emails/gerenciar.html', empresa=empresa, emails=emails)


@empresa_emails_bp.route('/adicionar/<int:empresa_id>', methods=['GET', 'POST'])
@login_required
@permissao_required('empresa_emails', 'criar')
def adicionar(empresa_id):
    """Adicionar novo email para empresa"""
    empresa = Empresa.query.get_or_404(empresa_id)
    
    # Verificar permissão
    if current_user.empresa_id and current_user.empresa_id != empresa_id:
        if not (current_user.perfil_rel and current_user.perfil_rel.nome == 'Administrador'):
            flash('Você não tem permissão para acessar esta empresa.', 'danger')
            return redirect(url_for('empresas.listar'))
    
    form = EmpresaEmailForm()
    
    if form.validate_on_submit():
        try:
            # Verificar se email já existe para esta empresa
            email_existente = EmpresaEmail.query.filter_by(
                empresa_id=empresa_id,
                email=form.email.data
            ).first()
            
            if email_existente:
                flash('Este email já está cadastrado para esta empresa.', 'warning')
                return render_template('empresa_emails/form.html', form=form, empresa=empresa, titulo='Adicionar Email')
            
            email = EmpresaEmail(
                empresa_id=empresa_id,
                email=form.email.data,
                nome_contato=form.nome_contato.data,
                receber_notificacoes=form.receber_notificacoes.data,
                ativo=form.ativo.data
            )
            
            db.session.add(email)
            db.session.commit()
            
            log_acao(
                modulo='empresa_emails',
                acao='create',
                descricao=f'Adicionou email {email.email} para empresa {empresa.razao_social}',
                operacao_sql='INSERT',
                tabela_afetada='empresa_emails',
                registro_id=email.id,
                dados_novos={
                    'email': email.email,
                    'nome_contato': email.nome_contato,
                    'empresa_id': empresa_id
                }
            )
            
            flash(f'Email {email.email} adicionado com sucesso!', 'success')
            return redirect(url_for('empresa_emails.gerenciar', empresa_id=empresa_id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao adicionar email: {str(e)}', 'danger')
            log_acao(
                modulo='empresa_emails',
                acao='create',
                descricao=f'Erro ao adicionar email: {str(e)}',
                sucesso=False,
                mensagem_erro=str(e)
            )
    
    return render_template('empresa_emails/form.html', form=form, empresa=empresa, titulo='Adicionar Email')


@empresa_emails_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@permissao_required('empresa_emails', 'editar')
def editar(id):
    """Editar email de empresa"""
    email = EmpresaEmail.query.get_or_404(id)
    empresa = email.empresa
    
    # Verificar permissão
    if current_user.empresa_id and current_user.empresa_id != empresa.id:
        if not (current_user.perfil_rel and current_user.perfil_rel.nome == 'Administrador'):
            flash('Você não tem permissão para acessar esta empresa.', 'danger')
            return redirect(url_for('empresas.listar'))
    
    form = EmpresaEmailForm(obj=email)
    
    if form.validate_on_submit():
        try:
            # Verificar se email já existe para esta empresa (exceto o atual)
            email_existente = EmpresaEmail.query.filter(
                EmpresaEmail.empresa_id == empresa.id,
                EmpresaEmail.email == form.email.data,
                EmpresaEmail.id != id
            ).first()
            
            if email_existente:
                flash('Este email já está cadastrado para esta empresa.', 'warning')
                return render_template('empresa_emails/form.html', form=form, empresa=empresa, email=email, titulo='Editar Email')
            
            dados_anteriores = {
                'email': email.email,
                'nome_contato': email.nome_contato,
                'receber_notificacoes': email.receber_notificacoes,
                'ativo': email.ativo
            }
            
            email.email = form.email.data
            email.nome_contato = form.nome_contato.data
            email.receber_notificacoes = form.receber_notificacoes.data
            email.ativo = form.ativo.data
            
            db.session.commit()
            
            log_acao(
                modulo='empresa_emails',
                acao='update',
                descricao=f'Editou email {email.email} da empresa {empresa.razao_social}',
                operacao_sql='UPDATE',
                tabela_afetada='empresa_emails',
                registro_id=email.id,
                dados_anteriores=dados_anteriores,
                dados_novos={
                    'email': email.email,
                    'nome_contato': email.nome_contato,
                    'receber_notificacoes': email.receber_notificacoes,
                    'ativo': email.ativo
                }
            )
            
            flash(f'Email {email.email} atualizado com sucesso!', 'success')
            return redirect(url_for('empresa_emails.gerenciar', empresa_id=empresa.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar email: {str(e)}', 'danger')
            log_acao(
                modulo='empresa_emails',
                acao='update',
                descricao=f'Erro ao editar email: {str(e)}',
                sucesso=False,
                mensagem_erro=str(e)
            )
    
    return render_template('empresa_emails/form.html', form=form, empresa=empresa, email=email, titulo='Editar Email')


@empresa_emails_bp.route('/excluir/<int:id>', methods=['POST'])
@login_required
@permissao_required('empresa_emails', 'excluir')
def excluir(id):
    """Excluir email de empresa"""
    email = EmpresaEmail.query.get_or_404(id)
    empresa_id = email.empresa_id
    empresa_nome = email.empresa.razao_social
    
    # Verificar permissão
    if current_user.empresa_id and current_user.empresa_id != empresa_id:
        if not (current_user.perfil_rel and current_user.perfil_rel.nome == 'Administrador'):
            flash('Você não tem permissão para acessar esta empresa.', 'danger')
            return redirect(url_for('empresas.listar'))
    
    try:
        dados_email = {
            'email': email.email,
            'nome_contato': email.nome_contato,
            'empresa': empresa_nome
        }
        
        db.session.delete(email)
        db.session.commit()
        
        log_acao(
            modulo='empresa_emails',
            acao='delete',
            descricao=f'Excluiu email {dados_email["email"]} da empresa {empresa_nome}',
            operacao_sql='DELETE',
            tabela_afetada='empresa_emails',
            registro_id=id,
            dados_anteriores=dados_email
        )
        
        flash(f'Email {dados_email["email"]} excluído com sucesso!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir email: {str(e)}', 'danger')
        log_acao(
            modulo='empresa_emails',
            acao='delete',
            descricao=f'Erro ao excluir email: {str(e)}',
            sucesso=False,
            mensagem_erro=str(e)
        )
    
    return redirect(url_for('empresa_emails.gerenciar', empresa_id=empresa_id))
