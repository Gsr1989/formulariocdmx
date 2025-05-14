from flask import Flask, render_template, request, send_file, redirect, url_for, flash, session from datetime import datetime, timedelta import fitz  # PyMuPDF import os import string import csv

app = Flask(name) app.secret_key = "secreto_perro"

OUTPUT_DIR = "static/pdfs" USUARIO = "Gsr89roja" CONTRASENA = "serg890105"

meses_es = { "January":"ENERO","February":"FEBRERO","March":"MARZO", "April":"ABRIL","May":"MAYO","June":"JUNIO", "July":"JULIO","August":"AGOSTO","September":"SEPTIEMBRE", "October":"OCTUBRE","November":"NOVIEMBRE","December":"DICIEMBRE" }

coords_cdmx = { "folio":    (87,130,14,(1,0,0)), "fecha":    (130,145,12,(0,0,0)), "marca":    (87,290,11,(0,0,0)), "serie":    (375,290,11,(0,0,0)), "linea":    (87,307,11,(0,0,0)), "motor":    (375,307,11,(0,0,0)), "anio":     (87,323,11,(0,0,0)), "vigencia": (375,323,11,(0,0,0)), "nombre":   (375,340,11,(0,0,0)), } coords_edomex = { "folio":     (535,135,14,(1,0,0)), "marca":     (109,190,10,(0,0,0)), "serie":     (230,233,10,(0,0,0)), "linea":     (238,190,10,(0,0,0)), "motor":     (104,233,10,(0,0,0)), "anio":      (410,190,10,(0,0,0)), "color":     (400,233,10,(0,0,0)), "fecha_exp": (190,280,10,(0,0,0)), "fecha_ven": (380,280,10,(0,0,0)), "nombre":    (394,320,10,(0,0,0)), } coords_morelos = { "folio":       (665,282,18,(1,0,0)), "placa":       (200,200,60,(0,0,0)), "fecha":       (200,340,14,(0,0,0)), "vigencia":    (600,340,14,(0,0,0)), "marca":       (110,425,14,(0,0,0)), "serie":       (460,420,14,(0,0,0)), "linea":       (110,455,14,(0,0,0)), "motor":       (460,445,14,(0,0,0)), "anio":        (110,485,14,(0,0,0)), "color":       (460,395,14,(0,0,0)), "tipo":        (510,470,14,(0,0,0)), "nombre":      (150,370,14,(0,0,0)), "fecha_hoja2": (100,100,14,(0,0,0)), } coords_oaxaca = { "folio":    (553,96,16,(1,0,0)), "fecha1":   (168,130,12,(0,0,0)), "fecha2":   (140,540,10,(0,0,0)), "marca":    (50,215,12,(0,0,0)), "serie":    (200,258,12,(0,0,0)), "linea":    (200,215,12,(0,0,0)), "motor":    (360,258,12,(0,0,0)), "anio":     (360,215,12,(0,0,0)), "color":    (50,258,12,(0,0,0)), "vigencia": (410,130,12,(0,0,0)), "nombre":   (133,149,10,(0,0,0)), } coords_gto = { "folio":    (1800,455,60,(1,0,0)), "fecha":    (2200,580,35,(0,0,0)), "marca":    (385,715,35,(0,0,0)), "serie":    (350,800,35,(0,0,0)), "linea":    (800,715,35,(0,0,0)), "motor":    (1290,800,35,(0,0,0)), "anio":     (1500,715,35,(0,0,0)), "color":    (1960,715,35,(0,0,0)), "nombre":   (950,1100,50,(0,0,0)), "vigencia": (2200,645,35,(0,0,0)), }

def generar_folio_automatico(ruta="folios_globales.txt"): mes = datetime.now().strftime("%m") if not os.path.exists(ruta): open(ruta, "w").close() with open(ruta) as f: lineas = [l.strip() for l in f] este_mes = [x for x in lineas if x.startswith(mes)] fol = f"{mes}{len(este_mes)+1:03d}" with open(ruta, "a") as f: f.write(fol+"\n") return fol

def generar_placa_digital(): archivo = "placas_digitales.txt" abc = string.ascii_uppercase if not os.path.exists(archivo): with open(archivo, "w") as f: f.write("LRU0000\n") ultimo = open(archivo).read().strip().split("\n")[-1] pref, num = ultimo[:3], int(ultimo[3:]) if num < 9999: nuevo = f"{pref}{num+1:04d}" else: l1, l2, l3 = list(pref) i3 = abc.index(l3) if i3 < 25: l3 = abc[i3+1] else: i2 = abc.index(l2) if i2 < 25: l2 = abc[i2+1]; l3 = 'A' else: l1 = abc[(abc.index(l1)+1)%26]; l2 = l3 = 'A' nuevo = f"{l1}{l2}{l3}0000" with open(archivo, "a") as f: f.write(nuevo+"\n") return nuevo

