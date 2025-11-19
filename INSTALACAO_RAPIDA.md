# 🚀 Instalação Rápida - Sistema de QR Code v51

## ❌ Erro: ModuleNotFoundError: No module named 'reportlab'

**Causa:** Faltam as bibliotecas necessárias para gerar PDF e QR Code.

---

## ✅ Solução Rápida (Windows)

### Opção 1: Script Automático (RECOMENDADO)

1. **Baixar:** `instalar_dependencias.bat`
2. **Executar:** Duplo clique no arquivo
3. **Aguardar:** Instalação automática
4. **Pronto!** Reiniciar o sistema

### Opção 2: Manual (Linha de Comando)

**Abrir CMD como Administrador:**

```cmd
cd C:\TaxiDigital\PROJETOS_PYTHON\flask-argon-system
env\Scripts\activate
pip install reportlab qrcode[pil]
```

**Reiniciar o sistema:**
```cmd
# Parar o servidor (Ctrl+C)
python run.py
```

---

## ✅ Solução para Linux

```bash
cd /root/epallet-2025
source venv/bin/activate  # ou env/bin/activate
pip install reportlab qrcode[pil]
sudo systemctl restart epallet
```

---

## 📦 Bibliotecas Instaladas

Após a instalação, você terá:

- ✅ **reportlab** - Geração de PDF profissional
- ✅ **qrcode[pil]** - Geração de QR Code com imagens
- ✅ **Pillow** - Processamento de imagens (instalado automaticamente)

---

## 🧪 Testar Instalação

**Verificar bibliotecas:**

```cmd
cd C:\TaxiDigital\PROJETOS_PYTHON\flask-argon-system
env\Scripts\activate
pip list | findstr reportlab
pip list | findstr qrcode
```

**Deve mostrar:**
```
qrcode         8.2
reportlab      4.2.5
```

---

## ✅ Após Instalação

1. **Reiniciar** o servidor Flask
2. **Acessar** Vale Pallet > Visualizar
3. **Clicar** em "Imprimir PDF"
4. **Verificar** se o PDF é gerado com QR Code

---

## ⚠️ Problemas Comuns

### Erro: pip não encontrado

**Solução:**
```cmd
cd C:\TaxiDigital\PROJETOS_PYTHON\flask-argon-system
env\Scripts\activate
python -m pip install --upgrade pip
pip install reportlab qrcode[pil]
```

### Erro: Permission denied

**Solução:**
- Executar CMD como **Administrador**
- Ou usar: `pip install --user reportlab qrcode[pil]`

### Erro: No matching distribution found

**Solução:**
```cmd
pip install --upgrade pip setuptools wheel
pip install reportlab qrcode[pil]
```

---

## 📝 Resumo

**Passo a Passo:**

1. ✅ Baixar: `instalar_dependencias.bat`
2. ✅ Executar: Duplo clique
3. ✅ Aguardar: Instalação
4. ✅ Reiniciar: `python run.py`
5. ✅ Testar: Imprimir PDF

**Tempo estimado:** 2-3 minutos

---

**Versão:** v51  
**Data:** 12/11/2024

🚀 **Instalação simples e rápida!**

Qualquer dúvida, me avise!
