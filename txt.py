import tkinter as tk
from tkinter import filedialog, messagebox
import os

def seleccionar_txt():
    root = tk.Tk()
    root.withdraw()
    ruta_txt = filedialog.askopenfilename(
        title="Selecciona el archivo TXT con buffer",
        filetypes=[("Archivos TXT", "*.txt")]
    )
    return ruta_txt

def guardar_pdf():
    root = tk.Tk()
    root.withdraw()
    ruta_pdf = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("Archivos PDF", "*.pdf")],
        title="Guardar PDF recuperado como"
    )
    return ruta_pdf

def txt_a_pdf(nombre_txt, nombre_pdf_salida):
    try:
        if not os.path.isfile(nombre_txt):
            messagebox.showerror("Error", f"No existe el archivo TXT:\n{nombre_txt}")
            return

        with open(nombre_txt, 'r', encoding='utf-8') as f:
            contenido = f.read().strip()

        if contenido.startswith("<Buffer ") and contenido.endswith(">"):
            hex_str = contenido[len("<Buffer "):-1]
        else:
            messagebox.showerror("Error", "El archivo TXT no tiene el formato esperado <Buffer ...>")
            return

        buffer = bytes.fromhex(hex_str)

        with open(nombre_pdf_salida, 'wb') as f:
            f.write(buffer)

        messagebox.showinfo("Éxito", f"PDF recuperado y guardado en:\n{nombre_pdf_salida}")

    except Exception as e:
        messagebox.showerror("Error inesperado", str(e))

if __name__ == "__main__":
    ruta_txt = seleccionar_txt()
    if not ruta_txt:
        print("⚠️ No se seleccionó ningún archivo TXT.")
        exit()

    ruta_pdf = guardar_pdf()
    if not ruta_pdf:
        print("⚠️ No se seleccionó dónde guardar el PDF.")
        exit()

    txt_a_pdf(ruta_txt, ruta_pdf)
