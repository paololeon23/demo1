FROM python:3.10-slim

# 1. Configuración inicial del sistema
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    software-properties-common \
    wget && \
    apt-add-repository non-free && \
    apt-get update

# 2. Instalación de todas las dependencias (con fuentes alternativas para poppler)
RUN apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-spa \
    tesseract-ocr-eng \
    libgl1-mesa-glx \
    poppler-utils \ 
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 3. Configuración garantizada de Tesseract
RUN mkdir -p /usr/share/tesseract-ocr/tessdata && \
    (cp /usr/share/tesseract-ocr/*/tessdata/* /usr/share/tesseract-ocr/tessdata/ 2>/dev/null || true)

WORKDIR /app
COPY . .

# 4. Instalación de Python
RUN pip install --no-cache-dir -r requirements.txt

# 5. Verificación
RUN echo "Dependencias instaladas:" && \
    tesseract --version && \
    pdftoppm -v && \
    tesseract --list-langs

EXPOSE 5000
CMD ["python", "extraer_texto.py"]