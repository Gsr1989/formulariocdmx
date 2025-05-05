from flask import Flask, render_template, request, send_file, redirect, url_for
from datetime import datetime, timedelta
import fitz  # PyMuPDF
import os, string, csv

app = Flask(__name__)
OUTPUT_DIR = "static/pdfs"
USUARIO = "Gsr89roja"
CONTRASENA = "serg890105"

meses_es = {
    "January": "ENERO",   "February": "FEBRERO",
    "March":   "MARZO",   "April":    "ABRIL",
    "May":     "MAYO",    "June":     "JUNIO",
    "July":    "JULIO",   "August":   "AGOSTO",
    "September":"SEPTIEMBRE","October":"OCTUBRE",
    "November":"NOVIEMBRE","December":"DICIEMBRE",
}

# Coordenadas para cada plantilla...
coords_cdmx = {
    "folio": (87,130,14,(1,0,0)), "fecha": (130,145,12,(0,0,0)),
    "marca": (87,290,11,(0,0,0)), "serie": (375,290,11,(0,0,0)),
    "linea": (87,307,11,(0,0,0)), "motor": (375,307,11,(0,0,0)),
    "anio":  (87,323,11,(0,0,0)), "vigencia": (375,323,11,(0,0,0)),
    "nombre":(375,340,11,(0,0,0)),
}
coords_edomex = {
    "folio": (535,135,14,(1,0,0)), "marca": (109,190,10,(0,0,0)),
    "linea": (238,190,10,(0,0,0)), "anio": (410,190,10,(0,0,0)),
    "motor": (104,233,10,(0,0,0)), "serie": (230,233,10,(0,0,0)),
    "color": (400,233,10,(0,0,0)), "fecha_exp": (190,280,10,(0,0,0)),
    "fecha_ven": (380,280,10,(0,0,0)), "nombre": (394,320,10,(0,0,0)),
}
coords_morelos = {
    "folio": (665,282,18,(1,0,0)), "placa": (200,200,60,(0,0,0)),
    "fecha": (200,340,14,(0,0,0)), "vigencia": (600,340,14,(0,0,0)),
    "marca": (110,425,14,(0,0,0)), "linea": (110,455,14,(0,0,0)),
    "anio":  (110,485,14,(0,0,0)), "serie": (460,420,14,(0,0,0)),
    "motor": (460,445,14,(0,0,0)), "color": (460,395,14,(0,0,0)),
    "tipo":  (510,470,14,(0,0,0)), "nombre": (150,370,14,(0,0,0)),
    "fecha_hoja2": (100,100,14,(0,0,0)),
}
coords_oaxaca = {
    "folio": (553,96,16,(1,0,0)), "fecha1": (168,130,12,(0,0,0)),
    "fecha2": (140,540,10,(0,0,0)), "marca": (50,215,12,(0,0,0)),
    "serie": (200,258,12,(0,0,0)), "linea": (200,215,12,(0,0,0)),
    "motor": (360,258,12,(0,0,0)), "anio": (360,215,12,(0,0,0)),
    "color": (50,258,12,(0,0,0)), "vigencia": (410,130,12,(0,0,0)),
    "nombre": (133,149,10,(0,0,0)),
}
coords_gto = {
    "folio": (1800,455,60,(1,0,0)), "fecha": (2200,580,35,(0,0,0)),
    "marca": (385,715,35,(0,0,0)), "linea": (800,715,35,(0,0,0)),
    "anio":  (1145,715,35,(0,0,0)), "serie": (350,800,35,(0,0,0)),
    "motor": (1290,800,35,(0,0,0)), "color": (1960,715,35,(0,0,0)),
    "nombre": (950,1100,90,(0,0,0)), "vigencia": (2200,645,35,(0,0,0)),
}

def generar_folio_automatico(ruta="folios_globales.txt"):
    mes = datetime.now().strftime("%m")
    if not os.path.exists(ruta):
        open(ruta,"w").close()
    with open(ruta) as f:
        líneas = [l.strip() for l in f]
    este_mes = [x for x in líneas if x.startswith(mes)]
    nuevo = f"{mes}{len(este_mes)+1:03d}"
    with open(ruta,"a") as f:
        f.write(nuevo+"\n")
    return nuevo

