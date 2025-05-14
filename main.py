# main.py
from flask import Flask, render_template, request, send_file, redirect, url_for, flash, session
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
    "January":"ENERO","February":"FEBRERO","March":"MARZO",
    "April":"ABRIL","May":"MAYO","June":"JUNIO",
    "July":"JULIO","August":"AGOSTO","September":"SEPTIEMBRE",
    "October":"OCTUBRE","November":"NOVIEMBRE","December":"DICIEMBRE"
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
        open(ruta,"w").close()
    with open(ruta) as f:
        lineas = [l.strip() for l in f]
    este_mes = [x for x in lineas if x.startswith(mes)]
    fol = f"{mes}{len(este_mes)+1:03d}"
    with open(ruta,"a") as f:
        f.write(fol+"\n")
    return fol

def generar_placa_digital():
    archivo = "placas_digitales.txt"
    abc = string.ascii_uppercase
    if not os.path.exists(archivo):
        with open(archivo,"w") as f:
            f.write("LRU0000\n")
    ultimo = open(archivo).read().strip().split("\n")[-1]
    pref, num = ultimo[:3], int(ultimo[3:])
    if num<9999:
        nuevo = f"{pref}{num+1:04d}"
    else:
        l1,l2,l3 = list(pref)
        i3 = abc.index(l3)
        if i3<25: l3 = abc[i3+1]
        else:
            i2 = abc.index(l2)
            if i2<25: l2=abc[i2+1]; l3="A"
            else: l1=abc[(abc.index(l1)+1)%26]; l2=l3="A"
        nuevo = f"{l1}{l2}{l3}0000"
    with open(archivo,"a") as f:
        f.write(nuevo+"\n")
    return nuevo

def _guardar(folio, entidad, serie, marca, linea, motor, anio, color, fecha_exp, fecha_ven, nombre):
    existe = os.path.exists("registros.csv")
    with open("registros.csv","a",newline="",encoding="utf-8") as f:
        w = csv.writer(f)
        if not existe:
            w.writerow([
                "folio","entidad","serie",
                "marca","linea","motor","anio","color",
                "fecha_exp","fecha_ven","nombre"
            ])
        w.writerow([
            folio, entidad, serie,
            marca, linea, motor, anio, color,
            fecha_exp, fecha_ven, nombre
        ])

def cargar_registros():
    regs=[]
    if os.path.exists("registros.csv"):
        with open("registros.csv",encoding="utf-8") as f:
            r=csv.reader(f)
            next(r,None)
            for row in r:
                if len(row)==11:
                    regs.append({
                        "folio":    row[0],
                        "entidad":  row[1],
                        "serie":    row[2],
                        "marca":    row[3],
                        "linea":    row[4],
                        "motor":    row[5],
                        "anio":     row[6],
                        "color":    row[7],
                        "fecha_exp":row[8],
                        "fecha_ven":row[9],
                        "nombre":   row[10]
                    })
    return regs

def guardar_registros(regs):
    with open("registros.csv","w",newline="",encoding="utf-8") as f:
        w=csv.writer(f)
        w.writerow([
            "folio","entidad","serie",
            "marca","linea","motor","anio","color",
            "fecha_exp","fecha_ven","nombre"
        ])
        for r in regs:
            w.writerow([
                r["folio"],r["entidad"],r["serie"],
                r["marca"],r["linea"],r["motor"],r["anio"],r["color"],
                r["fecha_exp"],r["fecha_ven"],r["nombre"]
            ])

@app.route("/", methods=["GET","POST"])
def login():
    if request.method=="POST" and \
       request.form["user"]==USUARIO and request.form["pass"]==CONTRASENA:
        session["user"]=USUARIO
        return redirect(url_for("seleccionar_entidad"))
    return render_template("login.html")

@app.route("/seleccionar_entidad")
def seleccionar_entidad():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("seleccionar_entidad.html")

