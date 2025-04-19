from flask import Flask, render_template, request, send_file
from datetime import datetime, timedelta
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
import os

app = Flask(__name__)
TEMPLATE_IMAGE = "cdmxdigital2025ppp.png"
OUTPUT_DIR = "static/pdfs"

# Coordenadas finales
coords = {
    "folio": (87, 662, 12, (1, 0, 0)),         # Rojo
    "fecha": (147, 650, 12, (0, 0, 0)),        # Negro
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
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        output_path = os.path.join(OUTPUT_DIR, f"{serie}.pdf")

        c = canvas.Canvas(output_path, pagesize=letter)
        bg = ImageReader(TEMPLATE_IMAGE)
        c.drawImage(bg, 0, 0, width=612, height=792)

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

        # Resto de los datos
        datos = {
            "marca": data["marca"],
            "serie": data["serie"],
            "linea": data["linea"],
            "motor": data["motor"],
            "anio": data["anio"],
            "vigencia": vigencia_fecha,
            "nombre": data["nombre"]
        }

        for campo, valor in datos.items():
            x, y, size, color = coords[campo]
            c.setFont("Helvetica-Bold", size)
            c.setFillColorRGB(*color)
            c.drawString(x, y, valor)

        c.showPage()
        c.save()
        return send_file(output_path, as_attachment=True)

    return render_template("formulario.html")
