from flask import Flask, render_template, request, send_file, redirect, url_for
from datetime import datetime, timedelta
import fitz  # PyMuPDF
import os

app = Flask(__name__)
OUTPUT_DIR = "static/pdfs"
USUARIO = "Gsr89roja"
CONTRASENA = "serg890105"

meses_es = {
    "January": "ENERO",   "February": "FEBRERO", "March": "MARZO",   "April": "ABRIL",
    "May": "MAYO",        "June": "JUNIO",       "July": "JULIO",    "August": "AGOSTO",
    "September": "SEPTIEMBRE", "October": "OCTUBRE", "November": "NOVIEMBRE", "December": "DICIEMBRE"
}

# ———————————————— Coordenadas ————————————————

coords_cdmx = {
    "folio":   ( 87, 130, 12, (1, 0, 0)),
    "fecha":   (130, 145, 12, (0, 0, 0)),
    "marca":   ( 87, 290, 12, (0, 0, 0)),
    "serie":   (375, 290, 12, (0, 0, 0)),
    "linea":   ( 87, 307, 12, (0, 0, 0)),
    "motor":   (375, 307, 12, (0, 0, 0)),
    "anio":    ( 87, 323, 12, (0, 0, 0)),
    "vigencia":(375, 323, 12, (0, 0, 0)),
    "nombre":  (375, 340, 12, (0, 0, 0)),
}

coords_edomex = {
    "folio":    (535, 135, 14, (1, 0, 0)),
    "marca":    (109, 190, 10, (0, 0, 0)),
    "linea":    (238, 190, 10, (0, 0, 0)),
    "anio":     (410, 190, 10, (0, 0, 0)),
    "motor":    (104, 233, 10, (0, 0, 0)),
    "serie":    (230, 233, 10, (0, 0, 0)),
    "color":    (400, 233, 10, (0, 0, 0)),
    "fecha_exp":(190, 280, 10, (0, 0, 0)),
    "fecha_ven":(380, 280, 10, (0, 0, 0)),
    "nombre":   (394, 320, 10, (0, 0, 0)),
}

coords_morelos = {
    "folio":      (665, 282, 18, (1, 0, 0)),
    "fecha":      (200, 340, 14, (0, 0, 0)),
    "vigencia":   (600, 340, 14, (0, 0, 0)),
    "marca":      (110, 425, 14, (0, 0, 0)),
    "linea":      (110, 455, 14, (0, 0, 0)),
    "anio":       (110, 485, 14, (0, 0, 0)),
    "serie":      (460, 420, 14, (0, 0, 0)),
    "motor":      (460, 445, 14, (0, 0, 0)),
    "color":      (460, 395, 14, (0, 0, 0)),
    "tipo":       (510, 470, 14, (0, 0, 0)),
    "nombre":     (150, 370, 14, (0, 0, 0)),
    "fecha_hoja2":(100, 100, 14, (0, 0, 0)),
}

coords_oaxaca = {
    "folio":  (553,  96, 16, (1, 0, 0)),
    "fecha1": (168, 130, 12, (0, 0, 0)),
    "fecha2": (140, 540, 10, (0, 0, 0)),
    "marca":  ( 50, 215, 12, (0, 0, 0)),
    "serie":  (200, 258, 12, (0, 0, 0)),
    "linea":  (200, 215, 12, (0, 0, 0)),
    "motor":  (360, 258, 12, (0, 0, 0)),
    "anio":   (360, 215, 12, (0, 0, 0)),
    "color":  (50, 258, 12, (0, 0, 0)),
    "vigencia":(410, 130, 12, (0, 0, 0)),
    "nombre":  (133, 149, 10, (0, 0, 0)),
}