@app.route("/formulario", methods=["GET","POST"])
def formulario_cdmx():
    if "user" not in session: return redirect(url_for("login"))
    if request.method=="POST":
        d=request.form
        fol=generar_folio_automatico()
        ahora=datetime.now()
        f_exp=ahora.strftime(f"%d DE {meses_es[ahora.strftime('%B')]} DEL %Y").upper()
        f_ven=(ahora+timedelta(days=30)).strftime("%d/%m/%Y")
        out=os.path.join(OUTPUT_DIR,f"{fol}_cdmx.pdf"); os.makedirs(OUTPUT_DIR,exist_ok=True)
        doc=fitz.open("cdmxdigital2025ppp.pdf"); pg=doc[0]
        pg.insert_text(coords_cdmx["folio"][:2],fol,fontsize=coords_cdmx["folio"][2],color=coords_cdmx["folio"][3])
        pg.insert_text(coords_cdmx["fecha"][:2],f_exp,fontsize=coords_cdmx["fecha"][2],color=coords_cdmx["fecha"][3])
        for k in ["marca","serie","linea","motor","anio","color"]:
            x,y,s,col=coords_cdmx[k] if k!="color" else coords_edomex["color"]
            pg.insert_text((x,y),d[k],fontsize=s,color=col)
        x,y,s,col=coords_cdmx["vigencia"]; pg.insert_text((x,y),f_ven,fontsize=s,color=col)
        x,y,s,col=coords_cdmx["nombre"]; pg.insert_text((x,y),d["nombre"],fontsize=s,color=col)
        doc.save(out); doc.close()
        _guardar(fol,"CDMX",d["serie"],d["marca"],d["linea"],d["motor"],d["anio"],d["color"],f_exp,f_ven,d["nombre"])
        return render_template("exitoso.html",folio=fol,cdmx=True)
    return render_template("formulario.html")

@app.route("/formulario_edomex", methods=["GET","POST"])
def formulario_edomex():
    if "user" not in session: return redirect(url_for("login"))
    if request.method=="POST":
        d=request.form; fol=generar_folio_automatico(); ahora=datetime.now()
        f_exp=ahora.strftime("%d/%m/%Y"); f_ven=(ahora+timedelta(days=30)).strftime("%d/%m/%Y")
        out=os.path.join(OUTPUT_DIR,f"{fol}_edomex.pdf"); os.makedirs(OUTPUT_DIR,exist_ok=True)
        doc=fitz.open("edomex_plantilla_alta_res.pdf"); pg=doc[0]
        pg.insert_text(coords_edomex["folio"][:2],fol,fontsize=coords_edomex["folio"][2],color=coords_edomex["folio"][3])
        for k in ["marca","serie","linea","motor","anio","color"]:
            x,y,s,col=coords_edomex[k]; pg.insert_text((x,y),d[k],fontsize=s,color=col)
        x,y,s,col=coords_edomex["fecha_exp"]; pg.insert_text((x,y),f_exp,fontsize=s,color=col)
        x,y,s,col=coords_edomex["fecha_ven"]; pg.insert_text((x,y),f_ven,fontsize=s,color=col)
        x,y,s,col=coords_edomex["nombre"]; pg.insert_text((x,y),d["nombre"],fontsize=s,color=col)
        doc.save(out); doc.close()
        _guardar(fol,"EDOMEX",d["serie"],d["marca"],d["linea"],d["motor"],d["anio"],d["color"],f_exp,f_ven,d["nombre"])
        return render_template("exitoso.html",folio=fol,edomex=True)
    return render_template("formulario_edomex.html")

@app.route("/formulario_morelos", methods=["GET","POST"])
def formulario_morelos():
    if "user" not in session: return redirect(url_for("login"))
    if request.method=="POST":
        d=request.form; fol=generar_folio_automatico(); placa=generar_placa_digital()
        ahora=datetime.now()
        f_larga=ahora.strftime(f"%d DE {meses_es[ahora.strftime('%B')]} DEL %Y").upper()
        f_ven=(ahora+timedelta(days=30)).strftime("%d/%m/%Y")
        out=os.path.join(OUTPUT_DIR,f"{fol}_morelos.pdf"); os.makedirs(OUTPUT_DIR,exist_ok=True)
        doc=fitz.open("morelos_hoja1_imagen.pdf"); pg=doc[0]
        pg.insert_text(coords_morelos["folio"][:2],fol,fontsize=coords_morelos["folio"][2],color=coords_morelos["folio"][3])
        pg.insert_text(coords_morelos["placa"][:2],placa,fontsize=coords_morelos["placa"][2],color=coords_morelos["placa"][3])
        pg.insert_text(coords_morelos["fecha"][:2],f_larga,fontsize=coords_morelos["fecha"][2],color=coords_morelos["fecha"][3])
        pg.insert_text(coords_morelos["vigencia"][:2],f_ven,fontsize=coords_morelos["vigencia"][2],color=coords_morelos["vigencia"][3])
        for k in ["marca","serie","linea","motor","anio","color","tipo"]:
            x,y,s,col=coords_morelos[k]; pg.insert_text((x,y),d[k],fontsize=s,color=col)
        x,y,s,col=coords_morelos["nombre"]; pg.insert_text((x,y),d["nombre"],fontsize=s,color=col)
        if len(doc)>1:
            x,y,s,col=coords_morelos["fecha_hoja2"]; doc[1].insert_text((x,y),ahora.strftime("%d/%m/%Y"),fontsize=s,color=col)
        doc.save(out); doc.close()
        _guardar(fol,"MOR",d["serie"],d["marca"],d["linea"],d["motor"],d["anio"],d["color"],f_larga,f_ven,d["nombre"])
        return render_template("exitoso.html",folio=fol,morelos=True)
    return render_template("formulario_morelos.html")

