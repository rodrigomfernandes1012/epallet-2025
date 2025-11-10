"""
Módulo de integração com WhatsGw API para envio de mensagens WhatsApp
API: https://app.whatsgw.com.br
"""
import requests
import json
import os
from flask import current_app


def formatar_numero_whatsapp(celular):
    """
    Formata número de celular para o padrão WhatsApp (55DDDNÚMERO)
    Remove caracteres especiais e adiciona código do país se necessário
    
    Exemplos:
    - (11) 98765-4321 -> 5511987654321
    - 11987654321 -> 5511987654321
    - 5511987654321 -> 5511987654321
    """
    if not celular:
        return None
    
    # Remove todos os caracteres não numéricos
    numero = ''.join(filter(str.isdigit, celular))
    
    # Se não tem código do país (55), adiciona
    if not numero.startswith('55'):
        numero = '55' + numero
    
    # Verifica se o número tem tamanho válido (13 dígitos: 55 + DDD + 9 dígitos)
    if len(numero) < 12 or len(numero) > 13:
        return None
    
    return numero


def enviar_whatsapp(numero, mensagem):
    """
    Envia mensagem de WhatsApp usando WhatsGw API
    
    Args:
        numero (str): Número do WhatsApp no formato 5511987654321
        mensagem (str): Texto da mensagem a ser enviada
    
    Returns:
        dict: Resposta da API ou None em caso de erro
    """
    try:
        # Obter configurações do .env
        apikey = os.getenv('WHATSGW_APIKEY')
        phone_number = os.getenv('WHATSGW_PHONE_NUMBER')
        
        if not apikey:
            current_app.logger.error('WHATSGW_APIKEY não configurado no .env')
            return None
        
        if not phone_number:
            current_app.logger.error('WHATSGW_PHONE_NUMBER não configurado no .env')
            return None
        
        # Formatar número
        numero_formatado = formatar_numero_whatsapp(numero)
        if not numero_formatado:
            current_app.logger.error(f'Número de WhatsApp inválido: {numero}')
            return None
        
        # URL da API WhatsGw
        url = "https://app.whatsgw.com.br/api/WhatsGw/Send"
        
        # Payload
        payload = json.dumps({
            "apikey": apikey,
            "phone_number": phone_number,
            "contact_phone_number": numero_formatado,
            "message_custom_id": "epallet_system",
            "message_type": "text",
            "message_body": mensagem
        })
        
        # Headers
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {apikey}'
        }
        
        # Enviar requisição
        response = requests.post(url, headers=headers, data=payload, timeout=10)
        
        # Verificar resposta
        if response.status_code == 200:
            current_app.logger.info(f'WhatsApp enviado com sucesso para {numero_formatado}')
            return response.json()
        else:
            current_app.logger.error(f'Erro ao enviar WhatsApp: {response.status_code} - {response.text}')
            return None
            
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f'Erro de conexão ao enviar WhatsApp: {str(e)}')
        return None
    except Exception as e:
        current_app.logger.error(f'Erro inesperado ao enviar WhatsApp: {str(e)}')
        return None


def enviar_whatsapp_vale_criado(motorista, vale):
    """
    Envia WhatsApp para o motorista quando um vale pallet é criado
    
    Args:
        motorista: Objeto Motorista
        vale: Objeto ValePallet
    
    Returns:
        bool: True se enviado com sucesso, False caso contrário
    """
    if not motorista or not motorista.celular:
        return False
    
    mensagem = f"""Sr.(a) Motorista: {motorista.nome}

Esta empresa usa o sistema Epallet, ao realizar a entrega da nota "{vale.numero_documento}" peça o código do PIN ao receber.

Acesse motorista.epallet.com.br e confirme o número do documento e PIN.

Sistema Epallet - Gestão de Pallets"""
    
    resultado = enviar_whatsapp(motorista.celular, mensagem)
    return resultado is not None


def enviar_whatsapp_recebimento_confirmado(motorista, vale):
    """
    Envia WhatsApp para o motorista quando o recebimento é confirmado
    
    Args:
        motorista: Objeto Motorista
        vale: Objeto ValePallet
    
    Returns:
        bool: True se enviado com sucesso, False caso contrário
    """
    if not motorista or not motorista.celular:
        return False
    
    mensagem = f"""Sr.(a) Motorista: {motorista.nome}

Sua entrega de pallets foi confirmada!

📦 Cliente: {vale.cliente_nome}
🚚 Transportadora: {vale.transportadora_nome}
📄 Documento: {vale.numero_documento}
🔐 PIN: {vale.pin}

Acesse motorista.epallet.com.br e valide sua entrega.

Sistema Epallet - Gestão de Pallets"""
    
    resultado = enviar_whatsapp(motorista.celular, mensagem)
    return resultado is not None


def enviar_whatsapp_entrega_concluida(motorista, vale):
    """
    Envia WhatsApp para o motorista quando a entrega é concluída
    
    Args:
        motorista: Objeto Motorista
        vale: Objeto ValePallet
    
    Returns:
        bool: True se enviado com sucesso, False caso contrário
    """
    try:
        if not motorista:
            current_app.logger.warning('Tentativa de enviar WhatsApp sem motorista')
            return False
            
        if not motorista.celular:
            current_app.logger.warning(f'Motorista {motorista.nome} não tem celular cadastrado')
            return False
        
        mensagem = f"""Sr.(a) {motorista.nome}, a nota "{vale.numero_documento}", foi registrado entrega concluida em nosso sistema."""
        
        current_app.logger.info(f'Enviando WhatsApp de entrega concluída para {motorista.nome} ({motorista.celular})')
        resultado = enviar_whatsapp(motorista.celular, mensagem)
        
        if resultado:
            current_app.logger.info(f'WhatsApp enviado com sucesso para {motorista.nome}')
            return True
        else:
            current_app.logger.error(f'Falha ao enviar WhatsApp para {motorista.nome}')
            return False
            
    except Exception as e:
        current_app.logger.error(f'Erro ao enviar WhatsApp entrega concluída: {str(e)}')
        return False
