#!/usr/bin/env python3
"""
Script de Migração do Banco de Dados
Adiciona coluna motorista_id na tabela vales_pallet
"""
import os
import sys
from sqlalchemy import create_engine, text, inspect
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def migrate_database():
    """
    Adiciona a coluna motorista_id na tabela vales_pallet
    """
    # Obter URL do banco de dados
    database_url = os.getenv('DATABASE_URL', 'sqlite:///app.db')
    
    print("=" * 60)
    print("MIGRAÇÃO DO BANCO DE DADOS")
    print("=" * 60)
    print(f"Banco de dados: {database_url}")
    print()
    
    try:
        # Criar engine
        engine = create_engine(database_url)
        
        # Verificar se a tabela existe
        inspector = inspect(engine)
        if 'vales_pallet' not in inspector.get_table_names():
            print("❌ Erro: Tabela 'vales_pallet' não encontrada!")
            print("Execute primeiro: python init_db.py init")
            return False
        
        # Verificar se a coluna já existe
        columns = [col['name'] for col in inspector.get_columns('vales_pallet')]
        
        if 'motorista_id' in columns:
            print("✅ Coluna 'motorista_id' já existe na tabela 'vales_pallet'")
            print("Nenhuma migração necessária.")
            return True
        
        print("📝 Adicionando coluna 'motorista_id' na tabela 'vales_pallet'...")
        
        # Executar migração
        with engine.connect() as conn:
            # SQLite
            if 'sqlite' in database_url:
                conn.execute(text("""
                    ALTER TABLE vales_pallet 
                    ADD COLUMN motorista_id INTEGER
                """))
                conn.commit()
            
            # PostgreSQL
            elif 'postgresql' in database_url:
                conn.execute(text("""
                    ALTER TABLE vales_pallet 
                    ADD COLUMN motorista_id INTEGER REFERENCES motoristas(id)
                """))
                conn.commit()
            
            else:
                print(f"❌ Tipo de banco de dados não suportado: {database_url}")
                return False
        
        print("✅ Migração concluída com sucesso!")
        print()
        print("Coluna 'motorista_id' adicionada na tabela 'vales_pallet'")
        print("Seus dados existentes foram preservados.")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao migrar banco de dados: {str(e)}")
        return False


if __name__ == '__main__':
    print()
    success = migrate_database()
    print("=" * 60)
    
    if success:
        print("✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
        print()
        print("Você pode agora:")
        print("1. Executar o sistema: python run.py")
        print("2. Criar vales pallet com motoristas")
        print()
        sys.exit(0)
    else:
        print("❌ MIGRAÇÃO FALHOU!")
        print()
        print("Verifique os erros acima e tente novamente.")
        print()
        sys.exit(1)
