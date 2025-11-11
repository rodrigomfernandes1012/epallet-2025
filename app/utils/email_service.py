"""
Serviço de Envio de Emails
Gerencia envio de emails do sistema
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from flask import current_app, render_template_string
from app import db
from app.models import EmailEnviado, EmpresaEmail, ValePallet
from app.utils.auditoria import log_acao


def get_smtp_config():
    """Retorna configurações SMTP do .env"""
    return {
        'server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
        'port': int(os.getenv('SMTP_PORT', 587)),
        'username': os.getenv('SMTP_USERNAME', ''),
        'password': os.getenv('SMTP_PASSWORD', ''),
        'from_email': os.getenv('SMTP_FROM_EMAIL', ''),
        'from_name': os.getenv('SMTP_FROM_NAME', 'Sistema ePallet')
    }


def get_email_template():
    """Retorna template HTML do email"""
    return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { 
            font-family: Arial, sans-serif; 
            line-height: 1.6; 
            color: #333; 
            margin: 0;
            padding: 0;
        }
        .container { 
            max-width: 600px; 
            margin: 0 auto; 
            padding: 20px; 
        }
        .header { 
            background: #344767; 
            color: white; 
            padding: 30px 20px; 
            text-align: center;
            border-radius: 5px 5px 0 0;
        }
        .header h2 {
            margin: 0;
            font-size: 24px;
        }
        .content { 
            background: #ffffff; 
            padding: 30px 20px; 
            border: 1px solid #e0e0e0;
        }
        .info-section {
            background: #f8f9fa;
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
        }
        .info-row { 
            margin: 12px 0; 
            padding: 12px; 
            background: white; 
            border-left: 4px solid #344767;
            border-radius: 3px;
        }
        .label { 
            font-weight: bold; 
            color: #344767;
            display: inline-block;
            min-width: 180px;
        }
        .value {
            color: #555;
        }
        .alert { 
            background: #fff3cd; 
            border: 2px solid #ffc107; 
            padding: 20px; 
            margin: 25px 0;
            border-radius: 5px;
            text-align: center;
        }
        .alert strong {
            color: #856404;
            font-size: 18px;
        }
        .alert .date {
            font-size: 20px;
            color: #d39e00;
            font-weight: bold;
            margin-top: 10px;
        }
        .footer { 
            text-align: center; 
            color: #666; 
            font-size: 12px; 
            margin-top: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 0 0 5px 5px;
        }
        .footer p {
            margin: 5px 0;
        }
        .divider {
            height: 2px;
            background: linear-gradient(to right, transparent, #344767, transparent);
            margin: 25px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>🚚 Notificação de Envio de Pallets</h2>
        </div>
        
        <div class="content">
            <p style="font-size: 16px; margin-bottom: 20px;">
                Prezado(a) <strong>{{ destinatario_nome }}</strong>,
            </p>
            
            <p style="font-size: 14px; color: #555;">
                Foi emitido pelo sistema <strong>ePallet</strong> um envio de pallets.
            </p>
            
            <p style="font-size: 14px; color: #555; margin-top: 15px;">
                <strong>⚠️ IMPORTANTE:</strong> É necessário informar o número do <strong>PIN</strong> ao motorista para a entrega dos pallets.
            </p>
            
            <!-- PIN em Destaque -->
            <div style="background: #fff3cd; border: 3px solid #ff0000; border-radius: 10px; padding: 25px; margin: 25px 0; text-align: center;">
                <div style="font-size: 14px; color: #856404; margin-bottom: 10px; font-weight: bold;">
                    🔑 NÚMERO DO PIN
                </div>
                <div style="font-size: 48px; font-weight: bold; color: #ff0000; letter-spacing: 8px; font-family: 'Courier New', monospace;">
                    {{ pin }}
                </div>
                <div style="font-size: 12px; color: #856404; margin-top: 10px;">
                    Informe este PIN ao motorista para realizar a entrega
                </div>
            </div>
            
            <div class="divider"></div>
            
            <p style="font-size: 14px; color: #555; font-weight: bold;">
                Informações do Envio:
            </p>
            
            <div class="info-section">
                <div class="info-row">
                    <span class="label">📦 Quantidade de Pallets:</span>
                    <span class="value"><strong>{{ quantidade_pallets }}</strong></span>
                </div>
                
                <div class="info-row">
                    <span class="label">🏢 Pertencente a:</span>
                    <span class="value">{{ cliente_nome }}</span>
                </div>
                
                <div class="info-row">
                    <span class="label">🚛 Transportadora:</span>
                    <span class="value">{{ transportadora_nome }}</span>
                </div>
                
                <div class="info-row">
                    <span class="label">👤 Motorista:</span>
                    <span class="value">{{ motorista_nome }}</span>
                </div>
                
                <div class="info-row">
                    <span class="label">🚗 Placa do Veículo:</span>
                    <span class="value"><strong>{{ placa_veiculo }}</strong></span>
                </div>
            </div>
            
            <div class="alert">
                <div>⚠️ <strong>ATENÇÃO - PRAZO DE DEVOLUÇÃO</strong></div>
                <div style="margin-top: 15px; font-size: 14px;">
                    Os pallets deverão ser devolvidos até:
                </div>
                <div class="date">{{ data_vencimento }}</div>
            </div>
            
            <div class="divider"></div>
            
            <div class="info-section">
                <div class="info-row">
                    <span class="label">📄 Número do Documento:</span>
                    <span class="value">{{ numero_documento }}</span>
                </div>
                
                <div class="info-row">
                    <span class="label">📅 Data de Emissão:</span>
                    <span class="value">{{ data_emissao }}</span>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p><strong>Este é um email automático. Por favor, não responda.</strong></p>
            <p>Sistema ePallet - Gestão de Pallets</p>
            <p>© {{ ano_atual }} - Todos os direitos reservados</p>
        </div>
    </div>
</body>
</html>
"""


