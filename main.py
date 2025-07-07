from flask import Flask, render_template, request, send_file, redirect, url_for, session
from datetime import datetime, timedelta
import fitz  # PyMuPDF
import os
import string
import csv
from supabase import create_client, Client

# Configuración básica
app = Flask(__name__)
app.secret_key = "secreto_perro"
OUTPUT_DIR = "static/pdfs"
USUARIO = "Gsr89roja"
CONTRASENA = "serg890105"
SUPABASE_URL = "https://xsagwqepoljfsogusubw.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhzYWd3cWVwb2xqZnNvZ3VzdWJ3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDM5NjM3NTUsImV4cCI6MjA1OTUzOTc1NX0.NUixULn0m2o49At8j6X58UqbXre2O2_JStqzls_8Gws"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

BUCKET = "pdfs"

def subir_pdf_supabase(path_local, nombre_pdf):
    with open(path_local, "rb") as f:
        data = f.read()
    # Elimina si ya existe
    try:
        supabase.storage.from_(BUCKET).remove([nombre_pdf])
    except Exception:
        pass
    res = supabase.storage.from_(BUCKET).upload(nombre_pdf, data, {"content-type": "application/pdf"})
    url_publica = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET}/{nombre_pdf}"
    return url_publica

# Guardar registro en Supabase incluyendo url_pdf
def guardar_supabase(data):
    supabase.table("borradores_registros").insert(data).execute()

def _guardar(folio, entidad, serie, marca, linea, motor, anio, color, fecha_impresa, fecha_vencimiento, nombre):
    # Genera la ruta del archivo local
    nombre_pdf = f"{folio}_{entidad.lower()}.pdf"
    ruta_local = os.path.join(OUTPUT_DIR, nombre_pdf)

    # Convierte la fecha impresa (ej. "04 DE JUNIO DEL 2025") a ISO para Supabase
    fecha_expedicion_iso = datetime.now().isoformat()
    fecha_vencimiento_iso = (datetime.now() + timedelta(days=30)).isoformat()

    # Sube el PDF al bucket de Supabase
    url_pdf = subir_pdf_supabase(ruta_local, nombre_pdf)

    # Guarda todo en la tabla
    guardar_supabase({
        "folio": folio,
        "entidad": entidad,
        "numero_serie": serie,
        "marca": marca,
        "linea": linea,
        "numero_motor": motor,
        "anio": anio,
        "color": color,
        "fecha_expedicion": fecha_expedicion_iso,
        "fecha_vencimiento": fecha_vencimiento_iso,
        "contribuyente": nombre,
        "url_pdf": url_pdf  # <-- IMPORTANTE: esta es la nueva columna que debes tener
    })

meses_es = {
    "January": "ENERO", "February": "FEBRERO", "March": "MARZO",
    "April": "ABRIL", "May": "MAYO", "June": "JUNIO",
    "July": "JULIO", "August": "AGOSTO", "September": "SEPTIEMBRE",
    "October": "OCTUBRE", "November": "NOVIEMBRE", "December": "DICIEMBRE"
}

