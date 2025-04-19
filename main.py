from flask import Flask, render_template, request, send_file
from datetime import datetime, timedelta
import fitz  # PyMuPDF
import os

app = Flask(__name__)
TEMPLATE_PATH = "cdmxdigital2025ppp.pdf"
OUTPUT_DIR = "static/pdfs"

# Coordenadas en puntos (medidas desde la esquina superior izquierda)
coords = {
    "folio": (87, 130),
    "fecha": (147, 142),
    "marca": (97, 427),
    "serie": (455, 427),
    "linea": (97, 434),
    "motor": (430, 434),
    "anio": (97, 459),
    "vigencia": (455, 459),
    "nombre": (451, 466),
}

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        data = request.form
        fecha_actual = datetime.now()
        fecha_expedicion = fecha_actual.strftime("%d DE %B DEL %Y").upper()
        vigencia = (fecha_actual + timedelta(days=30)).strftime("%d/%m/%Y")

        doc = fitz.open(TEMPLATE_PATH)
        page = doc[0]

        # Insertar folio en rojo
        page.insert_text((coords["folio"][0], coords["folio"][1]), data["folio"],
                         fontsize=12, color=(1, 0, 0))

        # Insertar fecha en negro
        page.insert_text((coords["fecha"][0], coords["fecha"][1]), fecha_expedicion,
                         fontsize=12, color=(0, 0, 0))

        # Insertar los demás datos
        page.insert_text((coords["marca"][0], coords["marca"][1]), data["marca"], fontsize=12)
        page.insert_text((coords["serie"][0], coords["serie"][1]), data["serie"], fontsize=12)
        page.insert_text((coords["linea"][0], coords["linea"][1]), data["linea"], fontsize=12)
        page.insert_text((coords["motor"][0], coords["motor"][1]), data["motor"], fontsize=12)
        page.insert_text((coords["anio"][0], coords["anio"][1]), data["anio"], fontsize=12)
        page.insert_text((coords["vigencia"][0], coords["vigencia"][1]), vigencia, fontsize=12)
        page.insert_text((coords["nombre"][0], coords["nombre"][1]), data["nombre"], fontsize=8)

        os.makedirs(OUTPUT_DIR, exist_ok=True)
        output_path = os.path.join(OUTPUT_DIR, f"{data['serie']}.pdf")
        doc.save(output_path)
        doc.close()

        return send_file(output_path, as_attachment=True)

    return render_template("formulario.html")
