"""
Funções auxiliares para o webhook WhatsApp
"""
from app.utils.whatsapp import enviar_whatsapp


def enviar_resposta_validacao_sucesso(motorista, vale):
    """
    Envia mensagem de confirmação ao motorista após validação bem-sucedida
    
    Args:
        motorista: Objeto Motorista
        vale: Objeto ValePallet
    
    Returns:
        bool: True se enviado com sucesso
    """
    if not motorista or not motorista.celular:
        return False
    
    mensagem = f"""✅ VALIDAÇÃO CONFIRMADA!

Motorista: {motorista.nome}
Documento: {vale.numero_documento}
PIN: {vale.pin}

Sua entrega foi validada com sucesso!
Status: Entrega Concluída

Sistema Epallet - Gestão de Pallets"""
    
    resultado = enviar_whatsapp(motorista.celular, mensagem)
    return resultado is not None


def enviar_resposta_pin_invalido(celular, pin):
    """
    Envia mensagem informando que o PIN não foi encontrado
    
    Args:
        celular (str): Número do celular
        pin (str): PIN informado
    
    Returns:
        bool: True se enviado com sucesso
    """
    if not celular:
        return False
    
    mensagem = f"""❌ PIN NÃO ENCONTRADO

O PIN {pin} não foi encontrado ou não está vinculado ao seu cadastro.

Verifique:
• Se o PIN está correto
• Se você é o motorista responsável por esta entrega
• Se a entrega já foi confirmada pelo destinatário

Sistema Epallet - Gestão de Pallets"""
    
    resultado = enviar_whatsapp(celular, mensagem)
    return resultado is not None


def enviar_resposta_status_invalido(celular, vale):
    """
    Envia mensagem informando que o vale não pode ser validado
    
    Args:
        celular (str): Número do celular
        vale: Objeto ValePallet
    
    Returns:
        bool: True se enviado com sucesso
    """
    if not celular:
        return False
    
    mensagem = f"""⚠️ VALIDAÇÃO NÃO PERMITIDA

Documento: {vale.numero_documento}
Status atual: {vale.get_status_display()}

Este vale não pode ser validado no momento.

Para validar, o destinatário precisa primeiro confirmar o recebimento.

Sistema Epallet - Gestão de Pallets"""
    
    resultado = enviar_whatsapp(celular, mensagem)
    return resultado is not None


def enviar_resposta_motorista_nao_encontrado(celular):
    """
    Envia mensagem informando que o motorista não foi encontrado
    
    Args:
        celular (str): Número do celular
    
    Returns:
        bool: True se enviado com sucesso
    """
    if not celular:
        return False
    
    mensagem = f"""❌ MOTORISTA NÃO CADASTRADO

Seu número não está cadastrado no sistema.

Para usar a validação por WhatsApp, solicite ao administrador que cadastre seu celular no sistema.

Sistema Epallet - Gestão de Pallets"""
    
    resultado = enviar_whatsapp(celular, mensagem)
    return resultado is not None
