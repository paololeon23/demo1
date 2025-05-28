import tkinter as tk
from tkinter import filedialog

def seleccionar_pdf():
    root = tk.Tk()
    root.withdraw()
    ruta_archivo = filedialog.askopenfilename(
        title="Selecciona un archivo PDF",
        filetypes=[("Archivos PDF", "*.pdf")]
    )
    return ruta_archivo

def cargar_pdf_como_buffer(ruta_pdf):
    try:
        with open(ruta_pdf, 'rb') as archivo:
            buffer = archivo.read()
            # Verificamos que sea un buffer real (bytes)
            if isinstance(buffer, bytes):
                print("✅ Archivo leído como buffer (bytes) correctamente.")
                return buffer
            else:
                print("❌ El contenido NO es un buffer (bytes).")
                return None
    except Exception as e:
        print(f"❌ Error al leer el PDF: {e}")
        return None

def guardar_buffer_hex_en_txt(buffer, nombre_salida="buffer_salida.txt"):
    try:
        with open(nombre_salida, 'w') as salida:
            # Guardamos en formato tipo Node.js <Buffer ...> con hexadecimal
            salida.write("<Buffer " + buffer.hex() + ">")
        print(f"✅ Buffer guardado en formato hexadecimal en '{nombre_salida}'")
    except Exception as e:
        print(f"❌ Error al guardar el archivo: {e}")

# --- Flujo principal ---
if __name__ == "__main__":
    ruta = seleccionar_pdf()

    if ruta:
        buffer_pdf = cargar_pdf_como_buffer(ruta)
        if buffer_pdf:
            guardar_buffer_hex_en_txt(buffer_pdf)
        else:
            print("⚠️ No se pudo leer el PDF correctamente.")
    else:
        print("⚠️ No se seleccionó ningún archivo.")
