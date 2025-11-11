from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from app.models import ValePallet, Empresa, TipoEmpresa, Motorista
from sqlalchemy import or_, and_
from app.utils.auditoria import log_acesso_tela

bp = Blueprint('relatorios', __name__, url_prefix='/relatorios')


@bp.route('/movimentacao')
@login_required
def movimentacao():
    """Relatório de movimentação de vales pallet com filtros"""
    log_acesso_tela('relatorios', 'Relatório de Movimentação')
    
    # Obter filtros da query string
    filtro_tipo = request.args.get('tipo_empresa', '')
    filtro_empresa = request.args.get('empresa', '')
    filtro_motorista = request.args.get('motorista', '')
    filtro_documento = request.args.get('documento', '')
    
    # Query base de vales
    query = ValePallet.query
    
    # Aplicar filtros
    if filtro_tipo:
        # Filtrar por tipo de empresa (cliente, transportadora ou destinatário)
        if filtro_tipo == 'cliente':
            query = query.join(ValePallet.cliente).join(Empresa.tipo_empresa).filter(
                TipoEmpresa.nome == 'Cliente'
            )
        elif filtro_tipo == 'transportadora':
            query = query.join(ValePallet.transportadora).join(Empresa.tipo_empresa).filter(
                TipoEmpresa.nome == 'Transportadora'
            )
        elif filtro_tipo == 'destinatario':
            query = query.join(ValePallet.destinatario).join(Empresa.tipo_empresa).filter(
                TipoEmpresa.nome.in_(['Destinatário', 'Destinatario'])
            )
    
    if filtro_empresa:
        # Filtrar por nome de empresa (busca em cliente, transportadora ou destinatário)
        query = query.join(ValePallet.cliente, isouter=True).join(
            ValePallet.transportadora, isouter=True
        ).join(ValePallet.destinatario, isouter=True).filter(
            or_(
                Empresa.razao_social.ilike(f'%{filtro_empresa}%'),
                Empresa.nome_fantasia.ilike(f'%{filtro_empresa}%')
            )
        )
    
    if filtro_motorista:
        # Filtrar por nome do motorista
        query = query.join(ValePallet.motorista).filter(
            Motorista.nome.ilike(f'%{filtro_motorista}%')
        )
    
    if filtro_documento:
        # Filtrar por número do documento
        query = query.filter(
            ValePallet.numero_documento.ilike(f'%{filtro_documento}%')
        )
    
    # Ordenar por data de criação (mais recente primeiro)
    vales = query.order_by(ValePallet.data_criacao.desc()).all()
    
    # Calcular totais
    total_vales = len(vales)
    total_pallets = sum(vale.quantidade_pallets for vale in vales)
    
    # Buscar dados para os filtros
    tipos_empresa = TipoEmpresa.query.all()
    
    # Buscar empresas (todas as empresas que aparecem em vales)
    empresas_ids = set()
    for vale in ValePallet.query.all():
        if vale.cliente_id:
            empresas_ids.add(vale.cliente_id)
        if vale.transportadora_id:
            empresas_ids.add(vale.transportadora_id)
        if vale.destinatario_id:
            empresas_ids.add(vale.destinatario_id)
    
    empresas = Empresa.query.filter(Empresa.id.in_(empresas_ids)).order_by(Empresa.razao_social).all() if empresas_ids else []
    
    # Buscar motoristas que têm vales
    motoristas_ids = set(vale.motorista_id for vale in ValePallet.query.all() if vale.motorista_id)
    motoristas = Motorista.query.filter(Motorista.id.in_(motoristas_ids)).order_by(Motorista.nome).all() if motoristas_ids else []
    
    return render_template('relatorios/movimentacao.html',
                         vales=vales,
                         total_vales=total_vales,
                         total_pallets=total_pallets,
                         tipos_empresa=tipos_empresa,
                         empresas=empresas,
                         motoristas=motoristas,
                         filtro_tipo=filtro_tipo,
                         filtro_empresa=filtro_empresa,
                         filtro_motorista=filtro_motorista,
                         filtro_documento=filtro_documento)
