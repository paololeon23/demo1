#!/bin/bash
# Script para instalar dependencias del sistema en Render

set -e  # Detiene el script si hay errores

echo "➡️ Instalando dependencias para PyMuPDF..."
pip install --no-cache-dir PyMuPDF

echo "➡️ Instalando Tesseract OCR..."
# Instalar tesseract utilizando una versión precompilada o si es necesario, usar una instalación desde pip
pip install pytesseract

# Verificar que Tesseract está instalado correctamente
echo "➡️ Verificando instalación de Tesseract..."
python -c "import pytesseract; print(pytesseract.get_tesseract_version())"

echo "✅ Todas las dependencias de Python fueron instaladas correctamente."

