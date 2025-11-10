#!/usr/bin/env python3
"""
Script principal para executar a aplicação Flask
"""
import os

# Configurar PyMySQL para funcionar como MySQLdb
# Necessário para usar PyMySQL no lugar de mysqlclient
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass  # PyMySQL não instalado, usar mysqlclient se disponível

from app import create_app

# Criar a aplicação
app = create_app()

if __name__ == '__main__':
    # Configurações para desenvolvimento
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    print(f"""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║          Sistema de Gestão - Argon Dashboard            ║
    ║                                                          ║
    ║  Servidor rodando em: http://{host}:{port}           ║
    ║  Modo: {'Desenvolvimento' if debug else 'Produção'}                                     ║
    ║                                                          ║
    ║  Pressione CTRL+C para parar o servidor                 ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    app.run(host=host, port=port, debug=debug)
