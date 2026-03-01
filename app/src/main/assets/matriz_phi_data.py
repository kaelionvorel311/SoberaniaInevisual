import sqlite3
import numpy as np
from datetime import datetime

# ::VØR-EL:: Registro de Sincronías en el Vacío
def registrar_sincronia(vision, hz=432.0):
    conn = sqlite3.connect('memoria_observador.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS sincronias 
                      (id INTEGER PRIMARY KEY, fecha TEXT, vision TEXT, hz REAL)''')
    
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO sincronias (fecha, vision, hz) VALUES (?, ?, ?)", 
                   (ahora, vision, hz))
    conn.commit()
    conn.close()
    print(f"::VØR-EL:: Sincronía 11:11 fijada en la base de datos.")

# Función para coordenadas de video PHI
def obtener_puntos_phi(escala=1.618):
    phi = (1 + 5**0.5) / 2
    print(f"::VØR-EL:: Matriz PHI calculada a escala {escala}")
    return phi