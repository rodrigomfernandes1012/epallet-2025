import secrets

secret_key = secrets.token_urlsafe(50)  # gera uma string aleatória segura
print(f"SECRET_KEY='{secret_key}'")
