from flask import Flask, render_template, request, send_file
from datetime import datetime, timedelta
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
import os

app = Flask(__name__)
TEMPLATE_IMAGE = "cdmxdigital2025ppp.pdf"
OUTPUT_DIR = "static/pdfs"

# Coordenadas finales desde la esquina inferior izquierda
coords = {
    "folio": (87, 662, 12),        # rojo
    "fecha": (147, 650, 12),
    "marca": (97, 365, 12),
    "serie": (455, 365, 12),
    "linea": (97, 358, 12),
    "motor": (430, 358, 12),
    "anio": (97, 333, 12),
    "vigencia": (455, 333, 12),
    "nombre": (451, 326, 8),
}

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        data = request.form

        # Fechas
        fecha_actual = datetime.now()
        fecha_expedicion = fecha_actual.strftime("%d DE %B DEL %Y").upper()
        vigencia = (fecha_actual + timedelta(days=30)).strftime("%d/%m/%Y")

        serie = data["serie"]
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        output_path = os.path.join(OUTPUT_DIR, f"{serie}.pdf")

        c = canvas.Canvas(output_path, pagesize=letter)

        # Fondo PDF como imagen
        fondo = ImageReader(TEMPLATE_IMAGE)
        c.drawImage(fondo, 0, 0, width=612, height=792)

        # Folio en rojo
        c.setFont("Helvetica-Bold", coords["folio"][2])
        c.setFillColorRGB(1, 0, 0)
        c.drawString(coords["folio"][0], coords["folio"][1], data["folio"])
        c.setFillColorRGB(0, 0, 0)

        # Fecha
        c.setFont("Helvetica-Bold", coords["fecha"][2])
        c.drawString(coords["fecha"][0], coords["fecha"][1], fecha_expedicion)

        # Resto de campos
        valores = {
            "marca": data["marca"],
            "linea": data["linea"],
            "anio": data["anio"],
            "serie": data["serie"],
            "motor": data["motor"],
            "vigencia": vigencia,
            "nombre": data["nombre"],
        }

        for campo, valor in valores.items():
            c.setFont("Helvetica-Bold", coords[campo][2])
            c.drawString(coords[campo][0], coords[campo][1], valor)

        c.showPage()
        c.save()

        return send_file(output_path, as_attachment=True)

    return render_template("formulario.html")
