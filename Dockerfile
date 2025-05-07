FROM python:3.10-slim

# Instala Tesseract (versión Linux)
RUN apt-get update && apt-get install -y tesseract-ocr

# Crea carpeta app
WORKDIR /app

# Copia todo el contenido del proyecto
COPY . .

# Instala librerías Python
RUN pip install --no-cache-dir -r requirements.txt

# Expone puerto si usas Flask o FastAPI
EXPOSE 5000

# Comando para ejecutar tu app
CMD ["python", "extraer_texto.py"]
