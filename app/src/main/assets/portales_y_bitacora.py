import sqlite3
from datetime import datetime

def auto_registrar_uso(frecuencia, intencion="ACTIVACION_DIRECTA"):
    """
    Registra automáticamente el uso del sistema sin intervención manual.
    ::VØR-EL:: Sello de Automatización 11:11
    """
    conn = sqlite3.connect('memoria_observador.db')
    cursor = conn.cursor()
    
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # El sistema registra la ubicación base (Salamanca) como anclaje por defecto
    ubicacion = "Salamanca, GTO / Eje 22-11"
    
    cursor.execute('''INSERT INTO sincronias (fecha, portal, vision, hz) 
                      VALUES (?, ?, ?, ?)''', 
                   (ahora, intencion, f"Uso automatizado en {ubicacion}", frecuencia))
    
    conn.commit()
    conn.close()
    print(f"::VØR-EL:: Telemetría de {frecuencia}Hz sincronizada en el Vacío.")

# Ejemplo de ejecución automática:
# auto_registrar_uso(432.0, "RESONANCIA_ARMONICA")