#!/bin/bash
# Script para instalar dependencias del sistema en Render
set -e  # Detiene el script si hay errores

echo "➡️ Actualizando paquetes del sistema..."
sudo apt-get update -qq

echo "➡️ Instalando dependencias para PyMuPDF..."
sudo apt-get install -y --no-install-recommends \
    libmupdf-dev \
    python3-dev \
    gcc

echo "✅ Dependencias instaladas correctamente"