"""
Modelos do banco de dados
"""
from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import random
import string


@login_manager.user_loader
def load_user(user_id):
    """Callback para recarregar o objeto de usuário da sessão"""
    return User.query.get(int(user_id))


class TipoEmpresa(db.Model):
    """Modelo para tipos de empresa (Cliente, Transportadora, Destinatário)"""
    __tablename__ = 'tipos_empresa'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)
    descricao = db.Column(db.Text)
    ativo = db.Column(db.Boolean, default=True, nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    empresas = db.relationship('Empresa', backref='tipo_empresa_rel', lazy='dynamic')
    
    def __repr__(self):
        return f'<TipoEmpresa {self.nome}>'


class Empresa(db.Model):
    """Modelo para empresas"""
    __tablename__ = 'empresas'
    
    id = db.Column(db.Integer, primary_key=True)
    razao_social = db.Column(db.String(200), nullable=False)
    nome_fantasia = db.Column(db.String(200))
    cnpj = db.Column(db.String(18), unique=True, nullable=False, index=True)
    inscricao_estadual = db.Column(db.String(50))
    inscricao_municipal = db.Column(db.String(50))
    
    # Tipo de empresa
    tipo_empresa_id = db.Column(db.Integer, db.ForeignKey('tipos_empresa.id'))
    tipo = db.relationship('TipoEmpresa', backref='empresas_tipo')
    
    # Endereço
    cep = db.Column(db.String(10))
    logradouro = db.Column(db.String(200))
    numero = db.Column(db.String(20))
    complemento = db.Column(db.String(100))
    bairro = db.Column(db.String(100))
    cidade = db.Column(db.String(100))
    estado = db.Column(db.String(2))
    
    # Contato
    telefone = db.Column(db.String(20))
    celular = db.Column(db.String(20))
    email = db.Column(db.String(120))
    site = db.Column(db.String(200))
    
    # Status e controle
    ativa = db.Column(db.Boolean, default=True, nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamento com usuário que cadastrou
    criado_por_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    criado_por = db.relationship('User', foreign_keys=[criado_por_id], backref='empresas_criadas')
    
    # Relacionamentos
    usuarios_vinculados = db.relationship('User', foreign_keys='User.empresa_id', backref='empresa_vinculada', lazy='dynamic')
    motoristas = db.relationship('Motorista', backref='empresa_transportadora', lazy='dynamic')
    vales_pallet_cliente = db.relationship('ValePallet', foreign_keys='ValePallet.cliente_id', backref='cliente', lazy='dynamic')
    vales_pallet_transportadora = db.relationship('ValePallet', foreign_keys='ValePallet.transportadora_id', backref='transportadora', lazy='dynamic')
    vales_pallet_destinatario = db.relationship('ValePallet', foreign_keys='ValePallet.destinatario_id', backref='destinatario', lazy='dynamic')
    
    def __repr__(self):
        return f'<Empresa {self.razao_social}>'


class User(UserMixin, db.Model):
    """Modelo de Usuário para autenticação e gerenciamento"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    nome_completo = db.Column(db.String(150), nullable=False)
    ativo = db.Column(db.Boolean, default=True, nullable=False)
    
    # Vínculo com empresa
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'))
    
    # Vínculo com perfil
    perfil_id = db.Column(db.Integer, db.ForeignKey('perfis.id'))
    
    # Controle
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    vales_pallet_criados = db.relationship('ValePallet', backref='criado_por_user', lazy='dynamic')
    motoristas_cadastrados = db.relationship('Motorista', backref='cadastrado_por', lazy='dynamic')
    
    def set_password(self, password):
        """Gera hash da senha"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica se a senha está correta"""
        return check_password_hash(self.password_hash, password)
    
    def pode_ver_empresa(self, empresa_id):
        """Verifica se o usuário pode ver uma empresa"""
        empresa = Empresa.query.get(empresa_id)
        if not empresa:
            return False
        # Pode ver se for a empresa vinculada ou se foi ele quem cadastrou
        return empresa.criado_por_id == self.id or empresa.id == self.empresa_id
    
    def empresas_visiveis(self):
        """Retorna as empresas que o usuário pode ver"""
        # Empresas cadastradas pelo usuário + empresa vinculada
        empresas = Empresa.query.filter_by(criado_por_id=self.id).all()
        if self.empresa_id:
            empresa_vinculada = Empresa.query.get(self.empresa_id)
            if empresa_vinculada and empresa_vinculada not in empresas:
                empresas.append(empresa_vinculada)
        return empresas
    
    def tem_permissao(self, modulo, acao):
        """Verifica se o usuário tem permissão para uma ação em um módulo"""
        if not self.perfil_id:
            return False
        
        perfil = Perfil.query.get(self.perfil_id)
        if not perfil or not perfil.ativo:
            return False
        
        return perfil.tem_permissao(modulo, acao)
    
    def get_modulos_permitidos(self):
        """Retorna lista de módulos que o usuário tem permissão de visualizar"""
        if not self.perfil_id:
            return []
        
        perfil = Perfil.query.get(self.perfil_id)
        if not perfil or not perfil.ativo:
            return []
        
        modulos = []
        permissoes = PerfilPermissao.query.filter_by(perfil_id=self.perfil_id).all()
        for perm in permissoes:
            if perm.pode_visualizar:
                modulos.append(perm.modulo)
        
        return modulos
    
    def __repr__(self):
        return f'<User {self.username}>'


class Motorista(db.Model):
    """Modelo para motoristas"""
    __tablename__ = 'motoristas'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False, index=True)
    placa_caminhao = db.Column(db.String(10), nullable=False)
    
    # Vínculo com transportadora
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=False)
    
    # Contato
    telefone = db.Column(db.String(20))
    celular = db.Column(db.String(20))
    email = db.Column(db.String(120))
    
    # Status e controle
    ativo = db.Column(db.Boolean, default=True, nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamento com usuário que cadastrou
    cadastrado_por_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    def __repr__(self):
        return f'<Motorista {self.nome} - {self.placa_caminhao}>'


class ValePallet(db.Model):
    """Modelo para Vale Pallet"""
    __tablename__ = 'vales_pallet'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Empresas envolvidas
    cliente_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=False)
    transportadora_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=False)
    destinatario_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=False)
    
    # Motorista responsável pela entrega
    motorista_id = db.Column(db.Integer, db.ForeignKey('motoristas.id'))
    motorista = db.relationship('Motorista', backref='vales_pallet', lazy=True)
    
    # Dados do vale
    quantidade_pallets = db.Column(db.Integer, nullable=False)
    data_vencimento = db.Column(db.Date, nullable=False, index=True)
    numero_documento = db.Column(db.String(100), nullable=False)
    pin = db.Column(db.String(4), unique=True, nullable=False, index=True)
    
    # Status
    status = db.Column(db.String(30), default='pendente_entrega', nullable=False)  # pendente_entrega, entrega_realizada, entrega_concluida, cancelado
    data_confirmacao = db.Column(db.DateTime)  # Data da confirmação de recebimento
    
    # Controle de email
    email_enviado = db.Column(db.Boolean, default=False, nullable=False, index=True)
    data_envio_email = db.Column(db.DateTime)
    
    # Controle
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamento com usuário que criou
    criado_por_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    def get_status_display(self):
        """Retorna o nome do status em português"""
        status_map = {
            'pendente_entrega': 'Pendente de Entrega',
            'entrega_realizada': 'Entrega Realizada',
            'entrega_concluida': 'Entrega Concluída',
            'finalizado': 'Finalizado',
            'cancelado': 'Cancelado'
        }
        return status_map.get(self.status, self.status)
    
    def get_status_badge_class(self):
        """Retorna a classe CSS para o badge de status"""
        status_class = {
            'pendente_entrega': 'badge-warning',
            'entrega_realizada': 'badge-success',
            'entrega_concluida': 'badge-primary',
            'finalizado': 'badge-info',
            'cancelado': 'badge-danger'
        }
        return status_class.get(self.status, 'badge-secondary')
    
    @staticmethod
    def gerar_pin():
        """Gera um PIN aleatório de 4 dígitos único"""
        max_tentativas = 100
        for _ in range(max_tentativas):
            pin = ''.join(random.choices(string.digits, k=4))
            # Verifica se o PIN já existe
            if not ValePallet.query.filter_by(pin=pin).first():
                return pin
        # Se não conseguir gerar um PIN único, levanta exceção
        raise ValueError("Não foi possível gerar um PIN único")
    
    @property
    def cliente_nome(self):
        """Retorna o nome do cliente"""
        cliente = Empresa.query.get(self.cliente_id)
        return cliente.razao_social if cliente else '-'
    
    @property
    def transportadora_nome(self):
        """Retorna o nome da transportadora"""
        transportadora = Empresa.query.get(self.transportadora_id)
        return transportadora.razao_social if transportadora else '-'
    
    @property
    def destinatario_nome(self):
        """Retorna o nome do destinatário"""
        destinatario = Empresa.query.get(self.destinatario_id)
        return destinatario.razao_social if destinatario else '-'
    
    def __repr__(self):
        return f'<ValePallet {self.numero_documento} - PIN: {self.pin}>'



