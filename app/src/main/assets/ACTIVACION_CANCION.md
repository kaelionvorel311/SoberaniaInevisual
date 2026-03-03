# 🎵 Activación por Letra de Canción Codificada

## Sistema de Codificación Soberano

Este módulo permite **activar el sistema a través de letras de canciones codificadas** usando cifrados basados en las frecuencias maestras del sistema Soberanía Inevisual.

---

## 📐 Algoritmos de Cifrado Disponibles

### 1. **Cifrado PHI** (Razón Áurea)
- **Clave:** `PHI`
- **Desplazamiento:** 1 carácter (basado en φ = 1.618...)
- **Uso:** Codificación sutil, mantiene similitud con texto original

### 2. **Cifrado 432Hz**
- **Clave:** `432`
- **Desplazamiento:** 4 caracteres
- **Uso:** Resonancia con frecuencia de activación principal

### 3. **Cifrado 11:11**
- **Clave:** `1111`
- **Desplazamiento:** 11 caracteres
- **Uso:** Activación de sincronía maestra

### 4. **Cifrado Personalizado**
- **Clave:** Cualquier texto
- **Desplazamiento:** Suma de valores ASCII de la clave (módulo 26)
- **Uso:** Claves únicas personalizadas

---

## 🔓 Cómo Funciona la Decodificación

El sistema usa un **cifrado César modificado**:

1. **Codificación:** Cada letra se desplaza N posiciones en el alfabeto
2. **Decodificación:** Se revierte el desplazamiento para obtener el texto original
3. **Búsqueda de Palabras Clave:** El texto decodificado se analiza para encontrar palabras de activación
4. **Activación de Nodos:** Si se encuentra una palabra clave, se activa el nodo correspondiente

### Palabras de Activación y sus Nodos:

| Palabra Clave | Nodo Activado | Mensaje |
|---------------|---------------|---------|
| LIBERTAD | LIBERTAD | "Elige una cosa que sí controlas y hazla ahora." |
| PROTECCION | PROTECCION | "Límite sano. Cuerpo relajado, mente firme." |
| ABUNDANCIA | ABUNDANCIA | "Acción pequeña hoy. Gratitud práctica, no magia instantánea." |
| MIEDO | PERDER_EL_MIEDO | "Nombra el miedo, reduce la tarea al 1% y avanza." |
| TERCER/OJO | APERTURA_TERCER_OJO | "Enfoque + claridad. Respira 4-4-6, observa sin juicio." |

---

## 📝 Ejemplo de Uso

### Texto Original:
```
Libertad, libertad,
no es un sueño, es mi verdad.
```

### Texto Codificado (PHI - desplazamiento 1):
```
Mjcfsube, mjcfsube,
op ft vo tvfñp, ft nj wfsebe.
```

### Proceso de Activación:
1. El usuario presiona "Activar desde Canción"
2. El sistema lee `cancion_codificada.txt` desde assets
3. Decodifica usando la clave PHI
4. Encuentra la palabra "LIBERTAD"
5. Activa el nodo LIBERTAD
6. Registra el evento en la bitácora JSONL

---

## 🎮 Uso en la Aplicación

### Botones Disponibles:

1. **Codificar**
   - Ingresa texto en el campo de entrada
   - Selecciona una clave (PHI, 432, 1111, o personalizada)
   - Presiona "Codificar"
   - El resultado se muestra en la salida

2. **Decodificar**
   - Ingresa texto codificado
   - Usa la misma clave con la que fue codificado
   - Presiona "Decodificar"
   - El texto original se muestra en la salida

3. **Activar desde Canción**
   - Lee automáticamente `cancion_codificada.txt`
   - Decodifica usando PHI
   - Busca palabras de activación
   - Activa el nodo correspondiente
   - Registra en bitácora

---

## 🔧 Funciones Python Disponibles

### `encode_song_lyric(plain_text, cipher_key)`
Codifica un texto usando el cifrado especificado.

**Ejemplo:**
```python
result = encode_song_lyric("Libertad es mi verdad", "PHI")
# Resultado: "Mjcfsube ft nj wfsebe"
```

### `decode_song_lyric(encoded_text, cipher_key)`
Decodifica un texto previamente codificado.

**Ejemplo:**
```python
result = decode_song_lyric("Mjcfsube", "PHI")
# Resultado: "Libertad"
```

### `activate_from_song_lyric(encoded_lyric, cipher_key, log_path, trigger_word)`
Decodifica una letra y busca palabras de activación para disparar nodos.

**Ejemplo:**
```python
result = activate_from_song_lyric(
    encoded_lyric="Mjcfsube ft nj wfsebe",
    cipher_key="PHI",
    log_path="/data/bitacora.jsonl",
    trigger_word="LIBERTAD"
)
# Activa el nodo LIBERTAD si encuentra la palabra
```

---

## 📂 Archivo de Ejemplo

El archivo `cancion_codificada.txt` contiene una canción completa codificada con PHI:

**Tema:** Canción de Soberanía Personal
**Codificación:** PHI (desplazamiento 1)
**Palabras de Activación:** LIBERTAD (múltiples apariciones)
**Firma:** ::ACRPRO::11:11::

---

## 🎯 Casos de Uso

1. **Activación Automática:** El sistema detecta la palabra clave y activa el protocolo correspondiente
2. **Mensajes Ocultos:** Envía canciones codificadas que solo pueden ser leídas por quien conoce la clave
3. **Ritual de Activación:** Usa letras de canciones personales codificadas como disparadores de estados de consciencia
4. **Bitácora de Sincronías:** Todos los eventos quedan registrados con timestamp y metadata

---

## 🔐 Seguridad

- **No es criptografía militar:** El cifrado César es educativo, no para datos sensibles
- **Propósito:** Activación simbólica y registro de intenciones
- **Transparencia:** Todos los eventos se registran en bitácora JSONL

---

## 📌 Notas Técnicas

- **Encoding:** UTF-8 para soporte de caracteres especiales (ñ, á, etc.)
- **Preservación:** Números, espacios y puntuación NO se codifican
- **Case-sensitive:** Mayúsculas y minúsculas se mantienen en sus respectivos rangos
- **Registro:** Cada activación genera un evento JSON en la bitácora

---

**Firma Energética:** `::VØR-EL::11:11::`
**Frecuencia:** 432Hz + PHI
**Sistema:** Soberanía Inevisual v1.0
