import os
import psycopg2
import csv
import io
from flask import Flask, render_template, request, redirect, url_for, Response
from datetime import datetime
from zoneinfo import ZoneInfo  # Para manejar la zona horaria de España

app = Flask(__name__)

DB_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    url = DB_URL
    if url and url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    conn = psycopg2.connect(url)
    return conn

def init_db():
    if not DB_URL:
        return
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS registros (
            id SERIAL PRIMARY KEY,
            fecha_hora VARCHAR(50) NOT NULL,
            dato1 TEXT NOT NULL,
            dato2 TEXT NOT NULL
        );
    ''')
    conn.commit()
    cursor.close()
    conn.close()

try:
    init_db()
except Exception as e:
    print("Error inicializando BD:", e)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        d1 = request.form.get('dato1')
        d2 = request.form.get('dato2')
        
        # Obtenemos la hora actual configurada para la zona horaria de España (península/Baleares)
        fecha_actual = datetime.now(ZoneInfo("Europe/Madrid")).strftime("%Y-%m-%d %H:%M:%S")
        
        if d1 and d2 and DB_URL:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO registros (fecha_hora, dato1, dato2) VALUES (%s, %s, %s)',
                (fecha_actual, d1, d2)
            )
            conn.commit()
            cursor.close()
            conn.close()
        
        return redirect(url_for('index'))

    registros = []
    if DB_URL:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT fecha_hora, dato1, dato2 FROM registros ORDER BY id DESC')
            registros = cursor.fetchall()
            cursor.close()
            conn.close()
        except Exception as e:
            print("Error al leer BD:", e)

    return render_template('index.html', registros=registros)

# RUTA PARA DESCARGAR LA COPIA DE SEGURIDAD (COMPATIBLE CON EXCEL EN COLUMNAS)
@app.route('/descargar-backup')
def descargar_backup():
    if not DB_URL:
        return "No hay conexión a la base de datos", 500

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, fecha_hora, dato1, dato2 FROM registros ORDER BY id ASC')
        filas = cursor.fetchall()
        cursor.close()
        conn.close()

        output = io.StringIO()
        # Separador ';' para que Excel en español detecte las columnas
        writer = csv.writer(output, delimiter=';')
        
        # Cabeceras
        writer.writerow(['ID', 'Fecha y Hora', 'Dato 1', 'Dato 2'])
        
        # Datos
        for fila in filas:
            writer.writerow(fila)

        output.seek(0)

        # Prefijo '\ufeff' (BOM) para conservar tildes y eñes
        contenido_excel = '\ufeff' + output.getvalue()

        return Response(
            contenido_excel,
            mimetype="text/csv; charset=utf-8",
            headers={"Content-Disposition": "attachment;filename=copia_seguridad_registros.csv"}
        )
    except Exception as e:
        return f"Error al generar la copia de seguridad: {e}", 500

if __name__ == '__main__':
    app.run(debug=True)
