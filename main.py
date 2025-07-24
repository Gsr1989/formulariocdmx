from flask import Flask, render_template, request, send_file, redirect, url_for, session
from io import BytesIO
import base64
from pdf417gen import encode, render_image
from PIL import Image
import qrcode
from datetime import datetime, timedelta
import os
import string
import csv
from supabase import create_client, Client
import json
import io
import fitz  # <— ¡Aquí lo agregas!

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
    "fecha_hoja2": (126,310,15,(0,0,0)),
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
    "folio": (960, 391, 14, (0, 0, 0)),
    "marca": (330, 361, 14, (0, 0, 0)),
    "serie": (960, 361, 14, (0, 0, 0)),
    "linea": (330, 391, 14, (0, 0, 0)),
    "motor": (300, 260, 14, (0, 0, 0)),
    "anio": (330, 421, 14, (0, 0, 0)),
    "color": (330, 451, 14, (0, 0, 0)),
    "nombre": (330, 331, 14, (0, 0, 0)),

    # FECHAS
    "fecha_exp": (120, 350, 14, (0, 0, 0)),              # Solo fecha
    "fecha_exp_completa": (120, 370, 14, (0, 0, 0)),     # Fecha con hora
    "fecha_ven": (310, 605, 90, (0, 0, 0))               # Vencimiento gigante
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
    inicio_letras = "GR"
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
    nuevo_consecutivo = max(consecutivos) + 2 if consecutivos else 1

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
            f.write("GSR1989\n")
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

def obtener_folio_representativo():
    try:
        with open("folio_representativo.txt") as f:
            return int(f.read().strip())
    except FileNotFoundError:
        with open("folio_representativo.txt", "w") as f:
            f.write("331997")
        return 331997

def incrementar_folio_representativo(folio_actual):
    nuevo = folio_actual + 1
    with open("folio_representativo.txt", "w") as f:
        f.write(str(nuevo))
    return nuevo

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_input = request.form.get("user")
        pass_input = request.form.get("pass")

        # Validar admin
        if user_input == USUARIO and pass_input == CONTRASENA:
            session["user"] = USUARIO
            session["rol"] = "admin"
            return redirect(url_for("seleccionar_entidad"))

        # Validar usuario tercero
        resultado = supabase.table("usuarios_terceros").select("*").eq("username", user_input).eq("password", pass_input).execute()
        datos = resultado.data
        if datos:
            session["user"] = user_input
            session["rol"] = "tercero"
            session["entidades_permitidas"] = datos[0].get("entidades_permitidas")
            return redirect(url_for("panel_tercero"))

        # Fallido
        return render_template("login.html", error="Credenciales incorrectas")

    return render_template("login.html")
    
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/seleccionar_entidad")
def seleccionar_entidad():
    if "user" not in session or session.get("rol") != "admin":
        return redirect(url_for("login"))
    return render_template("seleccionar_entidad.html")
    
# --- Formularios por entidad ---
# ——— al inicio del archivo, justo después de tus otros imports ———
# ——— función modificada ———

