@echo off
title Gerando Executavel - Admin Ofertas
cd /d "%~dp0"

echo ============================================
echo    🚀  Gerando Executavel do Painel
echo    📋  Ofertas do Mercado
echo ============================================
echo.

:: Usar Python do .venv se existir
if exist ".venv\Scripts\python.exe" (
    set PYTHON=.venv\Scripts\python.exe
) else (
    set PYTHON=python
)

echo 📦  1. Instalando PyInstaller...
%PYTHON% -m pip install pyinstaller -q
echo     ✅ OK
echo.

echo 🔧  2. Gerando AdminOfertas.exe...
%PYTHON% -m PyInstaller --onefile --windowed --name AdminOfertas ^
    --hidden-import PIL._tkinter_finder ^
    --hidden-import customtkinter ^
    --collect-all customtkinter ^
    --collect-all PIL ^
    admin\app.py > NUL 2>&1

if %errorlevel% neq 0 (
    echo     ❌ Erro na geracao do executavel
    pause
    exit /b 1
)
echo     ✅ OK
echo.

:: Copiar para raiz
copy /Y dist\AdminOfertas.exe AdminOfertas.exe > NUL

:: Limpar
rmdir /S /Q build > NUL 2>&1
rmdir /S /Q dist > NUL 2>&1
del AdminOfertas.spec > NUL 2>&1

echo 📋  3. Executavel criado com sucesso!
echo.
echo     📍  %CD%\AdminOfertas.exe
echo.
echo ============================================
echo    ✅ PRONTO! Arquivo gerado com sucesso!
echo ============================================
echo.
echo  Agora copie a pasta envio_de_ofertas/
echo  para os outros computadores.
echo.
pause
