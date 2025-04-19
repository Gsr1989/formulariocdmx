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

# Coordenadas CDMX
coords_cdmx = {
    "folio": (87, 130, 12, (1, 0, 0)),
    "fecha": (130, 145, 12, (0, 0, 0)),
    "marca": (87, 283, 12, (0, 0, 0)),
    "serie": (375, 290, 12, (0, 0, 0)),
    "linea": (160, 283, 12, (0, 0, 0)),
    "motor": (375, 307, 12, (0, 0, 0)),
    "anio": (240, 283, 12, (0, 0, 0)),
    "vigencia": (375, 323, 12, (0, 0, 0)),
    "nombre": (375, 340, 12, (0, 0, 0)),
}

# Coordenadas EDOMEX
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

# Coordenadas MORELOS
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

# Coordenadas OAXACA
coords_oaxaca = {
    "folio": (553, 96, 16, (1, 0, 0)),
    "fecha1": (168, 130, 12, (0, 0, 0)),
    "fecha2": (147, 636, 12, (0, 0, 0)),
    "marca": (50, 215, 12, (0, 0, 0)),
    "serie": (200, 265, 12, (0, 0, 0)),
    "linea": (200, 215, 12, (0, 0, 0)),
    "motor": (360, 258, 12, (0, 0, 0)),
    "anio": (360, 215, 12, (0, 0, 0)),
    "vigencia": (410, 130, 12, (0, 0, 0)),
    "nombre": (133, 149, 10, (0, 0, 0)),
}

# Coordenadas GUANAJUATO
coords_gto = {
    "folio": (100, 150, 12, (1, 0, 0)),
    "marca": (100, 250, 12, (0, 0, 0)),
    "linea": (300, 250, 12, (0, 0, 0)),
    "anio": (500, 250, 12, (0, 0, 0)),
    "serie": (100, 280, 12, (0, 0, 0)),
    "motor": (300, 280, 12, (0, 0, 0)),
    "color": (500, 280, 12, (0, 0, 0)),
    "nombre": (100, 310, 12, (0, 0, 0)),
    "fecha": (200, 350, 12, (0, 0, 0)),
    "vigencia": (400, 350, 12, (0, 0, 0)),
}

def generar_folio_automatico(ruta="folios_globales.txt"):
    mes_actual = datetime.now().strftime("%m")
    if not os.path.exists(ruta):
        open(ruta, "w").close()
    with open(ruta) as f:
        existentes = [l.strip() for l in f]
    del_mes = [f for f in existentes if f.startswith(mes_actual)]
    nuevo = f"{mes_actual}{len(del_mes)+1:03d}"
    with open(ruta, "a") as f:
        f.write(nuevo+"\n")
    return nuevo

@app.route("/", methods=["GET","POST"])
def login():
    if request.method=="POST":
        if request.form["user"]==USUARIO and request.form["pass"]==CONTRASENA:
            return redirect(url_for("seleccionar_entidad"))
    return render_template("login.html")

@app.route("/seleccionar_entidad")
def seleccionar_entidad():
    return render_template("seleccionar_entidad.html")

# ——— CDMX —————————————————————————————————————————
@app.route("/formulario", methods=["GET","POST"])
def formulario_cdmx():
    if request.method=="POST":
        data=request.form
        folio=generar_folio_automatico()
        ahora=datetime.now()
        fecha_exp=ahora.strftime(f"%d DE {meses_es[ahora.strftime('%B')]} DEL %Y").upper()
        vigencia=(ahora+timedelta(days=30)).strftime("%d/%m/%Y")
        path=os.path.join(OUTPUT_DIR,f"{folio}_cdmx.pdf")
        os.makedirs(OUTPUT_DIR,exist_ok=True)
        doc=fitz.open("cdmxdigital2025ppp.pdf"); page=doc[0]
        page.insert_text(coords_cdmx["folio"][:2],folio,fontsize=coords_cdmx["folio"][2],color=coords_cdmx["folio"][3])
        page.insert_text(coords_cdmx["fecha"][:2],fecha_exp,fontsize=coords_cdmx["fecha"][2],color=coords_cdmx["fecha"][3])
        for c in ["marca","serie","linea","motor","anio","vigencia","nombre"]:
            val = vigencia if c=="vigencia" else data[c]
            x,y,s,col=coords_cdmx[c]; page.insert_text((x,y),val,fontsize=s,color=col)
        doc.save(path); doc.close()
        return send_file(path,as_attachment=True)
    return render_template("formulario.html")

# ——— EDOMEX ————————————————————————————————————————
@app.route("/formulario_edomex", methods=["GET","POST"])
def formulario_edomex():
    if request.method=="POST":
        data=request.form
        folio=generar_folio_automatico()
        ahora=datetime.now()
        fe=ahora.strftime("%d/%m/%Y")
        fv=(ahora+timedelta(days=30)).strftime("%d/%m/%Y")
        path=os.path.join(OUTPUT_DIR,f"{folio}_edomex.pdf")
        os.makedirs(OUTPUT_DIR,exist_ok=True)
        doc=fitz.open("edomex_plantilla_alta_res.pdf"); page=doc[0]
        page.insert_text(coords_edomex["folio"][:2],folio,fontsize=coords_edomex["folio"][2],color=coords_edomex["folio"][3])
        for c in ["marca","linea","anio","motor","serie","color"]:
            x,y,s,col=coords_edomex[c]; page.insert_text((x,y),data[c],fontsize=s,color=col)
        page.insert_text(coords_edomex["fecha_exp"][:2],fe,fontsize=coords_edomex["fecha_exp"][2],color=coords_edomex["fecha_exp"][3])
        page.insert_text(coords_edomex["fecha_ven"][:2],fv,fontsize=coords_edomex["fecha_ven"][2],color=coords_edomex["fecha_ven"][3])
        page.insert_text(coords_edomex["nombre"][:2],data["nombre"],fontsize=coords_edomex["nombre"][2],color=coords_edomex["nombre"][3])
        doc.save(path); doc.close()
        return send_file(path,as_attachment=True)
    return render_template("formulario_edomex.html")