def enviar_email_vale_pallet(vale_pallet_id, usuario_id):
    """
    Envia email de notificação para o destinatário do vale pallet
    
    Args:
        vale_pallet_id: ID do vale pallet
        usuario_id: ID do usuário que está enviando
        
    Returns:
        dict: {'sucesso': bool, 'mensagem': str, 'emails_enviados': int, 'emails_erro': int}
    """
    try:
        # Buscar vale pallet
        vale = ValePallet.query.get(vale_pallet_id)
        if not vale:
            return {
                'sucesso': False,
                'mensagem': 'Vale pallet não encontrado',
                'emails_enviados': 0,
                'emails_erro': 0
            }
        
        # Buscar emails do destinatário
        emails_destinatario = EmpresaEmail.query.filter_by(
            empresa_id=vale.destinatario_id,
            ativo=True,
            receber_notificacoes=True
        ).all()
        
        if not emails_destinatario:
            return {
                'sucesso': False,
                'mensagem': 'Destinatário não possui emails cadastrados para receber notificações',
                'emails_enviados': 0,
                'emails_erro': 0
            }
        
        # Preparar dados do email
        dados_email = {
            'destinatario_nome': vale.destinatario.razao_social,
            'quantidade_pallets': vale.quantidade_pallets,
            'cliente_nome': vale.cliente.razao_social,
            'transportadora_nome': vale.transportadora.razao_social,
            'motorista_nome': vale.motorista.nome if vale.motorista else 'Não informado',
            'placa_veiculo': vale.motorista.placa_caminhao if vale.motorista else 'Não informada',
            'data_vencimento': vale.data_vencimento.strftime('%d/%m/%Y'),
            'numero_documento': vale.numero_documento,
            'data_emissao': vale.data_criacao.strftime('%d/%m/%Y %H:%M'),
            'pin': vale.pin,
            'ano_atual': datetime.now().year
        }
        
        # Template do email
        template = get_email_template()
        corpo_html = render_template_string(template, **dados_email)
        assunto = 'Envio de Pallets'
        
        # Configurações SMTP
        smtp_config = get_smtp_config()
        
        # Verificar se SMTP está configurado
        if not smtp_config['username'] or not smtp_config['password']:
            # Modo de desenvolvimento - simular envio
            for email_dest in emails_destinatario:
                email_log = EmailEnviado(
                    vale_pallet_id=vale_pallet_id,
                    destinatario_email=email_dest.email,
                    destinatario_nome=email_dest.nome_contato or vale.destinatario.razao_social,
                    assunto=assunto,
                    corpo=corpo_html,
                    status='enviado',
                    enviado_por_id=usuario_id
                )
                db.session.add(email_log)
            
            # Atualizar vale pallet
            vale.email_enviado = True
            vale.data_envio_email = datetime.utcnow()
            db.session.commit()
            
            log_acao(
                modulo='vale_pallet',
                acao='email',
                descricao=f'Email simulado (dev) para vale #{vale_pallet_id} - {len(emails_destinatario)} destinatários',
                registro_id=vale_pallet_id
            )
            
            return {
                'sucesso': True,
                'mensagem': f'Modo desenvolvimento: {len(emails_destinatario)} emails simulados',
                'emails_enviados': len(emails_destinatario),
                'emails_erro': 0
            }
        
        # Enviar emails
        emails_enviados = 0
        emails_erro = 0
        
        for email_dest in emails_destinatario:
            try:
                # Criar mensagem
                msg = MIMEMultipart('alternative')
                msg['Subject'] = assunto
                msg['From'] = f"{smtp_config['from_name']} <{smtp_config['from_email']}>"
                msg['To'] = email_dest.email
                
                # Anexar HTML
                parte_html = MIMEText(corpo_html, 'html', 'utf-8')
                msg.attach(parte_html)
                
                # Enviar email com timeout de 10 segundos
                with smtplib.SMTP(smtp_config['server'], smtp_config['port'], timeout=10) as server:
                    server.starttls()
                    server.login(smtp_config['username'], smtp_config['password'])
                    server.send_message(msg)
                
                # Registrar sucesso
                email_log = EmailEnviado(
                    vale_pallet_id=vale_pallet_id,
                    destinatario_email=email_dest.email,
                    destinatario_nome=email_dest.nome_contato or vale.destinatario.razao_social,
                    assunto=assunto,
                    corpo=corpo_html,
                    status='enviado',
                    enviado_por_id=usuario_id
                )
                db.session.add(email_log)
                emails_enviados += 1
                
            except Exception as e:
                # Registrar erro
                email_log = EmailEnviado(
                    vale_pallet_id=vale_pallet_id,
                    destinatario_email=email_dest.email,
                    destinatario_nome=email_dest.nome_contato or vale.destinatario.razao_social,
                    assunto=assunto,
                    corpo=corpo_html,
                    status='erro',
                    erro_mensagem=str(e),
                    enviado_por_id=usuario_id
                )
                db.session.add(email_log)
                emails_erro += 1
        
        # Atualizar vale pallet
        if emails_enviados > 0:
            vale.email_enviado = True
            vale.data_envio_email = datetime.utcnow()
        
        db.session.commit()
        
        # Registrar no log
        log_acao(
            modulo='vale_pallet',
            acao='email',
            descricao=f'Enviado email para vale #{vale_pallet_id} - {emails_enviados} sucesso, {emails_erro} erros',
            registro_id=vale_pallet_id
        )
        
        if emails_erro > 0 and emails_enviados == 0:
            return {
                'sucesso': False,
                'mensagem': f'Erro ao enviar todos os emails ({emails_erro} erros)',
                'emails_enviados': emails_enviados,
                'emails_erro': emails_erro
            }
        
        return {
            'sucesso': True,
            'mensagem': f'Emails enviados com sucesso! ({emails_enviados} enviados, {emails_erro} erros)',
            'emails_enviados': emails_enviados,
            'emails_erro': emails_erro
        }
        
    except Exception as e:
        db.session.rollback()
        log_acao(
            modulo='vale_pallet',
            acao='email',
            descricao=f'Erro ao enviar email para vale #{vale_pallet_id}: {str(e)}',
            registro_id=vale_pallet_id,
            sucesso=False,
            mensagem_erro=str(e)
        )
        return {
            'sucesso': False,
            'mensagem': f'Erro ao enviar emails: {str(e)}',
            'emails_enviados': 0,
            'emails_erro': 0
        }


