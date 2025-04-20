```python
from flask import Flask, render_template, request, send_file, redirect, url_for
from datetime import datetime, timedelta
import fitz  # PyMuPDF
import os

app = Flask(__name__)
OUTPUT_DIR = "static/pdfs"
USUARIO = "Gsr89roja"
CONTRASENA = "serg890105"

meses_es = {
    "January":   "ENERO",   "February": "FEBRERO",
    "March":     "MARZO",   "April":    "ABRIL",
    "May":       "MAYO",    "June":     "JUNIO",
    "July":      "JULIO",   "August":   "AGOSTO",
    "September": "SEPTIEMBRE", "October": "OCTUBRE",
    "November":  "NOVIEMBRE",  "December": "DICIEMBRE"
}

# —————— Coordenadas de texto para cada plantilla PDF ——————
coords_cdmx = {
    "folio":    (87, 130, 12, (1, 0, 0)),
    "fecha":    (130, 145, 12, (0, 0, 0)),
    "marca":    (87, 290, 12, (0, 0, 0)),
    "serie":    (375, 290, 12, (0, 0, 0)),
    "linea":    (87, 307, 12, (0, 0, 0)),
    "motor":    (375, 307, 12, (0, 0, 0)),
    "anio":     (87, 323, 12, (0, 0, 0)),
    "vigencia": (375, 323, 12, (0, 0, 0)),
    "nombre":   (375, 340, 12, (0, 0, 0)),
}
coords_edomex = {
    "folio":     (535, 135, 14, (1, 0, 0)),
    "marca":     (109, 190, 10, (0, 0, 0)),
    "linea":     (238, 190, 10, (0, 0, 0)),
    "anio":      (410, 190, 10, (0, 0, 0)),
    "motor":     (104, 233, 10, (0, 0, 0)),
    "serie":     (230, 233, 10, (0, 0, 0)),
    "color":     (400, 233, 10, (0, 0, 0)),
    "fecha_exp": (190, 280, 10, (0, 0, 0)),
    "fecha_ven": (380, 280, 10, (0, 0, 0)),
    "nombre":    (394, 320, 10, (0, 0, 0)),
}
coords_morelos = {
    "folio":       (665, 282, 18, (1, 0, 0)),
    "fecha":       (200, 340, 14, (0, 0, 0)),
    "vigencia":    (600, 340, 14, (0, 0, 0)),
    "marca":       (110, 425, 14, (0, 0, 0)),
    "linea":       (110, 455, 14, (0, 0, 0)),
    "anio":        (110, 485, 14, (0, 0, 0)),
    "serie":       (460, 420, 14, (0, 0, 0)),
    "motor":       (460, 445, 14, (0, 0, 0)),
    "color":       (460, 395, 14, (0, 0, 0)),
    "tipo":        (510, 470, 14, (0, 0, 0)),
    "nombre":      (150, 370, 14, (0, 0, 0)),
    "fecha_hoja2": (100, 100, 14, (0, 0, 0)),
}
coords_oaxaca = {
    "folio":    (553,  96, 16, (1, 0, 0)),
    "fecha1":   (168, 130, 12, (0, 0, 0)),
    "fecha2":   (140, 540, 10, (0, 0, 0)),
    "marca":    (50,  215, 12, (0, 0, 0)),
    "serie":    (200, 258, 12, (0, 0, 0)),
    "linea":    (200, 215, 12, (0, 0, 0)),
    "motor":    (360, 258, 12, (0, 0, 0)),
    "anio":     (360, 215, 12, (0, 0, 0)),
    "color":    (50,  258, 12, (0, 0, 0)),
    "vigencia": (410, 130, 12, (0, 0, 0)),
    "nombre":   (133, 149, 10, (0, 0, 0)),
}
coords_gto = {
    "folio":    (1800, 455, 60, (1, 0, 0)),
    "fecha":    (2200, 580, 35, (0, 0, 0)),
    "marca":    (385,  715, 35, (0, 0, 0)),
    "linea":    (800,  715, 35, (0, 0, 0)),
    "anio":     (1145, 715, 35, (0, 0, 0)),
    "serie":    (350,  800, 35, (0, 0, 0)),
    "motor":    (1290, 800, 35, (0, 0, 0)),
    "color":    (1960, 715, 35, (0, 0, 0)),
    "nombre":   (950, 1100, 90, (0, 0, 0)),
    "vigencia": (2200, 645, 35, (0, 0, 0)),
}

# Generación automática de folio global e inyección a templates
@app.context_processor
def inject_folio():
    return {"folio_actual": generar_folio_automatico()}

def generar_folio_automatico(ruta="folios_globales.txt"):
    mes = datetime.now().strftime("%m")
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    if not os.path.exists(ruta): open(ruta, "w").close()
    with open(ruta, "r") as f: lineas = [l.strip() for l in f]
    del f
    count = sum(1 for l in lineas if l.startswith(mes)) + 1
    folio = f"{mes}{count:03d}"
    with open(ruta, "a") as f: f.write(folio + "\n")
    return folio

# —————— Rutas de autenticación y selección ——————
@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST" and \
       request.form.get("user") == USUARIO and \
       request.form.get("pass") == CONTRASENA:
        return redirect(url_for("seleccionar_entidad"))
    return render_template("login.html")

@app.route("/seleccionar_entidad")
def seleccionar_entidad():
    return render_template("seleccionar_entidad.html")

# —————— Formulario y PDF para CDMX ——————
@app.route("/formulario", methods=["GET","POST"])
def formulario_cdmx():
    if request.method == "POST":
        d = request.form
        fol = generar_folio_automatico()
        now = datetime.now()
        f_exp = now.strftime(f"%d DE {meses_es[now.strftime('%B')]} DEL %Y").upper()
        f_ven = (now + timedelta(days=30)).strftime("%d/%m/%Y")
        path = os.path.join(OUTPUT_DIR, f"{fol}_cdmx.pdf")
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        doc = fitz.open("cdmxdigital2025ppp.pdf"); pg = doc[0]
        pg.insert_text(coords_cdmx["folio"][0:2], fol, fontsize=coords_cdmx["folio"][2], color=coords_cdmx["folio"][3])
        pg.insert_text(coords_cdmx["fecha"][0:2], f_exp, fontsize=coords_cdmx["fecha"][2], color=coords_cdmx["fecha"][3])
        for k in ["marca","serie","linea","motor","anio"]:
            x,y,s,c = coords_cdmx[k]; pg.insert_text((x,y), d[k].upper(), fontsize=s, color=c)
        x,y,s,c = coords_cdmx["vigencia"]; pg.insert_text((x,y), f_ven, fontsize=s, color=c)
        x,y,s,c = coords_cdmx["nombre"]; pg.insert_text((x,y), d.get("nombre","").upper(), fontsize=s, color=c)
        doc.save(path); doc.close()
        return render_template("exitoso.html", folio=fol, cdmx=True)
    return render_template("formulario.html")

# —————— Formulario y PDF para EDOMEX ——————
@app.route("/formulario_edomex", methods=["GET","POST"])
def formulario_edomex():
    if request.method == "POST":
        d = request.form
        fol = generar_folio_automatico()
        now = datetime.now()
        f_exp = now.strftime("%d/%m/%Y")
        f_ven = (now + timedelta(days=30)).strftime("%d/%m/%Y")
        path = os.path.join(OUTPUT_DIR, f"{fol}_edomex.pdf")
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        doc = fitz.open("edomex_plantilla_alta_res.pdf"); pg = doc[0]
        pg.insert_text(coords_edomex["folio"][0:2], fol, fontsize=coords_edomex["folio"][2], color=coords_edomex["folio"][3])
        for k in ["marca","linea","anio","motor","serie","color"]:
            x,y,s,c = coords_edomex[k]; pg.insert_text((x,y), d[k].upper(), fontsize=s, color=c)
        x,y,s,c = coords_edomex["fecha_exp"]; pg.insert_text((x,y), f_exp, fontsize=s, color=c)
        x,y,s,c = coords_edomex["fecha_ven"]; pg.insert_text((x,y), f_ven, fontsize=s, color=c)
        x,y,s,c = coords_edomex["nombre"]; pg.insert_text((x,y), d.get("nombre","").upper(), fontsize=s, color=c)
        doc.save(path); doc.close()
        return render_template("exitoso.html", folio=fol, edomex=True)
    return render_template("formulario_edomex.html")

# —————— Formulario y PDF para Morelos ——————
@app.route("/formulario_morelos", methods=["GET","POST"])
def formulario_morelos():
    if request.method == "POST":
        d = request.form
        fol = generar_folio_automatico()
        now = datetime.now()
        f_larga = now.strftime(f"%d DE {meses_es[now.strftime('%B')]} DEL %Y").upper()
        f_corta = now.strftime("%d/%m/%Y")
        f_ven   = (now + timedelta(days=30)).strftime("%d/%m/%Y")
        path = os.path.join(OUTPUT_DIR, f"{fol}_morelos.pdf")
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        doc = fitz.open("morelos_hoja1_imagen.pdf"); pg = doc[0]
        pg.insert_text(coords_morelos["folio"][0:2], fol, fontsize=coords_morelos["folio"][2], color=coords_morelos["folio"][3])
        pg.insert_text(coords_morelos["fecha"][0:2], f_larga, fontsize=coords_morelos["fecha"][2], color=coords_morelos["fecha"][3])
        pg.insert_text(coords_morelos["vigencia"][0:2], f_ven, fontsize=coords_morelos["vigencia"][2], color=coords_morelos["vigencia"][3])
        for k in ["marca","linea","anio","serie","motor","color","tipo"]:
            x,y,s,c = coords_morelos[k]; pg.insert_text((x,y), d[k].upper(), fontsize=s, color=c)
        x,y,s,c = coords_morelos["nombre"]; pg.insert_text((x,y), d.get("nombre","").upper(), fontsize=s, color=c)
        if len(doc) > 1:
            x,y,s,c = coords_morelos["fecha_hoja2"]; doc[1].insert_text((x,y), f_corta, fontsize=s, color=c)
        doc.save(path); doc.close()
        return render_template("exitoso.html", folio=fol, morelos=True)
    return render_template("formulario_morelos.html")

# —————— Formulario y PDF para Oaxaca ——————
@app.route("/formulario_oaxaca", methods=["GET","POST"])
def formulario_oaxaca():
    if request.method == "POST":
        d = request.form
        fol = generar_folio_automatico()
        now = datetime.now()
        f1 = now.strftime("%d/%m/%Y")
        f_ven = (now + timedelta(days=30)).strftime("%d/%m/%Y")
        path = os.path.join(OUTPUT_DIR, f"{fol}_oaxaca.pdf")
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        doc = fitz.open("oaxacachido.pdf"); pg = doc[0]
        pg.insert_text(coords_oaxaca["folio"][0:2], fol, fontsize=coords_oaxaca["folio"][2], color=coords_oaxaca["folio"][3])
        pg.insert_text(coords_oaxaca["fecha1"][0:2], f1, fontsize=coords_oaxaca["fecha1"][2], color=coords_oaxaca["fecha1"][3])
        pg.insert_text(coords_oaxaca["fecha2"][0:2], f1, fontsize=coords_oaxaca["fecha2"][2], color=coords_oaxaca["fecha2"][3])
        for k in ["marca","serie","linea","motor","anio","color"]:
            x,y,s,c = coords_oaxaca[k]; pg.insert_text((x,y), d[k].upper(), fontsize=s, color=c)
        x,y,s,c = coords_oaxaca["vigencia"]; pg.insert_text((x,y), f_ven, fontsize=s, color=c)
        x,y,s,c = coords_oaxaca["nombre"]; pg.insert_text((x,y), d.get("nombre","").upper(), fontsize=s, color=c)
        doc.save(path); doc.close()
        return render_template("exitoso.html", folio=fol, oaxaca=True)
    return render_template("formulario_oaxaca.html")

# —————— Formulario y PDF para Guanajuato ——————
@app.route("/formulario_gto", methods=["GET","POST"])
def formulario_gto():
    if request.method == "POST":
        d = request.form
        fol = generar_folio_automatico()
        now = datetime.now()
        f_exp = now.strftime("%d/%m/%Y")
        f_ven = (now + timedelta(days=30)).strftime("%d/%m/%Y")
        path = os.path.join(OUTPUT_DIR, f"{fol}_gto.pdf")
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        doc = fitz.open("permiso guanajuato.pdf"); pg = doc[0]
        pg.insert_text(coords_gto["folio"][0:2], fol, fontsize=coords_gto["folio"][2], color=coords_gto["folio"][3])
        pg.insert_text(coords_gto["fecha"][0:2], f_exp, fontsize=coords_gto["fecha"][2], color=coords_gto["fecha"][3])
        for k in ["marca","linea","anio","serie","motor","color"]:
            x,y,s,c = coords_gto[k]; pg.insert_text((x,y), d[k].upper(), fontsize=s, color=c)
        x,y,s,c = coords_gto["vigencia"]; pg.insert_text((x,y), f_ven, fontsize=s, color=c)
        x,y,s,c = coords_gto["nombre"]; pg.insert_text((x,y), d.get("nombre","").upper(), fontsize=s, color=c)
        doc.save(path); doc.close()
        return render_template("exitoso.html", folio=fol, gto=True)
    return render_template("formulario_gto.html")

# —————— Endpoints para descargar PDFs ——————
@app.route("/abrir_pdf_cdmx/<folio>")
def abrir_pdf_cdmx(folio):
    path = os.path.join(OUTPUT_DIR, f"{folio}_cdmx.pdf")
    return send_file(path, as_attachment=True) if os.path.exists(path) else ("Archivo no encontrado",404)
@app.route("/abrir_pdf_edomex/<folio>")
def abrir_pdf_edomex(folio):
    path = os.path.join(OUTPUT_DIR, f"{folio}_edomex.pdf")
    return send_file(path, as_attachment=True) if os.path.exists(path) else ("Archivo no encontrado",404)
@app.route("/abrir_pdf_morelos/<folio>")
def abrir_pdf_morelos(folio):
    path = os.path.join(OUTPUT_DIR, f"{folio}_morelos.pdf")
    return send_file(path, as_attachment=True) if os.path.exists(path) else ("Archivo no encontrado",404)
@app.route("/abrir_pdf_oaxaca/<folio>")
def abrir_pdf_oaxaca(folio):
    path = os.path.join(OUTPUT_DIR, f"{folio}_oaxaca.pdf")
    return send_file(path, as_attachment=True) if os.path.exists(path) else ("Archivo no encontrado",404)
@app.route("/abrir_pdf_gto/<folio>")
def abrir_pdf_gto(folio):
    path = os.path.join(OUTPUT_DIR, f"{folio}_gto.pdf")
    return send_file(path, as_attachment=True) if os.path.exists(path) else ("Archivo no encontrado",404)

# —————— Cerrar sesión ——————
@app.route("/logout")
def logout():
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run()
```
