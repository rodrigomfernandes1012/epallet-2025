"""
Serviço de Devolução de Pallets
Lógica FIFO, envio de emails e WhatsApp
"""
from app import db
from app.models import DevolucaoPallet, DevolucaoBaixa, ValePallet, EmpresaEmail, EmailEnviado
from app.utils.whatsapp import enviar_whatsapp
from datetime import datetime
from sqlalchemy import func
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import requests


def gerar_pin_devolucao():
    """
    Gera um PIN único de 6 dígitos para devolução
    """
    while True:
        pin = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        
        # Verificar se já existe
        existe = DevolucaoPallet.query.filter_by(pin_devolucao=pin).first()
        if not existe:
            return pin


def calcular_saldo_disponivel(cliente_id, destinatario_id):
    """
    Calcula o saldo disponível de pallets para devolução
    """
    saldo = ValePallet.query.filter_by(
        cliente_id=cliente_id,
        destinatario_id=destinatario_id
    ).with_entities(
        func.sum(ValePallet.quantidade_pallets - ValePallet.quantidade_devolvida)
    ).scalar() or 0
    
    return int(saldo)


def processar_baixa_fifo(devolucao_id):
    """
    Processa a baixa dos vales pallet usando lógica FIFO (First In, First Out)
    Baixa os vales mais antigos primeiro
    """
    try:
        # Buscar devolução
        devolucao = DevolucaoPallet.query.get(devolucao_id)
        if not devolucao:
            return {'sucesso': False, 'mensagem': 'Devolução não encontrada'}
        
        if devolucao.status != 'coletado':
            return {'sucesso': False, 'mensagem': 'Devolução não está no status "coletado"'}
        
        # Buscar vales pallets com saldo (FIFO - mais antigos primeiro)
        vales = ValePallet.query.filter_by(
            cliente_id=devolucao.cliente_id,
            destinatario_id=devolucao.destinatario_id
        ).filter(
            ValePallet.quantidade_pallets > ValePallet.quantidade_devolvida
        ).order_by(
            ValePallet.data_criacao.asc()  # FIFO - mais antigos primeiro
        ).all()
        
        if not vales:
            return {'sucesso': False, 'mensagem': 'Nenhum vale pallet disponível para baixa'}
        
        quantidade_restante = devolucao.quantidade_pallets
        baixas_realizadas = []
        
        for vale in vales:
            if quantidade_restante <= 0:
                break
            
            # Calcular saldo do vale
            saldo_vale = vale.quantidade_pallets - vale.quantidade_devolvida
            
            if saldo_vale <= 0:
                continue
            
            # Calcular quanto baixar deste vale
            quantidade_baixar = min(quantidade_restante, saldo_vale)
            
            # Criar registro de baixa
            baixa = DevolucaoBaixa(
                devolucao_id=devolucao.id,
                vale_pallet_id=vale.id,
                quantidade_baixada=quantidade_baixar,
                data_baixa=datetime.utcnow()
            )
            db.session.add(baixa)
            
            # Atualizar vale pallet
            vale.quantidade_devolvida += quantidade_baixar
            
            # Atualizar datas de devolução
            if not vale.data_primeira_devolucao:
                vale.data_primeira_devolucao = datetime.utcnow()
            vale.data_ultima_devolucao = datetime.utcnow()
            
            # Se vale foi totalmente devolvido, finalizar
            if vale.quantidade_devolvida >= vale.quantidade_pallets:
                vale.status = 'finalizado'
            
            baixas_realizadas.append({
                'vale_id': vale.id,
                'quantidade': quantidade_baixar,
                'saldo_anterior': saldo_vale,
                'saldo_atual': vale.quantidade_pallets - vale.quantidade_devolvida
            })
            
            quantidade_restante -= quantidade_baixar
        
        # Atualizar devolução
        devolucao.status = 'finalizado'
        devolucao.data_confirmacao = datetime.utcnow()
        
        db.session.commit()
        
        return {
            'sucesso': True,
            'mensagem': f'{len(baixas_realizadas)} vale(s) baixado(s) com sucesso',
            'baixas': baixas_realizadas
        }
        
    except Exception as e:
        db.session.rollback()
        return {'sucesso': False, 'mensagem': f'Erro ao processar baixa: {str(e)}'}