@app.route("/formulario", methods=["GET", "POST"])
def formulario_cdmx():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        d = request.form
        fol = generar_folio_automatico()
        ahora = datetime.now()
        fecha_visual = ahora.strftime(f"%d DE {meses_es[ahora.strftime('%B')]} DEL %Y").upper()
        vigencia_visual = (ahora + timedelta(days=30)).strftime("%d/%m/%Y")
        fecha_iso = ahora.isoformat()
        vigencia_iso = (ahora + timedelta(days=30)).isoformat()

        os.makedirs(OUTPUT_DIR, exist_ok=True)
        out = os.path.join(OUTPUT_DIR, f"{fol}_cdmx.pdf")
        doc = fitz.open("cdmxdigital2025ppp.pdf")
        pg = doc[0]

        pg.insert_text(coords_cdmx["folio"][:2], fol,
                       fontsize=coords_cdmx["folio"][2], color=coords_cdmx["folio"][3])
        pg.insert_text(coords_cdmx["fecha"][:2], fecha_visual,
                       fontsize=coords_cdmx["fecha"][2], color=coords_cdmx["fecha"][3])

        for key in ["marca", "serie", "linea", "motor", "anio"]:
            x, y, s, col = coords_cdmx[key]
            pg.insert_text((x, y), d[key], fontsize=s, color=col)

        pg.insert_text(coords_cdmx["vigencia"][:2], vigencia_visual,
                       fontsize=coords_cdmx["vigencia"][2], color=coords_cdmx["vigencia"][3])
        pg.insert_text(coords_cdmx["nombre"][:2], d["nombre"],
                       fontsize=coords_cdmx["nombre"][2], color=coords_cdmx["nombre"][3])

        # -------- Generar QR de texto --------
        qr_text = (
            f"Folio: {fol}\n"
            f"Marca: {d['marca']}\n"
            f"Línea: {d['linea']}\n"
            f"Año: {d['anio']}\n"
            f"Serie: {d['serie']}\n"
            f"Motor: {d['motor']}\n"
            f"Nombre: {d['nombre']}\n"
            F"SEMOVICDMX DIGITAL"
        )

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=2,
        )
        qr.add_data(qr_text)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        qr_path = os.path.join(OUTPUT_DIR, f"{fol}_cdmx_qr.png")
        img.save(qr_path)

        # -------- Insertar QR centrado abajo --------
        tam_qr = 1.6 * 28.35  # 1.6 cm → 45.36 pts       
        ancho_pagina = pg.rect.width

        x0 = (ancho_pagina / 2) - (tam_qr / 2)-19
        x1 = (ancho_pagina / 2) + (tam_qr / 2)-19

        y0 = 680.17  # 0.5 cm desde abajo
        y1 = y0 + tam_qr

        qr_rect = fitz.Rect(x0, y0, x1, y1)
        pg.insert_image(qr_rect, filename=qr_path, keep_proportion=False, overlay=True)
        # --------------------------------------------

        doc.save(out)
        doc.close()

        _guardar(
            fol, "CDMX",
            d["serie"], d["marca"], d["linea"],
            d["motor"], d["anio"], "",
            fecha_iso, vigencia_iso, d["nombre"]
        )

        return render_template("exitoso.html", folio=fol, cdmx=True)

    return render_template("formulario.html")

@app.route("/formulario_edomex", methods=["GET", "POST"])
def formulario_edomex():
    if request.method == "POST":
        folio  = generar_folio_automatico()
        marca  = request.form["marca"].upper()
        linea  = request.form["linea"].upper()
        anio   = request.form["anio"].upper()
        serie  = request.form["serie"].upper()
        motor  = request.form["motor"].upper()
        color  = request.form["color"].upper()
        nombre = request.form["nombre"].upper()

        ahora     = datetime.now()
        fecha_exp = ahora.strftime("%d/%m/%Y")
        fecha_ven = (ahora + timedelta(days=30)).strftime("%d/%m/%Y")

        plantilla = fitz.open("edomex_plantilla_alta_res.pdf")
        page      = plantilla[0]

        valores = {
            "folio":     folio,
            "marca":     marca,
            "linea":     linea,
            "anio":      anio,
            "serie":     serie,
            "motor":     motor,
            "color":     color,
            "fecha_exp": fecha_exp,
            "fecha_ven": fecha_ven,
            "nombre":    nombre,
        }

        for campo, texto in valores.items():
            if campo in coords_edomex:
                x, y, fs, col = coords_edomex[campo]
                page.insert_text((x, y), texto, fontsize=fs, color=col)

        cadena = (
            f"FOLIO: {folio}  "
            f"MARCA: {marca}  "
            f"LINEA: {linea}  "
            f"ANO: {anio}  "
            f"SERIE: {serie}  "
            f"MOTOR: {motor}  "
            f"COLOR: {color}  "
            f"NOMBRE: {nombre} " 
            f"EDOMEX DIGITAL"
        )

        codes = encode(cadena, columns=6, security_level=5)

        # 🧼 GENERAMOS IMAGEN EN ALTA CALIDAD DESDE AQUÍ (sin resize después)
        barcode_img = render_image(codes, scale=4)  # <- Esta línea hace la magia

        buf       = BytesIO()
        barcode_img.save(buf, format="PNG")
        img_bytes = buf.getvalue()

        # 💥 MEDIDA FIJA DE 4.1cm x 1.1cm en puntos (no crece, no se deforma)
        ancho_pt = int(4.1 * 28.35)  # 708.75 pt
        alto_pt  = int(1.1 * 28.35)  # 56.7 pt

        x0 = coords_edomex["serie"][0] - 50 - 150
        y0 = coords_edomex["serie"][1] - 121

        rect = fitz.Rect(
            x0,
            y0,
            x0 + ancho_pt,
            y0 + alto_pt
        )

        page.insert_image(rect, stream=img_bytes, keep_proportion=False)

        os.makedirs(OUTPUT_DIR, exist_ok=True)
        out_path = os.path.join(OUTPUT_DIR, f"{folio}_edomex.pdf")
        plantilla.save(out_path)
        plantilla.close()

        return render_template(
            "exitoso.html",
            ruta_pdf=url_for("abrir_pdf_edomex", folio=folio),
            folio=folio,
            edomex=True
        )

    return render_template("formulario_edomex.html")
    
