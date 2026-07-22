@echo off
title Painel Administrativo - Ofertas
cd /d "%~dp0"
echo.
echo  🚀  Iniciando Painel Administrativo...
echo  📋  Ofertas do Mercado
echo.
.venv\Scripts\python.exe -m admin.app
if %errorlevel% neq 0 (
    echo.
    echo  ❌  Erro ao iniciar o painel.
    echo     Certifique-se de que o .venv esta configurado.
    pause
)
