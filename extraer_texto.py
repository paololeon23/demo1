import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
from flask import Flask, request, jsonify
import os
import uuid
from werkzeug.utils import secure_filename
from typing import Union

# Configura Tesseract OCR (ajusta la ruta según tu sistema)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

app = Flask(__name__)

# Configuración
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

class Buffer:
    def __init__(self, data: bytes):
        self._data = bytes(data)

    def toJSON(self):
        return {
            "type": "Buffer",
            "data": list(self._data)
        }

    def __repr__(self):
        hex_part = ' '.join(f'{b:02x}' for b in self._data[:50])
        suffix = f' ... {len(self._data) - 50} more bytes' if len(self._data) > 50 else ''
        return f'<Buffer {hex_part}{suffix}>'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convertir_pdf_a_ocr(pdf_path: str) -> Union[bool, bytes]:
    """Convierte un PDF escaneado a PDF con OCR (texto buscable)."""
    try:
        doc_original = fitz.open(pdf_path)
        doc_ocr = fitz.open()

        for pagina in doc_original:
            # Extraer imagen de la página (300 DPI para mejor OCR)
            pix = pagina.get_pixmap(dpi=300)
            img = Image.open(io.BytesIO(pix.tobytes("png")))

            # Añadir página al nuevo PDF
            nueva_pagina = doc_ocr.new_page(width=pix.width, height=pix.height)
            nueva_pagina.insert_image(fitz.Rect(0, 0, pix.width, pix.height), stream=pix.tobytes("png"))

            # Procesar texto con Tesseract
            ocr_data = pytesseract.image_to_data(
                img, 
                config='--oem 3 --psm 6 -l spa+eng',
                output_type=pytesseract.Output.DICT
            )

            # Añadir texto invisible al PDF
            for i, text in enumerate(ocr_data['text']):
                if int(ocr_data['conf'][i]) > 60 and text.strip():
                    x, y = ocr_data['left'][i], ocr_data['top'][i]
                    w, h = ocr_data['width'][i], ocr_data['height'][i]
                    rect = fitz.Rect(x, y, x + w, y + h)
                    nueva_pagina.insert_text(
                        rect.tl, 
                        text, 
                        fontsize=12,  # Tamaño fijo para simplificar
                        color=(0, 0, 0),
                        render_mode=3  # Texto invisible
                    )

        pdf_bytes = doc_ocr.write()
        doc_original.close()
        doc_ocr.close()
        return True, pdf_bytes

    except Exception as e:
        return False, f"Error: {str(e)}"

@app.route('/convert-to-ocr', methods=['POST'])
def procesar_pdf():
    if 'prueba' not in request.files:
        return jsonify({'error': 'Archivo no encontrado'}), 400

    file = request.files['prueba']
    if file.filename == '':
        return jsonify({'error': 'Nombre de archivo vacío'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Solo se permiten archivos PDF'}), 400

    # Guardar archivo temporalmente
    filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    try:
        success, result = convertir_pdf_a_ocr(filepath)
        if not success:
            return jsonify({'error': result}), 500

        # Devolver como Buffer
        buffer = Buffer(result)
        return jsonify({
            'success': True,
            'buffer': buffer.toJSON(),
            'size_bytes': len(result)
        })

    except Exception as e:
        return jsonify({'error': f"Error interno: {str(e)}"}), 500

    finally:
        if os.path.exists(filepath):
            os.remove(filepath)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)