#!/usr/bin/env python3
"""
Script para corrigir status de vales pallet antigos
"""
from app import create_app, db
from app.models import ValePallet

app = create_app()

with app.app_context():
    print("=" * 60)
    print("CORRIGINDO STATUS DE VALES PALLET")
    print("=" * 60)
    print()
    
    # Buscar vales sem status ou com status NULL
    vales_sem_status = ValePallet.query.filter(
        (ValePallet.status == None) | (ValePallet.status == '')
    ).all()
    
    if not vales_sem_status:
        print("✓ Todos os vales já possuem status definido!")
        print()
    else:
        print(f"Encontrados {len(vales_sem_status)} vales sem status")
        print()
        
        for vale in vales_sem_status:
            vale.status = 'pendente_entrega'
            print(f"✓ Vale {vale.numero_documento} (PIN: {vale.pin}) - Status atualizado para 'pendente_entrega'")
        
        db.session.commit()
        print()
        print(f"✓ {len(vales_sem_status)} vales atualizados com sucesso!")
        print()
    
    # Mostrar estatísticas
    print("-" * 60)
    print("ESTATÍSTICAS DE STATUS")
    print("-" * 60)
    
    pendentes = ValePallet.query.filter_by(status='pendente_entrega').count()
    realizadas = ValePallet.query.filter_by(status='entrega_realizada').count()
    concluidas = ValePallet.query.filter_by(status='entrega_concluida').count()
    cancelados = ValePallet.query.filter_by(status='cancelado').count()
    total = ValePallet.query.count()
    
    print(f"Pendente de Entrega:  {pendentes}")
    print(f"Entrega Realizada:    {realizadas}")
    print(f"Entrega Concluída:    {concluidas}")
    print(f"Cancelado:            {cancelados}")
    print(f"{'=' * 20}")
    print(f"Total:                {total}")
    print()
    print("=" * 60)
    print("CORREÇÃO CONCLUÍDA!")
    print("=" * 60)
