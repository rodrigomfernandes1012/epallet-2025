"""
Módulo de Auditoria - Sistema de Log Automático
Registra todas as ações do sistema de forma transparente
"""
from functools import wraps
from flask import request
from flask_login import current_user
from app.models import LogAuditoria
import json


def registrar_log(modulo, acao, descricao_template=None, operacao_sql=None, tabela_afetada=None):
    """
    Decorator para registrar automaticamente ações do sistema
    
    Args:
        modulo: Nome do módulo (ex: 'empresas', 'vale_pallet', 'auth')
        acao: Tipo de ação (ex: 'create', 'read', 'update', 'delete', 'login')
        descricao_template: Template da descrição (pode usar {var} para substituição)
        operacao_sql: Tipo de operação SQL (INSERT, SELECT, UPDATE, DELETE)
        tabela_afetada: Nome da tabela afetada
    
    Exemplo de uso:
        @registrar_log('empresas', 'create', 'Criou nova empresa: {nome}', 'INSERT', 'empresas')
        def criar_empresa():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Executar a função original
            resultado = f(*args, **kwargs)
            
            try:
                # Obter informações do usuário
                usuario_id = current_user.id if current_user.is_authenticated else None
                usuario_nome = current_user.username if current_user.is_authenticated else 'Público'
                
                # Obter IP e user agent
                ip_origem = request.remote_addr if request else 'unknown'
                user_agent = request.headers.get('User-Agent') if request else None
                
                # Montar descrição
                descricao = descricao_template if descricao_template else f'{acao} em {modulo}'
                
                # Registrar log
                LogAuditoria.registrar(
                    modulo=modulo,
                    acao=acao,
                    descricao=descricao,
                    usuario_id=usuario_id,
                    usuario_nome=usuario_nome,
                    ip_origem=ip_origem,
                    user_agent=user_agent,
                    operacao_sql=operacao_sql,
                    tabela_afetada=tabela_afetada,
                    sucesso=True
                )
            except Exception as e:
                print(f"Erro ao registrar log: {e}")
            
            return resultado
        return decorated_function
    return decorator


def log_acao(modulo, acao, descricao, registro_id=None, dados_anteriores=None, 
             dados_novos=None, operacao_sql=None, tabela_afetada=None, sucesso=True, mensagem_erro=None):
    """
    Função auxiliar para registrar log manualmente
    
    Args:
        modulo: Nome do módulo
        acao: Tipo de ação
        descricao: Descrição da ação
        registro_id: ID do registro afetado
        dados_anteriores: Dados antes da alteração
        dados_novos: Dados novos
        operacao_sql: Tipo de operação SQL
        tabela_afetada: Nome da tabela
        sucesso: Se a operação foi bem-sucedida
        mensagem_erro: Mensagem de erro se houver
    """
    try:
        usuario_id = current_user.id if current_user.is_authenticated else None
        usuario_nome = current_user.username if current_user.is_authenticated else 'Público'
        ip_origem = request.remote_addr if request else 'unknown'
        user_agent = request.headers.get('User-Agent') if request else None
        
        LogAuditoria.registrar(
            modulo=modulo,
            acao=acao,
            descricao=descricao,
            usuario_id=usuario_id,
            usuario_nome=usuario_nome,
            ip_origem=ip_origem,
            user_agent=user_agent,
            operacao_sql=operacao_sql,
            tabela_afetada=tabela_afetada,
            registro_id=registro_id,
            dados_anteriores=dados_anteriores,
            dados_novos=dados_novos,
            sucesso=sucesso,
            mensagem_erro=mensagem_erro
        )
    except Exception as e:
        print(f"Erro ao registrar log: {e}")


def log_acesso_tela(modulo, tela):
    """
    Registra acesso a uma tela/página
    
    Args:
        modulo: Nome do módulo
        tela: Nome da tela acessada
    """
    descricao = f'Acessou tela: {tela}'
    log_acao(modulo, 'acesso_tela', descricao, operacao_sql='SELECT', tabela_afetada=modulo)


def log_login(username, sucesso=True, mensagem_erro=None):
    """
    Registra tentativa de login
    
    Args:
        username: Nome do usuário
        sucesso: Se o login foi bem-sucedido
        mensagem_erro: Mensagem de erro se houver
    """
    descricao = f'Tentativa de login: {username}'
    if sucesso:
        descricao += ' - Sucesso'
    else:
        descricao += f' - Falha: {mensagem_erro}'
    
    log_acao('auth', 'login', descricao, sucesso=sucesso, mensagem_erro=mensagem_erro)


def log_logout(username):
    """
    Registra logout
    
    Args:
        username: Nome do usuário
    """
    descricao = f'Logout: {username}'
    log_acao('auth', 'logout', descricao)


def log_crud(modulo, operacao, tabela, registro_id=None, dados_anteriores=None, dados_novos=None, descricao=None):
    """
    Registra operações CRUD (Create, Read, Update, Delete)
    
    Args:
        modulo: Nome do módulo
        operacao: Tipo de operação ('create', 'read', 'update', 'delete')
        tabela: Nome da tabela afetada
        registro_id: ID do registro
        dados_anteriores: Dados antes da alteração
        dados_novos: Dados novos
        descricao: Descrição customizada
    """
    operacao_sql_map = {
        'create': 'INSERT',
        'read': 'SELECT',
        'update': 'UPDATE',
        'delete': 'DELETE'
    }
    
    operacao_sql = operacao_sql_map.get(operacao, 'SELECT')
    
    if not descricao:
        descricao_map = {
            'create': f'Criou registro em {tabela}',
            'read': f'Consultou registro em {tabela}',
            'update': f'Atualizou registro em {tabela}',
            'delete': f'Excluiu registro em {tabela}'
        }
        descricao = descricao_map.get(operacao, f'{operacao} em {tabela}')
    
    log_acao(
        modulo=modulo,
        acao=operacao,
        descricao=descricao,
        registro_id=registro_id,
        dados_anteriores=dados_anteriores,
        dados_novos=dados_novos,
        operacao_sql=operacao_sql,
        tabela_afetada=tabela
    )
