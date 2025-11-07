from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from app import db
from app.models import User
from app.forms import LoginForm, RegistrationForm
from app.utils.auditoria import log_login, log_logout, log_crud, log_acesso_tela

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Rota de login"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        # Buscar usuário por username ou email
        user = User.query.filter(
            (User.username == form.username.data) | (User.email == form.username.data)
        ).first()
        
        if user is None or not user.check_password(form.password.data):
            flash('Usuário ou senha inválidos', 'danger')
            log_login(form.username.data, sucesso=False, mensagem_erro='Usuário ou senha inválidos')
            return redirect(url_for('auth.login'))
        
        if not user.ativo:
            flash('Sua conta está inativa. Entre em contato com o administrador.', 'warning')
            log_login(user.username, sucesso=False, mensagem_erro='Conta inativa')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=form.remember_me.data)
        log_login(user.username, sucesso=True)
        
        # Redirecionar para a página solicitada ou dashboard
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('main.dashboard')
        
        flash(f'Bem-vindo, {user.nome_completo}!', 'success')
        return redirect(next_page)
    
    return render_template('auth/login.html', form=form)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Rota de registro de novo usuário"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            nome_completo=form.nome_completo.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Cadastro realizado com sucesso! Faça login para continuar.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)


@bp.route('/logout')
def logout():
    """Rota de logout"""
    username = current_user.username if current_user.is_authenticated else 'Desconhecido'
    log_logout(username)
    logout_user()
    flash('Você saiu do sistema.', 'info')
    return redirect(url_for('auth.login'))
