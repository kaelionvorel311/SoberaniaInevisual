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


def log_activacion_letra(log_path: str, letra_completa: str, total_versos: int) -> Dict[str, Any]:
    """Registra la activación completa por letra de canción codificada en la bitácora."""
    log_path = str(log_path)
    event = {
        "type": "activacion_letra_completa",
        "letra": str(letra_completa),
        "total_versos": int(total_versos),
        "sello": "11:11",
        "frecuencia_hz": 432.0,
    }
    log_event(log_path, event)
    return {"ok": True, "versos": total_versos, "sello": "11:11"}


def ping() -> str:
    return "Python OK"
