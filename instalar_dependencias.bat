@echo off
echo ========================================
echo Instalando dependencias para QR Code
echo ========================================
echo.

cd C:\TaxiDigital\PROJETOS_PYTHON\flask-argon-system

echo Ativando ambiente virtual...
call env\Scripts\activate

echo.
echo Instalando reportlab (geracao de PDF)...
pip install reportlab

echo.
echo Instalando qrcode (geracao de QR Code)...
pip install qrcode[pil]

echo.
echo ========================================
echo Instalacao concluida!
echo ========================================
echo.
echo Agora voce pode usar o sistema normalmente.
echo Pressione qualquer tecla para fechar...
pause > nul
