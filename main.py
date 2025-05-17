# main.py
from flask import Flask, render_template, request, send_file, redirect, url_for, session, jsonify
from datetime import datetime, timedelta
import fitz  # PyMuPDF
import os
import string
import csv

app = Flask(__name__)
app.secret_key = "secreto_perro"

OUTPUT_DIR = "static/pdfs"
USUARIO = "Gsr89roja"
CONTRASENA = "serg890105"

meses_es = {
    "January": "ENERO", "February": "FEBRERO", "March": "MARZO",
    "April": "ABRIL", "May": "MAYO", "June": "JUNIO",
    "July": "JULIO", "August": "AGOSTO", "September": "SEPTIEMBRE",
    "October": "OCTUBRE", "November": "NOVIEMBRE", "December": "DICIEMBRE"
}

coords = {
    "cdmx": {
        "folio":    (87,130,14,(1,0,0)),
        "fecha":    (130,145,12,(0,0,0)),
        "marca":    (87,290,11,(0,0,0)),
        "serie":    (375,290,11,(0,0,0)),
        "linea":    (87,307,11,(0,0,0)),
        "motor":    (375,307,11,(0,0,0)),
        "anio":     (87,323,11,(0,0,0)),
        "vigencia": (375,323,11,(0,0,0)),
        "nombre":   (375,340,11,(0,0,0)),
        "template": "cdmxdigital2025ppp.pdf",
        "download_route": "abrir_pdf_cdmx"
    },
    "edomex": {
        "folio":     (535,135,14,(1,0,0)),
        "marca":     (109,190,10,(0,0,0)),
        "serie":     (230,233,10,(0,0,0)),
        "linea":     (238,190,10,(0,0,0)),
        "motor":     (104,233,10,(0,0,0)),
        "anio":      (410,190,10,(0,0,0)),
        "color":     (400,233,10,(0,0,0)),
        "fecha_exp": (190,280,10,(0,0,0)),
        "fecha_ven": (380,280,10,(0,0,0)),
        "nombre":    (394,320,10,(0,0,0)),
        "template": "edomex_plantilla_alta_res.pdf",
        "download_route": "abrir_pdf_edomex"
    },
    "morelos": {
        "folio":       (665,282,18,(1,0,0)),
        "placa":       (200,200,60,(0,0,0)),
        "fecha":       (200,340,14,(0,0,0)),
        "vigencia":    (600,340,14,(0,0,0)),
        "marca":       (110,425,14,(0,0,0)),
        "serie":       (460,420,14,(0,0,0)),
        "linea":       (110,455,14,(0,0,0)),
        "motor":       (460,445,14,(0,0,0)),
        "anio":        (110,485,14,(0,0,0)),
        "color":       (460,395,14,(0,0,0)),
        "tipo":        (510,470,14,(0,0,0)),
        "nombre":      (150,370,14,(0,0,0)),
        "fecha_hoja2": (100,100,14,(0,0,0)),
        "template":    "morelos_hoja1_imagen.pdf",
        "download_route": "abrir_pdf_morelos"
    },
    "oaxaca": {
        "folio":    (553,96,16,(1,0,0)),
        "fecha1":   (168,130,12,(0,0,0)),
        "fecha2":   (140,540,10,(0,0,0)),
        "marca":    (50,215,12,(0,0,0)),
        "serie":    (200,258,12,(0,0,0)),
        "linea":    (200,215,12,(0,0,0)),
        "motor":    (360,258,12,(0,0,0)),
        "anio":     (360,215,12,(0,0,0)),
        "color":    (50,258,12,(0,0,0)),
        "vigencia": (410,130,12,(0,0,0)),
        "nombre":   (133,149,10,(0,0,0)),
        "template": "oaxacachido.pdf",
        "download_route": "abrir_pdf_oaxaca"
    },
    "gto": {
        "folio":    (1800,455,60,(1,0,0)),
        "fecha":    (2200,580,35,(0,0,0)),
        "marca":    (385,715,35,(0,0,0)),
        "serie":    (350,800,35,(0,0,0)),
        "linea":    (800,715,35,(0,0,0)),
        "motor":    (1290,800,35,(0,0,0)),
        "anio":     (1500,715,35,(0,0,0)),
        "color":    (1960,715,35,(0,0,0)),
        "nombre":   (950,1100,50,(0,0,0)),
        "vigencia": (2200,645,35,(0,0,0)),
        "template": "permiso guanajuato.pdf",
        "download_route": "abrir_pdf_gto"
    },
}

def generar_folio_automatico(ruta="folios_globales.txt"):
    mes = datetime.now().strftime("%m")
    if not os.path.exists(ruta):
        open(ruta, "w").close()
    with open(ruta) as f:
        lineas = [l.strip() for l in f]
    este_mes = [x for x in lineas if x.startswith(mes)]
    fol = f"{mes}{len(este_mes)+1:03d}"
    with open(ruta, "a") as f:
        f.write(fol + "\n")
    return fol