def enviar_email_devolucao(devolucao_id, usuario_id):
    """
    Envia email para o destinatário informando sobre a devolução agendada
    """
    try:
        # Buscar devolução
        devolucao = DevolucaoPallet.query.get(devolucao_id)
        if not devolucao:
            return {'sucesso': False, 'mensagem': 'Devolução não encontrada'}
        
        # Buscar emails do destinatário
        emails = EmpresaEmail.query.filter_by(
            empresa_id=devolucao.destinatario_id,
            ativo=True,
            receber_notificacoes=True
        ).all()
        
        if not emails:
            return {'sucesso': False, 'mensagem': 'Nenhum email cadastrado para o destinatário'}
        
        # Preparar dados do email
        assunto = 'Agendamento de Coleta de Pallets'
        
        corpo_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #007bff; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f8f9fa; }}
                .info-box {{ background-color: white; padding: 15px; margin: 10px 0; border-left: 4px solid #007bff; }}
                .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>🚛 Agendamento de Coleta de Pallets</h2>
                </div>
                
                <div class="content">
                    <p>Prezado(a) <strong>{devolucao.destinatario.razao_social}</strong>,</p>
                    
                    <p>Foi agendada uma coleta de pallets com as seguintes informações:</p>
                    
                    <div class="info-box">
                        <h3>📋 Informações da Coleta</h3>
                        <p><strong>Data Agendada:</strong> {devolucao.data_agendamento.strftime('%d/%m/%Y')}</p>
                        <p><strong>Cliente:</strong> {devolucao.cliente.razao_social}</p>
                        <p><strong>Quantidade de Pallets:</strong> {devolucao.quantidade_pallets}</p>
                    </div>
                    
                    <div class="info-box">
                        <h3>🚚 Informações do Transporte</h3>
                        <p><strong>Transportadora:</strong> {devolucao.transportadora.razao_social}</p>
                        <p><strong>Motorista:</strong> {devolucao.motorista.nome if devolucao.motorista else 'A definir'}</p>
                        {f'<p><strong>Placa do Veículo:</strong> {devolucao.motorista.placa_caminhao}</p>' if devolucao.motorista and devolucao.motorista.placa_caminhao else ''}
                    </div>
                    
                    {f'<div class="info-box"><h3>📝 Observações</h3><p>{devolucao.observacoes}</p></div>' if devolucao.observacoes else ''}
                    
                    <p style="margin-top: 20px;">Por favor, esteja preparado para a coleta na data agendada.</p>
                </div>
                
                <div class="footer">
                    <p>Este é um email automático do sistema ePallet.</p>
                    <p>Por favor, não responda este email.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Configurações SMTP
        smtp_config = {
            'server': os.getenv('SMTP_SERVER', 'localhost'),
            'port': int(os.getenv('SMTP_PORT', 587)),
            'username': os.getenv('SMTP_USERNAME', ''),
            'password': os.getenv('SMTP_PASSWORD', ''),
            'from_email': os.getenv('SMTP_FROM_EMAIL', 'noreply@epallet.com'),
            'from_name': os.getenv('SMTP_FROM_NAME', 'Sistema ePallet')
        }
        
        emails_enviados = 0
        
        # Enviar para cada email
        for email_dest in emails:
            try:
                # Criar mensagem
                msg = MIMEMultipart('alternative')
                msg['Subject'] = assunto
                msg['From'] = f"{smtp_config['from_name']} <{smtp_config['from_email']}>"
                msg['To'] = email_dest.email
                
                # Adicionar corpo HTML
                msg.attach(MIMEText(corpo_html, 'html', 'utf-8'))
                
                # Enviar email
                with smtplib.SMTP(smtp_config['server'], smtp_config['port'], timeout=10) as server:
                    server.starttls()
                    server.login(smtp_config['username'], smtp_config['password'])
                    server.send_message(msg)
                
                emails_enviados += 1
                
                # Registrar log (não vamos criar EmailEnviado para devolução, apenas para vale pallet)
                
            except Exception as e:
                print(f"Erro ao enviar email para {email_dest.email}: {str(e)}")
                continue
        
        if emails_enviados > 0:
            return {
                'sucesso': True,
                'mensagem': f'{emails_enviados} email(s) enviado(s) com sucesso',
                'emails_enviados': emails_enviados
            }
        else:
            return {'sucesso': False, 'mensagem': 'Falha ao enviar emails'}
            
    except Exception as e:
        return {'sucesso': False, 'mensagem': f'Erro ao enviar email: {str(e)}'}


def enviar_whatsapp_agendamento_motorista(devolucao_id):
    """
    Envia WhatsApp para o motorista informando sobre o agendamento da coleta
    (com PIN de devolução)
    """
    try:
        # Buscar devolução
        devolucao = DevolucaoPallet.query.get(devolucao_id)
        if not devolucao:
            return {'sucesso': False, 'mensagem': 'Devolução não encontrada'}
        
        if not devolucao.motorista:
            return {'sucesso': False, 'mensagem': 'Motorista não definido'}
        
        if not devolucao.motorista.celular:
            return {'sucesso': False, 'mensagem': 'Celular do motorista não cadastrado'}
        
        # Log do celular original
        print(f"[DEBUG WhatsApp] Celular original do motorista: '{devolucao.motorista.celular}'")
        
        # Preparar mensagem
        mensagem = f"""🚚 *COLETA DE PALLETS AGENDADA*

Sr(a) *{devolucao.motorista.nome}*,

Sua coleta de pallets está agendada para *{devolucao.data_agendamento.strftime('%d/%m/%Y')}*, na empresa: *{devolucao.destinatario.razao_social}*.

A quantidade a retirar de pallets é *{devolucao.quantidade_pallets} pallets*.

📍 *Detalhes:*
• Cliente: {devolucao.cliente.razao_social}
• Transportadora: {devolucao.transportadora.razao_social}
{f'• Placa: {devolucao.motorista.placa_caminhao}' if devolucao.motorista.placa_caminhao else ''}

🔑 *PIN DE DEVOLUÇÃO:* {devolucao.pin_devolucao}

⚠️ *IMPORTANTE:* 
Ao chegar no local, INFORME este PIN ao responsável.
Este é o código de segurança que autoriza a coleta!

{f'📋 Observações: {devolucao.observacoes}' if devolucao.observacoes else ''}

---
Sistema ePallet"""
        
        # Usar função centralizada de envio de WhatsApp
        print(f"[DEBUG WhatsApp] Enviando via função enviar_whatsapp()")
        resultado = enviar_whatsapp(devolucao.motorista.celular, mensagem)
        
        if resultado:
            print(f"[DEBUG WhatsApp] WhatsApp enviado com sucesso!")
            return {
                'sucesso': True,
                'mensagem': 'WhatsApp de agendamento enviado com sucesso'
            }
        else:
            print(f"[DEBUG WhatsApp] Falha ao enviar WhatsApp")
            return {
                'sucesso': False,
                'mensagem': 'Falha ao enviar WhatsApp. Verifique as configurações WHATSGW_APIKEY e WHATSGW_PHONE_NUMBER'
            }
            
    except Exception as e:
        print(f"[DEBUG WhatsApp] Erro geral: {str(e)}")
        return {'sucesso': False, 'mensagem': f'Erro ao enviar WhatsApp: {str(e)}'}


def enviar_whatsapp_motorista(devolucao_id):
    """
    Envia WhatsApp para o motorista com informações da coleta e PIN de segurança
    """
    try:
        # Buscar devolução
        devolucao = DevolucaoPallet.query.get(devolucao_id)
        if not devolucao:
            return {'sucesso': False, 'mensagem': 'Devolução não encontrada'}
        
        if not devolucao.motorista:
            return {'sucesso': False, 'mensagem': 'Motorista não definido'}
        
        if not devolucao.motorista.celular:
            return {'sucesso': False, 'mensagem': 'Celular do motorista não cadastrado'}
        
        # Preparar mensagem
        mensagem = f"""
🚛 *COLETA DE PALLETS AGENDADA*

Sr(a) Motorista *{devolucao.motorista.nome}*,

Você deve coletar *{devolucao.quantidade_pallets} pallets* em:

📍 *Local:* {devolucao.cliente.razao_social}
📅 *Data:* {devolucao.data_agendamento.strftime('%d/%m/%Y')}
📦 *Destino:* {devolucao.transportadora.razao_social}

🔑 *PIN DE SEGURANÇA:* {devolucao.pin_devolucao}

⚠️ *IMPORTANTE:* 
Ao chegar no local, INFORME este PIN ao responsável.
Este é o código de segurança que autoriza a coleta!

---
Sistema ePallet
        """.strip()
        
        # Configuração WhatsApp API (exemplo usando Evolution API ou similar)
        whatsapp_api_url = os.getenv('WHATSAPP_API_URL', '')
        whatsapp_api_key = os.getenv('WHATSAPP_API_KEY', '')
        
        if not whatsapp_api_url or not whatsapp_api_key:
            # Modo desenvolvimento - apenas simular envio
            print(f"[MODO DEV] WhatsApp para {devolucao.motorista.celular}:")
            print(mensagem)
            return {
                'sucesso': True,
                'mensagem': 'WhatsApp simulado (modo desenvolvimento)',
                'modo': 'desenvolvimento'
            }
        
        # Limpar número (remover caracteres não numéricos)
        numero = ''.join(filter(str.isdigit, devolucao.motorista.celular))
        
        # Adicionar código do país se não tiver
        if not numero.startswith('55'):
            numero = '55' + numero
        
        # Enviar via API
        try:
            response = requests.post(
                f"{whatsapp_api_url}/message/sendText",
                headers={
                    'Content-Type': 'application/json',
                    'apikey': whatsapp_api_key
                },
                json={
                    'number': numero,
                    'text': mensagem
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    'sucesso': True,
                    'mensagem': 'WhatsApp enviado com sucesso',
                    'numero': numero
                }
            else:
                return {
                    'sucesso': False,
                    'mensagem': f'Erro ao enviar WhatsApp: {response.status_code}'
                }
                
        except Exception as e:
            return {'sucesso': False, 'mensagem': f'Erro ao enviar WhatsApp: {str(e)}'}
            
    except Exception as e:
        return {'sucesso': False, 'mensagem': f'Erro ao enviar WhatsApp: {str(e)}'}


def validar_pin_devolucao(pin):
    """
    Valida o PIN de devolução e atualiza o status para 'coletado'
    """
    try:
        # Buscar devolução pelo PIN
        devolucao = DevolucaoPallet.query.filter_by(pin_devolucao=pin).first()
        
        if not devolucao:
            return {'sucesso': False, 'mensagem': 'PIN inválido'}
        
        if devolucao.status != 'agendado':
            return {'sucesso': False, 'mensagem': f'Devolução já está no status "{devolucao.get_status_display()}"'}
        
        # Atualizar status
        devolucao.status = 'coletado'
        devolucao.data_coleta = datetime.utcnow()
        
        db.session.commit()
        
        # Enviar WhatsApp ao motorista informando que pode buscar os pallets
        if devolucao.motorista_id:
            from app.utils.devolucao_service import enviar_whatsapp_motorista_confirmacao
            resultado_whatsapp = enviar_whatsapp_motorista_confirmacao(devolucao.id)
            if resultado_whatsapp['sucesso']:
                print(f"WhatsApp de confirmação enviado ao motorista: {resultado_whatsapp['mensagem']}")
        
        return {
            'sucesso': True,
            'mensagem': 'PIN validado com sucesso! Coleta confirmada.',
            'devolucao_id': devolucao.id,
            'quantidade': devolucao.quantidade_pallets
        }
        
    except Exception as e:
        db.session.rollback()
        return {'sucesso': False, 'mensagem': f'Erro ao validar PIN: {str(e)}'}


def enviar_whatsapp_motorista_confirmacao(devolucao_id):
    """
    Envia WhatsApp para o motorista informando que pode buscar os pallets
    (após destinatário validar o PIN)
    """
    try:
        # Buscar devolução
        devolucao = DevolucaoPallet.query.get(devolucao_id)
        if not devolucao:
            return {'sucesso': False, 'mensagem': 'Devolução não encontrada'}
        
        if not devolucao.motorista:
            return {'sucesso': False, 'mensagem': 'Motorista não definido'}
        
        if not devolucao.motorista.celular:
            return {'sucesso': False, 'mensagem': 'Celular do motorista não cadastrado'}
        
        # Preparar mensagem
        mensagem = f"""
✅ *PIN VALIDADO - COLETA AUTORIZADA!*

Sr(a) Motorista *{devolucao.motorista.nome}*,

O responsável no local validou seu PIN de segurança!

📦 *Quantidade:* {devolucao.quantidade_pallets} pallets
📍 *Local:* {devolucao.cliente.razao_social}
🚚 *Transportadora:* {devolucao.transportadora.razao_social}

✅ *PRÓXIMOS PASSOS:*
1. Colete os {devolucao.quantidade_pallets} pallets
2. Transporte até {devolucao.transportadora.razao_social}
3. A transportadora confirmará o recebimento no sistema

---
Sistema ePallet
        """.strip()
        
        # Configuração WhatsApp API
        whatsapp_api_url = os.getenv('WHATSAPP_API_URL', '')
        whatsapp_api_key = os.getenv('WHATSAPP_API_KEY', '')
        
        if not whatsapp_api_url or not whatsapp_api_key:
            # Modo desenvolvimento - apenas simular envio
            print(f"[MODO DEV] WhatsApp CONFIRMAÇÃO para {devolucao.motorista.celular}:")
            print(mensagem)
            return {
                'sucesso': True,
                'mensagem': 'WhatsApp de confirmação simulado (modo desenvolvimento)',
                'modo': 'desenvolvimento'
            }
        
        # Limpar número (remover caracteres não numéricos)
        numero = ''.join(filter(str.isdigit, devolucao.motorista.celular))
        
        # Adicionar código do país se não tiver
        if not numero.startswith('55'):
            numero = '55' + numero
        
        # Enviar via API
        try:
            response = requests.post(
                f"{whatsapp_api_url}/message/sendText",
                headers={
                    'Content-Type': 'application/json',
                    'apikey': whatsapp_api_key
                },
                json={
                    'number': numero,
                    'text': mensagem
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    'sucesso': True,
                    'mensagem': 'WhatsApp de confirmação enviado com sucesso',
                    'numero': numero
                }
            else:
                return {
                    'sucesso': False,
                    'mensagem': f'Erro ao enviar WhatsApp: {response.status_code}'
                }
                
        except Exception as e:
            return {'sucesso': False, 'mensagem': f'Erro ao enviar WhatsApp: {str(e)}'}
            
    except Exception as e:
        return {'sucesso': False, 'mensagem': f'Erro ao enviar WhatsApp: {str(e)}'}
