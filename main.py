from flask import Flask, render_template, request, send_file, redirect, url_for
from datetime import datetime, timedelta
import fitz  # PyMuPDF
import os

app = Flask(__name__)
TEMPLATE_PDF = "morelos_hoja1_imagen.pdf"
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

# Coordenadas MORELOS hoja 1 y hoja 2 (simulada)
coords_morelos = {
    "folio": (100, 420, 12, (1, 0, 0)),
    "fecha": (100, 400, 12, (0, 0, 0)),
    "vigencia": (100, 380, 12, (0, 0, 0)),
    "marca": (100, 350, 12, (0, 0, 0)),
    "linea": (100, 330, 12, (0, 0, 0)),
    "anio": (100, 310, 12, (0, 0, 0)),
    "serie": (100, 290, 12, (0, 0, 0)),
    "motor": (100, 270, 12, (0, 0, 0)),
    "color": (100, 250, 12, (0, 0, 0)),
    "tipo": (100, 230, 12, (0, 0, 0)),
    "nombre": (100, 210, 12, (0, 0, 0)),
    "fecha_hoja2": (100, 100, 12, (0, 0, 0)),  # Simulada
}

def generar_folio_automatico(ruta_archivo="folios_globales.txt"):
    mes_actual = datetime.now().strftime("%m")
    if not os.path.exists(ruta_archivo):
        with open(ruta_archivo, "w"): pass
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
            return redirect(url_for("seleccionar_entidad"))
    return render_template("login.html")

@app.route("/seleccionar_entidad")
def seleccionar_entidad():
    return render_template("seleccionar_entidad.html")

@app.route("/formulario_morelos", methods=["GET", "POST"])
def formulario_morelos():
    if request.method == "POST":
        data = request.form
        folio = generar_folio_automatico()
        ahora = datetime.now()
        mes_escrito = meses_es[ahora.strftime("%B")]
        fecha_expedicion = ahora.strftime(f"%d DE {mes_escrito} DEL %Y").upper()
        fecha_formato_corto = ahora.strftime("%d/%m/%Y")
        fecha_vencimiento = (ahora + timedelta(days=30)).strftime("%d/%m/%Y")

        output_path = os.path.join(OUTPUT_DIR, f"morelos_{folio}.pdf")
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        doc = fitz.open(TEMPLATE_PDF)
        page = doc[0]

        # Insertar datos en la hoja 1
        page.insert_text((coords_morelos["folio"][0], coords_morelos["folio"][1]), folio, fontsize=coords_morelos["folio"][2], color=coords_morelos["folio"][3])
        page.insert_text((coords_morelos["fecha"][0], coords_morelos["fecha"][1]), fecha_expedicion, fontsize=coords_morelos["fecha"][2], color=coords_morelos["fecha"][3])
        page.insert_text((coords_morelos["vigencia"][0], coords_morelos["vigencia"][1]), fecha_vencimiento, fontsize=coords_morelos["vigencia"][2], color=coords_morelos["vigencia"][3])

        for campo in ["marca", "linea", "anio", "serie", "motor", "color", "tipo", "nombre"]:
            valor = data.get(campo, "")
            x, y, size, color = coords_morelos[campo]
            page.insert_text((x, y), valor, fontsize=size, color=color)

        # Fecha automática en hoja 2 (si existe)
        if len(doc) > 1:
            page2 = doc[1]
            fx, fy, fz, fc = coords_morelos["fecha_hoja2"]
            page2.insert_text((fx, fy), fecha_formato_corto, fontsize=fz, color=fc)

        doc.save(output_path)
        doc.close()
        return send_file(output_path, as_attachment=True)

    return render_template("formulario_morelos.html")