def _guardar(...): # same as before pass

def cargar_registros(): # same as before pass

@app.route("/renovar/<folio>") def renovar(folio): regs = cargar_registros() viejo = next((r for r in regs if r['folio']==folio), None) if not viejo: return redirect(url_for('listar')) venc = datetime.strptime(viejo['fecha_ven'], "%d/%m/%Y") if datetime.now() < venc: return redirect(url_for('listar'))

nuevo = generar_folio_automatico()
ahora = datetime.now()
f_exp = ahora.strftime("%d/%m/%Y")
f_ven = (ahora+timedelta(days=30)).strftime("%d/%m/%Y")

plantillas = {
    'CDMX':'cdmxdigital2025ppp.pdf','EDOMEX':'edomex_plantilla_alta_res.pdf',
    'Morelos':'morelos_hoja1_imagen.pdf','Oaxaca':'oaxacachido.pdf','GTO':'permiso guanajuato.pdf'
}[viejo['entidad']]

coords_map = {
    'CDMX':coords_cdmx,'EDOMEX':coords_edomex,'Morelos':coords_morelos,
    'Oaxaca':coords_oaxaca,'GTO':coords_gto
}[viejo['entidad']]

out = os.path.join(OUTPUT_DIR, f"{nuevo}_{viejo['entidad'].lower()}.pdf")
os.makedirs(OUTPUT_DIR, exist_ok=True)
doc = fitz.open(plantillas); pg = doc[0]

# folio
pg.insert_text(coords_map['folio'][:2], nuevo,
               fontsize=coords_map['folio'][2], color=coords_map['folio'][3])

# escoger claves de fecha expedición y vencimiento
if 'fecha_exp' in coords_map:
    exp_key = 'fecha_exp'
elif 'fecha' in coords_map:
    exp_key = 'fecha'
elif 'fecha1' in coords_map:
    exp_key = 'fecha1'
else:
    exp_key = None

if 'fecha_ven' in coords_map:
    ven_key = 'fecha_ven'
elif 'vigencia' in coords_map:
    ven_key = 'vigencia'
elif 'fecha2' in coords_map:
    ven_key = 'fecha2'
else:
    ven_key = None

if exp_key:
    pg.insert_text(coords_map[exp_key][:2], f_exp,
                   fontsize=coords_map[exp_key][2], color=coords_map[exp_key][3])
if ven_key:
    pg.insert_text(coords_map[ven_key][:2], f_ven,
                   fontsize=coords_map[ven_key][2], color=coords_map[ven_key][3])

# datos restantes
for k in ['marca','serie','linea','motor','anio','color','nombre']:
    if k in coords_map:
        pg.insert_text(coords_map[k][:2], viejo[k],
                       fontsize=coords_map[k][2], color=coords_map[k][3])

doc.save(out); doc.close()
_guardar(nuevo, viejo['entidad'], viejo['serie'],
         viejo['marca'], viejo['linea'], viejo['motor'],
         viejo['anio'], viejo['color'], f_exp, f_ven, viejo['nombre'])

return redirect(url_for(f"abrir_pdf_{viejo['entidad'].lower()}", folio=nuevo))

Alias para descarga CDMX en plantilla 'abrir_pdf'

@app.route("/abrir_pdf/<folio>") def abrir_pdf(folio): p = os.path.join(OUTPUT_DIR, f"{folio}_cdmx.pdf") return send_file(p, as_attachment=True) if os.path.exists(p) else ("No encontrado",404)

rutas específicas

@app.route("/abrir_pdf_cdmx/<folio>") def abrir_pdf_cdmx(folio): p = os.path.join(OUTPUT_DIR, f"{folio}_cdmx.pdf") return send_file(p, as_attachment=True) if os.path.exists(p) else ("No encontrado",404) @app.route("/abrir_pdf_edomex/<folio>") def abrir_pdf_edomex(folio): p = os.path.join(OUTPUT_DIR, f"{folio}_edomex.pdf") return send_file(p, as_attachment=True) if os.path.exists(p) else ("No encontrado",404) @app.route("/abrir_pdf_morelos/<folio>") def abrir_pdf_morelos(folio): p = os.path.join(OUTPUT_DIR, f"{folio}_morelos.pdf") return send_file(p, as_attachment=True) if os.path.exists(p) else ("No encontrado",404) @app.route("/abrir_pdf_oaxaca/<folio>") def abrir_pdf_oaxaca(folio): p = os.path.join(OUTPUT_DIR, f"{folio}_oaxaca.pdf") return send_file(p, as_attachment=True) if os.path.exists(p) else ("No encontrado",404) @app.route("/abrir_pdf_gto/<folio>") def abrir_pdf_gto(folio): p = os.path.join(OUTPUT_DIR, f"{folio}_gto.pdf") return send_file(p, as_attachment=True) if os.path.exists(p) else ("No encontrado",404)

if name == "main": app.run(debug=True)

