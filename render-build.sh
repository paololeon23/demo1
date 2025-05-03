#!/bin/bash
# Script para instalar dependencias del sistema en Render
set -e  # Detiene el script si hay errores

echo "➡️ Actualizando paquetes del sistema..."
apt-get update -qq

echo "➡️ Instalando dependencias para PyMuPDF..."
apt-get install -y --no-install-recommends \
    libmupdf-dev \
    python3-dev \
    gcc

echo "➡️ Instalando Tesseract OCR..."
apt-get install -y tesseract-ocr

# Verificar que Tesseract está instalado correctamente
echo "➡️ Verificando instalación de Tesseract..."
tesseract --version

echo "✅ Todas las dependencias del sistema fueron instaladas correctamente."