def generar_placa_digital():
    archivo = "placas_digitales.txt"
    abc = string.ascii_uppercase
    if not os.path.exists(archivo):
        with open(archivo, "w") as f:
            f.write("LRU0000\n")
    ultimo = open(archivo).read().strip().split("\n")[-1]
    pref, num = ultimo[:3], int(ultimo[3:])
    if num < 9999:
        nuevo = f"{pref}{num+1:04d}"
    else:
        l1, l2, l3 = list(pref)
        i3 = abc.index(l3)
        if i3 < 25:
            l3 = abc[i3+1]
        else:
            i2 = abc.index(l2)
            if i2 < 25:
                l2 = abc[i2+1]; l3 = "A"
            else:
                l1 = abc[(abc.index(l1)+1)%26]; l2 = l3 = "A"
        nuevo = f"{l1}{l2}{l3}0000"
    with open(archivo, "a") as f:
        f.write(nuevo + "\n")
    return nuevo

def _guardar(folio, entidad, serie, marca, linea, motor, anio, color, fecha_exp, fecha_ven, nombre):
    existe = os.path.exists("registros.csv")
    with open("registros.csv", "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if not existe:
            w.writerow(["folio","entidad","serie","marca","linea","motor","anio","color","fecha_exp","fecha_ven","nombre"])
        w.writerow([folio, entidad, serie, marca, linea, motor, anio, color, fecha_exp, fecha_ven, nombre])

def cargar_registros():
    regs = []
    if os.path.exists("registros.csv"):
        with open("registros.csv", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                if len(row) == 11:
                    regs.append({
                        "folio": row[0], "entidad": row[1], "serie": row[2],
                        "marca": row[3], "linea": row[4], "motor": row[5],
                        "anio": row[6], "color": row[7],
                        "fecha_exp": row[8], "fecha_ven": row[9], "nombre": row[10]
                    })
    return regs

def guardar_registros(regs):
    with open("registros.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["folio","entidad","serie","marca","linea","motor","anio","color","fecha_exp","fecha_ven","nombre"])
        for r in regs:
            w.writerow([r["folio"],r["entidad"],r["serie"],r["marca"],r["linea"],r["motor"],r["anio"],r["color"],r["fecha_exp"],r["fecha_ven"],r["nombre"]])

def crear_pdf(entidad, datos, folio, f_exp, f_ven, placa=None):
    cfg = coords[entidad]
    plantilla = cfg["template"]
    out = os.path.join(OUTPUT_DIR, f"{folio}_{entidad}.pdf")
    doc = fitz.open(plantilla)
    pg = doc[0]
    # folio + fechas
    pg.insert_text(cfg["folio"][:2], folio, fontsize=cfg["folio"][2], color=cfg["folio"][3])
    if "fecha" in cfg:
        pg.insert_text(cfg["fecha"][:2], f_exp, fontsize=cfg["fecha"][2], color=cfg["fecha"][3])
    if "fecha_exp" in cfg:
        pg.insert_text(cfg["fecha_exp"][:2], f_exp, fontsize=cfg["fecha_exp"][2], color=cfg["fecha_exp"][3])
    pg.insert_text(cfg.get("vigencia", cfg.get("fecha2", cfg.get("fecha")) )[:2],
                   f_ven,
                   fontsize=cfg.get("vigencia", cfg.get("fecha2", cfg.get("fecha")))[2],
                   color=cfg.get("vigencia", cfg.get("fecha2", cfg.get("fecha")))[3])
    # placa (Morelos)
    if placa:
        pg.insert_text(cfg["placa"][:2], placa, fontsize=cfg["placa"][2], color=cfg["placa"][3])
    # resto de campos
    for campo in ["marca","serie","linea","motor","anio","color","tipo","nombre"]:
        if campo in cfg and campo in datos:
            x,y,s,col = cfg[campo]
            pg.insert_text((x,y), datos[campo], fontsize=s, color=col)
    # segunda hoja Morelos
    if entidad == "morelos" and len(doc) > 1:
        pg2 = doc[1]
        pg2.insert_text(cfg["fecha_hoja2"][:2], f_ven, fontsize=cfg["fecha_hoja2"][2], color=cfg["fecha_hoja2"][3])
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    doc.save(out)
    doc.close()
    _guardar(folio, entidad.upper(), datos.get("serie",""), datos.get("marca",""), datos.get("linea",""),
             datos.get("motor",""), datos.get("anio",""), datos.get("color",""), f_exp, f_ven, datos.get("nombre",""))
    return out

@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST" and request.form["user"] == USUARIO and request.form["pass"] == CONTRASENA:
        session["user"] = USUARIO
        return redirect(url_for("seleccionar_entidad"))
    return render_template("login.html")

@app.route("/seleccionar_entidad")
def seleccionar_entidad():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("seleccionar_entidad.html")

def procesar_formulario(entidad):
    d = request.form.to_dict()
    fol = generar_folio_automatico()
    ahora = datetime.now()
    # fechas
    if entidad == "cdmx" or entidad == "morelos":
        f_exp = ahora.strftime(f"%d DE {meses_es[ahora.strftime('%B')]} DEL %Y").upper()
    else:
        f_exp = ahora.strftime("%d/%m/%Y")
    f_ven = (ahora + timedelta(days=30)).strftime("%d/%m/%Y")
    # placa para Morelos
    placa = generar_placa_digital() if entidad == "morelos" else None
    crear_pdf(entidad, d, fol, f_exp, f_ven, placa)
    return render_template("exitoso.html", entidad=entidad, folio=fol)

# Formularios por entidad
@app.route("/formulario", methods=["GET","POST"])
def formulario_cdmx():
    if "user" not in session: return redirect(url_for("login"))
    if request.method == "POST": return procesar_formulario("cdmx")
    return render_template("formulario.html")

@app.route("/formulario_edomex", methods=["GET","POST"])
def formulario_edomex():
    if "user" not in session: return redirect(url_for("login"))
    if request.method == "POST": return procesar_formulario("edomex")
    return render_template("formulario_edomex.html")

@app.route("/formulario_morelos", methods=["GET","POST"])
def formulario_morelos():
    if "user" not in session: return redirect(url_for("login"))
    if request.method == "POST": return procesar_formulario("morelos")
    return render_template("formulario_morelos.html")

@app.route("/formulario_oaxaca", methods=["GET","POST"])
def formulario_oaxaca():
    if "user" not in session: return redirect(url_for("login"))
    if request.method == "POST": return procesar_formulario("oaxaca")
    return render_template("formulario_oaxaca.html")

@app.route("/formulario_gto", methods=["GET","POST"])
def formulario_gto():
    if "user" not in session: return redirect(url_for("login"))
    if request.method == "POST": return procesar_formulario("gto")
    return render_template("formulario_gto.html")

# Listar, eliminar y renovar
@app.route("/listar")
def listar():
    if "user" not in session: return redirect(url_for("login"))
    regs = cargar_registros()
    return render_template("listar.html", registros=regs, now=datetime.now())

@app.route("/eliminar/<folio>", methods=["POST"])
def eliminar_folio(folio):
    regs = [r for r in cargar_registros() if r["folio"] != folio]
    guardar_registros(regs)
    return redirect(url_for("listar"))

@app.route("/eliminar_multiples", methods=["POST"])
def eliminar_multiples():
    folios = request.form.getlist("folios")
    if folios:
        regs = [r for r in cargar_registros() if r["folio"] not in folios]
        guardar_registros(regs)
    return redirect(url_for("listar"))

@app.route("/renovar/<folio>")
def renovar(folio):
    regs = cargar_registros()
    viejo = next((r for r in regs if r["folio"] == folio), None)
    if not viejo: return redirect(url_for("listar"))
    venc = datetime.strptime(viejo["fecha_ven"], "%d/%m/%Y")
    if datetime.now() < venc: return redirect(url_for("listar"))
    # reutilizar datos viejos
    return procesar_formulario(viejo["entidad"].lower())

# Rutas de descarga
@app.route("/abrir_pdf_cdmx/<folio>")
def abrir_pdf_cdmx(folio):
    p = os.path.join(OUTPUT_DIR, f"{folio}_cdmx.pdf")
    return send_file(p, as_attachment=True)

@app.route("/abrir_pdf_edomex/<folio>")
def abrir_pdf_edomex(folio):
    p = os.path.join(OUTPUT_DIR, f"{folio}_edomex.pdf")
    return send_file(p, as_attachment=True)

@app.route("/abrir_pdf_morelos/<folio>")
def abrir_pdf_morelos(folio):
    p = os.path.join(OUTPUT_DIR, f"{folio}_morelos.pdf")
    return send_file(p, as_attachment=True)

@app.route("/abrir_pdf_oaxaca/<folio>")
def abrir_pdf_oaxaca(folio):
    p = os.path.join(OUTPUT_DIR, f"{folio}_oaxaca.pdf")
    return send_file(p, as_attachment=True)

@app.route("/abrir_pdf_gto/<folio>")
def abrir_pdf_gto(folio):
    p = os.path.join(OUTPUT_DIR, f"{folio}_gto.pdf")
    return send_file(p, as_attachment=True)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
