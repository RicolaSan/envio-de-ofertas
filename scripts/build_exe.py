"""
Script para gerar um executável (.exe) do painel administrativo.

Uso:
    python scripts/build_exe.py

O .exe será gerado em: dist/AdminOfertas.exe
Copie para a raiz da pasta do projeto em cada computador.
Não precisa instalar Python nem Git nas máquinas.
"""

import subprocess
import os
import sys
import shutil

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(RAIZ)

print("=" * 60)
print("  🚀  Gerando executável do Painel Administrativo")
print("=" * 60)
print()

# 1. Instalar PyInstaller
print("📦  1. Instalando PyInstaller...")
subprocess.run(
    [sys.executable, "-m", "pip", "install", "pyinstaller"],
    check=True, capture_output=True,
)
print("     ✅ OK")
print()

# 2. Gerar .exe
print("🔧  2. Gerando .exe (pode levar alguns minutos)...")
subprocess.run(
    [
        sys.executable, "-m", "PyInstaller",
        "--onefile",                # Único .exe
        "--windowed",               # Sem console (roda invisível)
        "--name", "AdminOfertas",   # Nome do executável
        "--hidden-import", "PIL._tkinter_finder",
        "--hidden-import", "customtkinter",
        "--collect-all", "customtkinter",
        "--collect-all", "PIL",
        "admin/app.py",
    ],
    check=True,
)
print("     ✅ OK")
print()

# 3. Copiar .exe para a raiz do projeto
exe_origem = os.path.join(RAIZ, "dist", "AdminOfertas.exe")
exe_destino = os.path.join(RAIZ, "AdminOfertas.exe")
if os.path.isfile(exe_origem):
    shutil.copy2(exe_origem, exe_destino)
    print(f"📋  3. Copiado para: {exe_destino}")
    print()

# 4. Limpar pasta build
for pasta in ["build", "dist"]:
    caminho = os.path.join(RAIZ, pasta)
    if os.path.isdir(caminho):
        shutil.rmtree(caminho)
os.remove(os.path.join(RAIZ, "AdminOfertas.spec"))

# 5. Resumo
tamanho = os.path.getsize(exe_destino) / 1024 / 1024
print("=" * 60)
print("  ✅  EXECUTÁVEL CRIADO COM SUCESSO!")
print("=" * 60)
print()
print(f"  📍  {exe_destino}")
print(f"  📦  Tamanho: {tamanho:.1f} MB")
print()
print("  📋  Como distribuir na empresa:")
print()
print("  1. Copie a pasta envio_de_ofertas/ para cada computador")
print("     (pode ser por rede, pendrive ou nuvem)")
print()
print("  2. Pronto! Dê duplo clique em AdminOfertas.exe")
print()
print("  ✅  NÃO precisa instalar Python, Git ou nada!")
print()
