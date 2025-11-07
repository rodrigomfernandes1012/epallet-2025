#!/usr/bin/env python3
"""
Script para inicializar o banco de dados
Cria as tabelas e opcionalmente cria um usuário administrador
"""
import sys
from app import create_app, db
from app.models import User

def init_database():
    """Inicializa o banco de dados criando todas as tabelas"""
    app = create_app()
    
    with app.app_context():
        print("Criando tabelas no banco de dados...")
        db.drop_all()  # Remover tabelas antigas
        db.create_all()  # Criar novas tabelas
        print("✓ Tabelas criadas com sucesso!")
        
        # Verificar se já existe algum usuário
        user_count = User.query.count()
        
        if user_count == 0:
            print("\nNenhum usuário encontrado no banco de dados.")
            criar_admin = input("Deseja criar um usuário administrador? (s/n): ").lower()
            
            if criar_admin == 's':
                criar_usuario_admin()
        else:
            print(f"\n✓ Banco de dados já possui {user_count} usuário(s) cadastrado(s).")

def criar_usuario_admin():
    """Cria um usuário administrador"""
    app = create_app()
    
    with app.app_context():
        print("\n=== Criar Usuário Administrador ===")
        
        # Solicitar dados
        nome_completo = input("Nome Completo: ").strip()
        username = input("Nome de Usuário: ").strip()
        email = input("Email: ").strip()
        senha = input("Senha: ").strip()
        
        # Validar campos obrigatórios
        if not all([nome_completo, username, email, senha]):
            print("✗ Erro: Todos os campos são obrigatórios!")
            return
        
        # Verificar se usuário já existe
        if User.query.filter_by(username=username).first():
            print(f"✗ Erro: Usuário '{username}' já existe!")
            return
        
        if User.query.filter_by(email=email).first():
            print(f"✗ Erro: Email '{email}' já está cadastrado!")
            return
        
        # Criar usuário
        try:
            user = User(
                nome_completo=nome_completo,
                username=username,
                email=email
            )
            user.set_password(senha)
            
            db.session.add(user)
            db.session.commit()
            
            print(f"\n✓ Usuário '{username}' criado com sucesso!")
            print(f"  Nome: {nome_completo}")
            print(f"  Email: {email}")
            print(f"  Status: Ativo")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n✗ Erro ao criar usuário: {str(e)}")

def reset_database():
    """Remove todas as tabelas e recria o banco de dados"""
    app = create_app()
    
    with app.app_context():
        print("⚠️  ATENÇÃO: Esta ação irá APAGAR TODOS OS DADOS do banco!")
        confirmacao = input("Digite 'CONFIRMAR' para continuar: ")
        
        if confirmacao != 'CONFIRMAR':
            print("Operação cancelada.")
            return
        
        print("\nRemovendo tabelas existentes...")
        db.drop_all()
        print("✓ Tabelas removidas!")
        
        print("\nCriando novas tabelas...")
        db.create_all()
        print("✓ Tabelas criadas!")
        
        print("\nBanco de dados resetado com sucesso!")
        
        criar_admin = input("\nDeseja criar um usuário administrador? (s/n): ").lower()
        if criar_admin == 's':
            criar_usuario_admin()

def main():
    """Função principal"""
    if len(sys.argv) > 1:
        comando = sys.argv[1]
        
        if comando == 'init':
            init_database()
        elif comando == 'reset':
            reset_database()
        elif comando == 'create-admin':
            criar_usuario_admin()
        else:
            print(f"Comando desconhecido: {comando}")
            print_help()
    else:
        print_help()

def print_help():
    """Exibe ajuda sobre os comandos disponíveis"""
    print("""
Uso: python3 init_db.py [comando]

Comandos disponíveis:
  init          Inicializa o banco de dados (cria tabelas)
  reset         Remove e recria todas as tabelas (APAGA DADOS!)
  create-admin  Cria um novo usuário administrador

Exemplos:
  python3 init_db.py init
  python3 init_db.py create-admin
  python3 init_db.py reset
    """)

if __name__ == '__main__':
    main()
