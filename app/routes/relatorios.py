from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from app.models import ValePallet, DevolucaoPallet, Empresa, TipoEmpresa, Motorista
from sqlalchemy import or_, and_
from app.utils.auditoria import log_acesso_tela

bp = Blueprint('relatorios', __name__, url_prefix='/relatorios')


@bp.route('/movimentacao')
@login_required
def movimentacao():
    """Relatório de movimentação de vales pallet e devoluções com filtros"""
    log_acesso_tela('relatorios', 'Relatório de Movimentação')
    
    # Obter filtros da query string
    filtro_tipo_relatorio = request.args.get('tipo_relatorio', 'vales')  # vales, devolucoes, consolidado
    filtro_tipo = request.args.get('tipo_empresa', '')
    filtro_empresa = request.args.get('empresa', '')
    filtro_motorista = request.args.get('motorista', '')
    filtro_documento = request.args.get('documento', '')
    filtro_status = request.args.get('status', '')
    
    vales = []
    devolucoes = []
    
    # Buscar Vales Pallet
    if filtro_tipo_relatorio in ['vales', 'consolidado']:
        query_vales = ValePallet.query
        
        # Aplicar filtros em vales
        if filtro_tipo:
            if filtro_tipo == 'cliente':
                query_vales = query_vales.join(ValePallet.cliente).join(Empresa.tipo_empresa).filter(
                    TipoEmpresa.nome == 'Cliente'
                )
            elif filtro_tipo == 'transportadora':
                query_vales = query_vales.join(ValePallet.transportadora).join(Empresa.tipo_empresa).filter(
                    TipoEmpresa.nome == 'Transportadora'
                )
            elif filtro_tipo == 'destinatario':
                query_vales = query_vales.join(ValePallet.destinatario).join(Empresa.tipo_empresa).filter(
                    TipoEmpresa.nome.in_(['Destinatário', 'Destinatario'])
                )
        
        if filtro_empresa:
            # Filtrar por nome de empresa
            empresas_filtradas = Empresa.query.filter(
                or_(
                    Empresa.razao_social.ilike(f'%{filtro_empresa}%'),
                    Empresa.nome_fantasia.ilike(f'%{filtro_empresa}%')
                )
            ).all()
            empresas_ids = [e.id for e in empresas_filtradas]
            
            if empresas_ids:
                query_vales = query_vales.filter(
                    or_(
                        ValePallet.cliente_id.in_(empresas_ids),
                        ValePallet.transportadora_id.in_(empresas_ids),
                        ValePallet.destinatario_id.in_(empresas_ids)
                    )
                )
        
        if filtro_motorista:
            query_vales = query_vales.join(ValePallet.motorista).filter(
                Motorista.nome.ilike(f'%{filtro_motorista}%')
            )
        
        if filtro_documento:
            query_vales = query_vales.filter(
                ValePallet.numero_documento.ilike(f'%{filtro_documento}%')
            )
        
        if filtro_status:
            query_vales = query_vales.filter(ValePallet.status == filtro_status)
        
        vales = query_vales.order_by(ValePallet.data_criacao.desc()).all()
    
    # Buscar Devoluções
    if filtro_tipo_relatorio in ['devolucoes', 'consolidado']:
        query_devolucoes = DevolucaoPallet.query
        
        # Aplicar filtros em devoluções
        if filtro_tipo:
            if filtro_tipo == 'cliente':
                query_devolucoes = query_devolucoes.join(DevolucaoPallet.cliente).join(Empresa.tipo_empresa).filter(
                    TipoEmpresa.nome == 'Cliente'
                )
            elif filtro_tipo == 'transportadora':
                query_devolucoes = query_devolucoes.join(DevolucaoPallet.transportadora).join(Empresa.tipo_empresa).filter(
                    TipoEmpresa.nome == 'Transportadora'
                )
            elif filtro_tipo == 'destinatario':
                query_devolucoes = query_devolucoes.join(DevolucaoPallet.destinatario).join(Empresa.tipo_empresa).filter(
                    TipoEmpresa.nome.in_(['Destinatário', 'Destinatario'])
                )
        
        if filtro_empresa:
            # Filtrar por nome de empresa
            empresas_filtradas = Empresa.query.filter(
                or_(
                    Empresa.razao_social.ilike(f'%{filtro_empresa}%'),
                    Empresa.nome_fantasia.ilike(f'%{filtro_empresa}%')
                )
            ).all()
            empresas_ids = [e.id for e in empresas_filtradas]
            
            if empresas_ids:
                query_devolucoes = query_devolucoes.filter(
                    or_(
                        DevolucaoPallet.cliente_id.in_(empresas_ids),
                        DevolucaoPallet.transportadora_id.in_(empresas_ids),
                        DevolucaoPallet.destinatario_id.in_(empresas_ids)
                    )
                )
        
        if filtro_motorista:
            query_devolucoes = query_devolucoes.join(DevolucaoPallet.motorista).filter(
                Motorista.nome.ilike(f'%{filtro_motorista}%')
            )
        
        if filtro_status:
            query_devolucoes = query_devolucoes.filter(DevolucaoPallet.status == filtro_status)
        
        devolucoes = query_devolucoes.order_by(DevolucaoPallet.criado_em.desc()).all()
    
    # Calcular totais
    total_vales = len(vales)
    total_pallets_vales = sum(vale.quantidade_pallets for vale in vales)
    total_devolucoes = len(devolucoes)
    total_pallets_devolucoes = sum(dev.quantidade_pallets for dev in devolucoes)
    
    # Buscar dados para os filtros
    tipos_empresa = TipoEmpresa.query.all()
    
    # Buscar empresas (todas as empresas que aparecem em vales ou devoluções)
    empresas_ids = set()
    for vale in ValePallet.query.all():
        if vale.cliente_id:
            empresas_ids.add(vale.cliente_id)
        if vale.transportadora_id:
            empresas_ids.add(vale.transportadora_id)
        if vale.destinatario_id:
            empresas_ids.add(vale.destinatario_id)
    
    for dev in DevolucaoPallet.query.all():
        if dev.cliente_id:
            empresas_ids.add(dev.cliente_id)
        if dev.transportadora_id:
            empresas_ids.add(dev.transportadora_id)
        if dev.destinatario_id:
            empresas_ids.add(dev.destinatario_id)
    
    empresas = Empresa.query.filter(Empresa.id.in_(empresas_ids)).order_by(Empresa.razao_social).all() if empresas_ids else []
    
    # Buscar motoristas que têm vales ou devoluções
    motoristas_ids = set()
    for vale in ValePallet.query.all():
        if vale.motorista_id:
            motoristas_ids.add(vale.motorista_id)
    for dev in DevolucaoPallet.query.all():
        if dev.motorista_id:
            motoristas_ids.add(dev.motorista_id)
    
    motoristas = Motorista.query.filter(Motorista.id.in_(motoristas_ids)).order_by(Motorista.nome).all() if motoristas_ids else []
    
    return render_template('relatorios/movimentacao.html',
                         filtro_tipo_relatorio=filtro_tipo_relatorio,
                         vales=vales,
                         devolucoes=devolucoes,
                         total_vales=total_vales,
                         total_pallets_vales=total_pallets_vales,
                         total_devolucoes=total_devolucoes,
                         total_pallets_devolucoes=total_pallets_devolucoes,
                         tipos_empresa=tipos_empresa,
                         empresas=empresas,
                         motoristas=motoristas,
                         filtro_tipo=filtro_tipo,
                         filtro_empresa=filtro_empresa,
                         filtro_motorista=filtro_motorista,
                         filtro_documento=filtro_documento,
                         filtro_status=filtro_status)
