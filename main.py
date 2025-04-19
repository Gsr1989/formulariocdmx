from flask import Flask, render_template, request, send_file
from datetime import datetime, timedelta
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
import os

app = Flask(__name__)

TEMPLATE_IMAGE = "cdmxdigital2025ppp.pdf"  # Nombre de tu plantilla
OUTPUT_DIR = "static/pdfs"

# Coordenadas finales corregidas
coords = {
    "folio": (87, 662, 12, (1, 0, 0)),
    "fecha": (147, 650, 12, (0, 0, 0)),
    "marca": (97, 365, 12, (0, 0, 0)),
    "serie": (455, 365, 12, (0, 0, 0)),
    "linea": (97, 358, 12, (0, 0, 0)),
    "motor": (430, 358, 12, (0, 0, 0)),
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
        vigencia_fecha = (fecha_actual + timedelta(days=30)).strftime("%d/%m/%Y")

        serie = data["serie"]
        output_path = os.path.join(OUTPUT_DIR, f"{serie}.pdf")
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        c = canvas.Canvas(output_path, pagesize=letter)
        fondo = ImageReader(TEMPLATE_IMAGE)
        c.drawImage(fondo, 0, 0, width=612, height=792)

        # Folio
        x, y, size, color = coords["folio"]
        c.setFont("Helvetica-Bold", size)
        c.setFillColorRGB(*color)
        c.drawString(x, y, data["folio"])

        # Fecha
        x, y, size, color = coords["fecha"]
        c.setFont("Helvetica-Bold", size)
        c.setFillColorRGB(*color)
        c.drawString(x, y, fecha_expedicion)

        # Otros campos
        campos = ["marca", "serie", "linea", "motor", "anio", "vigencia", "nombre"]
        valores = [
            data["marca"],
            data["serie"],
            data["linea"],
            data["motor"],
            data["anio"],
            vigencia_fecha,
            data["nombre"],
        ]

        for campo, valor in zip(campos, valores):
            x, y, size, color = coords[campo]
            c.setFont("Helvetica-Bold", size)
            c.setFillColorRGB(*color)
            c.drawString(x, y, valor)

        c.save()
        return send_file(output_path, as_attachment=True)

    return render_template("formulario.html")
