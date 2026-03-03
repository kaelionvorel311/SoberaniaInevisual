# -*- coding: utf-8 -*-
"""Módulo Python para Soberanía Inevisual (modo Android con Chaquopy).

Objetivo: utilidades REALES (sin "magia bonita"):
- Generar audios WAV (tono senoidal) y guardarlos en almacenamiento interno.
- Leer archivos de texto (assets copiados o rutas internas).
- Correr "nodos" como acciones definidas (paquetes de UX) + bitácora pro en JSONL.
- QRNG realista: opción online (ANU QRNG) y fallback offline (secrets).

Notas técnicas:
- En Android no es realista correr Qiskit completo en el dispositivo (tamaño/compilación).
  Lo realista es: 1) QRNG via API, 2) Qiskit en un servidor y la app consume el resultado.
"""

from __future__ import annotations

import json
import math
import os
import time
import wave
import struct
import secrets
from typing import List, Dict, Any, Optional

PHI = (1 + 5 ** 0.5) / 2


# -------------------------
# Secuencias / animación
# -------------------------
def phi_sequence(n: int = 16) -> List[float]:
    n = max(1, int(n))
    return [round(PHI ** i, 6) for i in range(n)]


def breath_wave(steps: int = 64) -> List[float]:
    steps = max(8, int(steps))
    out = []
    for i in range(steps):
        x = (2 * math.pi * i) / (steps - 1)
        out.append(round((math.sin(x - math.pi / 2) + 1) / 2, 6))
    return out


# -------------------------
# Bitácora pro (JSONL)
# -------------------------
def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def log_event(log_path: str, event: Dict[str, Any]) -> str:
    """Guarda un evento en JSON Lines (1 JSON por línea). Devuelve el log_path."""
    log_path = str(log_path)
    _ensure_dir(os.path.dirname(log_path))
    payload = dict(event)
    payload.setdefault("ts", int(time.time() * 1000))
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    return log_path


