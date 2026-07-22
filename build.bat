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
if %errorlevel% neq 0 (
    echo     ❌ Erro ao instalar PyInstaller
    pause
    exit /b 1
)
echo     ✅ OK
echo.

echo 🔧  2. Gerando AdminOfertas.exe...
echo     (Isso pode levar ate 5 minutos. Aguarde...)
echo.

%PYTHON% -m PyInstaller --onefile --windowed --name AdminOfertas --hidden-import PIL._tkinter_finder --hidden-import customtkinter --collect-all customtkinter --collect-all PIL admin\app.py

if %errorlevel% neq 0 (
    echo     ❌ Erro na geracao do executavel
    pause
    exit /b 1
)
echo     ✅ OK
echo.

:: Copiar para raiz
copy /Y dist\AdminOfertas.exe AdminOfertas.exe

:: Limpar
rmdir /S /Q build
rmdir /S /Q dist
del AdminOfertas.spec

echo.
echo 📋  3. Executavel criado com sucesso!
echo     📍  %CD%\AdminOfertas.exe
echo.
echo ============================================
echo    ✅ PRONTO!
echo ============================================
echo.
echo  Agora copie a pasta envio_de_ofertas/
echo  para os outros computadores da empresa.
echo  Cada um pode dar duplo clique no AdminOfertas.exe
echo.
echo  Nao precisa instalar Python nem Git!
echo.
pause
