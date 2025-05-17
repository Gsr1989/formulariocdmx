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

coords_cdmx = {
    "folio":    (87,130,14,(1,0,0)),
    "fecha":    (130,145,12,(0,0,0)),
    "marca":    (87,290,11,(0,0,0)),
    "serie":    (375,290,11,(0,0,0)),
    "linea":    (87,307,11,(0,0,0)),
    "motor":    (375,307,11,(0,0,0)),
    "anio":     (87,323,11,(0,0,0)),
    "vigencia": (375,323,11,(0,0,0)),
    "nombre":   (375,340,11,(0,0,0)),
}

coords_edomex = {
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
}

coords_morelos = {
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
}

coords_oaxaca = {
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
}

coords_gto = {
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
            w.writerow([
                "folio","entidad","serie","marca","linea","motor","anio","color","fecha_exp","fecha_ven","nombre"
            ])
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
        w.writerow([
            "folio","entidad","serie","marca","linea","motor","anio","color","fecha_exp","fecha_ven","nombre"
        ])
        for r in regs:
            w.writerow([
                r["folio"],r["entidad"],r["serie"],r["marca"],r["linea"],r["motor"],
                r["anio"],r["color"],r["fecha_exp"],r["fecha_ven"],r["nombre"]
            ])

@app.route("/", methods=["GET","POST"])
def login():
    if request.method=="POST" and request.form["user"]==USUARIO and request.form["pass"]==CONTRASENA:
        session["user"] = USUARIO
        return redirect(url_for("seleccionar_entidad"))
    return render_template("login.html")

@app.route("/seleccionar_entidad")
def seleccionar_entidad():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("seleccionar_entidad.html")

# --- FORMULARIOS ---
def _procesar_formulario(entidad, plantilla, coords, campos, color_incluido=False, genera_placa=False):
    fol = generar_folio_automatico()
    ahora = datetime.now()
    if entidad == "CDMX" or entidad == "Morelos":
        f_exp = ahora.strftime(f"%d DE {meses_es[ahora.strftime('%B')]} DEL %Y").upper()
    else:
        f_exp = ahora.strftime("%d/%m/%Y")
    f_ven = (ahora + timedelta(days=30)).strftime("%d/%m/%Y")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out = os.path.join(OUTPUT_DIR, f"{fol}_{entidad.lower()}.pdf")
    doc = fitz.open(plantilla); pg = doc[0]
    # folio y fechas
    pg.insert_text(coords["folio"][:2], fol, fontsize=coords["folio"][2], color=coords["folio"][3])
    clave_exp = "fecha_exp" if "fecha_exp" in coords else ("fecha" if "fecha" in coords else "fecha1")
    clave_ven = "fecha_ven" if "fecha_ven" in coords else ("vigencia" if "vigencia" in coords else "fecha2")
    pg.insert_text(coords[clave_exp][:2], f_exp, fontsize=coords[clave_exp][2], color=coords[clave_exp][3])
    pg.insert_text(coords[clave_ven][:2], f_ven, fontsize=coords[clave_ven][2], color=coords[clave_ven][3])
    # placa extra
    if genera_placa:
        placa = generar_placa_digital()
        pg.insert_text(coords["placa"][:2], placa, fontsize=coords["placa"][2], color=coords["placa"][3])
    # resto de campos
    for campo in campos:
        if campo in coords:
            x,y,s,col = coords[campo]
            pg.insert_text((x,y), request.form[campo], fontsize=s, color=col)
    if "nombre" in coords:
        pg.insert_text(coords["nombre"][:2], request.form["nombre"], fontsize=coords["nombre"][2], color=coords["nombre"][3])
    # segunda hoja Morelos
    if entidade=="Morelos" and len(doc)>1:
        pg2 = doc[1]
        pg2.insert_text(coords["fecha_hoja2"][:2], f_ven, fontsize=coords["fecha_hoja2"][2], color=coords["fecha_hoja2"][3])
    doc.save(out); doc.close()
    _guardar(fol, entidad, request.form.get("serie",""), request.form.get("marca",""),
             request.form.get("linea",""), request.form.get("motor",""),
             request.form.get("anio",""), request.form.get("color",""), f_exp, f_ven, request.form.get("nombre",""))
    return fol

@app.route("/formulario", methods=["GET","POST"])
def formulario_cdmx():
    if "user" not in session: return redirect(url_for("login"))
    if request.method=="POST":
        fol = _procesar_formulario(
            "CDMX", "cdmxdigital2025ppp.pdf", coords_cdmx,
            ["marca","serie","linea","motor","anio"]
        )
        return render_template("exitoso.html", folio=fol, entidad="cdmx")
    return render_template("formulario.html")

@app.route("/formulario_edomex", methods=["GET","POST"])
def formulario_edomex():
    if "user" not in session: return redirect(url_for("login"))
    if request.method=="POST":
        fol = _procesar_formulario(
            "EDOMEX", "edomex_plantilla_alta_res.pdf", coords_edomex,
            ["marca","serie","linea","motor","anio","color"]
        )
        return render_template("exitoso.html", folio=fol, entidad="edomex")
    return render_template("formulario_edomex.html")

@app.route("/formulario_morelos", methods=["GET","POST"])
def formulario_morelos():
    if "user" not in session: return redirect(url_for("login"))
    if request.method=="POST":
        fol = _procesar_formulario(
            "Morelos", "morelos_hoja1_imagen.pdf", coords_morelos,
            ["marca","serie","linea","motor","anio","color","tipo"],
            color_incluido=True, genera_placa=True
        )
        return render_template("exitoso.html", folio=fol, entidad="morelos")
    return render_template("formulario_morelos.html")

@app.route("/formulario_oaxaca", methods=["GET","POST"])
def formulario_oaxaca():
    if "user" not in session: return redirect(url_for("login"))
    if request.method=="POST":
        fol = _procesar_formulario(
            "Oaxaca", "oaxacachido.pdf", coords_oaxaca,
            ["marca","serie","linea","motor","anio","color"]
        )
        return render_template("exitoso.html", folio=fol, entidad="oaxaca")
    return render_template("formulario_oaxaca.html")

@app.route("/formulario_gto", methods=["GET","POST"])
def formulario_gto():
    if "user" not in session: return redirect(url_for("login"))
    if request.method=="POST":
        fol = _procesar_formulario(
            "GTO", "permiso guanajuato.pdf", coords_gto,
            ["marca","serie","linea","motor","anio","color"]
        )
        return render_template("exitoso.html", folio=fol, entidad="gto")
    return render_template("formulario_gto.html")

# Listar / eliminar / renovar
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
    if not viejo:
        return redirect(url_for("listar"))
    venc = datetime.strptime(viejo["fecha_ven"], "%d/%m/%Y")
    if datetime.now() < venc:
        return redirect(url_for("listar"))
    # usa mismo flujo de _procesar_formulario con datos viejos
    nuevo = generar_folio_automatico()
    ahora = datetime.now()
    exp_f = ahora.strftime("%d/%m/%Y")
    ven_f = (ahora + timedelta(days=30)).strftime("%d/%m/%Y")
    plantillas = {
        "CDMX":"cdmxdigital2025ppp.pdf","EDOMEX":"edomex_plantilla_alta_res.pdf",
        "Morelos":"morelos_hoja1_imagen.pdf","Oaxaca":"oaxacachido.pdf","GTO":"permiso guanajuato.pdf"
    }[viejo["entidad"]]
    coords_map = {
        "CDMX":coords_cdmx,"EDOMEX":coords_edomex,
        "Morelos":coords_morelos,"Oaxaca":coords_oaxaca,"GTO":coords_gto
    }[viejo["entidad"]]
    # generar pdf
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out = os.path.join(OUTPUT_DIR, f"{nuevo}_{viejo['entidad'].lower()}.pdf")
    doc = fitz.open(plantillas); pg = doc[0]
    pg.insert_text(coords_map["folio"][:2], nuevo, fontsize=coords_map["folio"][2], color=coords_map["folio"][3])
    clave_exp = "fecha_exp" if "fecha_exp" in coords_map else ("fecha" if "fecha" in coords_map else "fecha1")
    clave_ven = "fecha_ven" if "fecha_ven" in coords_map else ("vigencia" if "vigencia" in coords_map else "fecha2")
    pg.insert_text(coords_map[clave_exp][:2], exp_f, fontsize=coords_map[clave_exp][2], color=coords_map[clave_exp][3])
    pg.insert_text(coords_map[clave_ven][:2], ven_f, fontsize=coords_map[clave_ven][2], color=coords_map[clave_ven][3])
    for campo in ["marca","serie","linea","motor","anio","color","nombre"]:
        if campo in coords_map:
            x,y,s,col = coords_map[campo]
            pg.insert_text((x,y), viejo[campo], fontsize=s, color=col)
    doc.save(out); doc.close()
    _guardar(nuevo, viejo["entidad"], viejo["serie"], viejo["marca"], viejo["linea"],
             viejo["motor"], viejo["anio"], viejo["color"], exp_f, ven_f, viejo["nombre"])
    return redirect(url_for(f"abrir_pdf_{viejo['entidad'].lower()}", folio=nuevo))

# Descarga de PDFs
@app.route("/abrir_pdf_<entidad>/<folio>")
def abrir_pdf(entidad, folio):
    p = os.path.join(OUTPUT_DIR, f"{folio}_{entidad}.pdf")
    return send_file(p, as_attachment=True) if os.path.exists(p) else ("No encontrado", 404)

# Activación automática vía API
def _api_patch(entidad, plantilla, coords, campos, genera_placa=False):
    data = request.get_json()
    if data.get("clave") != "ElvisTopaElSistema123":
        return jsonify({"error":"No autorizado"}), 403
    folio = data["folio"]
    salida = os.path.join(OUTPUT_DIR, f"{folio}_{entidad.lower()}.pdf")
    doc = fitz.open(plantilla); pg = doc[0]
    pg.insert_text(coords["folio"][:2], folio, fontsize=coords["folio"][2], color=coords["folio"][3])
    pg.insert_text(coords.get("fecha_exp",coords.get("fecha",coords.get("fecha1")))[:2],
                   data["fecha_exp"], fontsize=coords.get("fecha_exp",coords.get("fecha",coords.get("fecha1")))[2],
                   color=coords.get("fecha_exp",coords.get("fecha",coords.get("fecha1")))[3])
    pg.insert_text(coords.get("fecha_ven",coords.get("vigencia",coords.get("fecha2")))[:2],
                   data["fecha_ven"], fontsize=coords.get("fecha_ven",coords.get("vigencia",coords.get("fecha2")))[2],
                   color=coords.get("fecha_ven",coords.get("vigencia",coords.get("fecha2")))[3])
    if genera_placa:
        placa = generar_placa_digital()
        pg.insert_text(coords["placa"][:2], placa, fontsize=coords["placa"][2], color=coords["placa"][3])
    for campo in campos:
        if campo in coords:
            x,y,s,col = coords[campo]
            pg.insert_text((x,y), data[campo], fontsize=s, color=col)
    pg.insert_text(coords["nombre"][:2], data["nombre"], fontsize=coords["nombre"][2], color=coords["nombre"][3])
    doc.save(salida); doc.close()
    _guardar(folio, entidad, data.get("serie",""), data.get("marca",""), data.get("linea",""),
             data.get("motor",""), data.get("anio",""), data.get("color",""),
             data.get("fecha_exp",""), data.get("fecha_ven",""), data.get("nombre",""))
    return jsonify({"pdf_url": f"https://tu-dominio.com/static/pdfs/{folio}_{entidad.lower()}.pdf"})

@app.route("/activar_auto", methods=["POST"])
def activar_auto():
    return _api_patch("CDMX", "cdmxdigital2025ppp.pdf", coords_cdmx, ["marca","serie","linea","motor","anio"])

@app.route("/activar_auto_edomex", methods=["POST"])
def activar_auto_edomex():
    return _api_patch("EDOMEX", "edomex_plantilla_alta_res.pdf", coords_edomex,
                      ["marca","serie","linea","motor","anio","color"])

@app.route("/activar_auto_morelos", methods=["POST"])
def activar_auto_morelos():
    return _api_patch("Morelos", "morelos_hoja1_imagen.pdf", coords_morelos,
                      ["marca","serie","linea","motor","anio","color","tipo"], genera_placa=True)

@app.route("/activar_auto_oaxaca", methods=["POST"])
def activar_auto_oaxaca():
    return _api_patch("Oaxaca", "oaxacachido.pdf", coords_oaxaca,
                      ["marca","serie","linea","motor","anio","color"])

@app.route("/activar_auto_gto", methods=["POST"])
def activar_auto_gto():
    return _api_patch("GTO", "permiso guanajuato.pdf", coords_gto,
                      ["marca","serie","linea","motor","anio","color"])

if __name__ == "__main__":
    app.run(debug=True)
