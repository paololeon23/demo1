import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
from flask import Flask, request, send_file, jsonify
import os
import uuid
from werkzeug.utils import secure_filename

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

app = Flask(__name__)

# Configuración para archivos subidos
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB máximo

# Crear carpeta de uploads si no existe
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convertir_pdf_escaneado_a_ocr(pdf_path):
    """
    Convierte un PDF escaneado (imagen) a un PDF OCR (texto buscable) en memoria.
    Devuelve los bytes del PDF resultante.
    """
    try:
        doc_original = fitz.open(pdf_path)
        doc_ocr = fitz.open()  # Nuevo documento PDF OCR en memoria

        for pagina in doc_original:
            pix = pagina.get_pixmap(dpi=300)  # Exportar imagen de la página a alta resolución
            img = Image.open(io.BytesIO(pix.tobytes("png")))

            # Crear nueva página con el mismo tamaño
            nueva_pagina = doc_ocr.new_page(width=pix.width, height=pix.height)
            nueva_pagina.insert_image(fitz.Rect(0, 0, pix.width, pix.height), stream=pix.tobytes("png"))

            # Obtener datos OCR con posición
            config = r'--oem 3 --psm 6 -l spa+eng --dpi 300'
            data = pytesseract.image_to_data(img, config=config, output_type=pytesseract.Output.DICT)

            # Insertar texto OCR invisible en la página (solo para búsqueda)
            for i in range(len(data['text'])):
                try:
                    # Convertir confianza a entero
                    confianza = int(float(data['conf'][i]))
                    if confianza > 60:  # Solo texto con una alta confianza
                        texto = data['text'][i].strip()
                        if texto:
                            # Convertir coordenadas a float primero, luego redondear si es necesario
                            x = float(data['left'][i])
                            y = float(data['top'][i])
                            w = float(data['width'][i])
                            h = float(data['height'][i])
                            
                            # Crear rectángulo con las coordenadas
                            rect = fitz.Rect(x, y, x + w, y + h)
                            
                            # Insertar texto en la capa OCR
                            nueva_pagina.insert_text(
                                rect.tl, 
                                texto, 
                                fontsize=round(h),  # Redondear el tamaño de fuente
                                color=(0, 0, 0), 
                                render_mode=3
                            )
                except (ValueError, TypeError) as e:
                    print(f"Advertencia: Error procesando bloque de texto {i}: {str(e)}")
                    continue

        # Guardar nuevo PDF OCR en un buffer de memoria
        pdf_bytes = doc_ocr.write()
        doc_original.close()
        doc_ocr.close()
        
        return True, pdf_bytes
    except Exception as e:
        return False, f"Error al procesar PDF: {str(e)}"

# Ruta raíz para comprobar si el servidor Flask está funcionando
@app.route('/')
def home():
    return "¡Servidor Flask en Docker funcionando correctamente!"

@app.route('/convert-to-ocr', methods=['POST'])
def upload_file():

    print('---------------- archivo ------------')
    print(request.files)  # Esto imprimirá todo lo que se recibe en request.files
    # Verificar si se envió un archivo
    if 'prueba' not in request.files:
        return jsonify({'error': 'No se encontró el archivo en la solicitud'}), 400
    
    file = request.files['prueba']
    
    # Verificar si se seleccionó un archivo
    if file.filename == '':
        return jsonify({'error': 'No se seleccionó ningún archivo'}), 400
    
    # Verificar extensión permitida
    if not allowed_file(file.filename):
        return jsonify({'error': 'Tipo de archivo no permitido. Solo se aceptan PDFs'}), 400
    
    # Generar nombre único para el archivo temporal
    unique_id = str(uuid.uuid4())
    original_filename = secure_filename(file.filename)
    upload_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{unique_id}_{original_filename}")
    
    try:
        file.save(upload_path)
        success, result = convertir_pdf_escaneado_a_ocr(upload_path)
        
        if not success:
            return jsonify({'error': result}), 500
        
        # Convertir a formato Buffer simplificado
        hex_start = ' '.join(f"{byte:02x}" for byte in result[:20])  # Primeros 20 bytes
        total_bytes = len(result)
        buffer_repr = f"<Buffer {hex_start} ... {total_bytes - 20} more bytes>"
        
        # Crear un objeto BytesIO para enviar el PDF
        pdf_io = io.BytesIO(result)
        pdf_io.seek(0)
        
        return jsonify({
            'success': True,
            'buffer': buffer_repr,
            'size_bytes': total_bytes,
        })
        
    except Exception as e:
        return jsonify({'error': f"Error en el servidor: {str(e)}"}), 500
    finally:
        if os.path.exists(upload_path):
            os.remove(upload_path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)