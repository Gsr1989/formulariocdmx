from flask import Flask, render_template, request, send_file, redirect, url_for, session from datetime import datetime, timedelta import fitz  # PyMuPDF import os import string import csv

app = Flask(name) app.secret_key = "secreto_perro"

OUTPUT_DIR = "static/pdfs" USUARIO = "Gsr89roja" CONTRASENA = "serg890105"

meses_es = { "January": "ENERO", "February": "FEBRERO", "March": "MARZO", "April": "ABRIL", "May": "MAYO", "June": "JUNIO", "July": "JULIO", "August": "AGOSTO", "September": "SEPTIEMBRE", "October": "OCTUBRE", "November": "NOVIEMBRE", "December": "DICIEMBRE" }

Coordenadas para cada plantilla

coords = { "CDMX": { "folio":    (87,130,14,(1,0,0)), "fecha":    (130,145,12,(0,0,0)), "marca":    (87,290,11,(0,0,0)), "serie":    (375,290,11,(0,0,0)), "linea":    (87,307,11,(0,0,0)), "motor":    (375,307,11,(0,0,0)), "anio":     (87,323,11,(0,0,0)), "vigencia": (375,323,11,(0,0,0)), "nombre":   (375,340,11,(0,0,0)), "archivo":  "cdmxdigital2025ppp.pdf" }, "EDOMEX": { "folio":     (535,135,14,(1,0,0)), "marca":     (109,190,10,(0,0,0)), "serie":     (230,233,10,(0,0,0)), "linea":     (238,190,10,(0,0,0)), "motor":     (104,233,10,(0,0,0)), "anio":      (410,190,10,(0,0,0)), "color":     (400,233,10,(0,0,0)), "fecha_exp": (190,280,10,(0,0,0)), "fecha_ven": (380,280,10,(0,0,0)), "nombre":    (394,320,10,(0,0,0)), "archivo":   "edomex_plantilla_alta_res.pdf" }, "Morelos": { "folio":       (665,282,18,(1,0,0)), "placa":       (200,200,60,(0,0,0)), "fecha":       (200,340,14,(0,0,0)), "vigencia":    (600,340,14,(0,0,0)), "marca":       (110,425,14,(0,0,0)), "serie":       (460,420,14,(0,0,0)), "linea":       (110,455,14,(0,0,0)), "motor":       (460,445,14,(0,0,0)), "anio":        (110,485,14,(0,0,0)), "color":       (460,395,14,(0,0,0)), "tipo":        (510,470,14,(0,0,0)), "nombre":      (150,370,14,(0,0,0)), "fecha_hoja2": (100,100,14,(0,0,0)), "archivo":     "morelos_hoja1_imagen.pdf" }, "Oaxaca": { "folio":    (553,96,16,(1,0,0)), "fecha1":   (168,130,12,(0,0,0)), "fecha2":   (140,540,10,(0,0,0)), "marca":    (50,215,12,(0,0,0)), "serie":    (200,258,12,(0,0,0)), "linea":    (200,215,12,(0,0,0)), "motor":    (360,258,12,(0,0,0)), "anio":     (360,215,12,(0,0,0)), "color":    (50,258,12,(0,0,0)), "vigencia": (410,130,12,(0,0,0)), "nombre":   (133,149,10,(0,0,0)), "archivo":  "oaxacachido.pdf" }, "GTO": { "folio":    (1800,455,60,(1,0,0)), "fecha":    (2200,580,35,(0,0,0)), "marca":    (385,715,35,(0,0,0)), "serie":    (350,800,35,(0,0,0)), "linea":    (800,715,35,(0,0,0)), "motor":    (1290,800,35,(0,0,0)), "anio":     (1500,715,35,(0,0,0)), "color":    (1960,715,35,(0,0,0)), "nombre":   (950,1100,50,(0,0,0)), "vigencia": (2200,645,35,(0,0,0)), "archivo":  "permiso guanajuato.pdf" } }

Generación de folio incremental