coords_cdmx = {
    "folio": (87, 130, 14, (1,0,0)),
    "fecha": (130,145,12,(0,0,0)),
    "marca": (87,290,11,(0,0,0)),
    "serie": (375,290,11,(0,0,0)),
    "linea": (87,307,11,(0,0,0)),
    "motor": (375,307,11,(0,0,0)),
    "anio": (87,323,11,(0,0,0)),
    "vigencia": (375,323,11,(0,0,0)),
    "nombre": (375,340,11,(0,0,0)),
}
coords_edomex = {
    "folio": (535,135,14,(1,0,0)),
    "marca": (109,190,10,(0,0,0)),
    "serie": (230,233,10,(0,0,0)),
    "linea": (238,190,10,(0,0,0)),
    "motor": (104,233,10,(0,0,0)),
    "anio":  (410,190,10,(0,0,0)),
    "color": (400,233,10,(0,0,0)),
    "fecha_exp": (190,280,10,(0,0,0)),
    "fecha_ven": (380,280,10,(0,0,0)),
    "nombre": (394,320,10,(0,0,0)),
}
coords_morelos = {
    "folio": (665,282,18,(1,0,0)),
    "placa": (200,200,60,(0,0,0)),
    "fecha": (200,340,14,(0,0,0)),
    "vigencia": (600,340,14,(0,0,0)),
    "marca": (110,425,14,(0,0,0)),
    "serie": (460,420,14,(0,0,0)),
    "linea": (110,455,14,(0,0,0)),
    "motor": (460,445,14,(0,0,0)),
    "anio": (110,485,14,(0,0,0)),
    "color": (460,395,14,(0,0,0)),
    "tipo": (510,470,14,(0,0,0)),
    "nombre": (150,370,14,(0,0,0)),
    "fecha_hoja2": (100,100,14,(0,0,0)),
}
coords_oaxaca = {
    "folio": (553,96,16,(1,0,0)),
    "fecha1": (168,130,12,(0,0,0)),
    "fecha2": (140,540,10,(0,0,0)),
    "marca": (50,215,12,(0,0,0)),
    "serie": (200,258,12,(0,0,0)),
    "linea": (200,215,12,(0,0,0)),
    "motor": (360,258,12,(0,0,0)),
    "anio": (360,215,12,(0,0,0)),
    "color": (50,258,12,(0,0,0)),
    "vigencia": (410,130,12,(0,0,0)),
    "nombre": (133,149,10,(0,0,0)),
}
coords_gto = {
    "folio": (1800,455,60,(1,0,0)),
    "fecha": (2200,580,35,(0,0,0)),
    "marca": (385,715,35,(0,0,0)),
    "serie": (350,800,35,(0,0,0)),
    "linea": (800,715,35,(0,0,0)),
    "motor": (1290,800,35,(0,0,0)),
    "anio": (1500,715,35,(0,0,0)),
    "color": (1960,715,35,(0,0,0)),
    "nombre": (950,1100,50,(0,0,0)),
    "vigencia": (2200,645,35,(0,0,0)),
}

# ---------------- COORDENADAS GUERRERO ----------------
coords_guerrero = {
    "folio": (376,769,8,(1,0,0)),
    "fecha_exp": (122,755,8,(0,0,0)),
    "fecha_ven": (122,768,8,(0,0,0)),
    "serie": (376,742,8,(0,0,0)),
    "motor": (376,729,8,(0,0,0)),
    "marca": (376,700,8,(0,0,0)),
    "linea": (376,714,8,(0,0,0)),
    "color": (376,756,8,(0,0,0)),
    "nombre": (122,700,8,(0,0,0)),
    "rot_folio": (440,200,83,(0,0,0)),
    "rot_fecha_exp": (77,205,8,(0,0,0)),
    "rot_fecha_ven": (63,205,8,(0,0,0)),
    "rot_serie": (168,110,18,(0,0,0)),
    "rot_motor": (224,110,18,(0,0,0)),
    "rot_marca": (280,110,18,(0,0,0)),
    "rot_linea": (280,340,18,(0,0,0)),
    "rot_anio": (305,530,18,(0,0,0)),
    "rot_color": (224,410,18,(0,0,0)),
    "rot_nombre": (115,205,8,(0,0,0))
}

coords_jalisco = {
    "folio": (960, 391, 14, (0,0,0)),
    "marca": (330, 361, 14, (0,0,0)),
    "serie": (960, 361, 14, (0,0,0)),
    "linea": (330, 391, 14, (0,0,0)),
    "motor": (300, 260, 14, (0,0,0)),
    "anio": (330, 421, 14, (0,0,0)),
    "color": (330, 451, 14, (0,0,0)),
    "nombre": (330, 331, 14, (0,0,0)),
    "fecha_exp": (130, 350, 14, (0,0,0)),
    "fecha_ven": (330, 550, 14, (0,0,0)),
}

