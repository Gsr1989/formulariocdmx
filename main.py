from flask import Flask, render_template, request, send_file, redirect, url_for
from datetime import datetime, timedelta
import fitz  # PyMuPDF
import os

app = Flask(__name__)
OUTPUT_DIR = "static/pdfs"
USUARIO = "Gsr89roja"
CONTRASENA = "serg890105"

meses_es = {
    "January": "ENERO", "February": "FEBRERO", "March": "MARZO", "April": "ABRIL",
    "May": "MAYO", "June": "JUNIO", "July": "JULIO", "August": "AGOSTO",
    "September": "SEPTIEMBRE", "October": "OCTUBRE", "November": "NOVIEMBRE", "December": "DICIEMBRE"
}

# Coordenadas por entidad
coords_cdmx = {
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

coords_edomex = {
    "folio": (535, 135, 14, (1, 0, 0)),
    "marca": (109, 190, 10, (0, 0, 0)),
    "linea": (238, 190, 10, (0, 0, 0)),
    "anio": (410, 190, 10, (0, 0, 0)),
    "motor": (104, 233, 10, (0, 0, 0)),
    "serie": (230, 233, 10, (0, 0, 0)),
    "color": (400, 233, 10, (0, 0, 0)),
    "fecha_exp": (190, 280, 10, (0, 0, 0)),
    "fecha_ven": (380, 280, 10, (0, 0, 0)),
    "nombre": (394, 320, 10, (0, 0, 0)),
}

coords_morelos = {
    "folio": (665, 282, 18, (1, 0, 0)),
    "fecha": (200, 340, 14, (0, 0, 0)),
    "vigencia": (600, 340, 14, (0, 0, 0)),
    "marca": (110, 425, 14, (0, 0, 0)),
    "linea": (110, 455, 14, (0, 0, 0)),
    "anio": (110, 485, 14, (0, 0, 0)),
    "serie": (460, 420, 14, (0, 0, 0)),
    "motor": (460, 445, 14, (0, 0, 0)),
    "color": (460, 395, 14, (0, 0, 0)),
    "tipo": (510, 470, 14, (0, 0, 0)),
    "nombre": (150, 370, 14, (0, 0, 0)),
    "fecha_hoja2": (100, 100, 14, (0, 0, 0)),
}

coords_oaxaca = {
    "folio": (553, 96, 16, (1, 0, 0)),
    "fecha1": (168, 130, 12, (0, 0, 0)),
    "fecha2": (168, 150, 12, (0, 0, 0)),
    "marca": (50, 215, 12, (0, 0, 0)),
    "serie": (200, 258, 12, (0, 0, 0)),
    "linea": (200, 215, 12, (0, 0, 0)),
    "motor": (360, 258, 12, (0, 0, 0)),
    "anio": (360, 215, 12, (0, 0, 0)),
    "color": (300, 400, 12, (0, 0, 0)),
    "vigencia": (410, 130, 12, (0, 0, 0)),
    "nombre": (133, 149, 10, (0, 0, 0)),
}

coords_gto = {
    "folio": (100, 100, 12, (1, 0, 0)),
    "fecha": (150, 150, 12, (0, 0, 0)),
    "marca": (100, 200, 12, (0, 0, 0)),
    "linea": (100, 220, 12, (0, 0, 0)),
    "anio": (100, 240, 12, (0, 0, 0)),
    "serie": (300, 200, 12, (0, 0, 0)),
    "motor": (300, 220, 12, (0, 0, 0)),
    "color": (300, 400, 12, (0, 0, 0)),
    "nombre": (100, 260, 12, (0, 0, 0)),
    "vigencia": (150, 280, 12, (0, 0, 0)),
}

def generar_folio_automatico(ruta="folios_globales.txt"):
    mes_actual = datetime.now().strftime("%m")
    if not os.path.exists(ruta):
        open(ruta, "w").close()
    with open(ruta, "r") as f:
        existentes = [l.strip() for l in f]
    este_mes = [f for f in existentes if f.startswith(mes_actual)]
    nuevo = f"{mes_actual}{len(este_mes)+1:03d}"
    with open(ruta, "a") as f:
        f.write(nuevo + "\n")
    return nuevo

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["user"] == USUARIO and request.form["pass"] == CONTRASENA:
            return redirect(url_for("seleccionar_entidad"))
    return render_template("login.html")

@app.route("/seleccionar_entidad")
def seleccionar_entidad():
    return render_template("seleccionar_entidad.html")

# Cada entidad
@app.route("/formulario", methods=["GET", "POST"])
def formulario_cdmx():
    if request.method == "POST":
        d = request.form
        folio = generar_folio_automatico()
        ahora = datetime.now()
        fecha = ahora.strftime(f"%d DE {meses_es[ahora.strftime('%B')]} DEL %Y").upper()
        vencimiento = (ahora + timedelta(days=30)).strftime("%d/%m/%Y")
        path = os.path.join(OUTPUT_DIR, f"{folio}_cdmx.pdf")
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        doc = fitz.open("cdmxdigital2025ppp.pdf")
        page = doc[0]
        for campo in coords_cdmx:
            x, y, s, col = coords_cdmx[campo]
            val = folio if campo == "folio" else fecha if campo == "fecha" else vencimiento if campo == "vigencia" else d[campo]
            page.insert_text((x, y), val, fontsize=s, color=col)
        doc.save(path)
        return send_file(path, as_attachment=True)
    return render_template("formulario.html")

@app.route("/formulario_edomex", methods=["GET", "POST"])
def formulario_edomex():
    if request.method == "POST":
        d = request.form
        folio = generar_folio_automatico()
        ahora = datetime.now()
        fecha_exp = ahora.strftime("%d/%m/%Y")
        fecha_ven = (ahora + timedelta(days=30)).strftime("%d/%m/%Y")
        path = os.path.join(OUTPUT_DIR, f"{folio}_edomex.pdf")
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        doc = fitz.open("edomex_plantilla_alta_res.pdf")
        page = doc[0]
        for campo in coords_edomex:
            x, y, s, col = coords_edomex[campo]
            val = folio if campo == "folio" else fecha_exp if campo == "fecha_exp" else fecha_ven if campo == "fecha_ven" else d[campo]
            page.insert_text((x, y), val, fontsize=s, color=col)
        doc.save(path)
        return send_file(path, as_attachment=True)
    return render_template("formulario_edomex.html")

@app.route("/formulario_morelos", methods=["GET", "POST"])
def formulario_morelos():
    if request.method == "POST":
        d = request.form
        folio = generar_folio_automatico()
        ahora = datetime.now()
        fecha_larga = ahora.strftime(f"%d DE {meses_es[ahora.strftime('%B')]} DEL %Y").upper()
        fecha_corta = ahora.strftime("%d/%m/%Y")
        vencimiento = (ahora + timedelta(days=30)).strftime("%d/%m/%Y")
        path = os.path.join(OUTPUT_DIR, f"{folio}_morelos.pdf")
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        doc = fitz.open("morelos_hoja1_imagen.pdf")
        page = doc[0]
        for campo in coords_morelos:
            x, y, s, col = coords_morelos[campo]
            val = folio if campo == "folio" else fecha_larga if campo == "fecha" else vencimiento if campo == "vigencia" else d.get(campo, "")
            page.insert_text((x, y), val, fontsize=s, color=col)
        if len(doc) > 1:
            x, y, s, col = coords_morelos["fecha_hoja2"]
            doc[1].insert_text((x, y), fecha_corta, fontsize=s, color=col)
        doc.save(path)
        return send_file(path, as_attachment=True)
    return render_template("formulario_morelos.html")

@app.route("/formulario_oaxaca", methods=["GET", "POST"])
def formulario_oaxaca():
    if request.method == "POST":
        d = request.form
        folio = generar_folio_automatico()
        ahora = datetime.now()
        fecha = ahora.strftime("%d/%m/%Y")
        vencimiento = (ahora + timedelta(days=30)).strftime("%d/%m/%Y")
        path = os.path.join(OUTPUT_DIR, f"{folio}_oaxaca.pdf")
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        doc = fitz.open("oaxacachido.pdf")
        page = doc[0]
        for campo in coords_oaxaca:
            x, y, s, col = coords_oaxaca[campo]
            val = folio if campo == "folio" else fecha if campo in ["fecha1", "fecha2"] else vencimiento if campo == "vigencia" else d.get(campo, "")
            page.insert_text((x, y), val, fontsize=s, color=col)
        doc.save(path)
        return send_file(path, as_attachment=True)
    return render_template("formulario_oaxaca.html")

@app.route("/formulario_gto", methods=["GET", "POST"])
def formulario_gto():
    if request.method == "POST":
        d = request.form
        folio = generar_folio_automatico()
        ahora = datetime.now()
        fecha = ahora.strftime("%d/%m/%Y")
        vencimiento = (ahora + timedelta(days=30)).strftime("%d/%m/%Y")
        path = os.path.join(OUTPUT_DIR, f"{folio}_gto.pdf")
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        doc = fitz.open("permiso guanajuato.pdf")
        page = doc[0]
        for campo in coords_gto:
            x, y, s, col = coords_gto[campo]
            val = folio if campo == "folio" else fecha if campo == "fecha" else vencimiento if campo == "vigencia" else d[campo]
            page.insert_text((x, y), val, fontsize=s, color=col)
        doc.save(path)
        return send_file(path, as_attachment=True)
    return render_template("formulario_gto.html")

if __name__ == "__main__":
    app.run()