def generar_folio_automatico(ruta="folios_globales.txt"): mes = datetime.now().strftime("%m") if not os.path.exists(ruta): open(ruta, "w").close() with open(ruta) as f: lineas = [l.strip() for l in f] este_mes = [x for x in lineas if x.startswith(mes)] fol = f"{mes}{len(este_mes)+1:03d}" with open(ruta, "a") as f: f.write(fol + "\n") return fol

Generación de placa para Morelos

def generar_placa_digital(): archivo = "placas_digitales.txt" abc = string.ascii_uppercase if not os.path.exists(archivo): with open(archivo, "w") as f: f.write("LRU0000\n") ultimo = open(archivo).read().strip().split("\n")[-1] pref, num = ultimo[:3], int(ultimo[3:]) if num < 9999: nuevo = f"{pref}{num+1:04d}" else: l1,l2,l3 = list(pref) i3 = abc.index(l3) if i3 < 25: l3 = abc[i3+1] else: i2 = abc.index(l2) if i2 < 25: l2 = abc[i2+1]; l3 = "A" else: l1 = abc[(abc.index(l1)+1)%26]; l2 = l3 = "A" nuevo = f"{l1}{l2}{l3}0000" with open(archivo, "a") as f: f.write(nuevo + "\n") return nuevo

Guardar y cargar registros en CSV

def _guardar(folio, entidad, serie, marca, linea, motor, anio, color, fecha_exp, fecha_ven, nombre): existe = os.path.exists("registros.csv") with open("registros.csv", "a", newline="", encoding="utf-8") as f: w = csv.writer(f) if not existe: w.writerow(["folio","entidad","serie","marca","linea","motor","anio","color","fecha_exp","fecha_ven","nombre"]) w.writerow([folio, entidad, serie, marca, linea, motor, anio, color, fecha_exp, fecha_ven, nombre])

def cargar_registros(): regs = [] if os.path.exists("registros.csv"): with open("registros.csv", encoding="utf-8") as f: reader = csv.reader(f); next(reader, None) for row in reader: if len(row)==11: regs.append(dict(zip(["folio","entidad","serie","marca","linea","motor","anio","color","fecha_exp","fecha_ven","nombre"], row))) return regs

def guardar_registros(regs): with open("registros.csv", "w", newline="", encoding="utf-8") as f: w = csv.writer(f) w.writerow(["folio","entidad","serie","marca","linea","motor","anio","color","fecha_exp","fecha_ven","nombre"]) for r in regs: w.writerow([r[k] for k in ["folio","entidad","serie","marca","linea","motor","anio","color","fecha_exp","fecha_ven","nombre"]])

--- Autenticación ---

@app.route("/", methods=["GET","POST"]) def login(): if request.method=="POST" and request.form.get("user")==USUARIO and request.form.get("pass")==CONTRASENA: session["user"] = USUARIO return redirect(url_for("seleccionar_entidad")) return render_template("login.html")

@app.route("/logout") def logout(): session.clear() return redirect(url_for("login"))

--- Menú de selección ---

@app.route("/seleccionar_entidad") def seleccionar_entidad(): if "user" not in session: return redirect(url_for("login")) return render_template("seleccionar_entidad.html")

--- Creación dinámica de rutas de formulario ---

