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

# Coordenadas
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
    "folio": (650, 280, 12, (1, 0, 0)),
    "fecha": (200, 310, 12, (0, 0, 0)),
    "vigencia": (600, 310, 12, (0, 0, 0)),
    "marca": (100, 350, 12, (0, 0, 0)),
    "linea": (100, 330, 12, (0, 0, 0)),
    "anio": (100, 310, 12, (0, 0, 0)),
    "serie": (100, 290, 12, (0, 0, 0)),
    "motor": (100, 270, 12, (0, 0, 0)),
    "color": (100, 250, 12, (0, 0, 0)),
    "tipo": (100, 230, 12, (0, 0, 0)),
    "nombre": (100, 210, 12, (0, 0, 0)),
    "fecha_hoja2": (100, 100, 12, (0, 0, 0)),
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

@app.route("/formulario", methods=["GET", "POST"])
def formulario_cdmx():
    if request.method == "POST":
        data = request.form
        folio = generar_folio_automatico()
        ahora = datetime.now()
        fecha_exp = ahora.strftime(f"%d DE {meses_es[ahora.strftime('%B')]} DEL %Y").upper()
        vigencia = (ahora + timedelta(days=30)).strftime("%d/%m/%Y")
        path = os.path.join(OUTPUT_DIR, f"{folio}_cdmx.pdf")
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        doc = fitz.open("cdmxdigital2025ppp.pdf")
        page = doc[0]
        page.insert_text((coords_cdmx["folio"][0], coords_cdmx["folio"][1]), folio, fontsize=coords_cdmx["folio"][2], color=coords_cdmx["folio"][3])
        page.insert_text((coords_cdmx["fecha"][0], coords_cdmx["fecha"][1]), fecha_exp, fontsize=coords_cdmx["fecha"][2], color=coords_cdmx["fecha"][3])

        for campo in ["marca", "serie", "linea", "motor", "anio", "vigencia", "nombre"]:
            x, y, size, color = coords_cdmx[campo]
            val = vigencia if campo == "vigencia" else data[campo]
            page.insert_text((x, y), val, fontsize=size, color=color)

        doc.save(path)
        return send_file(path, as_attachment=True)
    return render_template("formulario.html")

@app.route("/formulario_edomex", methods=["GET", "POST"])
def formulario_edomex():
    if request.method == "POST":
        data = request.form
        folio = generar_folio_automatico()
        ahora = datetime.now()
        fecha_exp = ahora.strftime("%d/%m/%Y")
        fecha_ven = (ahora + timedelta(days=30)).strftime("%d/%m/%Y")
        path = os.path.join(OUTPUT_DIR, f"{folio}_edomex.pdf")
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        doc = fitz.open("edomex_plantilla_alta_res.pdf")
        page = doc[0]
        page.insert_text((coords_edomex["folio"][0], coords_edomex["folio"][1]), folio, fontsize=coords_edomex["folio"][2], color=coords_edomex["folio"][3])

        for campo in ["marca", "linea", "anio", "motor", "serie", "color", "fecha_exp", "fecha_ven", "nombre"]:
            x, y, size, color = coords_edomex[campo]
            val = fecha_exp if campo == "fecha_exp" else fecha_ven if campo == "fecha_ven" else data[campo]
            page.insert_text((x, y), val, fontsize=size, color=color)

        doc.save(path)
        return send_file(path, as_attachment=True)
    return render_template("formulario_edomex.html")

@app.route("/formulario_morelos", methods=["GET", "POST"])
def formulario_morelos():
    if request.method == "POST":
        data = request.form
        folio = generar_folio_automatico()
        ahora = datetime.now()
        fecha_larga = ahora.strftime(f"%d DE {meses_es[ahora.strftime('%B')]} DEL %Y").upper()
        fecha_corta = ahora.strftime("%d/%m/%Y")
        fecha_ven = (ahora + timedelta(days=30)).strftime("%d/%m/%Y")
        path = os.path.join(OUTPUT_DIR, f"{folio}_morelos.pdf")
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        doc = fitz.open("morelos_hoja1_imagen.pdf")
        page = doc[0]
        page.insert_text((coords_morelos["folio"][0], coords_morelos["folio"][1]), folio, fontsize=coords_morelos["folio"][2], color=coords_morelos["folio"][3])
        page.insert_text((coords_morelos["fecha"][0], coords_morelos["fecha"][1]), fecha_larga, fontsize=coords_morelos["fecha"][2], color=coords_morelos["fecha"][3])
        page.insert_text((coords_morelos["vigencia"][0], coords_morelos["vigencia"][1]), fecha_ven, fontsize=coords_morelos["vigencia"][2], color=coords_morelos["vigencia"][3])

        for campo in ["marca", "linea", "anio", "serie", "motor", "color", "tipo", "nombre"]:
            x, y, size, color = coords_morelos[campo]
            page.insert_text((x, y), data[campo], fontsize=size, color=color)

        if len(doc) > 1:
            fx, fy, fz, fc = coords_morelos["fecha_hoja2"]
            doc[1].insert_text((fx, fy), fecha_corta, fontsize=fz, color=fc)

        doc.save(path)
        return send_file(path, as_attachment=True)
    return render_template("formulario_morelos.html")