def reenviar_email(email_enviado_id, usuario_id):
    """
    Reenvia um email que já foi enviado anteriormente
    
    Args:
        email_enviado_id: ID do registro de email enviado
        usuario_id: ID do usuário que está reenviando
        
    Returns:
        dict: {'sucesso': bool, 'mensagem': str}
    """
    try:
        # Buscar registro de email
        email_log = EmailEnviado.query.get(email_enviado_id)
        if not email_log:
            return {'sucesso': False, 'mensagem': 'Registro de email não encontrado'}
        
        # Configurações SMTP
        smtp_config = get_smtp_config()
        
        # Verificar se SMTP está configurado
        if not smtp_config['username'] or not smtp_config['password']:
            # Modo de desenvolvimento - simular reenvio
            email_log.reenviado = True
            email_log.data_reenvio = datetime.utcnow()
            email_log.status = 'reenviado'
            db.session.commit()
            
            log_acao(
                modulo='emails',
                acao='reenvio',
                descricao=f'Email simulado (dev) reenviado para {email_log.destinatario_email}',
                registro_id=email_enviado_id
            )
            
            return {'sucesso': True, 'mensagem': 'Modo desenvolvimento: Email simulado reenviado'}
        
        # Criar mensagem
        msg = MIMEMultipart('alternative')
        msg['Subject'] = email_log.assunto
        msg['From'] = f"{smtp_config['from_name']} <{smtp_config['from_email']}>"
        msg['To'] = email_log.destinatario_email
        
        # Anexar HTML
        parte_html = MIMEText(email_log.corpo, 'html', 'utf-8')
        msg.attach(parte_html)
        
        # Enviar email
        with smtplib.SMTP(smtp_config['server'], smtp_config['port']) as server:
            server.starttls()
            server.login(smtp_config['username'], smtp_config['password'])
            server.send_message(msg)
        
        # Atualizar registro
        email_log.reenviado = True
        email_log.data_reenvio = datetime.utcnow()
        email_log.status = 'reenviado'
        email_log.erro_mensagem = None
        db.session.commit()
        
        # Registrar no log
        log_acao(
            modulo='emails',
            acao='reenvio',
            descricao=f'Email reenviado para {email_log.destinatario_email} - Vale #{email_log.vale_pallet_id}',
            registro_id=email_enviado_id
        )
        
        return {'sucesso': True, 'mensagem': 'Email reenviado com sucesso!'}
        
    except Exception as e:
        db.session.rollback()
        log_acao(
            modulo='emails',
            acao='reenvio',
            descricao=f'Erro ao reenviar email #{email_enviado_id}: {str(e)}',
            registro_id=email_enviado_id,
            sucesso=False,
            mensagem_erro=str(e)
        )
        return {'sucesso': False, 'mensagem': f'Erro ao reenviar email: {str(e)}'}
