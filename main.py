from flask import Flask, render_template, request, send_file, redirect, url_for
from datetime import datetime, timedelta
import fitz  # PyMuPDF
import os

app = Flask(__name__)
OUTPUT_DIR = "static/pdfs"
USUARIO = "Gsr89roja"
CONTRASENA = "serg890105"

meses_es = {
    "January":   "ENERO",      "February": "FEBRERO",
    "March":     "MARZO",      "April":    "ABRIL",
    "May":       "MAYO",       "June":     "JUNIO",
    "July":      "JULIO",      "August":   "AGOSTO",
    "September": "SEPTIEMBRE", "October":  "OCTUBRE",
    "November":  "NOVIEMBRE",  "December": "DICIEMBRE"
}

# Coordenadas para cada campo en las plantillas PDF
coords_cdmx = {
    "folio":    ( 87, 130, 12, (1, 0, 0)),
    "fecha":    (130, 145, 12, (0, 0, 0)),
    "marca":    ( 87, 290, 12, (0, 0, 0)),
    "serie":    (375, 290, 12, (0, 0, 0)),
    "linea":    ( 87, 307, 12, (0, 0, 0)),
    "motor":    (375, 307, 12, (0, 0, 0)),
    "anio":     ( 87, 323, 12, (0, 0, 0)),
    "vigencia": (375, 323, 12, (0, 0, 0)),
    "nombre":   (375, 340, 12, (0, 0, 0)),
}

coords_edomex = {
    "folio":     (535, 135, 14, (1, 0, 0)),
    "marca":     (109, 190, 10, (0, 0, 0)),
    "linea":     (238, 190, 10, (0, 0, 0)),
    "anio":      (410, 190, 10, (0, 0, 0)),
    "motor":     (104, 233, 10, (0, 0, 0)),
    "serie":     (230, 233, 10, (0, 0, 0)),
    "color":     (400, 233, 10, (0, 0, 0)),
    "fecha_exp": (190, 280, 10, (0, 0, 0)),
    "fecha_ven": (380, 280, 10, (0, 0, 0)),
    "nombre":    (394, 320, 10, (0, 0, 0)),
}

coords_morelos = {
    "folio":       (665, 282, 18, (1, 0, 0)),
    "fecha":       (200, 340, 14, (0, 0, 0)),
    "vigencia":    (600, 340, 14, (0, 0, 0)),
    "marca":       (110, 425, 14, (0, 0, 0)),
    "linea":       (110, 455, 14, (0, 0, 0)),
    "anio":        (110, 485, 14, (0, 0, 0)),
    "serie":       (460, 420, 14, (0, 0, 0)),
    "motor":       (460, 445, 14, (0, 0, 0)),
    "color":       (460, 395, 14, (0, 0, 0)),
    "tipo":        (510, 470, 14, (0, 0, 0)),
    "nombre":      (150, 370, 14, (0, 0, 0)),
    "fecha_hoja2": (100, 100, 14, (0, 0, 0)),
}

coords_oaxaca = {
    "folio":    (553,  96, 16, (1, 0, 0)),
    "fecha1":   (168, 130, 12, (0, 0, 0)),
    "fecha2":   (140, 540, 10, (0, 0, 0)),
    "marca":    ( 50, 215, 12, (0, 0, 0)),
    "serie":    (200, 258, 12, (0, 0, 0)),
    "linea":    (200, 215, 12, (0, 0, 0)),
    "motor":    (360, 258, 12, (0, 0, 0)),
    "anio":     (360, 215, 12, (0, 0, 0)),
    "color":    ( 50, 258, 12, (0, 0, 0)),
    "vigencia": (410, 130, 12, (0, 0, 0)),
    "nombre":   (133, 149, 10, (0, 0, 0)),
}

coords_gto = {
    "folio":    (1800, 455, 60, (1, 0, 0)),
    "fecha":    (2200, 580, 35, (0, 0, 0)),
    "marca":    ( 385, 715, 35, (0, 0, 0)),
    "linea":    ( 800, 715, 35, (0, 0, 0)),
    "anio":     (1145, 715, 35, (0, 0, 0)),
    "serie":    ( 350, 800, 35, (0, 0, 0)),
    "motor":    (1290, 800, 35, (0, 0, 0)),
    "color":    (1960, 715, 35, (0, 0, 0)),
    "nombre":   ( 950,1100, 90, (0, 0, 0)),
    "vigencia": (2200, 645, 35, (0, 0, 0)),
}

@app.context_processor
def inject_folio():
    return {"folio_actual": generar_folio_automatico()}

def generar_folio_automatico(ruta="folios_globales.txt"):
    mes_actual = datetime.now().strftime("%m")
    if not os.path.exists(ruta):
        open(ruta, "w").close()
    with open(ruta, "r") as f:
        existentes = [l.strip() for l in f]
    este_mes = [f for f in existentes if f.startswith(mes_actual)]
    nuevo = f"{mes_actual}{len(este_mes)+1:03d}"
    with open(ruta, "a") as f:
        f.write(nuevo + "\n")
    return nuevo

@app.route("/abrir_pdf_cdmx/<folio>")
def abrir_pdf_cdmx(folio):
    ruta = os.path.join(OUTPUT_DIR, f"{folio}_cdmx.pdf")
    if os.path.exists(ruta):
        return send_file(ruta, as_attachment=True)
    return "Archivo no encontrado", 404

@app.route("/abrir_pdf_edomex/<folio>")
def abrir_pdf_edomex(folio):
    ruta = os.path.join(OUTPUT_DIR, f"{folio}_edomex.pdf")
    if os.path.exists(ruta):
        return send_file(ruta, as_attachment=True)
    return "Archivo no encontrado", 404

@app.route("/abrir_pdf_morelos/<folio>")
def abrir_pdf_morelos(folio):
    ruta = os.path.join(OUTPUT_DIR, f"{folio}_morelos.pdf")
    if os.path.exists(ruta):
        return send_file(ruta, as_attachment=True)
    return "Archivo no encontrado", 404

@app.route("/abrir_pdf_oaxaca/<folio>")
def abrir_pdf_oaxaca(folio):
    ruta = os.path.join(OUTPUT_DIR, f"{folio}_oaxaca.pdf")
    if os.path.exists(ruta):
        return send_file(ruta, as_attachment=True)
    return "Archivo no encontrado", 404

@app.route("/abrir_pdf_gto/<folio>")
def abrir_pdf_gto(folio):
    ruta = os.path.join(OUTPUT_DIR, f"{folio}_gto.pdf")
    if os.path.exists(ruta):
        return send_file(ruta, as_attachment=True)
    return "Archivo no encontrado", 404

@app.route("/logout")
def logout():
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run()