@app.route("/formulario_oaxaca", methods=["GET","POST"])
def formulario_oaxaca():
    if "user" not in session: return redirect(url_for("login"))
    if request.method=="POST":
        d=request.form; fol=generar_folio_automatico(); ahora=datetime.now()
        f1=ahora.strftime("%d/%m/%Y"); f_ven=(ahora+timedelta(days=30)).strftime("%d/%m/%Y")
        out=os.path.join(OUTPUT_DIR,f"{fol}_oaxaca.pdf"); os.makedirs(OUTPUT_DIR,exist_ok=True)
        doc=fitz.open("oaxacachido.pdf"); pg=doc[0]
        pg.insert_text(coords_oaxaca["folio"][:2],fol,fontsize=coords_oaxaca["folio"][2],color=coords_oaxaca["folio"][3])
        pg.insert_text(coords_oaxaca["fecha1"][:2],f1,fontsize=coords_oaxaca["fecha1"][2],color=coords_oaxaca["fecha1"][3])
        pg.insert_text(coords_oaxaca["fecha2"][:2],f1,fontsize=coords_oaxaca["fecha2"][2],color=coords_oaxaca["fecha2"][3])
        for k in ["marca","serie","linea","motor","anio","color"]:
            x,y,s,col=coords_oaxaca[k]; pg.insert_text((x,y),d[k],fontsize=s,color=col)
        x,y,s,col=coords_oaxaca["vigencia"]; pg.insert_text((x,y),f_ven,fontsize=s,color=col)
        x,y,s,col=coords_oaxaca["nombre"]; pg.insert_text((x,y),d["nombre"],fontsize=s,color=col)
        doc.save(out); doc.close()
        _guardar(fol,"OAX",d["serie"],d["marca"],d["linea"],d["motor"],d["anio"],d["color"],f1,f_ven,d["nombre"])
        return render_template("exitoso.html",folio=fol,oaxaca=True)
    return render_template("formulario_oaxaca.html")

@app.route("/formulario_gto", methods=["GET","POST"])
def formulario_gto():
    if "user" not in session: return redirect(url_for("login"))
    if request.method=="POST":
        d=request.form; fol=generar_folio_automatico(); ahora=datetime.now()
        f_exp=ahora.strftime("%d/%m/%Y"); f_ven=(ahora+timedelta(days=30)).strftime("%d/%m/%Y")
        out=os.path.join(OUTPUT_DIR,f"{fol}_gto.pdf"); os.makedirs(OUTPUT_DIR,exist_ok=True)
        doc=fitz.open("permiso guanajuato.pdf"); pg=doc[0]
        pg.insert_text(coords_gto["folio"][:2],fol,fontsize=coords_gto["folio"][2],color=coords_gto["folio"][3])
        pg.insert_text(coords_gto["fecha"][:2],f_exp,fontsize=coords_gto["fecha"][2],color=coords_gto["fecha"][3])
        for k in ["marca","serie","linea","motor","anio","color"]:
            x,y,s,col=coords_gto[k]; pg.insert_text((x,y),d[k],fontsize=s,color=col)
        x,y,s,col=coords_gto["vigencia"]; pg.insert_text((x,y),f_ven,fontsize=s,color=col)
        x,y,s,col=coords_gto["nombre"]; pg.insert_text((x,y),d["nombre"],fontsize=s,color=col)
        doc.save(out); doc.close()
        _guardar(fol,"GTO",d["serie"],d["marca"],d["linea"],d["motor"],d["anio"],d["color"],f_exp,f_ven,d["nombre"])
        return render_template("exitoso.html",folio=fol,gto=True)
    return render_template("formulario_gto.html")

