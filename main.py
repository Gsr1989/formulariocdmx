
from flask import Flask, render_template, request, send_file
from datetime import datetime
import fitz
import os

app = Flask(__name__)
TEMPLATE_PATH = "cdmxdigital2025ppp.pdf"
OUTPUT_DIR = "static/pdfs"

# Coordenadas fijas
coords = {
    "fecha": (247, 285, 20),
    "folio": (187, 252, 24),
    "marca": (177, 290, 22),
    "linea": (177, 293, 22),
    "anio": (177, 296, 22),
    "serie": (455, 290, 22),
    "motor": (455, 296, 22),
    "vigencia": (455, 328, 22),
    "nombre": (455, 360, 22),
}

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        data = request.form
        doc = fitz.open(TEMPLATE_PATH)
        page = doc[0]

        # Insertar cada campo
        page.insert_text((coords["fecha"][0], coords["fecha"][1]), data["fecha"], fontsize=coords["fecha"][2])
        page.insert_text((coords["folio"][0], coords["folio"][1]), data["folio"], fontsize=coords["folio"][2], color=(1, 0, 0))
        page.insert_text((coords["marca"][0], coords["marca"][1]), data["marca"], fontsize=coords["marca"][2])
        page.insert_text((coords["linea"][0], coords["linea"][1]), data["linea"], fontsize=coords["linea"][2])
        page.insert_text((coords["anio"][0], coords["anio"][1]), data["anio"], fontsize=coords["anio"][2])
        page.insert_text((coords["serie"][0], coords["serie"][1]), data["serie"], fontsize=coords["serie"][2])
        page.insert_text((coords["motor"][0], coords["motor"][1]), data["motor"], fontsize=coords["motor"][2])
        page.insert_text((coords["vigencia"][0], coords["vigencia"][1]), data["vigencia"], fontsize=coords["vigencia"][2])
        page.insert_text((coords["nombre"][0], coords["nombre"][1]), data["nombre"], fontsize=coords["nombre"][2])

        os.makedirs(OUTPUT_DIR, exist_ok=True)
        output_path = os.path.join(OUTPUT_DIR, f"{data['serie']}.pdf")
        doc.save(output_path)
        doc.close()

        return send_file(output_path, as_attachment=True)

    return render_template("formulario.html")
