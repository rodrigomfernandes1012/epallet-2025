"""
Formulários para Emails de Empresa
"""
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length


class EmpresaEmailForm(FlaskForm):
    """Formulário para adicionar/editar email de empresa"""
    email = StringField('Email', validators=[
        DataRequired(message='Email é obrigatório'),
        Email(message='Email inválido'),
        Length(max=120, message='Email deve ter no máximo 120 caracteres')
    ])
    nome_contato = StringField('Nome do Contato', validators=[
        Length(max=150, message='Nome deve ter no máximo 150 caracteres')
    ])
    receber_notificacoes = BooleanField('Receber Notificações', default=True)
    ativo = BooleanField('Ativo', default=True)
    submit = SubmitField('Salvar')