@app.route("/listar")
def listar():
    if "user" not in session: return redirect(url_for("login"))
    regs=cargar_registros()
    return render_template("listar.html",registros=regs,now=datetime.now())

@app.route("/eliminar/<folio>",methods=["POST"])
def eliminar_folio(folio):
    regs=[r for r in cargar_registros() if r["folio"]!=folio]
    guardar_registros(regs)
    return redirect(url_for("listar"))

@app.route("/renovar/<folio>")
def renovar(folio):
    regs=cargar_registros()
    viejo=next((r for r in regs if r["folio"]==folio),None)
    if not viejo: return redirect(url_for("listar"))
    venc=datetime.strptime(viejo["fecha_ven"],"%d/%m/%Y")
    if datetime.now()<venc: return redirect(url_for("listar"))
    nuevo=generar_folio_automatico(); ahora=datetime.now()
    f_exp=ahora.strftime("%d/%m/%Y"); f_ven=(ahora+timedelta(days=30)).strftime("%d/%m/%Y")
    plantillas={
        "CDMX":"cdmxdigital2025ppp.pdf","EDOMEX":"edomex_plantilla_alta_res.pdf",
        "MOR":"morelos_hoja1_imagen.pdf","OAX":"oaxacachido.pdf",
        "GTO":"permiso guanajuato.pdf"
    }[viejo["entidad"]]
    coords_map={
        "CDMX":coords_cdmx,"EDOMEX":coords_edomex,"MOR":coords_morelos,
        "OAX":coords_oaxaca,"GTO":coords_gto
    }[viejo["entidad"]]
    out=os.path.join(OUTPUT_DIR,f"{nuevo}_{viejo['entidad'].lower()}.pdf")
    os.makedirs(OUTPUT_DIR,exist_ok=True)
    doc=fitz.open(plantillas); pg=doc[0]
    pg.insert_text(coords_map["folio"][:2],nuevo,fontsize=coords_map["folio"][2],color=coords_map["folio"][3])
    key_exp="fecha" if "fecha" in coords_map else "fecha1"
    key_ven="vigencia" if "vigencia" in coords_map else "fecha2"
    pg.insert_text(coords_map[key_exp][:2],f_exp,fontsize=coords_map[key_exp][2],color=coords_map[key_exp][3])
    pg.insert_text(coords_map[key_ven][:2],f_ven,fontsize=coords_map[key_ven][2],color=coords_map[key_ven][3])
    for k in ["marca","serie","linea","motor","anio","color","nombre"]:
        if k in coords_map:
            x,y,s,col=coords_map[k]; pg.insert_text((x,y),viejo[k],fontsize=s,color=col)
    doc.save(out); doc.close()
    _guardar(nuevo,viejo["entidad"],viejo["serie"],viejo["marca"],viejo["linea"],viejo["motor"],viejo["anio"],viejo["color"],f_exp,f_ven,viejo["nombre"])
    return redirect(url_for(f"abrir_pdf_{viejo['entidad'].lower()}",folio=nuevo))

@app.route("/abrir_pdf/<folio>")
def abrir_pdf(folio):
    p=os.path.join(OUTPUT_DIR,f"{folio}_cdmx.pdf")
    return send_file(p,as_attachment=True) if os.path.exists(p) else ("No encontrado",404)
@app.route("/abrir_pdf_edomex/<folio>")
def abrir_pdf_edomex(folio):
    p=os.path.join(OUTPUT_DIR,f"{folio}_edomex.pdf")
    return send_file(p,as_attachment=True) if os.path.exists(p) else ("No encontrado",404)
@app.route("/abrir_pdf_morelos/<folio>")
def abrir_pdf_morelos(folio):
    p=os.path.join(OUTPUT_DIR,f"{folio}_morelos.pdf")
    return send_file(p,as_attachment=True) if os.path.exists(p) else ("No encontrado",404)
@app.route("/abrir_pdf_oaxaca/<folio>")
def abrir_pdf_oaxaca(folio):
    p=os.path.join(OUTPUT_DIR,f"{folio}_oaxaca.pdf")
    return send_file(p,as_attachment=True) if os.path.exists(p) else ("No encontrado",404)
@app.route("/abrir_pdf_gto/<folio>")
def abrir_pdf_gto(folio):
    p=os.path.join(OUTPUT_DIR,f"{folio}_gto.pdf")
    return send_file(p,as_attachment=True) if os.path.exists(p) else ("No encontrado",404)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__=="__main__":
    app.run(debug=True)
