@bp.route('/<int:id>/imprimir-pdf')
@login_required
def imprimir_pdf(id):
    """Gera PDF do vale pallet com QR Code de validação - Meia folha A4"""
    from flask import make_response
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.pdfgen import canvas
    from reportlab.lib import colors
    from io import BytesIO
    from app.utils.qrcode_utils import gerar_qrcode_vale
    import base64
    
    vale = ValePallet.query.get_or_404(id)
    
    # Verificar se o usuário pode ver este vale
    if not (current_user.pode_ver_empresa(vale.cliente_id) or 
            current_user.pode_ver_empresa(vale.transportadora_id) or 
            current_user.pode_ver_empresa(vale.destinatario_id)):
        flash('Você não tem permissão para visualizar este vale pallet!', 'danger')
        return redirect(url_for('vale_pallet.listar'))
    
    # Criar buffer para PDF
    buffer = BytesIO()
    
    # Criar PDF - A4 completo (mas vamos usar só metade)
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # Definir altura de meia folha (A4 dividido ao meio horizontalmente)
    half_height = height / 2
    
    # Começar do topo da meia folha superior
    y_start = height - 1*cm
    y = y_start
    
    # ==================== CABEÇALHO ====================
    # Fundo do cabeçalho
    p.setFillColor(colors.HexColor('#5e72e4'))
    p.rect(0, y - 2.5*cm, width, 2.5*cm, fill=True, stroke=False)
    
    # Título
    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 18)
    p.drawCentredString(width/2, y - 1*cm, "VALE PALLET")
    
    # Documento e PIN
    p.setFont("Helvetica-Bold", 11)
    p.drawString(1.5*cm, y - 1.8*cm, f"Doc: {vale.numero_documento}")
    p.drawRightString(width - 1.5*cm, y - 1.8*cm, f"PIN: {vale.pin}")
    
    y -= 3*cm
    
    # ==================== CORPO - 2 COLUNAS ====================
    p.setFillColor(colors.black)
    
    # Coluna esquerda (informações principais)
    col1_x = 1.5*cm
    col2_x = width/2 + 0.5*cm
    
    # === COLUNA 1 ===
    y_col = y
    
    # Empresas
    p.setFont("Helvetica-Bold", 9)
    p.setFillColor(colors.HexColor('#5e72e4'))
    p.drawString(col1_x, y_col, "EMPRESAS")
    p.setFillColor(colors.black)
    y_col -= 0.5*cm
    
    p.setFont("Helvetica", 8)
    p.drawString(col1_x, y_col, f"Cliente:")
    y_col -= 0.35*cm
    p.setFont("Helvetica-Bold", 8)
    cliente_nome = vale.cliente.razao_social[:35] if vale.cliente else '-'
    p.drawString(col1_x + 0.3*cm, y_col, cliente_nome)
    y_col -= 0.5*cm
    
    p.setFont("Helvetica", 8)
    p.drawString(col1_x, y_col, f"Destinatário:")
    y_col -= 0.35*cm
    p.setFont("Helvetica-Bold", 8)
    dest_nome = vale.destinatario.razao_social[:35] if vale.destinatario else '-'
    p.drawString(col1_x + 0.3*cm, y_col, dest_nome)
    y_col -= 0.5*cm
    
    p.setFont("Helvetica", 8)
    p.drawString(col1_x, y_col, f"Transportadora:")
    y_col -= 0.35*cm
    p.setFont("Helvetica-Bold", 8)
    transp_nome = vale.transportadora.razao_social[:35] if vale.transportadora else '-'
    p.drawString(col1_x + 0.3*cm, y_col, transp_nome)
    y_col -= 0.7*cm
    
    # Motorista
    p.setFont("Helvetica-Bold", 9)
    p.setFillColor(colors.HexColor('#5e72e4'))
    p.drawString(col1_x, y_col, "MOTORISTA")
    p.setFillColor(colors.black)
    y_col -= 0.5*cm
    
    p.setFont("Helvetica", 8)
    if vale.motorista:
        motorista_nome = vale.motorista.nome[:35] if vale.motorista.nome else '-'
        p.drawString(col1_x, y_col, f"{motorista_nome}")
        y_col -= 0.35*cm
        p.drawString(col1_x, y_col, f"Placa: {vale.motorista.placa_caminhao or '-'} | Cel: {vale.motorista.celular or '-'}")
    else:
        p.drawString(col1_x, y_col, "Não informado")
    
    # === COLUNA 2 ===
    y_col = y
    
    # Pallets
    p.setFont("Helvetica-Bold", 9)
    p.setFillColor(colors.HexColor('#5e72e4'))
    p.drawString(col2_x, y_col, "PALLETS")
    p.setFillColor(colors.black)
    y_col -= 0.5*cm
    
    p.setFont("Helvetica", 8)
    p.drawString(col2_x, y_col, f"Quantidade Total:")
    p.setFont("Helvetica-Bold", 10)
    p.drawRightString(col2_x + 4*cm, y_col, f"{vale.quantidade_pallets}")
    y_col -= 0.45*cm
    
    p.setFont("Helvetica", 8)
    p.drawString(col2_x, y_col, f"Devolvidos:")
    p.setFont("Helvetica-Bold", 10)
    p.drawRightString(col2_x + 4*cm, y_col, f"{vale.quantidade_devolvida}")
    y_col -= 0.45*cm
    
    saldo = vale.quantidade_pallets - vale.quantidade_devolvida
    p.setFont("Helvetica-Bold", 8)
    p.drawString(col2_x, y_col, f"Saldo a Devolver:")
    p.setFont("Helvetica-Bold", 11)
    p.setFillColor(colors.HexColor('#28a745') if saldo > 0 else colors.grey)
    p.drawRightString(col2_x + 4*cm, y_col, f"{saldo}")
    p.setFillColor(colors.black)
    y_col -= 0.7*cm
    
    # Status
    p.setFont("Helvetica-Bold", 9)
    p.setFillColor(colors.HexColor('#5e72e4'))
    p.drawString(col2_x, y_col, "STATUS")
    p.setFillColor(colors.black)
    y_col -= 0.5*cm
    
    status_display = {
        'pendente_entrega': 'Pendente de Entrega',
        'entrega_realizada': 'Entrega Realizada',
        'entrega_concluida': 'Entrega Concluída',
        'cancelado': 'Cancelado'
    }.get(vale.status, vale.status)
    
    p.setFont("Helvetica-Bold", 8)
    p.drawString(col2_x, y_col, status_display)
    y_col -= 0.6*cm
    
    # Datas
    p.setFont("Helvetica-Bold", 9)
    p.setFillColor(colors.HexColor('#5e72e4'))
    p.drawString(col2_x, y_col, "DATAS")
    p.setFillColor(colors.black)
    y_col -= 0.5*cm
    
    p.setFont("Helvetica", 7)
    p.drawString(col2_x, y_col, f"Criação: {vale.data_criacao.strftime('%d/%m/%Y %H:%M')}")
    y_col -= 0.35*cm
    p.drawString(col2_x, y_col, f"Vencimento: {vale.data_vencimento.strftime('%d/%m/%Y')}")
    
    # ==================== QR CODE ====================
    # Gerar QR Code
    qr_base64 = gerar_qrcode_vale(vale.id, vale.numero_documento, vale.pin, vale.data_criacao)
    
    from reportlab.lib.utils import ImageReader
    qr_image = ImageReader(BytesIO(base64.b64decode(qr_base64)))
    
    # Posicionar QR Code no canto inferior direito
    qr_size = 3.5*cm
    qr_x = width - 1.5*cm - qr_size
    qr_y = half_height + 0.8*cm
    
    # Borda ao redor do QR Code
    p.setStrokeColor(colors.HexColor('#5e72e4'))
    p.setLineWidth(2)
    p.rect(qr_x - 0.2*cm, qr_y - 0.2*cm, qr_size + 0.4*cm, qr_size + 0.4*cm, fill=False, stroke=True)
    
    p.drawImage(qr_image, qr_x, qr_y, width=qr_size, height=qr_size)
    
    # Texto abaixo do QR Code
    p.setFont("Helvetica-Bold", 7)
    p.setFillColor(colors.HexColor('#5e72e4'))
    p.drawCentredString(qr_x + qr_size/2, qr_y - 0.4*cm, "Escaneie para validar")
    
    # ==================== RODAPÉ ====================
    p.setStrokeColor(colors.HexColor('#5e72e4'))
    p.setLineWidth(1)
    p.line(1.5*cm, half_height + 0.5*cm, width - 1.5*cm, half_height + 0.5*cm)
    
    p.setFont("Helvetica", 6)
    p.setFillColor(colors.grey)
    p.drawCentredString(width/2, half_height + 0.2*cm, f"Sistema ePallet | Documento com assinatura digital | Gerado por: {current_user.username}")
    
    # ==================== LINHA DE CORTE ====================
    # Linha tracejada no meio da folha
    p.setStrokeColor(colors.grey)
    p.setLineWidth(0.5)
    p.setDash(3, 3)
    p.line(0, half_height, width, half_height)
    
    # Texto "CORTE AQUI"
    p.setFont("Helvetica", 7)
    p.setFillColor(colors.grey)
    p.drawCentredString(width/2, half_height - 0.3*cm, "✂ CORTE AQUI ✂")
    
    # Finalizar PDF
    p.showPage()
    p.save()
    
    # Retornar PDF
    buffer.seek(0)
    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=vale_pallet_{vale.numero_documento}.pdf'
    
    return response
