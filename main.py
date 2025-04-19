from flask import Flask, render_template, request, send_file, redirect, url_for
from datetime import datetime, timedelta
import fitz  # PyMuPDF
import os

app = Flask(__name__)
OUTPUT_DIR = "static/pdfs"
USUARIO = "Gsr89roja"
CONTRASENA = "serg890105"

meses_es = {
    "January": "ENERO", "February": "FEBRERO", "March": "MARZO", "April": "ABRIL",
    "May": "MAYO", "June": "JUNIO", "July": "JULIO", "August": "AGOSTO",
    "September": "SEPTIEMBRE", "October": "OCTUBRE", "November": "NOVIEMBRE", "December": "DICIEMBRE"
}

coords_cdmx = {
    "folio": (87, 130, 12, (1, 0, 0)),
    "fecha": (130, 145, 12, (0, 0, 0)),
    "marca": (87, 290, 12, (0, 0, 0)),
    "serie": (375, 290, 12, (0, 0, 0)),
    "linea": (87, 307, 12, (0, 0, 0)),
    "motor": (375, 307, 12, (0, 0, 0)),
    "anio": (87, 323, 12, (0, 0, 0)),
    "vigencia": (375, 323, 12, (0, 0, 0)),
    "nombre": (375, 340, 12, (0, 0, 0)),
}

coords_edomex = {
    "folio": (535, 135, 14, (1, 0, 0)),
    "marca": (109, 190, 10, (0, 0, 0)),
    "linea": (238, 190, 10, (0, 0, 0)),
    "anio": (410, 190, 10, (0, 0, 0)),
    "motor": (104, 233, 10, (0, 0, 0)),
    "serie": (230, 233, 10, (0, 0, 0)),
    "color": (400, 233, 10, (0, 0, 0)),
    "fecha_exp": (190, 280, 10, (0, 0, 0)),
    "fecha_ven": (380, 280, 10, (0, 0, 0)),
    "nombre": (394, 320, 10, (0, 0, 0)),
}

coords_morelos = {
    "folio": (665, 282, 18, (1, 0, 0)),
    "fecha": (200, 340, 14, (0, 0, 0)),
    "vigencia": (600, 340, 14, (0, 0, 0)),
    "marca": (110, 425, 14, (0, 0, 0)),
    "linea": (110, 455, 14, (0, 0, 0)),
    "anio": (110, 485, 14, (0, 0, 0)),
    "serie": (460, 420, 14, (0, 0, 0)),
    "motor": (460, 445, 14, (0, 0, 0)),
    "color": (460, 395, 14, (0, 0, 0)),
    "tipo": (510, 470, 14, (0, 0, 0)),
    "nombre": (150, 370, 14, (0, 0, 0)),
    "fecha_hoja2": (100, 100, 14, (0, 0, 0)),
}

coords_oaxaca = {
    "folio": (87, 662, 12, (1, 0, 0)),
    "fecha1": (147, 650, 12, (0, 0, 0)),
    "fecha2": (147, 636, 12, (0, 0, 0)),
    "marca": (97, 365, 12, (0, 0, 0)),
    "serie": (455, 365, 12, (0, 0, 0)),
    "linea": (97, 358, 12, (0, 0, 0)),
    "motor": (430, 358, 12, (0, 0, 0)),
    "anio": (97, 333, 12, (0, 0, 0)),
    "vigencia": (455, 333, 12, (0, 0, 0)),
    "nombre": (451, 326, 10, (0, 0, 0)),
}

def generar_folio_automatico(ruta="folios_globales.txt"):
    mes_actual = datetime.now().strftime("%m")
    if not os.path.exists(ruta):
        open(ruta, "w").close()
    with open(ruta, "r") as f:
        existentes = [line.strip() for line in f]
    del_mes = [f for f in existentes if f.startswith(mes_actual)]
    nuevo = f"{mes_actual}{len(del_mes)+1:03d}"
    with open(ruta, "a") as f:
        f.write(nuevo + "\n")
    return nuevo

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["user"]
        pw = request.form["pass"]
        if user == USUARIO and pw == CONTRASENA:
            return redirect(url_for("seleccionar_entidad"))
    return render_template("login.html")

@app.route("/seleccionar_entidad")
def seleccionar_entidad():
    return render_template("seleccionar_entidad.html")

@app.route("/formulario_oaxaca", methods=["GET", "POST"])
def formulario_oaxaca():
    if request.method == "POST":
        data = request.form
        folio = generar_folio_automatico()
        ahora = datetime.now()
        fecha1 = ahora.strftime("%d/%m/%Y")
        fecha2 = fecha1
        vencimiento = (ahora + timedelta(days=30)).strftime("%d/%m/%Y")
        path = os.path.join(OUTPUT_DIR, f"{folio}_oaxaca.pdf")
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        doc = fitz.open("oaxacachido.pdf")
        page = doc[0]

        page.insert_text((coords_oaxaca["folio"][0], coords_oaxaca["folio"][1]), folio, fontsize=coords_oaxaca["folio"][2], color=coords_oaxaca["folio"][3])
        page.insert_text((coords_oaxaca["fecha1"][0], coords_oaxaca["fecha1"][1]), fecha1, fontsize=coords_oaxaca["fecha1"][2], color=coords_oaxaca["fecha1"][3])
        page.insert_text((coords_oaxaca["fecha2"][0], coords_oaxaca["fecha2"][1]), fecha2, fontsize=coords_oaxaca["fecha2"][2], color=coords_oaxaca["fecha2"][3])

        for campo in ["marca", "serie", "linea", "motor", "anio", "vigencia", "nombre"]:
            x, y, size, color = coords_oaxaca[campo]
            val = vencimiento if campo == "vigencia" else data[campo]
            page.insert_text((x, y), val, fontsize=size, color=color)

        doc.save(path)
        return send_file(path, as_attachment=True)
    return render_template("formulario_oaxaca.html")
