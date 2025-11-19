"""
Utilitários para geração e validação de QR Code
"""
import hashlib
import qrcode
from io import BytesIO
import base64
from flask import current_app


def gerar_hash_vale(vale_id, numero_documento, pin, data_criacao):
    """
    Gera hash criptográfico único para o vale
    
    Args:
        vale_id: ID do vale
        numero_documento: Número do documento
        pin: PIN de 4 dígitos
        data_criacao: Data de criação do vale
        
    Returns:
        str: Hash SHA256 em formato hexadecimal (primeiros 16 caracteres)
    """
    # Chave secreta do app (deve estar no .env em produção)
    secret_key = current_app.config.get('SECRET_KEY', 'chave-padrao-dev')
    
    # Concatenar dados + chave secreta
    dados = f"{vale_id}|{numero_documento}|{pin}|{data_criacao.isoformat()}|{secret_key}"
    
    # Gerar hash SHA256
    hash_completo = hashlib.sha256(dados.encode('utf-8')).hexdigest()
    
    # Retornar primeiros 16 caracteres (suficiente para unicidade)
    return hash_completo[:16]


def gerar_qrcode_vale(vale_id, numero_documento, pin, data_criacao):
    """
    Gera QR Code para validação do vale
    
    Args:
        vale_id: ID do vale
        numero_documento: Número do documento
        pin: PIN de 4 dígitos
        data_criacao: Data de criação do vale
        
    Returns:
        str: Imagem do QR Code em base64
    """
    # Gerar hash de validação
    hash_validacao = gerar_hash_vale(vale_id, numero_documento, pin, data_criacao)
    
    # URL de validação
    url_validacao = f"{current_app.config.get('BASE_URL', 'http://localhost:5000')}/publico/validar-vale/{vale_id}/{hash_validacao}"
    
    # Criar QR Code
    qr = qrcode.QRCode(
        version=1,  # Tamanho automático
        error_correction=qrcode.constants.ERROR_CORRECT_M,  # Correção média
        box_size=10,
        border=2,
    )
    
    qr.add_data(url_validacao)
    qr.make(fit=True)
    
    # Gerar imagem
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Converter para base64
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    return img_base64


def validar_hash_vale(vale_id, numero_documento, pin, data_criacao, hash_fornecido):
    """
    Valida se o hash fornecido corresponde aos dados do vale
    
    Args:
        vale_id: ID do vale
        numero_documento: Número do documento
        pin: PIN de 4 dígitos
        data_criacao: Data de criação do vale
        hash_fornecido: Hash a ser validado
        
    Returns:
        bool: True se válido, False caso contrário
    """
    hash_esperado = gerar_hash_vale(vale_id, numero_documento, pin, data_criacao)
    return hash_esperado == hash_fornecido