@app.route("/formulario_guerrero", methods=["GET","POST"])
def formulario_guerrero():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        d = request.form
        fol = generar_folio_guerrero()
        ahora = datetime.now()
        f_exp = ahora.strftime("%d/%m/%Y")
        f_exp_iso = ahora.isoformat()
        f_ven = (ahora + timedelta(days=30)).strftime("%d/%m/%Y")
        f_ven_iso = (ahora + timedelta(days=30)).isoformat()

        os.makedirs(OUTPUT_DIR, exist_ok=True)
        out = os.path.join(OUTPUT_DIR, f"{fol}_guerrero.pdf")
        doc = fitz.open("Guerrero.pdf")
        pg = doc[0]

        for campo in ["folio", "fecha_exp", "fecha_ven", "serie", "motor", "marca", "linea", "color", "nombre"]:
            x, y, s, col = coords_guerrero[campo]
            texto = fol if campo == "folio" else (f_exp if campo == "fecha_exp" else (f_ven if campo == "fecha_ven" else d.get(campo)))
            pg.insert_text((x, y), texto, fontsize=s, color=col)

        pg.insert_text(coords_guerrero["rot_folio"][:2], fol, fontsize=coords_guerrero["rot_folio"][2], rotate=270)
        pg.insert_text(coords_guerrero["rot_fecha_exp"][:2], f_exp, fontsize=coords_guerrero["rot_fecha_exp"][2], rotate=270)
        pg.insert_text(coords_guerrero["rot_fecha_ven"][:2], f_ven, fontsize=coords_guerrero["rot_fecha_ven"][2], rotate=270)
        pg.insert_text(coords_guerrero["rot_serie"][:2], d["serie"], fontsize=coords_guerrero["rot_serie"][2], rotate=270)
        pg.insert_text(coords_guerrero["rot_motor"][:2], d["motor"], fontsize=coords_guerrero["rot_motor"][2], rotate=270)
        pg.insert_text(coords_guerrero["rot_marca"][:2], d["marca"], fontsize=coords_guerrero["rot_marca"][2], rotate=270)
        pg.insert_text(coords_guerrero["rot_linea"][:2], d["linea"], fontsize=coords_guerrero["rot_linea"][2], rotate=270)
        pg.insert_text(coords_guerrero["rot_anio"][:2], d["anio"], fontsize=coords_guerrero["rot_anio"][2], rotate=270)
        pg.insert_text(coords_guerrero["rot_color"][:2], d["color"], fontsize=coords_guerrero["rot_color"][2], rotate=270)
        pg.insert_text(coords_guerrero["rot_nombre"][:2], d["nombre"], fontsize=coords_guerrero["rot_nombre"][2], rotate=270)

        doc.save(out)
        doc.close()

        _guardar(fol, "Guerrero", d["serie"], d["marca"], d["linea"], d["motor"], d["anio"], d["color"], f_exp_iso, f_ven_iso, d["nombre"])
        return render_template("exitoso.html", folio=fol, guerrero=True)

    return render_template("formulario_guerrero.html")


@app.route("/abrir_pdf_guerrero/<folio>")
def abrir_pdf_guerrero(folio):
    p = os.path.join(OUTPUT_DIR, f"{folio}_guerrero.pdf")
    return send_file(p, as_attachment=True)


def generar_folio_guerrero():
    letras = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    supa = supabase
    inicio_letras = "AZ"
    inicio_num = 2364

    existentes = supa.table("borradores_registros").select("folio").eq("entidad", "Guerrero").execute().data
    usados = [r["folio"] for r in existentes if r["folio"] and len(r["folio"]) == 6 and r["folio"][:2].isalpha()]

    empezar = False
    for l1 in letras:
        for l2 in letras:
            par = l1 + l2
            for num in range(1, 10000):
                if not empezar:
                    if par == inicio_letras and num == inicio_num:
                        empezar = True
                    else:
                        continue
                nuevo = f"{par}{str(num).zfill(4)}"
                if nuevo not in usados:
                    return nuevo

def generar_folio_por_mes():
    ahora = datetime.now()
    mes = ahora.strftime("%m")  # 01, 02, ..., 12

    supa = supabase
    registros = supa.table("borradores_registros").select("folio").execute().data

    existentes = [r["folio"] for r in registros if r["folio"] and r["folio"].startswith(mes)]

    consecutivos = [int(folio[2:]) for folio in existentes if folio[2:].isdigit()]
    nuevo_consecutivo = max(consecutivos) + 1 if consecutivos else 1

    return f"{mes}{str(nuevo_consecutivo).zfill(2)}"

import pdf417gen
from PIL import Image

def generar_codigo_ine(contenido, ruta_salida):
    # Genera los datos PDF417 (como INE)
    codes = pdf417gen.encode(contenido, columns=6, security_level=5)
    image = pdf417gen.render_image(codes)  # Devuelve un objeto PIL.Image
    image.save(ruta_salida)

def generar_folio_jalisco():
    """
    Lee el mayor folio en la entidad Jalisco y suma +1
    """
    registros = supabase.table("borradores_registros").select("folio").eq("entidad","Jalisco").execute().data
    numeros = []
    for r in registros:
        f = r["folio"]
        try:
            numeros.append(int(f))
        except:
            continue
    siguiente = max(numeros) + 1 if numeros else 5008167415
    return str(siguiente)