@app.route("/formulario_morelos", methods=["GET", "POST"])
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

            # Generar contenido del QR
            texto_qr = f"""FOLIO: {fol}
NOMBRE: {d["nombre"]}
MARCA: {d["marca"]}
LINEA: {d["linea"]}
ANO: {d["anio"]}
SERIE: {d["serie"]}
MOTOR: {d["motor"]}
COLOR: {d["color"]}
TIPO: {d["tipo"]}
PERMISO MORELOS DIGITAL"""

            # Generar código QR como imagen
            qr = qrcode.make(texto_qr)
            img_buffer = io.BytesIO()
            qr.save(img_buffer, format="PNG")
            img_buffer.seek(0)

            img_pdf = fitz.Pixmap(img_buffer)
            width_cm = 0.4
            px_per_cm = 300 / 1.0  # 1 inch = 1.0 cm
            size_px = int(px_per_cm * width_cm)

            # Convertir a fitz.Rect
            x, y = 650, 128
            rect = fitz.Rect(x, y, x + size_px, y + size_px)

            pg2.insert_image(rect, pixmap=img_pdf)

        doc.save(out)
        doc.close()

        _guardar(fol, "Morelos", d["serie"], d["marca"], d["linea"], d["motor"], d["anio"], d["color"], fecha_iso, fecha_ven_iso, d["nombre"])
        return render_template("exitoso.html", folio=fol, morelos=True)

    return render_template("formulario_morelos.html")