# ——— MORELOS ———————————————————————————————————————
@app.route("/formulario_morelos", methods=["GET","POST"])
def formulario_morelos():
    if request.method=="POST":
        data=request.form
        folio=generar_folio_automatico()
        ahora=datetime.now()
        fl=ahora.strftime(f"%d DE {meses_es[ahora.strftime('%B')]} DEL %Y").upper()
        fc=ahora.strftime("%d/%m/%Y")
        fv=(ahora+timedelta(days=30)).strftime("%d/%m/%Y")
        path=os.path.join(OUTPUT_DIR,f"{folio}_morelos.pdf")
        os.makedirs(OUTPUT_DIR,exist_ok=True)
        doc=fitz.open("morelos_hoja1_imagen.pdf"); page=doc[0]
        page.insert_text(coords_morelos["folio"][:2],folio,fontsize=coords_morelos["folio"][2],color=coords_morelos["folio"][3])
        page.insert_text(coords_morelos["fecha"][:2],fl,fontsize=coords_morelos["fecha"][2],color=coords_morelos["fecha"][3])
        page.insert_text(coords_morelos["vigencia"][:2],fv,fontsize=coords_morelos["vigencia"][2],color=coords_morelos["vigencia"][3])
        for c in ["marca","linea","anio","serie","motor","color","tipo","nombre"]:
            x,y,s,col=coords_morelos[c]; page.insert_text((x,y),data[c],fontsize=s,color=col)
        if len(doc)>1:
            fx,fy,fz,fc=coords_morelos["fecha_hoja2"]
            doc[1].insert_text((fx,fy),fc,fontsize=fz,color=fc)
        doc.save(path); doc.close()
        return send_file(path,as_attachment=True)
    return render_template("formulario_morelos.html")

# ——— OAXACA ———————————————————————————————————————
@app.route("/formulario_oaxaca", methods=["GET","POST"])
def formulario_oaxaca():
    if request.method=="POST":
        data=request.form
        folio=generar_folio_automatico()
        ahora=datetime.now()
        f1=ahora.strftime("%d/%m/%Y")
        f2=f1
        fv=(ahora+timedelta(days=30)).strftime("%d/%m/%Y")
        path=os.path.join(OUTPUT_DIR,f"{folio}_oaxaca.pdf")
        os.makedirs(OUTPUT_DIR,exist_ok=True)
        doc=fitz.open("oaxacachido.pdf"); page=doc[0]
        page.insert_text(coords_oaxaca["folio"][:2],folio,fontsize=coords_oaxaca["folio"][2],color=coords_oaxaca["folio"][3])
        page.insert_text(coords_oaxaca["fecha1"][:2],f1,fontsize=coords_oaxaca["fecha1"][2],color=coords_oaxaca["fecha1"][3])
        page.insert_text(coords_oaxaca["fecha2"][:2],f2,fontsize=coords_oaxaca["fecha2"][2],color=coords_oaxaca["fecha2"][3])
        for c in ["marca","serie","linea","motor","anio","vigencia","nombre"]:
            x,y,s,col=coords_oaxaca[c]; val=fv if c=="vigencia" else data[c]
            page.insert_text((x,y),val,fontsize=s,color=col)
        doc.save(path); doc.close()
        return send_file(path,as_attachment=True)
    return render_template("formulario_oaxaca.html")

# ——— GUANAJUATO —————————————————————————————————————
@app.route("/formulario_guanajuato", methods=["GET","POST"])
def formulario_gto():
    if request.method=="POST":
        data=request.form
        folio=generar_folio_automatico()
        ahora=datetime.now()
        f=ahora.strftime("%d/%m/%Y")
        fv=(ahora+timedelta(days=30)).strftime("%d/%m/%Y")
        path=os.path.join(OUTPUT_DIR,f"{folio}_gto.pdf")
        os.makedirs(OUTPUT_DIR,exist_ok=True)
        doc=fitz.open("permiso guanajuato.pdf"); page=doc[0]
        page.insert_text(coords_gto["folio"][:2],folio,fontsize=coords_gto["folio"][2],color=coords_gto["folio"][3])
        page.insert_text(coords_gto["fecha"][:2],f,fontsize=coords_gto["fecha"][2],color=coords_gto["fecha"][3])
        page.insert_text(coords_gto["vigencia"][:2],fv,fontsize=coords_gto["vigencia"][2],color=coords_gto["vigencia"][3])
        for c in ["marca","linea","anio","serie","motor","color","nombre"]:
            x,y,s,col=coords_gto[c]; page.insert_text((x,y),data[c],fontsize=s,color=col)
        doc.save(path); doc.close()
        return send_file(path,as_attachment=True)
    return render_template("formulario_guanajuato.html")

if __name__ == "__main__":
    app.run()
