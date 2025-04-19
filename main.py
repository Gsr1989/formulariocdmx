from flask import Flask, render_template, request, send_file, redirect, url_for
from datetime import datetime, timedelta
import fitz  # PyMuPDF
import os

app = Flask(__name__)
TEMPLATE_PDF = "cdmxdigital2025ppp.pdf"
OUTPUT_DIR = "static/pdfs"

# Login
USUARIO = "Gsr89roja"
CONTRASENA = "serg890105"

# Meses en español
meses_es = {
    "January": "ENERO", "February": "FEBRERO", "March": "MARZO", "April": "ABRIL",
    "May": "MAYO", "June": "JUNIO", "July": "JULIO", "August": "AGOSTO",
    "September": "SEPTIEMBRE", "October": "OCTUBRE", "November": "NOVIEMBRE", "December": "DICIEMBRE"
}

# Coordenadas finales (X, Y, tamaño, color)
coords = {
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

def generar_folio_automatico(ruta_archivo="folios_usados.txt"):
    mes_actual = datetime.now().strftime("%m")

    if not os.path.exists(ruta_archivo):
        with open(ruta_archivo, "w") as f:
            pass

    with open(ruta_archivo, "r") as f:
        folios = [line.strip() for line in f.readlines()]

    folios_mes = [f for f in folios if f.startswith(mes_actual)]
    siguiente_numero = len(folios_mes) + 1
    folio_generado = f"{mes_actual}{siguiente_numero:03d}"

    with open(ruta_archivo, "a") as f:
        f.write(folio_generado + "\n")

    return folio_generado

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["user"]
        pw = request.form["pass"]
        if user == USUARIO and pw == CONTRASENA:
            return redirect(url_for("formulario"))
    return render_template("login.html")

@app.route("/formulario", methods=["GET", "POST"])
def formulario():
    if request.method == "POST":
        data = request.form

        folio = generar_folio_automatico()

        ahora = datetime.now()
        mes_es = meses_es[ahora.strftime("%B")]
        fecha_expedicion = ahora.strftime(f"%d DE {mes_es} DEL %Y").upper()
        vigencia_final = (ahora + timedelta(days=30)).strftime("%d/%m/%Y")

        output_path = os.path.join(OUTPUT_DIR, f"{folio}.pdf")
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        doc = fitz.open(TEMPLATE_PDF)
        page = doc[0]

        page.insert_text((coords["folio"][0], coords["folio"][1]), folio, fontsize=coords["folio"][2], color=coords["folio"][3])
        page.insert_text((coords["fecha"][0], coords["fecha"][1]), fecha_expedicion, fontsize=coords["fecha"][2], color=coords["fecha"][3])

        campos = ["marca", "serie", "linea", "motor", "anio", "vigencia", "nombre"]
        valores = [data["marca"], data["serie"], data["linea"], data["motor"], data["anio"], vigencia_final, data["nombre"]]

        for campo, valor in zip(campos, valores):
            x, y, font_size, color = coords[campo]
            page.insert_text((x, y), valor, fontsize=font_size, color=color)

        doc.save(output_path)
        doc.close()

        return send_file(output_path, as_attachment=True)

    return render_template("formulario.html")
