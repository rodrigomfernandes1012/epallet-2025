"""
Utilitários para geração de QR Code para validação de vales
"""
import qrcode
import hashlib
from io import BytesIO
import base64
from flask import current_app


def gerar_qrcode_vale(vale_id, numero_documento, pin, data_criacao):
    """
    Gera QR Code para validação de vale pallet
    
    Args:
        vale_id: ID do vale
        numero_documento: Número do documento do vale
        pin: PIN de validação
        data_criacao: Data de criação do vale
        
    Returns:
        String base64 da imagem do QR Code
    """
    # Gerar assinatura digital (hash SHA256)
    # Combinar dados sensíveis para criar assinatura única
    dados_assinatura = f"{vale_id}|{numero_documento}|{pin}|{data_criacao.isoformat()}"
    assinatura = hashlib.sha256(dados_assinatura.encode()).hexdigest()
    
    # URL de produção
    base_url = "https://portal.epallet.com.br"
    
    # Construir URL de validação com parâmetros
    url_validacao = f"{base_url}/publico/validar-vale?id={vale_id}&doc={numero_documento}&sig={assinatura}"
    
    # Gerar QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url_validacao)
    qr.make(fit=True)
    
    # Criar imagem
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Converter para base64
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    img_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    return img_base64