def generar_placa_digital():
    archivo = "placas_digitales.txt"
    abc = string.ascii_uppercase
    if not os.path.exists(archivo):
        with open(archivo,"w") as f:
            f.write("LRU0000\n")
    pref, num = open(archivo).read().strip().split("\n")[-1][:3], int(open(archivo).read().strip().split("\n")[-1][3:])
    if num < 9999:
        nuevo = f"{pref}{num+1:04d}"
    else:
        l1,l2,l3 = list(pref)
        i3 = abc.index(l3)
        if i3<25:      l3=abc[i3+1]
        else:
            i2=abc.index(l2)
            if i2<25: l2=abc[i2+1]; l3='A'
            else:    l1=abc[(abc.index(l1)+1)%26]; l2=l3='A'
        nuevo = f"{l1}{l2}{l3}0000"
    with open(archivo,"a") as f:
        f.write(nuevo+"\n")
    return nuevo

@app.route("/", methods=["GET","POST"])
def login():
    if request.method=="POST" and \
       request.form["user"]==USUARIO and request.form["pass"]==CONTRASENA:
        return redirect(url_for("seleccionar_entidad"))
    return render_template("login.html")

@app.route("/seleccionar_entidad")
def seleccionar_entidad():
    return render_template("seleccionar_entidad.html")

