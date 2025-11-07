#!/usr/bin/env python3
"""
Script para popular os tipos de empresa padrão
"""
from app import create_app, db
from app.models import TipoEmpresa

def popular_tipos():
    """Popula os tipos de empresa padrão"""
    app = create_app()
    
    with app.app_context():
        # Tipos padrão
        tipos_padrao = [
            {
                'nome': 'Cliente',
                'descricao': 'Empresas clientes que solicitam o transporte de pallets',
                'ativo': True
            },
            {
                'nome': 'Transportadora',
                'descricao': 'Empresas responsáveis pelo transporte de pallets',
                'ativo': True
            },
            {
                'nome': 'Destinatário',
                'descricao': 'Empresas que recebem os pallets transportados',
                'ativo': True
            }
        ]
        
        print("Populando tipos de empresa...")
        
        for tipo_data in tipos_padrao:
            # Verificar se já existe
            tipo_existente = TipoEmpresa.query.filter_by(nome=tipo_data['nome']).first()
            
            if tipo_existente:
                print(f"  ✓ Tipo '{tipo_data['nome']}' já existe")
            else:
                tipo = TipoEmpresa(**tipo_data)
                db.session.add(tipo)
                print(f"  + Tipo '{tipo_data['nome']}' criado")
        
        db.session.commit()
        print("\n✓ Tipos de empresa populados com sucesso!")

if __name__ == '__main__':
    popular_tipos()
