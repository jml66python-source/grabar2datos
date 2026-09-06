import os
import psycopg2
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

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
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
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

if __name__ == '__main__':
    app.run(debug=True)