@app.route("/formulario_oaxaca", methods=["GET", "POST"])
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

        # Insertar texto del formulario
        pg.insert_text(coords_oaxaca["folio"][:2], fol, fontsize=coords_oaxaca["folio"][2], color=coords_oaxaca["folio"][3])
        pg.insert_text(coords_oaxaca["fecha1"][:2], f1, fontsize=coords_oaxaca["fecha1"][2], color=coords_oaxaca["fecha1"][3])
        pg.insert_text(coords_oaxaca["fecha2"][:2], f1, fontsize=coords_oaxaca["fecha2"][2], color=coords_oaxaca["fecha2"][3])
        for key in ["marca", "serie", "linea", "motor", "anio", "color"]:
            x, y, s, col = coords_oaxaca[key]
            pg.insert_text((x, y), d[key], fontsize=s, color=col)
        pg.insert_text(coords_oaxaca["vigencia"][:2], f_ven, fontsize=coords_oaxaca["vigencia"][2], color=coords_oaxaca["vigencia"][3])
        pg.insert_text(coords_oaxaca["nombre"][:2], d["nombre"], fontsize=coords_oaxaca["nombre"][2], color=coords_oaxaca["nombre"][3])

        # --- Generar QR ---
        texto_qr = f"""FOLIO: {fol}
NOMBRE: {d['nombre']}
MARCA: {d['marca']}
LINEA: {d['linea']}
AÑO: {d['anio']}
SERIE: {d['serie']}
MOTOR: {d['motor']}
COLOR: {d['color']}
OAXACA PERMISOS DIGITALES"""

        qr = qrcode.QRCode(
            version=2,  # Ajusta para que el texto quepa sin pixelarse
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,  # Aumenta resolución
            border=2
        )
        qr.add_data(texto_qr.upper())
        qr.make(fit=True)

        img_qr = qr.make_image(fill_color="black", back_color="white").convert("RGB")

        # Convertir a Pixmap para PyMuPDF
        buf = BytesIO()
        img_qr.save(buf, format="PNG")
        buf.seek(0)
        qr_pix = fitz.Pixmap(buf.read())

        # Tamaño fijo: 1 cm x 1 cm
        cm = 42.52  # puntos por cm
        ancho_qr = alto_qr = cm * 1.5

        # Posición: desde la esquina inferior izquierda: 5cm hacia arriba y 3cm desde la derecha
        page_width = pg.rect.width
        x_qr = page_width - (0.5 * cm) - ancho_qr
        y_qr = 11.5 * cm

        # Insertar imagen
        pg.insert_image(
            fitz.Rect(x_qr, y_qr, x_qr + ancho_qr, y_qr + alto_qr),
            pixmap=qr_pix,
            overlay=True
        )

        # Guardar y cerrar
        doc.save(out)
        doc.close()

        _guardar(fol, "Oaxaca", d["serie"], d["marca"], d["linea"], d["motor"], d["anio"], d["color"], f1_iso, f_ven_iso, d["nombre"])
        return render_template("exitoso.html", folio=fol, oaxaca=True)

    return render_template("formulario_oaxaca.html")