class LogAuditoria(db.Model):
    """Modelo para Log de Auditoria - Registra todas as ações do sistema"""
    __tablename__ = 'logs_auditoria'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Informações do evento
    modulo = db.Column(db.String(100), nullable=False, index=True)  # Ex: 'empresas', 'vale_pallet', 'auth'
    acao = db.Column(db.String(50), nullable=False, index=True)  # Ex: 'create', 'read', 'update', 'delete', 'login', 'logout'
    descricao = db.Column(db.Text, nullable=False)  # Descrição detalhada da ação
    
    # Dados técnicos
    operacao_sql = db.Column(db.String(20))  # INSERT, SELECT, UPDATE, DELETE
    tabela_afetada = db.Column(db.String(100))  # Nome da tabela afetada
    registro_id = db.Column(db.Integer)  # ID do registro afetado
    dados_anteriores = db.Column(db.Text)  # JSON com dados antes da alteração (para UPDATE/DELETE)
    dados_novos = db.Column(db.Text)  # JSON com dados novos (para INSERT/UPDATE)
    
    # Informações do usuário
    usuario_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # NULL se ação pública
    usuario_nome = db.Column(db.String(100))  # Nome do usuário (para facilitar consultas)
    
    # Informações de rede
    ip_origem = db.Column(db.String(45), nullable=False, index=True)  # IPv4 ou IPv6
    user_agent = db.Column(db.String(500))  # Navegador/dispositivo
    
    # Informações de tempo
    data_hora = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Status e resultado
    sucesso = db.Column(db.Boolean, default=True, nullable=False)  # Se a operação foi bem-sucedida
    mensagem_erro = db.Column(db.Text)  # Mensagem de erro se sucesso=False
    
    # Relacionamento
    usuario = db.relationship('User', backref='logs_auditoria', foreign_keys=[usuario_id])
    
    def __repr__(self):
        return f'<LogAuditoria {self.modulo}.{self.acao} - {self.data_hora}>'
    
    @staticmethod
    def registrar(modulo, acao, descricao, usuario_id=None, usuario_nome=None, 
                  ip_origem=None, operacao_sql=None, tabela_afetada=None, 
                  registro_id=None, dados_anteriores=None, dados_novos=None,
                  user_agent=None, sucesso=True, mensagem_erro=None):
        """
        Método estático para facilitar o registro de logs
        
        Args:
            modulo: Nome do módulo/tela (ex: 'empresas', 'vale_pallet')
            acao: Tipo de ação (ex: 'create', 'read', 'update', 'delete', 'login')
            descricao: Descrição detalhada da ação
            usuario_id: ID do usuário (None para ações públicas)
            usuario_nome: Nome do usuário
            ip_origem: IP de origem da requisição
            operacao_sql: Tipo de operação SQL (INSERT, SELECT, UPDATE, DELETE)
            tabela_afetada: Nome da tabela afetada
            registro_id: ID do registro afetado
            dados_anteriores: Dados antes da alteração (dict ou JSON string)
            dados_novos: Dados novos (dict ou JSON string)
            user_agent: User agent do navegador
            sucesso: Se a operação foi bem-sucedida
            mensagem_erro: Mensagem de erro se houver
        """
        import json
        from flask import request
        
        # Obter IP automaticamente se não fornecido
        if ip_origem is None and request:
            ip_origem = request.remote_addr or 'unknown'
        
        # Obter user agent automaticamente se não fornecido
        if user_agent is None and request:
            user_agent = request.headers.get('User-Agent', 'unknown')
        
        # Converter dicts para JSON se necessário
        if isinstance(dados_anteriores, dict):
            dados_anteriores = json.dumps(dados_anteriores, ensure_ascii=False)
        if isinstance(dados_novos, dict):
            dados_novos = json.dumps(dados_novos, ensure_ascii=False)
        
        log = LogAuditoria(
            modulo=modulo,
            acao=acao,
            descricao=descricao,
            operacao_sql=operacao_sql,
            tabela_afetada=tabela_afetada,
            registro_id=registro_id,
            dados_anteriores=dados_anteriores,
            dados_novos=dados_novos,
            usuario_id=usuario_id,
            usuario_nome=usuario_nome,
            ip_origem=ip_origem or 'unknown',
            user_agent=user_agent,
            sucesso=sucesso,
            mensagem_erro=mensagem_erro
        )
        
        db.session.add(log)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao registrar log: {e}")


