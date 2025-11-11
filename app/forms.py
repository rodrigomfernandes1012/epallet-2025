from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional
from app.models import User, Empresa
import re


class LoginForm(FlaskForm):
    """Formulário de Login"""
    username = StringField('Usuário ou Email', validators=[DataRequired(message='Campo obrigatório')])
    password = PasswordField('Senha', validators=[DataRequired(message='Campo obrigatório')])
    remember_me = BooleanField('Lembrar-me')
    submit = SubmitField('Entrar')


class RegistrationForm(FlaskForm):
    """Formulário de Registro de Usuário"""
    username = StringField('Nome de Usuário', validators=[
        DataRequired(message='Campo obrigatório'),
        Length(min=3, max=80, message='O nome de usuário deve ter entre 3 e 80 caracteres')
    ])
    email = StringField('Email', validators=[
        DataRequired(message='Campo obrigatório'),
        Email(message='Email inválido')
    ])
    nome_completo = StringField('Nome Completo', validators=[
        DataRequired(message='Campo obrigatório'),
        Length(min=3, max=150, message='O nome completo deve ter entre 3 e 150 caracteres')
    ])
    password = PasswordField('Senha', validators=[
        DataRequired(message='Campo obrigatório'),
        Length(min=6, message='A senha deve ter no mínimo 6 caracteres')
    ])
    password2 = PasswordField('Confirmar Senha', validators=[
        DataRequired(message='Campo obrigatório'),
        EqualTo('password', message='As senhas devem ser iguais')
    ])
    submit = SubmitField('Cadastrar')
    
    def validate_username(self, username):
        """Valida se o nome de usuário já existe"""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Este nome de usuário já está em uso. Por favor, escolha outro.')
    
    def validate_email(self, email):
        """Valida se o email já existe"""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Este email já está cadastrado. Por favor, use outro email.')


class EmpresaForm(FlaskForm):
    """Formulário de Cadastro de Empresa"""
    razao_social = StringField('Razão Social', validators=[
        DataRequired(message='Campo obrigatório'),
        Length(max=200, message='Máximo de 200 caracteres')
    ])
    tipo_empresa_id = SelectField('Tipo de Empresa', coerce=int, validators=[
        Optional()
    ])
    nome_fantasia = StringField('Nome Fantasia', validators=[
        Optional(),
        Length(max=200, message='Máximo de 200 caracteres')
    ])
    cnpj = StringField('CNPJ', validators=[
        DataRequired(message='Campo obrigatório'),
        Length(min=14, max=18, message='CNPJ inválido')
    ])
    inscricao_estadual = StringField('Inscrição Estadual', validators=[
        Optional(),
        Length(max=20, message='Máximo de 20 caracteres')
    ])
    inscricao_municipal = StringField('Inscrição Municipal', validators=[
        Optional(),
        Length(max=20, message='Máximo de 20 caracteres')
    ])
    
    # Endereço
    cep = StringField('CEP', validators=[Optional(), Length(max=10)])
    logradouro = StringField('Logradouro', validators=[Optional(), Length(max=200)])
    numero = StringField('Número', validators=[Optional(), Length(max=20)])
    complemento = StringField('Complemento', validators=[Optional(), Length(max=100)])
    bairro = StringField('Bairro', validators=[Optional(), Length(max=100)])
    cidade = StringField('Cidade', validators=[Optional(), Length(max=100)])
    estado = SelectField('Estado', choices=[
        ('', 'Selecione'),
        ('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amapá'), ('AM', 'Amazonas'),
        ('BA', 'Bahia'), ('CE', 'Ceará'), ('DF', 'Distrito Federal'),
        ('ES', 'Espírito Santo'), ('GO', 'Goiás'), ('MA', 'Maranhão'),
        ('MT', 'Mato Grosso'), ('MS', 'Mato Grosso do Sul'), ('MG', 'Minas Gerais'),
        ('PA', 'Pará'), ('PB', 'Paraíba'), ('PR', 'Paraná'), ('PE', 'Pernambuco'),
        ('PI', 'Piauí'), ('RJ', 'Rio de Janeiro'), ('RN', 'Rio Grande do Norte'),
        ('RS', 'Rio Grande do Sul'), ('RO', 'Rondônia'), ('RR', 'Roraima'),
        ('SC', 'Santa Catarina'), ('SP', 'São Paulo'), ('SE', 'Sergipe'),
        ('TO', 'Tocantins')
    ], validators=[Optional()])
    
    # Contato
    telefone = StringField('Telefone', validators=[Optional(), Length(max=20)])
    celular = StringField('Celular', validators=[Optional(), Length(max=20)])
    email = StringField('Email', validators=[Optional(), Email(message='Email inválido')])
    site = StringField('Site', validators=[Optional(), Length(max=200)])
    
    ativa = BooleanField('Empresa Ativa', default=True)
    submit = SubmitField('Salvar')
    
    def validate_cnpj(self, cnpj):
        """Valida se o CNPJ já existe (apenas números)"""
        # Remove caracteres não numéricos
        cnpj_numeros = re.sub(r'\D', '', cnpj.data)
        
        # Verifica se tem 14 dígitos
        if len(cnpj_numeros) != 14:
            raise ValidationError('CNPJ deve conter 14 dígitos')
        
        # Verifica se já existe no banco (exceto se for edição)
        # Não valida em edição, pois a validação é feita na rota
        # Para evitar falso positivo ao editar a própria empresa