def _guardar(folio, entidad, fecha, nombre):
    """Escribe en registros.csv: folio,entidad,fecha,nombre"""
    with open("registros.csv","a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([folio, entidad, fecha, nombre])

@app.route("/formulario", methods=["GET","POST"])
def formulario_cdmx():
    if request.method=="POST":
        d=request.form
        folio=generar_folio_automatico()
        ahora=datetime.now()
        f_exp=ahora.strftime(f"%d DE {meses_es[ahora.strftime('%B')]} DEL %Y").upper()
        f_ven=(ahora+timedelta(days=30)).strftime("%d/%m/%Y")
        out=os.path.join(OUTPUT_DIR,f"{folio}_cdmx.pdf")
        os.makedirs(OUTPUT_DIR,exist_ok=True)
        doc, pg = fitz.open("cdmxdigital2025ppp.pdf"), None
        pg=doc[0]
        pg.insert_text(coords_cdmx["folio"][:2],folio,fontsize=coords_cdmx["folio"][2],color=coords_cdmx["folio"][3])
        pg.insert_text(coords_cdmx["fecha"][:2],f_exp,fontsize=coords_cdmx["fecha"][2],color=coords_cdmx["fecha"][3])
        for k in ["marca","serie","linea","motor","anio"]:
            x,y,s,col=coords_cdmx[k]
            pg.insert_text((x,y),d[k],fontsize=s,color=col)
        x,y,s,col=coords_cdmx["vigencia"]
        pg.insert_text((x,y),f_ven,fontsize=s,color=col)
        x,y,s,col=coords_cdmx["nombre"]
        pg.insert_text((x,y),d["nombre"],fontsize=s,color=col)
        doc.save(out); doc.close()
        _guardar(folio, "CDMX", f_exp, d["nombre"])
        return render_template("exitoso.html", folio=folio, cdmx=True)
    return render_template("formulario.html")

@app.route("/formulario_edomex", methods=["GET","POST"])
def formulario_edomex():
    if request.method=="POST":
        d=request.form
        folio=generar_folio_automatico()
        ahora=datetime.now()
        f_exp=ahora.strftime("%d/%m/%Y")
        f_ven=(ahora+timedelta(days=30)).strftime("%d/%m/%Y")
        out=os.path.join(OUTPUT_DIR,f"{folio}_edomex.pdf")
        os.makedirs(OUTPUT_DIR,exist_ok=True)
        doc, pg = fitz.open("edomex_plantilla_alta_res.pdf"), None
        pg=doc[0]
        pg.insert_text(coords_edomex["folio"][:2],folio,fontsize=coords_edomex["folio"][2],color=coords_edomex["folio"][3])
        for key in ["marca","linea","anio","motor","serie","color"]:
            x,y,s,col=coords_edomex[key]
            pg.insert_text((x,y),d[key],fontsize=s,color=col)
        x,y,s,col=coords_edomex["fecha_exp"]
        pg.insert_text((x,y),f_exp,fontsize=s,color=col)
        x,y,s,col=coords_edomex["fecha_ven"]
        pg.insert_text((x,y),f_ven,fontsize=s,color=col)
        x,y,s,col=coords_edomex["nombre"]
        pg.insert_text((x,y),d["nombre"],fontsize=s,color=col)
        doc.save(out); doc.close()
        _guardar(folio, "EDOMEX", f_exp, d["nombre"])
        return render_template("exitoso.html", folio=folio, edomex=True)
    return render_template("formulario_edomex.html")

@app.route("/formulario_morelos", methods=["GET","POST"])
def formulario_morelos():
    if request.method=="POST":
        d=request.form
        folio=generar_folio_automatico()
        placa=generar_placa_digital()
        ahora=datetime.now()
        f_larga=ahora.strftime(f"%d DE {meses_es[ahora.strftime('%B')]} DEL %Y").upper()
        f_corta=ahora.strftime("%d/%m/%Y")
        f_ven=(ahora+timedelta(days=30)).strftime("%d/%m/%Y")
        out=os.path.join(OUTPUT_DIR,f"{folio}_morelos.pdf")
        os.makedirs(OUTPUT_DIR,exist_ok=True)
        doc, pg = fitz.open("morelos_hoja1_imagen.pdf"), None
        pg=doc[0]
        pg.insert_text(coords_morelos["folio"][:2],folio,fontsize=coords_morelos["folio"][2],color=coords_morelos["folio"][3])
        pg.insert_text(coords_morelos["placa"][:2],placa,fontsize=coords_morelos["placa"][2],color=coords_morelos["placa"][3])
        pg.insert_text(coords_morelos["fecha"][:2],f_larga,fontsize=coords_morelos["fecha"][2],color=coords_morelos["fecha"][3])
        pg.insert_text(coords_morelos["vigencia"][:2],f_ven,fontsize=coords_morelos["vigencia"][2],color=coords_morelos["vigencia"][3])
        for key in ["marca","linea","anio","serie","motor","color","tipo"]:
            x,y,s,col=coords_morelos[key]
            pg.insert_text((x,y),d[key],fontsize=s,color=col)
        x,y,s,col=coords_morelos["nombre"]
        pg.insert_text((x,y),d["nombre"],fontsize=s,color=col)
        if len(doc)>1:
            x,y,s,col=coords_morelos["fecha_hoja2"]
            doc[1].insert_text((x,y),f_corta,fontsize=s,color=col)
        doc.save(out); doc.close()
        _guardar(folio, "Morelos", f_larga, d["nombre"])
        return render_template("exitoso.html", folio=folio, morelos=True)
    return render_template("formulario_morelos.html")

@app.route("/formulario_oaxaca", methods=["GET","POST"])
def formulario_oaxaca():
    if request.method=="POST":
        d=request.form
        folio=generar_folio_automatico()
        ahora=datetime.now()
        f1=ahora.strftime("%d/%m/%Y")
        f_ven=(ahora+timedelta(days=30)).strftime("%d/%m/%Y")
        out=os.path.join(OUTPUT_DIR,f"{folio}_oaxaca.pdf")
        os.makedirs(OUTPUT_DIR,exist_ok=True)
        doc, pg = fitz.open("oaxacachido.pdf"), None
        pg=doc[0]
        pg.insert_text(coords_oaxaca["folio"][:2],folio,fontsize=coords_oaxaca["folio"][2],color=coords_oaxaca["folio"][3])
        pg.insert_text(coords_oaxaca["fecha1"][:2],f1,fontsize=coords_oaxaca["fecha1"][2],color=coords_oaxaca["fecha1"][3])
        pg.insert_text(coords_oaxaca["fecha2"][:2],f1,fontsize=coords_oaxaca["fecha2"][2],color=coords_oaxaca["fecha2"][3])
        for key in ["marca","serie","linea","motor","anio","color"]:
            x,y,s,col=coords_oaxaca[key]
            pg.insert_text((x,y),d[key],fontsize=s,color=col)
        x,y,s,col=coords_oaxaca["vigencia"]
        pg.insert_text((x,y),f_ven,fontsize=s,color=col)
        x,y,s,col=coords_oaxaca["nombre"]
        pg.insert_text((x,y),d["nombre"],fontsize=s,color=col)
        doc.save(out); doc.close()
        _guardar(folio, "Oaxaca", f1, d["nombre"])
        return render_template("exitoso.html", folio=folio, oaxaca=True)
    return render_template("formulario_oaxaca.html")

@app.route("/formulario_gto", methods=["GET","POST"])
def formulario_gto():
    if request.method=="POST":
        d=request.form
        folio=generar_folio_automatico()
        ahora=datetime.now()
        f_exp=ahora.strftime("%d/%m/%Y")
        f_ven=(ahora+timedelta(days=30)).strftime("%d/%m/%Y")
        out=os.path.join(OUTPUT_DIR,f"{folio}_gto.pdf")
        os.makedirs(OUTPUT_DIR,exist_ok=True)
        doc, pg = fitz.open("permiso guanajuato.pdf"), None
        pg=doc[0]
        pg.insert_text(coords_gto["folio"][:2],folio,fontsize=coords_gto["folio"][2],color=coords_gto["folio"][3])
        pg.insert_text(coords_gto["fecha"][:2],f_exp,fontsize=coords_gto["fecha"][2],color=coords_gto["fecha"][3])
        for key in ["marca","linea","anio","serie","motor","color"]:
            x,y,s,col=coords_gto[key]
            pg.insert_text((x,y),d[key],fontsize=s,color=col)
        x,y,s,col=coords_gto["vigencia"]
        pg.insert_text((x,y),f_ven,fontsize=s,color=col)
        x,y,s,col=coords_gto["nombre"]
        pg.insert_text((x,y),d["nombre"],fontsize=s,color=col)
        doc.save(out); doc.close()
        _guardar(folio, "GTO", f_exp, d["nombre"])
        return render_template("exitoso.html", folio=folio, gto=True)
    return render_template("formulario_gto.html")

@app.route("/listar")
def listar():
    registros = []
    if os.path.exists("registros.csv"):
        with open("registros.csv", encoding="utf-8") as f:
            for folio, entidad, fecha, nombre in csv.reader(f):
                registros.append({
                    "folio": folio,
                    "entidad": entidad,
                    "fecha": fecha,
                    "nombre": nombre
                })
    return render_template("listar.html", registros=registros)

# Rutas de descarga:
@app.route("/abrir_pdf/<folio>")
def abrir_pdf(folio):
    p = os.path.join(OUTPUT_DIR, f"{folio}_cdmx.pdf")
    return send_file(p, as_attachment=True) if os.path.exists(p) else ("No encontrado",404)
@app.route("/abrir_pdf_edomex/<folio>")
def abrir_pdf_edomex(folio):
    p = os.path.join(OUTPUT_DIR, f"{folio}_edomex.pdf")
    return send_file(p, as_attachment=True) if os.path.exists(p) else ("No encontrado",404)
@app.route("/abrir_pdf_morelos/<folio>")
def abrir_pdf_morelos(folio):
    p = os.path.join(OUTPUT_DIR, f"{folio}_morelos.pdf")
    return send_file(p, as_attachment=True) if os.path.exists(p) else ("No encontrado",404)
@app.route("/abrir_pdf_oaxaca/<folio>")
def abrir_pdf_oaxaca(folio):
    p = os.path.join(OUTPUT_DIR, f"{folio}_oaxaca.pdf")
    return send_file(p, as_attachment=True) if os.path.exists(p) else ("No encontrado",404)
@app.route("/abrir_pdf_gto/<folio>")
def abrir_pdf_gto(folio):
    p = os.path.join(OUTPUT_DIR, f"{folio}_gto.pdf")
    return send_file(p, as_attachment=True) if os.path.exists(p) else ("No encontrado",404)

@app.route("/logout")
def logout():
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
