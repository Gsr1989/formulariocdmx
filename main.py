from flask import Flask, render_template, request, send_file
from datetime import datetime, timedelta
import fitz  # PyMuPDF
import os

app = Flask(__name__)
TEMPLATE_PDF = "cdmxdigital2025ppp.pdf"
OUTPUT_DIR = "static/pdfs"

# Coordenadas finales (X, Y, tamaño, color)
coords = {
    "folio": (87, 130, 12, (1, 0, 0)),
    "fecha": (130, 145, 12, (0, 0, 0)),
    "marca": (87, 290, 12, (0, 0, 0)),
    "serie": (375, 290, 12, (0, 0, 0)),
    "linea": (87, 300, 12, (1, 0, 0)),
    "motor": (375, 300, 12, (1, 0, 0)),
    "anio": (97, 333, 12, (0, 0, 0)),
    "vigencia": (455, 333, 12, (0, 0, 0)),
    "nombre": (451, 326, 8, (0, 0, 0)),
}

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        data = request.form

        fecha_actual = datetime.now()
        fecha_expedicion = fecha_actual.strftime("%d DE %B DEL %Y").upper()
        vigencia_final = (fecha_actual + timedelta(days=30)).strftime("%d/%m/%Y")

        output_path = os.path.join(OUTPUT_DIR, f"{data['folio']}.pdf")
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        doc = fitz.open(TEMPLATE_PDF)
        page = doc[0]

        # Insertar textos
        page.insert_text((coords["folio"][0], coords["folio"][1]), data["folio"], fontsize=coords["folio"][2], color=coords["folio"][3])
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
