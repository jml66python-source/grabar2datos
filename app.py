from flask import Response
import csv
import io

@app.route('/descargar-backup')
def descargar_backup():
    # Aquí obtienes los datos de tu base de datos Supabase
    # (dependiendo de cómo los consultes normalmente en tu app)
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Escribes las cabeceras de tus columnas (cámbialas por los nombres reales de tus datos)
    writer.writerow(['ID', 'Dato1', 'Dato2', 'Fecha'])
    
    # Aquí harías un bucle para rellenar las filas con tus registros reales de la base de datos
    # Ejemplo:
    # for item in lista_de_datos:
    #     writer.writerow([item.id, item.campo1, item.campo2, item.fecha])
    
    output.seek(0)
    
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=copia_seguridad.csv"}
    )
