"""
Configuração do Gunicorn para produção
"""
import multiprocessing
import os

# Endereço e porta
bind = "127.0.0.1:8000"

# Número de workers
# Fórmula recomendada: (2 x CPU cores) + 1
workers = multiprocessing.cpu_count() * 2 + 1

# Tipo de worker
worker_class = "sync"

# Threads por worker
threads = 2

# Timeout para requisições (segundos)
timeout = 120

# Timeout para workers inativos (segundos)
graceful_timeout = 30

# Número máximo de requisições por worker antes de reiniciar
max_requests = 1000
max_requests_jitter = 50

# Logs
accesslog = os.environ.get('GUNICORN_ACCESS_LOG', '/var/log/gunicorn/access.log')
errorlog = os.environ.get('GUNICORN_ERROR_LOG', '/var/log/gunicorn/error.log')
loglevel = os.environ.get('GUNICORN_LOG_LEVEL', 'info')

# Formato do log de acesso
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Processo daemon (False para systemd)
daemon = False

# PID file
pidfile = '/tmp/gunicorn.pid'

# Usuário e grupo (descomente se necessário)
# user = 'www-data'
# group = 'www-data'

# Diretório temporário
tmp_upload_dir = None

# Preload da aplicação
preload_app = True

# Recarregar quando o código mudar (apenas desenvolvimento)
reload = os.environ.get('FLASK_ENV', 'production') == 'development'

# Callbacks para eventos
def on_starting(server):
    """Executado quando o servidor está iniciando"""
    print("Gunicorn está iniciando...")

def on_reload(server):
    """Executado quando o servidor recarrega"""
    print("Gunicorn está recarregando...")

def when_ready(server):
    """Executado quando o servidor está pronto"""
    print(f"Gunicorn está pronto! Workers: {workers}")

def on_exit(server):
    """Executado quando o servidor está encerrando"""
    print("Gunicorn está encerrando...")