class TipoEmpresaForm(FlaskForm):
    """Formulário de Cadastro de Tipo de Empresa"""
    nome = StringField('Nome do Tipo', validators=[
        DataRequired(message='Campo obrigatório'),
        Length(max=100, message='Máximo de 100 caracteres')
    ])
    descricao = StringField('Descrição', validators=[
        Optional(),
        Length(max=500, message='Máximo de 500 caracteres')
    ])
    ativo = BooleanField('Ativo', default=True)
    submit = SubmitField('Salvar')


class MotoristaForm(FlaskForm):
    """Formulário de Cadastro de Motorista"""
    nome = StringField('Nome Completo', validators=[
        DataRequired(message='Campo obrigatório'),
        Length(max=200, message='Máximo de 200 caracteres')
    ])
    cpf = StringField('CPF', validators=[
        DataRequired(message='Campo obrigatório'),
        Length(min=11, max=14, message='CPF inválido')
    ])
    placa_caminhao = StringField('Placa do Caminhão', validators=[
        DataRequired(message='Campo obrigatório'),
        Length(max=10, message='Máximo de 10 caracteres')
    ])
    empresa_id = SelectField('Transportadora', coerce=int, validators=[
        DataRequired(message='Campo obrigatório')
    ])
    
    # Contato
    telefone = StringField('Telefone', validators=[Optional(), Length(max=20)])
    celular = StringField('Celular', validators=[Optional(), Length(max=20)])
    email = StringField('Email', validators=[Optional(), Email(message='Email inválido')])
    
    ativo = BooleanField('Motorista Ativo', default=True)
    submit = SubmitField('Salvar')
    
    def validate_cpf(self, cpf):
        """Valida formato do CPF (apenas números)"""
        # Remove caracteres não numéricos
        cpf_numeros = re.sub(r'\D', '', cpf.data)
        
        # Verifica se tem 11 dígitos
        if len(cpf_numeros) != 11:
            raise ValidationError('CPF deve conter 11 dígitos')
        
        # Nota: Validação de CPF duplicado é feita na rota,
        # pois precisa excluir o próprio motorista em caso de edição


class ValePalletForm(FlaskForm):
    """Formulário de Vale Pallet"""
    cliente_id = SelectField('Cliente', coerce=int, validators=[
        DataRequired(message='Campo obrigatório')
    ])
    transportadora_id = SelectField('Transportadora', coerce=int, validators=[
        DataRequired(message='Campo obrigatório')
    ])
    destinatario_id = SelectField('Destinatário', coerce=int, validators=[
        DataRequired(message='Campo obrigatório')
    ])
    motorista_id = SelectField('Motorista', coerce=int, validators=[
        Optional()
    ])
    quantidade_pallets = StringField('Quantidade de Pallets', validators=[
        DataRequired(message='Campo obrigatório')
    ])
    numero_documento = StringField('Número do Documento', validators=[
        DataRequired(message='Campo obrigatório'),
        Length(max=100, message='Máximo de 100 caracteres')
    ])
    submit = SubmitField('Salvar')
    
    def validate_quantidade_pallets(self, quantidade_pallets):
        """Valida se a quantidade é um número inteiro positivo"""
        try:
            qtd = int(quantidade_pallets.data)
            if qtd <= 0:
                raise ValidationError('A quantidade deve ser maior que zero')
        except ValueError:
            raise ValidationError('A quantidade deve ser um número inteiro')
