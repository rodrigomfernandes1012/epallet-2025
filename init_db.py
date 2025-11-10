#!/usr/bin/env python3
"""
Script para inicializar o banco de dados
"""
import os
import sys

# Configurar PyMySQL ANTES de importar o app
try:
    import pymysql

    pymysql.install_as_MySQLdb()
except ImportError:
    print("ERRO: PyMySQL não instalado. Execute: pip install PyMySQL")
    sys.exit(1)

from app import create_app, db
from app.models import User, TipoEmpresa
from getpass import getpass


def criar_usuario_admin():
    """Cria um usuário administrador"""
    app = create_app()

    with app.app_context():
        print("\n=== Criar Usuário Administrador ===\n")

        username = input("Username: ").strip()
        if not username:
            print("Username não pode ser vazio!")
            return

        # Verificar se já existe
        if User.query.filter_by(username=username).first():
            print(f"Erro: Usuário '{username}' já existe!")
            return

        email = input("Email: ").strip()
        if not email:
            print("Email não pode ser vazio!")
            return

        # Verificar se email já existe
        if User.query.filter_by(email=email).first():
            print(f"Erro: Email '{email}' já está em uso!")
            return

        senha = getpass("Senha: ")
        if not senha:
            print("Senha não pode ser vazia!")
            return

        senha_confirmacao = getpass("Confirme a senha: ")
        if senha != senha_confirmacao:
            print("Erro: As senhas não coincidem!")
            return

        nome_completo = input("Nome completo: ").strip()
        if not nome_completo:
            print("Nome completo não pode ser vazio!")
            return

        # Criar usuário
        user = User(
            username=username,
            email=email,
            nome_completo=nome_completo,
            ativo=True
        )
        user.set_password(senha)

        try:
            db.session.add(user)
            db.session.commit()
            print(f"\n✓ Usuário '{username}' criado com sucesso!")
            print(f"  Email: {email}")
            print(f"  Nome: {nome_completo}")
        except Exception as e:
            db.session.rollback()
            print(f"\nErro ao criar usuário: {str(e)}")


def inicializar_banco():
    """Inicializa o banco de dados"""
    app = create_app()

    with app.app_context():
        print("\n=== Inicializando Banco de Dados ===\n")

        try:
            db.create_all()
            print("✓ Tabelas criadas com sucesso!")
        except Exception as e:
            print(f"Erro ao criar tabelas: {str(e)}")
            return

        # Verificar se tipos de empresa já existem
        if TipoEmpresa.query.count() == 0:
            print("\nCriando tipos de empresa padrão...")
            tipos = [
                TipoEmpresa(nome='Cliente', descricao='Empresa que envia pallets', ativo=True),
                TipoEmpresa(nome='Transportadora', descricao='Empresa responsável pelo transporte', ativo=True),
                TipoEmpresa(nome='Destinatário', descricao='Empresa que recebe pallets', ativo=True)
            ]

            try:
                for tipo in tipos:
                    db.session.add(tipo)
                db.session.commit()
                print("✓ Tipos de empresa criados com sucesso!")
            except Exception as e:
                db.session.rollback()
                print(f"Erro ao criar tipos de empresa: {str(e)}")
        else:
            print("Tipos de empresa já existem, pulando...")


def resetar_banco():
    """Remove e recria todas as tabelas (APAGA DADOS!)"""
    app = create_app()

    with app.app_context():
        print("\n⚠️  ATENÇÃO: Esta operação irá APAGAR TODOS OS DADOS! ⚠️")
        confirmacao = input("Digite 'CONFIRMAR' para continuar: ")

        if confirmacao != 'CONFIRMAR':
            print("Operação cancelada.")
            return

        print("\nRemovendo tabelas...")
        db.drop_all()
        print("✓ Tabelas removidas")

        print("\nCriando tabelas...")
        db.create_all()
        print("✓ Tabelas criadas")

        print("\nBanco de dados resetado com sucesso!")


def main():
    """Função principal"""
    if len(sys.argv) < 2:
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
        sys.exit(1)

    comando = sys.argv[1].lower()

    if comando == 'init':
        inicializar_banco()
    elif comando == 'create-admin':
        criar_usuario_admin()
    elif comando == 'reset':
        resetar_banco()
    else:
        print(f"Comando desconhecido: {comando}")
        print("Use: init, create-admin ou reset")
        sys.exit(1)


if __name__ == '__main__':
    main()