@app.route("/formulario_gto", methods=["GET", "POST"])
def formulario_gto():
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
        out = os.path.join(OUTPUT_DIR, f"{fol}_gto.pdf")

        doc = fitz.open("permiso guanajuato.pdf")
        pg = doc[0]

        # Insertar texto del formulario
        pg.insert_text(coords_gto["folio"][:2], fol, fontsize=coords_gto["folio"][2], color=coords_gto["folio"][3])
        pg.insert_text(coords_gto["fecha1"][:2], f1, fontsize=coords_gto["fecha1"][2], color=coords_gto["fecha1"][3])
        pg.insert_text(coords_gto["fecha2"][:2], f1, fontsize=coords_gto["fecha2"][2], color=coords_gto["fecha2"][3])
        for key in ["marca", "serie", "linea", "motor", "anio", "color"]:
            x, y, s, col = coords_gto[key]
            pg.insert_text((x, y), d[key], fontsize=s, color=col)
        pg.insert_text(coords_gto["vigencia"][:2], f_ven, fontsize=coords_gto["vigencia"][2], color=coords_gto["vigencia"][3])
        pg.insert_text(coords_gto["nombre"][:2], d["nombre"], fontsize=coords_gto["nombre"][2], color=coords_gto["nombre"][3])

        # --- Generar QR ---
        texto_qr = f"""FOLIO: {fol}
NOMBRE: {d['nombre']}
MARCA: {d['marca']}
LINEA: {d['linea']}
AÑO: {d['anio']}
SERIE: {d['serie']}
MOTOR: {d['motor']}
COLOR: {d['color']}
GUANAJUATO PERMISOS DIGITALES"""

        qr = qrcode.QRCode(
            version=2,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=2
        )
        qr.add_data(texto_qr.upper())
        qr.make(fit=True)

        img_qr = qr.make_image(fill_color="black", back_color="white").convert("RGB")

        buf = BytesIO()
        img_qr.save(buf, format="PNG")
        buf.seek(0)
        qr_pix = fitz.Pixmap(buf.read())

        # Tamaño fijo: 1.5 cm x 1.5 cm
        cm = 42.52
        ancho_qr = alto_qr = cm * 1.5

        # Posición: 5cm arriba desde abajo y 3cm desde la derecha
        page_width = pg.rect.width
        x_qr = page_width - (0.5 * cm) - ancho_qr
        y_qr = 11.5 * cm

        pg.insert_image(
            fitz.Rect(x_qr, y_qr, x_qr + ancho_qr, y_qr + alto_qr),
            pixmap=qr_pix,
            overlay=True
        )

        doc.save(out)
        doc.close()

        _guardar(fol, "GTO", d["serie"], d["marca"], d["linea"], d["motor"], d["anio"], d["color"], f1_iso, f_ven_iso, d["nombre"])
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
    entidad = actual["entidad"]

    if request.method == "POST":
        # Actualiza datos en Supabase
        nuevos_datos = {
            "marca": request.form.get("marca"),
            "linea": request.form.get("linea"),
            "anio": request.form.get("anio"),
            "numero_serie": request.form.get("serie"),
            "numero_motor": request.form.get("motor"),
            "color": request.form.get("color"),
            "contribuyente": request.form.get("nombre"),
        }

        supabase.table("borradores_registros").update(nuevos_datos).eq("folio", folio).execute()

        # Solo Jalisco: regenera el PDF417 y el PDF
        if entidad == "Jalisco":
            generar_pdf_editado_jalisco(folio, nuevos_datos)

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
        pg.insert_text((930, 391), fol, fontsize=14, color=(0, 0, 0))

        # --- Imprimir FOLIO REPRESENTATIVO dos veces ---
        fol_representativo = int(obtener_folio_representativo())
        pg.insert_text((328, 804), str(fol_representativo), fontsize=32, color=(0, 0, 0))
        pg.insert_text((653, 200), str(fol_representativo), fontsize=45, color=(0, 0, 0))
        incrementar_folio_representativo(fol_representativo)

        # --- Imprimir FOLIO con asteriscos al estilo etiqueta ---
        pg.insert_text((910, 620), f"*{fol}*", fontsize=30, color=(0,0,0), fontname="Courier")
        pg.insert_text((1083, 800), "DIGITAL", fontsize=14, color=(0, 0, 0)) 
        
        # --- Generar imagen tipo INE y colocarla ---
        contenido_ine = f"""
FOLIO:{fol}
MARCA:{d.get('marca')}
LINEA:{d.get('linea')}
ANIO:{d.get('anio')}
SERIE:{d.get('serie')}
MOTOR:{d.get('motor')}
"""
        ine_img_path = os.path.join(OUTPUT_DIR, f"{fol}_inecode.png")
        generar_codigo_ine(contenido_ine, ine_img_path)

        # --- Insertar imagen en tamaño FIJO (siempre igual) ---
        pg.insert_image(fitz.Rect(937.65, 75, 1168.955, 132), filename=ine_img_path, keep_proportion=False, overlay=True)
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

import json

@app.route("/crear_usuario", methods=["GET", "POST"])
def crear_usuario():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        entidades = request.form.getlist("entidades")  # Lista de entidades seleccionadas

        # Serializa la lista para guardarla en texto en Supabase
        entidades_json = json.dumps(entidades)

        # Guardar en la tabla usuarios_terceros
        supabase.table("usuarios_terceros").insert({
            "username": username,
            "password": password,
            "entidades_permitidas": entidades_json
        }).execute()

        return redirect(url_for("seleccionar_entidad"))

    return render_template("crear_usuario.html")

@app.route("/panel_tercero")
def panel_tercero():
    if "user" not in session or session.get("rol") != "tercero":
        return redirect(url_for("login"))

    # Cargar de supabase el user logueado
    username = session.get("user")
    res = supabase.table("usuarios_terceros").select("*").eq("username", username).execute()
    if not res.data:
        return redirect(url_for("login"))

    entidades_json = res.data[0]["entidades_permitidas"]
    try:
        entidades = json.loads(entidades_json)
    except Exception:
        entidades = []

    return render_template("panel_tercero.html", entidades=entidades)

