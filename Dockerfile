# Usamos una imagen base de Python
FROM python:3.8-slim

# Instalamos las dependencias necesarias, incluyendo Tesseract
RUN apt-get update && \
    apt-get install -y tesseract-ocr && \
    apt-get install -y libpq-dev

# Copiamos el archivo requirements.txt (si lo tienes) al contenedor
COPY requirements.txt .

# Instalamos las dependencias de Python
RUN pip install -r requirements.txt

# Copiamos todo el código fuente al contenedor
COPY . /app

# Establecemos el directorio de trabajo dentro del contenedor
WORKDIR /app

# Comando para ejecutar la aplicación (ajustalo si el nombre de tu archivo es otro)
CMD ["python", "extraer_texto.py"]