def generar_placa_digital():
    archivo = "placas_digitales.txt"
    abc = string.ascii_uppercase
    if not os.path.exists(archivo):
        with open(archivo, "w") as f:
            f.write("LRX0790\n")
    ultimo = open(archivo).read().strip().split("\n")[-1]
    pref, num = ultimo[:3], int(ultimo[3:])
    if num < 9999:
        nuevo = f"{pref}{num+1:04d}"
    else:
        l1,l2,l3 = list(pref)
        i3 = abc.index(l3)
        if i3 < 25:
            l3 = abc[i3+1]
        else:
            i2 = abc.index(l2)
            if i2 < 25:
                l2 = abc[i2+1]; l3 = "A"
            else:
                l1 = abc[(abc.index(l1)+1)%26]; l2=l3="A"
        nuevo = f"{l1}{l2}{l3}0000"
    with open(archivo,"a") as f:
        f.write(nuevo+"\n")
    return nuevo

def _guardar(folio, entidad, serie, marca, linea, motor, anio, color, fecha_exp, fecha_ven, nombre):
    guardar_supabase({
        "folio": folio,
        "entidad": entidad,
        "numero_serie": serie,
        "marca": marca,
        "linea": linea,
        "numero_motor": motor,
        "anio": anio,
        "color": color,
        "fecha_expedicion": fecha_exp,
        "fecha_vencimiento": fecha_ven,
        "contribuyente": nombre
    })

def cargar_registros():
    response = supabase.table("borradores_registros").select("*").order("id", desc=True).execute()
    datos = response.data
    registros = []
    for item in datos:
        registros.append({
            "folio": item.get("folio"),
            "entidad": item.get("entidad"),
            "serie": item.get("numero_serie"),
            "marca": item.get("marca"),
            "linea": item.get("linea"),
            "motor": item.get("numero_motor"),
            "anio": item.get("anio"),
            "color": item.get("color"),
            "fecha_exp": item.get("fecha_expedicion"),
            "fecha_ven": item.get("fecha_vencimiento"),
            "nombre": item.get("contribuyente"),
        })
    return registros

def guardar_registros(regs):
    with open("registros.csv","w",newline="",encoding="utf-8") as f:
        w=csv.writer(f)
        w.writerow(["folio","entidad","serie","marca","linea","motor","anio","color","fecha_exp","fecha_ven","nombre"])
        for r in regs:
            w.writerow([r["folio"],r["entidad"],r["serie"],r["marca"],r["linea"],r["motor"],r["anio"],r["color"],r["fecha_exp"],r["fecha_ven"],r["nombre"]])