def generar_pdf_editado_jalisco(folio, datos):
    ahora = datetime.now()
    ven_f = (ahora + timedelta(days=30)).strftime("%d/%m/%Y")
    f_exp_iso = ahora.isoformat()
    f_ven_iso = (ahora + timedelta(days=30)).isoformat()

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, f"{folio}_jalisco.pdf")
    doc = fitz.open("jalisco.pdf")
    pg = doc[0]

    # Insertar datos editados
    for campo in ["marca", "linea", "anio", "serie", "nombre", "color"]:
        x, y, s, col = coords_jalisco[campo]
        valor = datos.get(campo, "")
        pg.insert_text((x, y), valor, fontsize=s, color=col)
    
    # Insertar nueva vigencia
    pg.insert_text(coords_jalisco["fecha_ven"][:2], ven_f, fontsize=coords_jalisco["fecha_ven"][2], color=coords_jalisco["fecha_ven"][3])

    # Insertar el folio
    pg.insert_text((930, 391), folio, fontsize=14, color=(0,0,0))

    # Folio representativo (opcional, puedes quitar esto si ya no se actualiza al editar)
    fol_representativo = int(obtener_folio_representativo())
    pg.insert_text((328, 804), str(fol_representativo), fontsize=32, color=(0,0,0))
    pg.insert_text((653, 200), str(fol_representativo), fontsize=45, color=(0,0,0))

    # Formato tipo etiqueta
    pg.insert_text((910, 620), f"*{folio}*", fontsize=30, color=(0,0,0), fontname="Courier")
    pg.insert_text((1083, 800), "DIGITAL", fontsize=14, color=(0,0,0)) 

    # Generar nuevo PDF417
    contenido_ine = f"""
FOLIO:{folio}
MARCA:{datos.get('marca')}
LINEA:{datos.get('linea')}
ANIO:{datos.get('anio')}
SERIE:{datos.get('serie')}
MOTOR:{datos.get('numero_motor')}
NOMBRE:{datos.get('nombre')}
"""
    ine_img_path = os.path.join(OUTPUT_DIR, f"{folio}_inecode.png")
    generar_codigo_ine(contenido_ine, ine_img_path)

    # Insertar imagen en el PDF
    pg.insert_image(fitz.Rect(937.65, 75, 1168.955, 132), filename=ine_img_path, keep_proportion=False, overlay=True)

    # Guardar el PDF editado
    doc.save(out_path)
    doc.close()

    # Subir a Supabase
    url_pdf = subir_pdf_supabase(out_path, f"{folio}_jalisco.pdf")
    supabase.table("borradores_registros").update({"url_pdf": url_pdf}).eq("folio", folio).execute()

@app.route("/reimprimir_jalisco/<folio>", methods=["GET", "POST"])
def reimprimir_jalisco(folio):
    if "user" not in session:
        return redirect(url_for("login"))

    # Obtener datos actuales de Supabase
    res = supabase.table("borradores_registros").select("*").eq("folio", folio).execute()
    if not res.data:
        return redirect(url_for("listar"))
    actual = res.data[0]

    if request.method == "POST":
        # Formulario enviado con datos editados
        nuevos_datos = {
            "marca": request.form.get("marca"),
            "linea": request.form.get("linea"),
            "anio": request.form.get("anio"),
            "serie": request.form.get("serie"),
            "numero_motor": request.form.get("numero_motor"),
            "nombre": request.form.get("nombre"),
            "color": request.form.get("color"),
        }
        generar_pdf_editado_jalisco(folio, nuevos_datos)
        return redirect(url_for("abrir_pdf_jalisco", folio=folio))

    # GET: Renderiza formulario precargado
    return render_template("editar_formulario_jalisco.html", datos=actual)

@app.route("/abrir_pdf/<entidad>/<folio>")
def abrir_pdf(entidad, folio):
    # Verifica sesión
    if "user" not in session:
        return redirect(url_for("login"))

    # Busca en Supabase
    res = supabase.table("borradores_registros").select("url_pdf").eq("folio", folio).execute()
    if not res.data or not res.data[0].get("url_pdf"):
        return "PDF no encontrado o no disponible.", 404

    url_pdf = res.data[0]["url_pdf"]
    return redirect(url_pdf)

# <- Aquí la pegas
generar_folio_automatico = generar_folio_por_mes

if __name__ == "__main__":
    import os
    puerto = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=puerto, debug=True)
