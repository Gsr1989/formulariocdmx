from flask import Flask, render_template, request, send_file
from datetime import datetime, timedelta
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
import os

app = Flask(__name__)
TEMPLATE_IMAGE = "fondo_plantilla.png"
OUTPUT_DIR = "static/pdfs"

# Coordenadas desde esquina inferior izquierda
coords = {
    "fecha": (247, 507, 20),
    "folio": (187, 540, 24),
    "marca": (177, 502, 22),
    "linea": (177, 489, 22),
    "anio": (177, 476, 22),
    "serie": (455, 502, 22),
    "motor": (455, 489, 22),
    "vigencia": (455, 459, 22),
    "nombre": (455, 427, 22),
}

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        data = request.form

        fecha_actual = datetime.now()
        fecha_expedicion = fecha_actual.strftime("%d DE %B DEL %Y").upper()
        vigencia = (fecha_actual + timedelta(days=30)).strftime("%d/%m/%Y")

        serie = data["serie"]
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        output_path = os.path.join(OUTPUT_DIR, f"{serie}.pdf")

        c = canvas.Canvas(output_path, pagesize=letter)

        # Fondo como imagen
        bg = ImageReader(TEMPLATE_IMAGE)
        c.drawImage(bg, 0, 0, width=612, height=792)

        # Insertar texto
        c.setFont("Helvetica-Bold", coords["fecha"][2])
        c.drawString(coords["fecha"][0], coords["fecha"][1], fecha_expedicion)

        c.setFont("Helvetica-Bold", coords["folio"][2])
        c.setFillColorRGB(1, 0, 0)
        c.drawString(coords["folio"][0], coords["folio"][1], data["folio"])
        c.setFillColorRGB(0, 0, 0)

        campos = ["marca", "linea", "anio", "serie", "motor", "vigencia", "nombre"]
        valores = [data["marca"], data["linea"], data["anio"], data["serie"],
                   data["motor"], vigencia, data["nombre"]]

        for campo, valor in zip(campos, valores):
            c.setFont("Helvetica-Bold", coords[campo][2])
            c.drawString(coords[campo][0], coords[campo][1], valor)

        c.showPage()
        c.save()

        return send_file(output_path, as_attachment=True)

    return render_template("formulario.html")
