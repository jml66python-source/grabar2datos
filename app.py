from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Función para conectar a la base de datos y crear la tabla si no existe
def init_db():
    conn = sqlite3.connect('historial.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS registros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_hora TEXT NOT NULL,
            dato1 TEXT NOT NULL,
            dato2 TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Inicializar BD al arrancar
init_db()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        d1 = request.form.get('dato1')
        d2 = request.form.get('dato2')
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if d1 and d2:
            conn = sqlite3.connect('historial.db')
            cursor = conn.cursor()
            cursor.execute('INSERT INTO registros (fecha_hora, dato1, dato2) VALUES (?, ?, ?)', (fecha_actual, d1, d2))
            conn.commit()
            conn.close()
        
        return redirect(url_for('index'))

    # Obtener historial de registros (los más recientes primero)
    conn = sqlite3.connect('historial.db')
    cursor = conn.cursor()
    cursor.execute('SELECT fecha_hora, dato1, dato2 FROM registros ORDER BY id DESC')
    registros = cursor.fetchall()
    conn.close()

    return render_template('index.html', registros=registros)

if __name__ == '__main__':
    app.run(debug=True)