def procesar(entidad, template_form, flag_name): if "user" not in session: return redirect(url_for("login")) if request.method=="POST": d = request.form; fol = generar_folio_automatico() ahora = datetime.now() f_exp = ahora.strftime("%d DE {0} DEL %Y".format(meses_es[ahora.strftime('%B')])).upper() f_ven = (ahora + timedelta(days=30)).strftime("%d/%m/%Y") if entidad=="Morelos": placa = generar_placa_digital() os.makedirs(OUTPUT_DIR, exist_ok=True) out = os.path.join(OUTPUT_DIR, f"{fol}_{entidad.lower()}.pdf") doc = fitz.open(coords[entidad]['archivo']); pg = doc[0] # Folio y fechas pg.insert_text(coords[entidad]['folio'][:2], fol, fontsize=coords[entidad]['folio'][2], color=coords[entidad]['folio'][3]) clave_fecha = 'fecha_exp' if 'fecha_exp' in coords[entidad] else ('fecha' if 'fecha' in coords[entidad] else 'fecha1') clave_ven   = 'fecha_ven' if 'fecha_ven' in coords[entidad] else ('vigencia' if 'vigencia' in coords[entidad] else 'fecha2') pg.insert_text(coords[entidad][clave_fecha][:2], f_exp, fontsize=coords[entidad][clave_fecha][2], color=coords[entidad][clave_fecha][3]) pg.insert_text(coords[entidad][clave_ven][:2], f_ven, fontsize=coords[entidad][clave_ven][2], color=coords[entidad][clave_ven][3]) # Campos variables if entidad=="Morelos": pg.insert_text(coords[entidad]['placa'][:2], placa, fontsize=coords[entidad]['placa'][2], color=coords[entidad]['placa'][3]) for key in ['marca','serie','linea','motor','anio','color','tipo','nombre']: if key in coords[entidad]: x,y,s,col = coords[entidad][key] pg.insert_text((x,y), d.get(key,'') , fontsize=s, color=col) # Segunda hoja Morelos if entidad=="Morelos" and len(doc)>1: pg2 = doc[1] pg2.insert_text(coords[entidad]['fecha_hoja2'][:2], f_ven, fontsize=coords[entidad]['fecha_hoja2'][2], color=coords[entidad]['fecha_hoja2'][3]) doc.save(out); doc.close() _guardar(fol, entidad, d.get('serie',''), d.get('marca',''), d.get('linea',''), d.get('motor',''), d.get('anio',''), d.get('color',''), f_exp, f_ven, d.get('nombre','')) return render_template("exitoso.html", folio=fol, **{flag_name: True}) return render_template(template_form)

Registrar rutas de cada entidad

entidades = [ ("CDMX",       "formulario","cdmx"), ("EDOMEX",     "formulario_edomex","edomex"), ("Morelos",    "formulario_morelos","morelos"), ("Oaxaca",     "formulario_oaxaca","oaxaca"), ("GTO",        "formulario_gto","gto"), ] for ent, route_name, flag in entidades: app.add_url_rule(f"/{route_name}", route_name, (lambda e=ent, r=route_name, f=flag: procesar(e, f"{route_name}.html", f)), methods=["GET","POST"])

Listar, eliminar y renovar

@app.route("/listar") def listar(): if "user" not in session: return redirect(url_for("login")) return render_template("listar.html", registros=cargar_registros(), now=datetime.now())

@app.route("/eliminar/<folio>", methods=["POST"]) def eliminar(folio): regs = [r for r in cargar_registros() if r['folio']!=folio] guardar_registros(regs) return redirect(url_for("listar"))

@app.route("/eliminar_multiples", methods=["POST"]) def eliminar_multiples(): fols = request.form.getlist("folios") if fols: regs = [r for r in cargar_registros() if r['folio'] not in fols] guardar_registros(regs) return redirect(url_for("listar"))

@app.route("/renovar/<folio>") def renovar(folio): regs = cargar_registros() viejo = next((r for r in regs if r['folio']==folio), None) if not viejo: return redirect(url_for("listar")) venc = datetime.strptime(viejo['fecha_ven'], "%d/%m/%Y") if datetime.now()<venc: return redirect(url_for("listar")) registro = antiguo = viejo.copy() registro['folio'] = generar_folio_automatico() now = datetime.now() registro['fecha_exp'] = now.strftime("%d/%m/%Y") registro['fecha_ven'] = (now+timedelta(days=30)).strftime("%d/%m/%Y") regs.append(registro) guardar_registros(regs) ent = registro['entidad'] return redirect(url_for(f"abrir_pdf_{ent.lower()}", folio=registro['folio']))

Rutas de descarga

for ent, , _ in entidades: def mk_open(ent): def abrir(folio): p = os.path.join(OUTPUT_DIR, f"{folio}{ent.lower()}.pdf") return send_file(p, as_attachment=True) if os.path.exists(p) else ("No encontrado", 404) return abrir app.add_url_rule(f"/abrir_pdf_{ent.lower()}/<folio>", f"abrir_pdf_{ent.lower()}", mk_open(ent))

Run

if name == "main": app.run(debug=True)

