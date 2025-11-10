"""
Rotas de Webhook para receber mensagens WhatsApp
"""
from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models import Motorista, ValePallet
from app.utils.auditoria import log_acao
from app.utils.webhook_helper import (
    enviar_resposta_validacao_sucesso,
    enviar_resposta_pin_invalido,
    enviar_resposta_status_invalido,
    enviar_resposta_motorista_nao_encontrado
)
from datetime import datetime
import re

webhook_bp = Blueprint('webhook', __name__, url_prefix='/webhook')


def extrair_pin_da_mensagem(mensagem):
    """
    Extrai PIN de 4 dígitos da mensagem
    
    Args:
        mensagem (str): Mensagem recebida
    
    Returns:
        str: PIN de 4 dígitos ou None
    """
    if not mensagem:
        return None
    
    # Procurar por 4 dígitos consecutivos
    match = re.search(r'\b\d{4}\b', mensagem)
    if match:
        return match.group(0)
    
    return None


def formatar_numero_whatsapp(numero):
    """
    Formata número de WhatsApp removendo caracteres especiais
    
    Args:
        numero (str): Número com ou sem formatação
    
    Returns:
        str: Número apenas com dígitos
    """
    if not numero:
        return None
    
    # Remove todos os caracteres não numéricos
    return ''.join(filter(str.isdigit, numero))


@webhook_bp.route('/whatsapp', methods=['POST'])
def receber_mensagem_whatsapp():
    """
    Webhook para receber mensagens do WhatsGw
    
    Payload esperado:
    {
        "phone": "5511987654321",
        "body": "1234",
        "fromMe": false,
        ...
    }
    """
    try:
        # Obter dados do webhook
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Nenhum dado recebido'}), 400
        
        # Ignorar mensagens enviadas por nós
        if data.get('fromMe', False):
            return jsonify({'status': 'ignored', 'reason': 'Mensagem enviada por nós'}), 200
        
        # Obter número do remetente e mensagem
        phone = data.get('phone') or data.get('from')
        body = data.get('body') or data.get('message', {}).get('body')
        
        if not phone or not body:
            return jsonify({'error': 'Dados incompletos'}), 400
        
        # Formatar número
        phone_formatado = formatar_numero_whatsapp(phone)
        
        # Registrar log
        log_acao(
            modulo='webhook',
            acao='webhook_recebido',
            descricao=f'Mensagem recebida de {phone_formatado}: {body[:50]}'
        )
        
        # Extrair PIN da mensagem
        pin = extrair_pin_da_mensagem(body)
        
        if not pin:
            return jsonify({
                'status': 'ignored',
                'reason': 'Nenhum PIN de 4 dígitos encontrado na mensagem'
            }), 200
        
        # Buscar motorista pelo celular
        motorista = Motorista.query.filter(
            db.or_(
                Motorista.celular.like(f'%{phone_formatado[-11:]}'),  # Últimos 11 dígitos (DDD + número)
                Motorista.celular.like(f'%{phone_formatado[-10:]}')   # Últimos 10 dígitos (sem 9)
            )
        ).first()
        
        if not motorista:
            # Registrar log
            log_acao(
                modulo='webhook',
                acao='motorista_nao_encontrado',
                descricao=f'Motorista não encontrado para o telefone {phone_formatado}'
            )
            
            # Enviar resposta ao motorista
            enviar_resposta_motorista_nao_encontrado(phone_formatado)
            
            return jsonify({
                'status': 'error',
                'message': 'Motorista não encontrado'
            }), 404
        
        # Buscar vale pallet pelo PIN e motorista
        vale = ValePallet.query.filter_by(
            pin=pin,
            motorista_id=motorista.id
        ).first()
        
        if not vale:
            # Registrar log
            log_acao(
                modulo='webhook',
                acao='vale_nao_encontrado',
                descricao=f'Vale não encontrado para PIN {pin} e motorista {motorista.nome}'
            )
            
            # Enviar resposta ao motorista
            enviar_resposta_pin_invalido(phone_formatado, pin)
            
            return jsonify({
                'status': 'error',
                'message': f'Vale não encontrado para o PIN {pin}'
            }), 404
        
        # Verificar se o status permite validação
        if vale.status != 'entrega_realizada':
            # Registrar log
            log_acao(
                modulo='webhook',
                acao='validacao_negada',
                descricao=f'Vale {vale.numero_documento} não está em status "Entrega Realizada". Status atual: {vale.status}'
            )
            
            # Enviar resposta ao motorista
            enviar_resposta_status_invalido(phone_formatado, vale)
            
            return jsonify({
                'status': 'error',
                'message': f'Este vale não pode ser validado. Status atual: {vale.get_status_display()}'
            }), 400
        
        # Atualizar status para "Entrega Concluída"
        vale.status = 'entrega_concluida'
        db.session.commit()
        
        # Registrar log
        log_acao(
            modulo='webhook',
            acao='validacao_pin_whatsapp',
            descricao=f'PIN {pin} validado via WhatsApp por {motorista.nome}. Vale: {vale.numero_documento}',
            operacao_sql='UPDATE',
            tabela_afetada='vales_pallet'
        )
        
        # Enviar notificação WhatsApp informando entrega concluída
        try:
            from app.utils.whatsapp import enviar_whatsapp_entrega_concluida
            enviar_whatsapp_entrega_concluida(motorista, vale)
        except Exception as whatsapp_error:
            # Log do erro mas não interrompe o fluxo
            current_app.logger.error(f'Erro ao enviar WhatsApp no webhook: {str(whatsapp_error)}')
        
        return jsonify({
            'status': 'success',
            'message': f'Entrega validada com sucesso! Vale: {vale.numero_documento}',
            'data': {
                'motorista': motorista.nome,
                'documento': vale.numero_documento,
                'pin': pin,
                'status': vale.get_status_display()
            }
        }), 200
        
    except Exception as e:
        # Registrar log de erro
        log_acao(
            modulo='webhook',
            acao='erro_webhook',
            descricao=f'Erro ao processar webhook: {str(e)}',
            sucesso=False,
            mensagem_erro=str(e)
        )
        
        return jsonify({
            'status': 'error',
            'message': 'Erro ao processar mensagem'
        }), 500


@webhook_bp.route('/test', methods=['GET'])
def test_webhook():
    """
    Endpoint de teste para verificar se o webhook está funcionando
    """
    return jsonify({
        'status': 'ok',
        'message': 'Webhook está funcionando',
        'endpoint': '/webhook/whatsapp'
    }), 200
