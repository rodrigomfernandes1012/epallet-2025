#!/usr/bin/env python3
"""
Script de Migração: SQLite para MySQL
Migra dados do banco SQLite para MySQL

Uso:
    python migrate_sqlite_to_mysql.py

Pré-requisitos:
    1. MySQL instalado e rodando
    2. Banco de dados MySQL criado
    3. Usuário MySQL com permissões
    4. Arquivo .env configurado com DATABASE_URL do MySQL
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def migrate_sqlite_to_mysql(sqlite_path, mysql_url):
    """
    Migra dados do SQLite para MySQL
    
    Args:
        sqlite_path: Caminho para o arquivo SQLite
        mysql_url: URL de conexão do MySQL
    """
    print("=" * 60)
    print("MIGRAÇÃO: SQLite → MySQL")
    print("=" * 60)
    
    # Verificar se arquivo SQLite existe
    if not os.path.exists(sqlite_path):
        print(f"❌ Erro: Arquivo SQLite não encontrado: {sqlite_path}")
        return False
    
    print(f"\n📂 SQLite: {sqlite_path}")
    print(f"🔗 MySQL: {mysql_url.replace(mysql_url.split('@')[0].split('//')[1], '***')}")
    
    try:
        # Conectar ao SQLite
        print("\n1️⃣ Conectando ao SQLite...")
        sqlite_engine = create_engine(f'sqlite:///{sqlite_path}')
        SQLiteSession = sessionmaker(bind=sqlite_engine)
        sqlite_session = SQLiteSession()
        print("   ✅ Conectado ao SQLite")
        
        # Conectar ao MySQL
        print("\n2️⃣ Conectando ao MySQL...")
        mysql_engine = create_engine(mysql_url)
        MySQLSession = sessionmaker(bind=mysql_engine)
        mysql_session = MySQLSession()
        print("   ✅ Conectado ao MySQL")
        
        # Obter lista de tabelas do SQLite
        print("\n3️⃣ Obtendo lista de tabelas...")
        tables_result = sqlite_session.execute(text(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        ))
        tables = [row[0] for row in tables_result]
        print(f"   ✅ Encontradas {len(tables)} tabelas: {', '.join(tables)}")
        
        # Migrar cada tabela
        print("\n4️⃣ Migrando dados...")
        total_rows = 0
        
        for table in tables:
            print(f"\n   📋 Tabela: {table}")
            
            # Contar registros
            count_result = sqlite_session.execute(text(f"SELECT COUNT(*) FROM {table}"))
            count = count_result.scalar()
            print(f"      Registros: {count}")
            
            if count == 0:
                print("      ⏭️  Vazia, pulando...")
                continue
            
            # Obter dados do SQLite
            data_result = sqlite_session.execute(text(f"SELECT * FROM {table}"))
            rows = data_result.fetchall()
            columns = data_result.keys()
            
            # Limpar tabela MySQL (se existir)
            try:
                mysql_session.execute(text(f"DELETE FROM {table}"))
                mysql_session.commit()
                print(f"      🗑️  Tabela MySQL limpa")
            except Exception as e:
                print(f"      ⚠️  Aviso ao limpar tabela: {str(e)}")
            
            # Inserir dados no MySQL
            inserted = 0
            for row in rows:
                try:
                    # Preparar valores
                    values = []
                    for value in row:
                        if value is None:
                            values.append('NULL')
                        elif isinstance(value, str):
                            # Escapar aspas simples
                            escaped = value.replace("'", "''")
                            values.append(f"'{escaped}'")
                        elif isinstance(value, (int, float)):
                            values.append(str(value))
                        else:
                            values.append(f"'{str(value)}'")
                    
                    # Montar query
                    columns_str = ', '.join([f'`{col}`' for col in columns])
                    values_str = ', '.join(values)
                    query = f"INSERT INTO {table} ({columns_str}) VALUES ({values_str})"
                    
                    # Executar
                    mysql_session.execute(text(query))
                    inserted += 1
                    
                except Exception as e:
                    print(f"      ❌ Erro ao inserir registro: {str(e)}")
                    continue
            
            # Commit
            mysql_session.commit()
            total_rows += inserted
            print(f"      ✅ Inseridos: {inserted}/{count}")
        
        # Fechar conexões
        sqlite_session.close()
        mysql_session.close()
        
        print("\n" + "=" * 60)
        print(f"✅ MIGRAÇÃO CONCLUÍDA!")
        print(f"📊 Total de registros migrados: {total_rows}")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO NA MIGRAÇÃO: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Função principal"""
    print("\n🔄 MIGRAÇÃO DE DADOS: SQLite → MySQL\n")
    
    # Verificar argumentos
    if len(sys.argv) > 1:
        sqlite_path = sys.argv[1]
    else:
        # Usar caminho padrão
        sqlite_path = input("Caminho do arquivo SQLite [instance/epallet.db]: ").strip()
        if not sqlite_path:
            sqlite_path = "instance/epallet.db"
    
    if len(sys.argv) > 2:
        mysql_url = sys.argv[2]
    else:
        # Ler do .env
        from dotenv import load_dotenv
        load_dotenv()
        mysql_url = os.getenv('DATABASE_URL')
        
        if not mysql_url or not mysql_url.startswith('mysql'):
            print("❌ Erro: DATABASE_URL não configurado ou não é MySQL")
            print("   Configure no .env: DATABASE_URL=mysql://user:pass@localhost:3306/dbname")
            return
    
    # Confirmar migração
    print(f"\n⚠️  ATENÇÃO:")
    print(f"   - SQLite: {sqlite_path}")
    print(f"   - MySQL: {mysql_url.split('@')[1] if '@' in mysql_url else mysql_url}")
    print(f"\n   Esta operação irá:")
    print(f"   1. Limpar todas as tabelas do MySQL")
    print(f"   2. Copiar todos os dados do SQLite para o MySQL")
    
    confirm = input("\n   Deseja continuar? (digite 'sim' para confirmar): ").strip().lower()
    
    if confirm != 'sim':
        print("\n❌ Migração cancelada pelo usuário.")
        return
    
    # Executar migração
    success = migrate_sqlite_to_mysql(sqlite_path, mysql_url)
    
    if success:
        print("\n✅ Migração concluída com sucesso!")
        print("\n📝 Próximos passos:")
        print("   1. Verificar dados no MySQL")
        print("   2. Fazer backup do SQLite (já não é mais usado)")
        print("   3. Reiniciar aplicação: systemctl restart epallet")
    else:
        print("\n❌ Migração falhou. Verifique os erros acima.")


if __name__ == '__main__':
    main()