class Perfil(db.Model):
    """Modelo para Perfis de Usuário com Permissões"""
    __tablename__ = 'perfis'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)
    descricao = db.Column(db.Text)
    ativo = db.Column(db.Boolean, default=True, nullable=False)
    sistema = db.Column(db.Boolean, default=False, nullable=False)  # Perfis do sistema não podem ser excluídos
    
    # Controle
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    usuarios = db.relationship('User', backref='perfil_rel', lazy='dynamic')
    permissoes = db.relationship('PerfilPermissao', backref='perfil_rel', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Perfil {self.nome}>'
    
    def get_permissao(self, modulo):
        """Retorna a permissão para um módulo específico"""
        return PerfilPermissao.query.filter_by(perfil_id=self.id, modulo=modulo).first()
    
    def tem_permissao(self, modulo, acao):
        """Verifica se o perfil tem permissão para uma ação em um módulo"""
        permissao = self.get_permissao(modulo)
        if not permissao:
            return False
        
        if acao == 'visualizar':
            return permissao.pode_visualizar
        elif acao == 'criar':
            return permissao.pode_criar
        elif acao == 'editar':
            return permissao.pode_editar
        elif acao == 'excluir':
            return permissao.pode_excluir
        
        return False


class PerfilPermissao(db.Model):
    """Modelo para Permissões de Perfil por Módulo"""
    __tablename__ = 'perfis_permissoes'
    
    id = db.Column(db.Integer, primary_key=True)
    perfil_id = db.Column(db.Integer, db.ForeignKey('perfis.id'), nullable=False)
    
    # Módulo do sistema
    modulo = db.Column(db.String(50), nullable=False, index=True)
    # Módulos: dashboard, empresas, tipos_empresa, motoristas, vale_pallet, 
    #          relatorios, logs, usuarios, perfis
    
    # Permissões
    pode_visualizar = db.Column(db.Boolean, default=False, nullable=False)
    pode_criar = db.Column(db.Boolean, default=False, nullable=False)
    pode_editar = db.Column(db.Boolean, default=False, nullable=False)
    pode_excluir = db.Column(db.Boolean, default=False, nullable=False)
    
    # Controle
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Constraint única para perfil + módulo
    __table_args__ = (
        db.UniqueConstraint('perfil_id', 'modulo', name='uq_perfil_modulo'),
    )
    
    def __repr__(self):
        return f'<PerfilPermissao {self.perfil_id} - {self.modulo}>'



class EmpresaEmail(db.Model):
    """Modelo para Emails de Empresa (múltiplos emails por empresa)"""
    __tablename__ = 'empresa_emails'
    
    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=False)
    email = db.Column(db.String(120), nullable=False, index=True)
    nome_contato = db.Column(db.String(150))
    receber_notificacoes = db.Column(db.Boolean, default=True, nullable=False)
    ativo = db.Column(db.Boolean, default=True, nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamento
    empresa = db.relationship('Empresa', backref=db.backref('emails', lazy='dynamic'))
    
    def __repr__(self):
        return f'<EmpresaEmail {self.email} - {self.empresa.razao_social if self.empresa else "N/A"}>'


class EmailEnviado(db.Model):
    """Modelo para Log de Emails Enviados"""
    __tablename__ = 'emails_enviados'
    
    id = db.Column(db.Integer, primary_key=True)
    vale_pallet_id = db.Column(db.Integer, db.ForeignKey('vales_pallet.id'), nullable=False)
    destinatario_email = db.Column(db.String(120), nullable=False, index=True)
    destinatario_nome = db.Column(db.String(150))
    assunto = db.Column(db.String(200), nullable=False)
    corpo = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='enviado', nullable=False, index=True)  # enviado, erro, reenviado
    erro_mensagem = db.Column(db.Text)
    data_envio = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    reenviado = db.Column(db.Boolean, default=False, nullable=False, index=True)
    data_reenvio = db.Column(db.DateTime)
    enviado_por_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relacionamentos
    vale_pallet = db.relationship('ValePallet', backref=db.backref('emails_enviados', lazy='dynamic'))
    enviado_por = db.relationship('User', backref='emails_enviados')
    
    def get_status_display(self):
        """Retorna o nome do status em português"""
        status_map = {
            'enviado': 'Enviado',
            'erro': 'Erro no Envio',
            'reenviado': 'Reenviado'
        }
        return status_map.get(self.status, self.status)
    
    def get_status_badge_class(self):
        """Retorna a classe CSS para o badge de status"""
        status_class = {
            'enviado': 'badge-success',
            'erro': 'badge-danger',
            'reenviado': 'badge-info'
        }
        return status_class.get(self.status, 'badge-secondary')
    
    def __repr__(self):
        return f'<EmailEnviado {self.destinatario_email} - Vale #{self.vale_pallet_id}>'