coords_gto = {
    "folio":    (1800, 455, 60, (1, 0, 0)),
    "fecha":    (2200, 580, 35, (0, 0, 0)),
    "marca":    (385, 715, 35, (0, 0, 0)),
    "linea":    (800, 715, 35, (0, 0, 0)),
    "anio":     (1145, 715, 35, (0, 0, 0)),
    "serie":    (350, 800, 35, (0, 0, 0)),
    "motor":    (1290, 800, 35, (0, 0, 0)),
    "color":    (1960, 715, 35, (0, 0, 0)),
    "nombre":   (950, 1100, 90, (0, 0, 0)),
    "vigencia": (2200, 645, 35, (0, 0, 0))
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

# ———————————————— RUTAS ————————————————

@app.route("/", methods=["GET","POST"])
def login():
    if request.method=="POST":
        if request.form["user"]==USUARIO and request.form["pass"]==CONTRASENA:
            return redirect(url_for("seleccionar_entidad"))
    return render_template("login.html")

@app.route("/seleccionar_entidad")
def seleccionar_entidad():
    return render_template("seleccionar_entidad.html")

@app.route("/formulario", methods=["GET","POST"])
def formulario_cdmx():
    if request.method=="POST":
        d = request.form
        folio = generar_folio_automatico()
        ahora = datetime.now()
        f_exp = ahora.strftime(f"%d DE {meses_es[ahora.strftime('%B')]} DEL %Y").upper()
        f_ven = (ahora + timedelta(days=30)).strftime("%d/%m/%Y")
        out = os.path.join(OUTPUT_DIR, f"{folio}_cdmx.pdf")
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        doc = fitz.open("cdmxdigital2025ppp.pdf"); pg=doc[0]
        pg.insert_text(coords_cdmx["folio"][:2], folio,
                       fontsize=coords_cdmx["folio"][2], color=coords_cdmx["folio"][3])
        pg.insert_text(coords_cdmx["fecha"][:2], f_exp,
                       fontsize=coords_cdmx["fecha"][2], color=coords_cdmx["fecha"][3])
        for c in ["marca","serie","linea","motor","anio"]:
            x,y,s,col = coords_cdmx[c]; pg.insert_text((x,y), d[c], fontsize=s, color=col)
        x,y,s,col = coords_cdmx["vigencia"]; pg.insert_text((x,y), f_ven, fontsize=s, color=col)
        x,y,s,col = coords_cdmx["nombre"]; pg.insert_text((x,y), d["nombre"], fontsize=s, color=col)
        doc.save(out); doc.close()
        return render_template("exitoso.html", folio=folio, cdmx=True)
    return render_template("formulario.html")

@app.route("/formulario_edomex", methods=["GET","POST"])
def formulario_edomex():
    if request.method=="POST":
        d = request.form
        folio = generar_folio_automatico()
        ahora = datetime.now()
        f_exp = ahora.strftime("%d/%m/%Y")
        f_ven = (ahora + timedelta(days=30)).strftime("%d/%m/%Y")
        out = os.path.join(OUTPUT_DIR, f"{folio}_edomex.pdf")
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        doc = fitz.open("edomex_plantilla_alta_res.pdf"); pg=doc[0]
        pg.insert_text(coords_edomex["folio"][:2], folio,
                       fontsize=coords_edomex["folio"][2], color=coords_edomex["folio"][3])
        for c,val in [("marca",d["marca"]),("linea",d["linea"]),("anio",d["anio"]),
                      ("motor",d["motor"]),("serie",d["serie"]),("color",d["color"])]:
            x,y,s,col = coords_edomex[c]; pg.insert_text((x,y), val, fontsize=s, color=col)
        x,y,s,col = coords_edomex["fecha_exp"]; pg.insert_text((x,y), f_exp, fontsize=s, color=col)
        x,y,s,col = coords_edomex["fecha_ven"]; pg.insert_text((x,y), f_ven, fontsize=s, color=col)
        x,y,s,col = coords_edomex["nombre"];  pg.insert_text((x,y), d["nombre"], fontsize=s, color=col)
        doc.save(out); doc.close()
        return send_file(out, as_attachment=True)
    return render_template("formulario_edomex.html")

@app.route("/formulario_morelos", methods=["GET","POST"])
def formulario_morelos():
    if request.method=="POST":
        d = request.form
        folio = generar_folio_automatico()
        ahora = datetime.now()
        f_larga = ahora.strftime(f"%d DE {meses_es[ahora.strftime('%B')]} DEL %Y").upper()
        f_corta = ahora.strftime("%d/%m/%Y")
        f_ven   = (ahora + timedelta(days=30)).strftime("%d/%m/%Y")
        out = os.path.join(OUTPUT_DIR, f"{folio}_morelos.pdf")
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        doc = fitz.open("morelos_hoja1_imagen.pdf"); pg=doc[0]
        pg.insert_text(coords_morelos["folio"][:2], folio,
                       fontsize=coords_morelos["folio"][2], color=coords_morelos["folio"][3])
        pg.insert_text(coords_morelos["fecha"][:2], f_larga,
                       fontsize=coords_morelos["fecha"][2], color=coords_morelos["fecha"][3])
        pg.insert_text(coords_morelos["vigencia"][:2], f_ven,
                       fontsize=coords_morelos["vigencia"][2], color=coords_morelos["vigencia"][3])
        for c in ["marca","linea","anio","serie","motor","color","tipo"]:
            x,y,s,col = coords_morelos[c]; pg.insert_text((x,y), d[c], fontsize=s, color=col)
        x,y,s,col = coords_morelos["nombre"]; pg.insert_text((x,y), d["nombre"], fontsize=s, color=col)
        if len(doc)>1:
            x,y,s,col = coords_morelos["fecha_hoja2"]; doc[1].insert_text((x,y), f_corta, fontsize=s, color=col)
        doc.save(out); doc.close()
        return send_file(out, as_attachment=True)
    return render_template("formulario_morelos.html")

@app.route("/formulario_oaxaca", methods=["GET","POST"])
def formulario_oaxaca():
    if request.method=="POST":
        d = request.form
        folio = generar_folio_automatico()
        ahora = datetime.now()
        f1 = ahora.strftime("%d/%m/%Y")
        f2 = f1
        f_ven = (ahora + timedelta(days=30)).strftime("%d/%m/%Y")
        out = os.path.join(OUTPUT_DIR, f"{folio}_oaxaca.pdf")
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        doc = fitz.open("oaxacachido.pdf"); pg=doc[0]
        pg.insert_text(coords_oaxaca["folio"][:2], folio,
                       fontsize=coords_oaxaca["folio"][2], color=coords_oaxaca["folio"][3])
        pg.insert_text(coords_oaxaca["fecha1"][:2], f1,
                       fontsize=coords_oaxaca["fecha1"][2], color=coords_oaxaca["fecha1"][3])
        pg.insert_text(coords_oaxaca["fecha2"][:2], f2,
                       fontsize=coords_oaxaca["fecha2"][2], color=coords_oaxaca["fecha2"][3])
        for c in ["marca","serie","linea","motor","anio","color"]:
            x,y,s,col = coords_oaxaca[c]; pg.insert_text((x,y), d[c], fontsize=s, color=col)
        x,y,s,col = coords_oaxaca["vigencia"]; pg.insert_text((x,y), f_ven, fontsize=s, color=col)
        x,y,s,col = coords_oaxaca["nombre"]; pg.insert_text((x,y), d["nombre"], fontsize=s, color=col)
        doc.save(out); doc.close()
        return send_file(out, as_attachment=True)
    return render_template("formulario_oaxaca.html")

@app.route("/formulario_gto", methods=["GET","POST"])
def formulario_gto():
    if request.method=="POST":
        d = request.form
        folio = generar_folio_automatico()
        ahora = datetime.now()
        f_exp = ahora.strftime("%d/%m/%Y")
        f_ven = (ahora + timedelta(days=30)).strftime("%d/%m/%Y")
        out = os.path.join(OUTPUT_DIR, f"{folio}_gto.pdf")
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        doc = fitz.open("permiso guanajuato.pdf"); pg=doc[0]
        pg.insert_text(coords_gto["folio"][:2], folio,
                       fontsize=coords_gto["folio"][2], color=coords_gto["folio"][3])
        pg.insert_text(coords_gto["fecha"][:2], f_exp,
                       fontsize=coords_gto["fecha"][2], color=coords_gto["fecha"][3])
        for c in ["marca","linea","anio","serie","motor","color"]:
            x,y,s,col = coords_gto[c]; pg.insert_text((x,y), d[c], fontsize=s, color=col)
        x,y,s,col = coords_gto["vigencia"]; pg.insert_text((x,y), f_ven, fontsize=s, color=col)
        x,y,s,col = coords_gto["nombre"];  pg.insert_text((x,y), d["nombre"], fontsize=s, color=col)
        doc.save(out); doc.close()
        return send_file(out, as_attachment=True)
    return render_template("formulario_gto.html")

# ABRIR PDF SOLO PARA CDMX
@app.route("/abrir_pdf/<folio>")
def abrir_pdf(folio):
    ruta = os.path.join(OUTPUT_DIR, f"{folio}_cdmx.pdf")
    if os.path.exists(ruta):
        return send_file(ruta, as_attachment=True)
    return "Archivo no encontrado", 404

if __name__ == "__main__":
    app.run()
