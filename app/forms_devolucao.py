"""
Formulários para Devolução de Pallets
"""
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DateField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional, ValidationError
from app.models import Empresa, Motorista, ValePallet
from datetime import date, timedelta
from sqlalchemy import func


class DevolucaoPalletForm(FlaskForm):
    """Formulário para agendar devolução de pallets"""
    
    cliente_id = SelectField(
        'Cliente (De quem vai buscar)',
        coerce=int,
        validators=[DataRequired(message='Cliente é obrigatório')]
    )
    
    destinatario_id = SelectField(
        'Destinatário (Para quem vai devolver)',
        coerce=int,
        validators=[DataRequired(message='Destinatário é obrigatório')]
    )
    
    transportadora_id = SelectField(
        'Transportadora',
        coerce=int,
        validators=[DataRequired(message='Transportadora é obrigatória')]
    )
    
    motorista_id = SelectField(
        'Motorista',
        coerce=int,
        validators=[Optional()]
    )
    
    quantidade_pallets = IntegerField(
        'Quantidade de Pallets',
        validators=[
            DataRequired(message='Quantidade é obrigatória'),
            NumberRange(min=1, message='Quantidade deve ser maior que zero')
        ]
    )
    
    data_agendamento = DateField(
        'Data de Agendamento',
        format='%Y-%m-%d',
        validators=[DataRequired(message='Data de agendamento é obrigatória')]
    )
    
    observacoes = TextAreaField(
        'Observações',
        validators=[Optional(), Length(max=500)]
    )
    
    submit = SubmitField('Agendar Devolução')
    
    def __init__(self, *args, **kwargs):
        super(DevolucaoPalletForm, self).__init__(*args, **kwargs)
        
        # Carregar clientes
        clientes = Empresa.query.join(Empresa.tipo_empresa_rel).filter(
            Empresa.tipo_empresa_rel.has(nome='Cliente'),
            Empresa.ativa == True
        ).order_by(Empresa.razao_social).all()
        self.cliente_id.choices = [(0, 'Selecione...')] + [(c.id, c.razao_social) for c in clientes]
        
        # Carregar destinatários
        destinatarios = Empresa.query.join(Empresa.tipo_empresa_rel).filter(
            Empresa.tipo_empresa_rel.has(nome='Destinatário'),
            Empresa.ativa == True
        ).order_by(Empresa.razao_social).all()
        self.destinatario_id.choices = [(0, 'Selecione...')] + [(d.id, d.razao_social) for d in destinatarios]
        
        # Carregar transportadoras
        transportadoras = Empresa.query.join(Empresa.tipo_empresa_rel).filter(
            Empresa.tipo_empresa_rel.has(nome='Transportadora'),
            Empresa.ativa == True
        ).order_by(Empresa.razao_social).all()
        self.transportadora_id.choices = [(0, 'Selecione...')] + [(t.id, t.razao_social) for t in transportadoras]
        
        # Carregar motoristas
        motoristas = Motorista.query.filter_by(ativo=True).order_by(Motorista.nome).all()
        self.motorista_id.choices = [(0, 'Selecione...')] + [(m.id, m.nome) for m in motoristas]
    
    def validate_cliente_id(self, field):
        """Validar se cliente foi selecionado"""
        if field.data == 0:
            raise ValidationError('Selecione um cliente')
    
    def validate_destinatario_id(self, field):
        """Validar se destinatário foi selecionado"""
        if field.data == 0:
            raise ValidationError('Selecione um destinatário')
    
    def validate_transportadora_id(self, field):
        """Validar se transportadora foi selecionada"""
        if field.data == 0:
            raise ValidationError('Selecione uma transportadora')
    
    def validate_data_agendamento(self, field):
        """Validar se data de agendamento é válida"""
        if field.data:
            # Não pode ser no passado
            if field.data < date.today():
                raise ValidationError('Data de agendamento não pode ser no passado')
            
            # Não pode ser mais de 90 dias no futuro
            if field.data > date.today() + timedelta(days=90):
                raise ValidationError('Data de agendamento não pode ser mais de 90 dias no futuro')
    
    def validate_quantidade_pallets(self, field):
        """Validar se quantidade está disponível para devolução"""
        if field.data and self.cliente_id.data and self.destinatario_id.data:
            # Buscar saldo disponível
            saldo = ValePallet.query.filter_by(
                cliente_id=self.cliente_id.data,
                destinatario_id=self.destinatario_id.data
            ).with_entities(
                func.sum(ValePallet.quantidade_pallets - ValePallet.quantidade_devolvida)
            ).scalar() or 0
            
            if field.data > saldo:
                raise ValidationError(f'Quantidade indisponível. Saldo disponível: {saldo} pallets')


class ValidarPinDevolucaoForm(FlaskForm):
    """Formulário para motorista validar PIN de devolução"""
    
    pin_devolucao = StringField(
        'PIN de Devolução',
        validators=[
            DataRequired(message='PIN é obrigatório'),
            Length(min=6, max=6, message='PIN deve ter 6 dígitos')
        ]
    )
    
    submit = SubmitField('Validar PIN')


class ConfirmarDevolucaoForm(FlaskForm):
    """Formulário para transportadora confirmar devolução"""
    
    observacoes = TextAreaField(
        'Observações da Confirmação',
        validators=[Optional(), Length(max=500)]
    )
    
    submit = SubmitField('Confirmar Devolução')


class CancelarDevolucaoForm(FlaskForm):
    """Formulário para cancelar devolução"""
    
    motivo_cancelamento = TextAreaField(
        'Motivo do Cancelamento',
        validators=[
            DataRequired(message='Motivo do cancelamento é obrigatório'),
            Length(min=10, max=500, message='Motivo deve ter entre 10 e 500 caracteres')
        ]
    )
    
    submit = SubmitField('Cancelar Devolução')
