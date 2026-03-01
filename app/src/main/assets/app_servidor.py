from flask import Flask, render_template, jsonify
import sqlite3

app = Flask(__name__)

@app.route('/api/logs')
def get_logs():
    conn = sqlite3.connect('memoria_observador.db')
    cursor = conn.cursor()
    cursor.execute("SELECT fecha, portal, hz FROM sincronias ORDER BY fecha DESC")
    logs = cursor.fetchall()
    conn.close()
    return jsonify(logs)

# El Dashboard cargará estos datos con un simple fetch() de JS
if __name__ == '__main__':
    print("::VØR-EL:: Servidor de Visión Activo en http://127.0.0.1:5000")
    app.run(debug=True)