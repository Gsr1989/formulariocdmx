from flask import Flask, render_template, request, send_file
from datetime import datetime, timedelta
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os

app = Flask(__name__)
TEMPLATE_PATH = "cdmxdigital2025ppp.pdf"
OUTPUT_DIR = "static/pdfs"

# Coordenadas finales confirmadas
coords = {
    "folio": (87, 662, 12, (1, 0, 0)),      # rojo
    "fecha": (147, 650, 12, (0, 0, 0)),
    "marca": (97, 365, 12, (0, 0, 0)),
    "serie": (455, 365, 12, (0, 0, 0)),
    "linea": (97, 358, 12, (0, 0, 0)),
    "motor": (430, 358, 12, (0, 0, 0)),
    "anio": (97, 333, 12, (0, 0, 0)),
    "vigencia": (455, 333, 12, (0, 0, 0)),
    "nombre": (451, 326, 8, (0, 0, 0))
}

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        data = request.form

        fecha_actual = datetime.now()
        fecha_expedicion = fecha_actual.strftime("%d DE %B DEL %Y").upper()
        vigencia = (fecha_actual + timedelta(days=30)).strftime("%d/%m/%Y")

        os.makedirs(OUTPUT_DIR, exist_ok=True)
        output_path = os.path.join(OUTPUT_DIR, f"{data['serie']}.pdf")

        c = canvas.Canvas(output_path, pagesize=letter)
        c.drawImage(TEMPLATE_PATH, 0, 0, width=612, height=792)

        # Insertar folio con color rojo
        c.setFont("Helvetica-Bold", coords["folio"][2])
        c.setFillColorRGB(*coords["folio"][3])
        c.drawString(coords["folio"][0], coords["folio"][1], data["folio"])

        # Insertar fecha
        c.setFont("Helvetica-Bold", coords["fecha"][2])
        c.setFillColorRGB(*coords["fecha"][3])
        c.drawString(coords["fecha"][0], coords["fecha"][1], fecha_expedicion)

        # Insertar resto de campos
        campos = ["marca", "linea", "anio", "serie", "motor", "vigencia", "nombre"]
        valores = [data["marca"], data["linea"], data["anio"], data["serie"],
                   data["motor"], vigencia, data["nombre"]]

        for campo, valor in zip(campos, valores):
            c.setFont("Helvetica-Bold", coords[campo][2])
            c.setFillColorRGB(*coords[campo][3])
            c.drawString(coords[campo][0], coords[campo][1], valor)

        c.showPage()
        c.save()
        return send_file(output_path, as_attachment=True)

    return render_template("formulario.html")