@app.route("/", methods=["GET","POST"])
def login():
    if request.method=="POST" and request.form.get("user")==USUARIO and request.form.get("pass")==CONTRASENA:
        session["user"]=USUARIO
        return redirect(url_for("seleccionar_entidad"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/seleccionar_entidad")
def seleccionar_entidad():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("seleccionar_entidad.html")

# --- Formularios por entidad ---
@app.route("/formulario", methods=["GET","POST"])
def formulario_cdmx():
    if "user" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        d = request.form
        fol = generar_folio_automatico()
        ahora = datetime.now()

        # Fecha para mostrar en el PDF
        fecha_visual = ahora.strftime(f"%d DE {meses_es[ahora.strftime('%B')]} DEL %Y").upper()
        vigencia_visual = (ahora + timedelta(days=30)).strftime("%d/%m/%Y")

        # Fecha para guardar en Supabase (formato timestamp válido)
        fecha_iso = ahora.isoformat()
        vigencia_iso = (ahora + timedelta(days=30)).isoformat()

        # Crear PDF
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        out = os.path.join(OUTPUT_DIR, f"{fol}_cdmx.pdf")
        doc = fitz.open("cdmxdigital2025ppp.pdf"); pg = doc[0]

        pg.insert_text(coords_cdmx["folio"][:2], fol, fontsize=coords_cdmx["folio"][2], color=coords_cdmx["folio"][3])
        pg.insert_text(coords_cdmx["fecha"][:2], fecha_visual, fontsize=coords_cdmx["fecha"][2], color=coords_cdmx["fecha"][3])

        for key in ["marca", "serie", "linea", "motor", "anio"]:
            x, y, s, col = coords_cdmx[key]
            pg.insert_text((x, y), d[key], fontsize=s, color=col)

        pg.insert_text(coords_cdmx["vigencia"][:2], vigencia_visual, fontsize=coords_cdmx["vigencia"][2], color=coords_cdmx["vigencia"][3])
        pg.insert_text(coords_cdmx["nombre"][:2], d["nombre"], fontsize=coords_cdmx["nombre"][2], color=coords_cdmx["nombre"][3])

        doc.save(out)
        doc.close()

        _guardar(
            fol, "CDMX",
            d["serie"], d["marca"], d["linea"], d["motor"], d["anio"], "",
            fecha_iso, vigencia_iso, d["nombre"]
        )

        return render_template("exitoso.html", folio=fol, cdmx=True)
    return render_template("formulario.html")
    
@app.route("/formulario_edomex", methods=["GET","POST"])
def formulario_edomex():
    if "user" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        d = request.form
        fol = generar_folio_automatico()
        ahora = datetime.now()
        f_exp = ahora.strftime("%d/%m/%Y")
        f_ven = (ahora + timedelta(days=30)).strftime("%d/%m/%Y")
        fecha_iso = ahora.isoformat()
        vigencia_iso = (ahora + timedelta(days=30)).isoformat()

        os.makedirs(OUTPUT_DIR, exist_ok=True)
        out = os.path.join(OUTPUT_DIR, f"{fol}_edomex.pdf")
        doc = fitz.open("edomex_plantilla_alta_res.pdf")
        pg = doc[0]
        pg.insert_text(coords_edomex["folio"][:2], fol, fontsize=coords_edomex["folio"][2], color=coords_edomex["folio"][3])
        for key in ["marca", "serie", "linea", "motor", "anio", "color"]:
            x, y, s, col = coords_edomex[key]
            pg.insert_text((x, y), d[key], fontsize=s, color=col)
        pg.insert_text(coords_edomex["fecha_exp"][:2], f_exp, fontsize=coords_edomex["fecha_exp"][2], color=coords_edomex["fecha_exp"][3])
        pg.insert_text(coords_edomex["fecha_ven"][:2], f_ven, fontsize=coords_edomex["fecha_ven"][2], color=coords_edomex["fecha_ven"][3])
        pg.insert_text(coords_edomex["nombre"][:2], d["nombre"], fontsize=coords_edomex["nombre"][2], color=coords_edomex["nombre"][3])
        doc.save(out); doc.close()

        _guardar(fol, "EDOMEX", d["serie"], d["marca"], d["linea"], d["motor"], d["anio"], d["color"], fecha_iso, vigencia_iso, d["nombre"])
        return render_template("exitoso.html", folio=fol, edomex=True)
    return render_template("formulario_edomex.html")
    
@app.route("/formulario_morelos", methods=["GET","POST"])
def formulario_morelos():
    if "user" not in session:
        return redirect(url_for("login"))
    
    if request.method == "POST":
        d = request.form
        fol = generar_folio_automatico()
        placa = generar_placa_digital()
        ahora = datetime.now()

        # Formatos de fechas
        f_exp = ahora.strftime(f"%d DE {meses_es[ahora.strftime('%B')]} DEL %Y").upper()
        f_ven = (ahora + timedelta(days=30)).strftime("%d/%m/%Y")
        fecha_iso = ahora.isoformat()
        fecha_ven_iso = (ahora + timedelta(days=30)).isoformat()

        # Crear PDF
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        out = os.path.join(OUTPUT_DIR, f"{fol}_morelos.pdf")
        doc = fitz.open("morelos_hoja1_imagen.pdf")
        pg = doc[0]

        pg.insert_text(coords_morelos["folio"][:2], fol, fontsize=coords_morelos["folio"][2], color=coords_morelos["folio"][3])
        pg.insert_text(coords_morelos["placa"][:2], placa, fontsize=coords_morelos["placa"][2], color=coords_morelos["placa"][3])
        pg.insert_text(coords_morelos["fecha"][:2], f_exp, fontsize=coords_morelos["fecha"][2], color=coords_morelos["fecha"][3])
        pg.insert_text(coords_morelos["vigencia"][:2], f_ven, fontsize=coords_morelos["vigencia"][2], color=coords_morelos["vigencia"][3])

        for key in ["marca", "serie", "linea", "motor", "anio", "color", "tipo"]:
            if key in d and d[key].strip():
                x, y, s, col = coords_morelos[key]
                pg.insert_text((x, y), d[key].strip(), fontsize=s, color=col)

        pg.insert_text(coords_morelos["nombre"][:2], d["nombre"], fontsize=coords_morelos["nombre"][2], color=coords_morelos["nombre"][3])

        if len(doc) > 1:
            pg2 = doc[1]
            pg2.insert_text(coords_morelos["fecha_hoja2"][:2], f_ven, fontsize=coords_morelos["fecha_hoja2"][2], color=coords_morelos["fecha_hoja2"][3])

        doc.save(out)
        doc.close()

        _guardar(fol, "Morelos", d["serie"], d["marca"], d["linea"], d["motor"], d["anio"], d["color"], fecha_iso, fecha_ven_iso, d["nombre"])
        return render_template("exitoso.html", folio=fol, morelos=True)

    return render_template("formulario_morelos.html")
    
@app.route("/formulario_oaxaca", methods=["GET","POST"])
def formulario_oaxaca():
    if "user" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        d = request.form
        fol = generar_folio_automatico()
        ahora = datetime.now()
        f1 = ahora.strftime("%d/%m/%Y")
        f1_iso = ahora.isoformat()
        f_ven = (ahora + timedelta(days=30)).strftime("%d/%m/%Y")
        f_ven_iso = (ahora + timedelta(days=30)).isoformat()

        os.makedirs(OUTPUT_DIR, exist_ok=True)
        out = os.path.join(OUTPUT_DIR, f"{fol}_oaxaca.pdf")
        doc = fitz.open("oaxacachido.pdf")
        pg = doc[0]
        pg.insert_text(coords_oaxaca["folio"][:2], fol, fontsize=coords_oaxaca["folio"][2], color=coords_oaxaca["folio"][3])
        pg.insert_text(coords_oaxaca["fecha1"][:2], f1, fontsize=coords_oaxaca["fecha1"][2], color=coords_oaxaca["fecha1"][3])
        pg.insert_text(coords_oaxaca["fecha2"][:2], f1, fontsize=coords_oaxaca["fecha2"][2], color=coords_oaxaca["fecha2"][3])
        for key in ["marca", "serie", "linea", "motor", "anio", "color"]:
            x, y, s, col = coords_oaxaca[key]
            pg.insert_text((x, y), d[key], fontsize=s, color=col)
        pg.insert_text(coords_oaxaca["vigencia"][:2], f_ven, fontsize=coords_oaxaca["vigencia"][2], color=coords_oaxaca["vigencia"][3])
        pg.insert_text(coords_oaxaca["nombre"][:2], d["nombre"], fontsize=coords_oaxaca["nombre"][2], color=coords_oaxaca["nombre"][3])
        doc.save(out); doc.close()

        _guardar(fol, "Oaxaca", d["serie"], d["marca"], d["linea"], d["motor"], d["anio"], d["color"], f1_iso, f_ven_iso, d["nombre"])
        return render_template("exitoso.html", folio=fol, oaxaca=True)
    return render_template("formulario_oaxaca.html")

@app.route("/formulario_gto", methods=["GET","POST"])
def formulario_gto():
    if "user" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        d = request.form
        fol = generar_folio_automatico()
        ahora = datetime.now()
        f_exp = ahora.strftime("%d/%m/%Y")
        f_exp_iso = ahora.isoformat()
        f_ven = (ahora + timedelta(days=30)).strftime("%d/%m/%Y")
        f_ven_iso = (ahora + timedelta(days=30)).isoformat()

        os.makedirs(OUTPUT_DIR, exist_ok=True)
        out = os.path.join(OUTPUT_DIR, f"{fol}_gto.pdf")
        doc = fitz.open("permiso guanajuato.pdf"); pg = doc[0]
        pg.insert_text(coords_gto["folio"][:2], fol, fontsize=coords_gto["folio"][2], color=coords_gto["folio"][3])
        pg.insert_text(coords_gto["fecha"][:2], f_exp, fontsize=coords_gto["fecha"][2], color=coords_gto["fecha"][3])
        for key in ["marca", "serie", "linea", "motor", "anio", "color"]:
            x, y, s, col = coords_gto[key]
            pg.insert_text((x, y), d[key], fontsize=s, color=col)
        pg.insert_text(coords_gto["vigencia"][:2], f_ven, fontsize=coords_gto["vigencia"][2], color=coords_gto["vigencia"][3])
        pg.insert_text(coords_gto["nombre"][:2], d["nombre"], fontsize=coords_gto["nombre"][2], color=coords_gto["nombre"][3])
        doc.save(out); doc.close()

        _guardar(fol, "GTO", d["serie"], d["marca"], d["linea"], d["motor"], d["anio"], d["color"], f_exp_iso, f_ven_iso, d["nombre"])
        return render_template("exitoso.html", folio=fol, gto=True)
    return render_template("formulario_gto.html")
    
# --- LISTAR, ELIMINAR, RENOVAR ---
@app.route("/listar")
def listar():
    if "user" not in session:
        return redirect(url_for("login"))
    registros = cargar_registros()
    registros.sort(key=lambda x: x["folio"], reverse=True)
    folio_actual = registros[0]["folio"] if registros else "NINGUNO"
    return render_template("listar.html", registros=registros, now=datetime.now(), folio_actual=folio_actual)

@app.route("/editar_folio/<folio>", methods=["GET", "POST"])
def editar_folio(folio):
    if "user" not in session:
        return redirect(url_for("login"))
    
    response = supabase.table("borradores_registros").select("*").eq("folio", folio).execute()
    if not response.data:
        return redirect(url_for("listar"))

    actual = response.data[0]

    if request.method == "POST":
        nuevos_datos = {
            "marca": request.form.get("marca"),
            "linea": request.form.get("linea"),
            "anio": request.form.get("anio"),
            "numero_serie": request.form.get("serie"),
            "numero_motor": request.form.get("motor"),
            "color": request.form.get("color"),
            "contribuyente": request.form.get("nombre")
        }
        supabase.table("borradores_registros").update(nuevos_datos).eq("folio", folio).execute()
        return redirect(url_for("listar"))

    return render_template("editar_formulario.html", datos=actual)

@app.route("/eliminar/<folio>", methods=["POST"])
def eliminar_folio(folio):
    regs = [r for r in cargar_registros() if r["folio"]!=folio]
    guardar_registros(regs)
    return redirect(url_for("listar"))

@app.route("/eliminar_multiples", methods=["POST"])
def eliminar_multiples():
    folios = request.form.getlist("folios")
    if folios:
        regs = cargar_registros()
        regs = [r for r in regs if r["folio"] not in folios]
        guardar_registros(regs)
    return redirect(url_for("listar"))

@app.route("/renovar/<folio>")
def renovar(folio):
    regs = cargar_registros()
    viejo = next((r for r in regs if r["folio"]==folio), None)
    if not viejo:
        return redirect(url_for("listar"))
    venc = datetime.strptime(viejo["fecha_ven"], "%d/%m/%Y")
    if datetime.now() < venc:
        return redirect(url_for("listar"))
    nuevo = generar_folio_automatico()
    ahora = datetime.now()
    exp_f = ahora.strftime("%d/%m/%Y")
    ven_f = (ahora + timedelta(days=30)).strftime("%d/%m/%Y")
    entidad = viejo["entidad"]
    plantilla = {
        "CDMX":"cdmxdigital2025ppp.pdf",
        "EDOMEX":"edomex_plantilla_alta_res.pdf",
        "Morelos":"morelos_hoja1_imagen.pdf",
        "Oaxaca":"oaxacachido.pdf",
        "GTO":"permiso guanajuato.pdf"
    }[entidad]
    coords_map = {
        "CDMX":coords_cdmx,"EDOMEX":coords_edomex,
        "Morelos":coords_morelos,"Oaxaca":coords_oaxaca,"GTO":coords_gto
    }[entidad]
    clave_exp = "fecha_exp" if "fecha_exp" in coords_map else ("fecha" if "fecha" in coords_map else "fecha1")
    clave_ven = "fecha_ven" if "fecha_ven" in coords_map else ("vigencia" if "vigencia" in coords_map else "fecha2")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out = os.path.join(OUTPUT_DIR, f"{nuevo}_{entidad.lower()}.pdf")
    doc = fitz.open(plantilla); pg = doc[0]
    pg.insert_text(coords_map["folio"][:2], nuevo, fontsize=coords_map["folio"][2], color=coords_map["folio"][3])
    pg.insert_text(coords_map[clave_exp][:2], exp_f, fontsize=coords_map[clave_exp][2], color=coords_map[clave_exp][3])
    pg.insert_text(coords_map[clave_ven][:2], ven_f, fontsize=coords_map[clave_ven][2], color=coords_map[clave_ven][3])
    for campo in ["marca","serie","linea","motor","anio","color","nombre"]:
        if campo in coords_map:
            x,y,s,col = coords_map[campo]
            pg.insert_text((x,y), viejo[campo], fontsize=s, color=col)
    # SOLO MORELOS: nueva placa digital en renovación
    if entidad == "Morelos":
        placa = generar_placa_digital()
        x, y, s, col = coords_morelos["placa"]
        pg.insert_text((x, y), placa, fontsize=s, color=col)
        if len(doc)>1:
            pg2 = doc[1]
            x2, y2, s2, col2 = coords_morelos["fecha_hoja2"]
            pg2.insert_text((x2, y2), ven_f, fontsize=s2, color=col2)
    doc.save(out); doc.close()
    _guardar(nuevo, entidad, viejo["serie"], viejo["marca"], viejo["linea"], viejo["motor"], viejo["anio"], viejo["color"], exp_f, ven_f, viejo["nombre"])
    return redirect(url_for(f"abrir_pdf_{entidad.lower()}", folio=nuevo))

# --- DESCARGA PDFs ---
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

@app.route("/formulario_jalisco", methods=["GET","POST"])
def formulario_jalisco():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        d = request.form
        fol = generar_folio_jalisco()
        ahora = datetime.now()

        # Fechas para guardar en Supabase (no se imprimen ya en el PDF)
        f_exp_iso = ahora.isoformat()
        f_ven_iso = (ahora + timedelta(days=30)).isoformat()

        # Crear carpeta de salida
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        out = os.path.join(OUTPUT_DIR, f"{fol}_jalisco.pdf")
        doc = fitz.open("jalisco.pdf")
        pg = doc[0]

        # --- Insertar campos normales del formulario ---
        for campo in ["marca", "linea", "anio", "serie", "nombre", "color"]:
            x, y, s, col = coords_jalisco[campo]
            pg.insert_text((x, y), d.get(campo, ""), fontsize=s, color=col)
            pg.insert_text(coords_jalisco["fecha_ven"][:2], (ahora + timedelta(days=30)).strftime("%d/%m/%Y"), fontsize=coords_jalisco["fecha_ven"][2], color=coords_jalisco["fecha_ven"][3])

        # --- Imprimir FOLIO generado automáticamente ---
        pg.insert_text((960, 391), fol, fontsize=14, color=(0, 0, 0))

        # --- Imprimir FOLIO REPRESENTATIVO dos veces ---
        fol_representativo = "331997"
        pg.insert_text((900, 150), fol_representativo, fontsize=14, color=(0, 0, 0))
        pg.insert_text((900, 200), fol_representativo, fontsize=14, color=(0, 0, 0))

        # --- Generar imagen tipo INE y colocarla ---
        contenido_ine = f"""
FOLIO:{fol}
MARCA:{d.get('marca')}
LINEA:{d.get('linea')}
ANIO:{d.get('anio')}
SERIE:{d.get('serie')}
NOMBRE:{d.get('nombre')}
"""
        ine_img_path = os.path.join(OUTPUT_DIR, f"{fol}_inecode.png")
        generar_codigo_ine(contenido_ine, ine_img_path)

        img_rect = fitz.Rect(882.5, 30, 1127.5, 180)
        pg.insert_image(img_rect, filename=ine_img_path)

        # Guardar PDF
        doc.save(out)
        doc.close()

        # Guardar en la base con todos los datos
        _guardar(fol, "Jalisco", d["serie"], d["marca"], d["linea"], d["motor"], d["anio"], d["color"], f_exp_iso, f_ven_iso, d["nombre"])

        return render_template("exitoso.html", folio=fol, jalisco=True)

    return render_template("formulario_jalisco.html")

@app.route("/abrir_pdf_jalisco/<folio>")
def abrir_pdf_jalisco(folio):
    p = os.path.join(OUTPUT_DIR, f"{folio}_jalisco.pdf")
    return send_file(p, as_attachment=True)

@app.route("/folio_actual")
def folio_actual():
    ruta = "folios_globales.txt"
    if not os.path.exists(ruta):
        return "No hay folios generados aún."
    with open(ruta) as f:
        lineas = [l.strip() for l in f if l.strip()]
    if not lineas:
        return "No hay folios generados aún."
    return f"Folio actual: {lineas[-1]}"


# <- Aquí la pegas
generar_folio_automatico = generar_folio_por_mes

if __name__ == "__main__":
    app.run(debug=True)