def read_log_tail(log_path: str, max_lines: int = 50) -> str:
    """Lee las últimas N líneas del log (sin cargar todo si es grande)."""
    log_path = str(log_path)
    max_lines = max(1, int(max_lines))
    if not os.path.exists(log_path):
        return ""
    # lectura simple: para logs chicos basta
    with open(log_path, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()
    tail = lines[-max_lines:]
    return "".join(tail)


# -------------------------
# Nodos (acciones)
# -------------------------
_NODE_MESSAGES = {
    "APERTURA_TERCER_OJO": "Enfoque + claridad. Respira 4-4-6, observa sin juicio.",
    "PROTECCION": "Límite sano. Cuerpo relajado, mente firme.",
    "ABUNDANCIA": "Acción pequeña hoy. Gratitud práctica, no magia instantánea.",
    "LIBERTAD": "Elige una cosa que sí controlas y hazla ahora.",
    "PERDER_EL_MIEDO": "Nombra el miedo, reduce la tarea al 1% y avanza.",
}


def activate_node(node: str = "APERTURA_TERCER_OJO") -> Dict[str, str]:
    node = str(node).strip().upper() or "NODO"
    ts = int(time.time() * 1000)
    msg = _NODE_MESSAGES.get(node, "Nodo activado. Mantén atención y presencia.")
    return {"node": node, "message": msg, "ts": str(ts)}


def run_node(node: str, log_path: str, meta_json: str = "{}") -> Dict[str, Any]:
    """Ejecuta un nodo y lo registra en la bitácora.

    meta_json: string JSON con datos opcionales (ej: {"source":"ui","note":"..."}).
    """
    pack = activate_node(node)
    try:
        meta = json.loads(meta_json or "{}")
        if not isinstance(meta, dict):
            meta = {}
    except Exception:
        meta = {}

    event = {
        "type": "node_run",
        "node": pack["node"],
        "message": pack["message"],
        "meta": meta,
    }
    log_event(log_path, event)
    return {"ok": True, "pack": pack}


# -------------------------
# Lectura de archivos
# -------------------------
def read_text_file(path: str, max_chars: int = 4000) -> Dict[str, Any]:
    """Lee un archivo de texto desde ruta interna. Devuelve preview + tamaño."""
    path = str(path)
    max_chars = max(256, int(max_chars))
    if not os.path.exists(path):
        return {"ok": False, "error": "NOT_FOUND", "path": path}

    with open(path, "r", encoding="utf-8", errors="replace") as f:
        data = f.read(max_chars + 1)
    truncated = len(data) > max_chars
    preview = data[:max_chars]
    return {"ok": True, "path": path, "preview": preview, "truncated": truncated}


# -------------------------
# Audio: generar WAV
# -------------------------
def generate_tone_wav(
    out_path: str,
    frequency_hz: float = 432.0,
    duration_s: float = 11.0,
    sample_rate: int = 44100,
    amplitude: float = 0.6,
) -> Dict[str, Any]:
    """Genera un WAV mono 16-bit PCM con tono senoidal."""
    out_path = str(out_path)
    _ensure_dir(os.path.dirname(out_path))

    frequency_hz = float(frequency_hz)
    duration_s = max(0.2, float(duration_s))
    sample_rate = int(sample_rate)
    amplitude = min(1.0, max(0.05, float(amplitude)))

    n_samples = int(duration_s * sample_rate)
    max_amp = int(32767 * amplitude)

    with wave.open(out_path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(sample_rate)

        for i in range(n_samples):
            t = i / sample_rate
            sample = int(max_amp * math.sin(2 * math.pi * frequency_hz * t))
            wf.writeframes(struct.pack("<h", sample))

    return {
        "ok": True,
        "out_path": out_path,
        "frequency_hz": frequency_hz,
        "duration_s": duration_s,
        "sample_rate": sample_rate,
        "samples": n_samples,
    }


# -------------------------
# QRNG realista
# -------------------------
def qrng_bytes(n_bytes: int = 16, mode: str = "anu") -> Dict[str, Any]:
    """Devuelve bytes aleatorios.

    mode:
      - 'anu': intenta ANU QRNG (internet), fallback a 'secrets'
      - 'secrets': offline (criptográficamente fuerte), NO cuántico
    """
    n_bytes = max(1, int(n_bytes))
    mode = (mode or "").strip().lower() or "anu"

    if mode == "anu":
        try:
            # ANU QRNG API: devuelve uint16; convertimos a bytes
            import requests  # instalado vía pip en Chaquopy

            # pedimos n_bytes*8 bits, pero API maneja arrays; pedimos uint8 directo si posible
            # Endpoint típico: /API/jsonI.php?length=...&type=uint8
            url = "https://qrng.anu.edu.au/API/jsonI.php"
            params = {"length": n_bytes, "type": "uint8"}
            r = requests.get(url, params=params, timeout=6)
            r.raise_for_status()
            j = r.json()
            if not j.get("success"):
                raise RuntimeError("ANU not success")
            data = j.get("data", [])
            b = bytes(int(x) & 0xFF for x in data[:n_bytes])
            return {"ok": True, "mode": "anu", "n_bytes": n_bytes, "hex": b.hex()}
        except Exception as e:
            b = secrets.token_bytes(n_bytes)
            return {"ok": True, "mode": "secrets_fallback", "n_bytes": n_bytes, "hex": b.hex(), "note": str(e)}

    # offline
    b = secrets.token_bytes(n_bytes)
    return {"ok": True, "mode": "secrets", "n_bytes": n_bytes, "hex": b.hex()}


def ping() -> str:
    return "Python OK"


# -------------------------
# Activación por Letra de Canción Codificada
# -------------------------
def decode_song_lyric(encoded_text: str, cipher_key: str = "PHI") -> Dict[str, Any]:
    """Decodifica una letra de canción usando un cifrado simple basado en desplazamiento.

    cipher_key determina el algoritmo:
    - "PHI": desplazamiento basado en la razón áurea (1.618... -> 1 o 2 chars)
    - "432": desplazamiento de 4 caracteres
    - "1111": desplazamiento de 11 caracteres
    - Cualquier otro: desplazamiento basado en la suma de valores ASCII del key
    """
    encoded_text = str(encoded_text)
    cipher_key = str(cipher_key).strip().upper() or "PHI"

    # Determinar desplazamiento
    if cipher_key == "PHI":
        shift = int(PHI)  # 1
    elif cipher_key == "432":
        shift = 4
    elif cipher_key == "1111":
        shift = 11
    else:
        shift = sum(ord(c) for c in cipher_key) % 26

    decoded = []
    for char in encoded_text:
        if char.isalpha():
            is_upper = char.isupper()
            base = ord('A') if is_upper else ord('a')
            # Decodificar: restar el desplazamiento
            decoded_char = chr((ord(char) - base - shift) % 26 + base)
            decoded.append(decoded_char)
        else:
            decoded.append(char)

    decoded_text = "".join(decoded)
    return {
        "ok": True,
        "cipher_key": cipher_key,
        "shift": shift,
        "encoded": encoded_text,
        "decoded": decoded_text
    }


def encode_song_lyric(plain_text: str, cipher_key: str = "PHI") -> Dict[str, Any]:
    """Codifica una letra de canción usando el mismo algoritmo de decode_song_lyric."""
    plain_text = str(plain_text)
    cipher_key = str(cipher_key).strip().upper() or "PHI"

    # Determinar desplazamiento
    if cipher_key == "PHI":
        shift = int(PHI)  # 1
    elif cipher_key == "432":
        shift = 4
    elif cipher_key == "1111":
        shift = 11
    else:
        shift = sum(ord(c) for c in cipher_key) % 26

    encoded = []
    for char in plain_text:
        if char.isalpha():
            is_upper = char.isupper()
            base = ord('A') if is_upper else ord('a')
            # Codificar: sumar el desplazamiento
            encoded_char = chr((ord(char) - base + shift) % 26 + base)
            encoded.append(encoded_char)
        else:
            encoded.append(char)

    encoded_text = "".join(encoded)
    return {
        "ok": True,
        "cipher_key": cipher_key,
        "shift": shift,
        "plain": plain_text,
        "encoded": encoded_text
    }


def activate_from_song_lyric(
    encoded_lyric: str,
    cipher_key: str = "PHI",
    log_path: str = "",
    trigger_word: str = "LIBERTAD"
) -> Dict[str, Any]:
    """Decodifica una letra y busca una palabra clave para activar el sistema.

    Si la letra decodificada contiene trigger_word, activa el nodo correspondiente.
    """
    encoded_lyric = str(encoded_lyric)
    cipher_key = str(cipher_key).strip().upper() or "PHI"
    trigger_word = str(trigger_word).strip().upper() or "LIBERTAD"

    # Decodificar
    decode_result = decode_song_lyric(encoded_lyric, cipher_key)
    decoded_text = decode_result["decoded"]

    # Buscar palabra clave
    found = trigger_word in decoded_text.upper()

    result = {
        "ok": True,
        "decoded": decoded_text,
        "trigger_word": trigger_word,
        "found": found,
        "activated": False,
        "node": None
    }

    if found:
        # Mapear palabra clave a nodo
        node_map = {
            "LIBERTAD": "LIBERTAD",
            "PROTECCION": "PROTECCION",
            "ABUNDANCIA": "ABUNDANCIA",
            "MIEDO": "PERDER_EL_MIEDO",
            "TERCER": "APERTURA_TERCER_OJO",
            "OJO": "APERTURA_TERCER_OJO"
        }

        # Buscar qué nodo activar
        node = None
        for keyword, node_name in node_map.items():
            if keyword in decoded_text.upper():
                node = node_name
                break

        if not node:
            node = "LIBERTAD"  # default

        # Activar nodo
        pack = activate_node(node)
        result["activated"] = True
        result["node"] = node
        result["message"] = pack["message"]

        # Registrar en bitácora si se proporciona ruta
        if log_path:
            event = {
                "type": "song_lyric_activation",
                "cipher_key": cipher_key,
                "trigger_word": trigger_word,
                "node": node,
                "decoded_preview": decoded_text[:100]
            }
            log_event(log_path, event)

    return result
