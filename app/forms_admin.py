"""
Formulários para administração (usuários e perfis)
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, SelectField, FieldList, FormField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, ValidationError
from app.models import User, Perfil, Empresa


class PerfilForm(FlaskForm):
    """Formulário para cadastro/edição de perfil"""
    nome = StringField('Nome do Perfil', validators=[DataRequired(), Length(min=3, max=100)])
    descricao = TextAreaField('Descrição', validators=[Optional()])
    ativo = BooleanField('Ativo', default=True)
    
    def __init__(self, perfil_id=None, *args, **kwargs):
        super(PerfilForm, self).__init__(*args, **kwargs)
        self.perfil_id = perfil_id
    
    def validate_nome(self, field):
        """Valida se o nome do perfil já existe"""
        perfil = Perfil.query.filter_by(nome=field.data).first()
        if perfil:
            # Se está editando, permite o mesmo nome
            if self.perfil_id and perfil.id == self.perfil_id:
                return
            raise ValidationError('Já existe um perfil com este nome.')


class PerfilPermissaoForm(FlaskForm):
    """Formulário para permissões de um módulo"""
    modulo = StringField('Módulo', validators=[DataRequired()])
    pode_visualizar = BooleanField('Visualizar', default=False)
    pode_criar = BooleanField('Criar', default=False)
    pode_editar = BooleanField('Editar', default=False)
    pode_excluir = BooleanField('Excluir', default=False)


class UsuarioForm(FlaskForm):
    """Formulário para cadastro/edição de usuário"""
    username = StringField('Nome de Usuário', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('E-mail', validators=[DataRequired(), Email(), Length(max=120)])
    nome_completo = StringField('Nome Completo', validators=[DataRequired(), Length(min=3, max=150)])
    
    empresa_id = SelectField('Empresa', coerce=int, validators=[DataRequired()])
    perfil_id = SelectField('Perfil', coerce=int, validators=[DataRequired()])
    
    ativo = BooleanField('Ativo', default=True)
    
    # Campos de senha (apenas para novo usuário)
    password = PasswordField('Senha', validators=[Optional(), Length(min=6)])
    password_confirm = PasswordField('Confirmar Senha', validators=[Optional(), EqualTo('password', message='As senhas devem ser iguais')])
    
    def __init__(self, user_id=None, *args, **kwargs):
        super(UsuarioForm, self).__init__(*args, **kwargs)
        self.user_id = user_id
        
        # Preencher choices de empresa
        self.empresa_id.choices = [(0, 'Selecione uma empresa')] + [
            (e.id, e.razao_social) for e in Empresa.query.filter_by(ativa=True).order_by(Empresa.razao_social).all()
        ]
        
        # Preencher choices de perfil
        self.perfil_id.choices = [(0, 'Selecione um perfil')] + [
            (p.id, p.nome) for p in Perfil.query.filter_by(ativo=True).order_by(Perfil.nome).all()
        ]
    
    def validate_username(self, field):
        """Valida se o username já existe"""
        user = User.query.filter_by(username=field.data).first()
        if user:
            # Se está editando, permite o mesmo username
            if self.user_id and user.id == self.user_id:
                return
            raise ValidationError('Este nome de usuário já está em uso.')
    
    def validate_email(self, field):
        """Valida se o email já existe"""
        user = User.query.filter_by(email=field.data).first()
        if user:
            # Se está editando, permite o mesmo email
            if self.user_id and user.id == self.user_id:
                return
            raise ValidationError('Este e-mail já está em uso.')
    
    def validate_empresa_id(self, field):
        """Valida se uma empresa foi selecionada"""
        if field.data == 0:
            raise ValidationError('Selecione uma empresa.')
    
    def validate_perfil_id(self, field):
        """Valida se um perfil foi selecionado"""
        if field.data == 0:
            raise ValidationError('Selecione um perfil.')
    
    def validate_password(self, field):
        """Valida senha para novo usuário"""
        # Se é novo usuário, senha é obrigatória
        if not self.user_id and not field.data:
            raise ValidationError('A senha é obrigatória para novos usuários.')


class AlterarSenhaForm(FlaskForm):
    """Formulário para alterar senha de usuário"""
    senha_atual = PasswordField('Senha Atual', validators=[DataRequired()])
    nova_senha = PasswordField('Nova Senha', validators=[DataRequired(), Length(min=6)])
    confirmar_senha = PasswordField('Confirmar Nova Senha', validators=[
        DataRequired(), 
        EqualTo('nova_senha', message='As senhas devem ser iguais')
    ])
