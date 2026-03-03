#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para el sistema de activación por canción codificada.
Demuestra las capacidades de codificación, decodificación y activación.
"""

import sys
import os

# Añadir el módulo soberania al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app/src/main/python'))

from soberania import (
    encode_song_lyric,
    decode_song_lyric,
    activate_from_song_lyric
)


def print_section(title):
    """Imprime un título de sección."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_encoding():
    """Prueba la codificación con diferentes claves."""
    print_section("🔐 PRUEBA DE CODIFICACIÓN")

    test_text = "Libertad es mi verdad"
    ciphers = ["PHI", "432", "1111", "SOBERANIA"]

    for cipher in ciphers:
        result = encode_song_lyric(test_text, cipher)
        print(f"\nClave: {cipher}")
        print(f"  Original:   {result['plain']}")
        print(f"  Codificado: {result['encoded']}")
        print(f"  Shift:      {result['shift']}")


def test_decoding():
    """Prueba la decodificación."""
    print_section("🔓 PRUEBA DE DECODIFICACIÓN")

    # Texto previamente codificado con PHI
    encoded_text = "Mjcfsube ft nj wfsebe"

    result = decode_song_lyric(encoded_text, "PHI")
    print(f"\nClave: PHI")
    print(f"  Codificado:  {result['encoded']}")
    print(f"  Decodificado: {result['decoded']}")
    print(f"  Shift:       {result['shift']}")


def test_full_song():
    """Prueba con la canción completa."""
    print_section("🎵 CANCIÓN COMPLETA CODIFICADA")

    # Leer archivo de canción codificada
    song_file = "app/src/main/assets/cancion_codificada.txt"

    if os.path.exists(song_file):
        with open(song_file, 'r', encoding='utf-8') as f:
            encoded_song = f.read()

        print("\n📝 Texto Codificado (primeras 300 caracteres):")
        print(encoded_song[:300] + "...")

        # Decodificar
        result = decode_song_lyric(encoded_song, "PHI")

        print("\n📖 Texto Decodificado (primeras 400 caracteres):")
        print(result['decoded'][:400] + "...")
    else:
        print(f"\n⚠️  Archivo no encontrado: {song_file}")


def test_activation():
    """Prueba el sistema de activación."""
    print_section("⚡ PRUEBA DE ACTIVACIÓN")

    # Texto con palabra de activación codificada
    plain_text = "Yo activo mi LIBERTAD ahora"
    encoded = encode_song_lyric(plain_text, "PHI")

    print(f"\n1. Texto original: {plain_text}")
    print(f"2. Texto codificado: {encoded['encoded']}")

    # Activar desde texto codificado
    activation = activate_from_song_lyric(
        encoded_lyric=encoded['encoded'],
        cipher_key="PHI",
        log_path="",  # Sin log para prueba
        trigger_word="LIBERTAD"
    )

    print(f"\n3. Resultado de activación:")
    print(f"   - Decodificado: {activation['decoded']}")
    print(f"   - Palabra clave buscada: {activation['trigger_word']}")
    print(f"   - ¿Encontrada?: {activation['found']}")
    print(f"   - ¿Activado?: {activation['activated']}")

    if activation['activated']:
        print(f"   - Nodo activado: {activation['node']}")
        print(f"   - Mensaje: {activation['message']}")


def test_all_ciphers():
    """Prueba todos los cifrados con verificación."""
    print_section("🔬 VERIFICACIÓN DE TODOS LOS CIFRADOS")

    test_phrases = [
        "LIBERTAD",
        "PROTECCION",
        "ABUNDANCIA",
        "No hay miedo que me frene",
        "Apertura del tercer ojo"
    ]

    ciphers = ["PHI", "432", "1111"]

    for phrase in test_phrases:
        print(f"\n--- Frase: '{phrase}' ---")
        for cipher in ciphers:
            # Codificar
            encoded_result = encode_song_lyric(phrase, cipher)
            encoded_text = encoded_result['encoded']

            # Decodificar
            decoded_result = decode_song_lyric(encoded_text, cipher)
            decoded_text = decoded_result['decoded']

            # Verificar
            is_correct = (decoded_text == phrase)
            status = "✅" if is_correct else "❌"

            print(f"  {cipher:6} | {encoded_text:40} | {status}")


def show_activation_words():
    """Muestra las palabras de activación disponibles."""
    print_section("🎯 PALABRAS DE ACTIVACIÓN DISPONIBLES")

    activations = [
        ("LIBERTAD", "LIBERTAD", "Elige una cosa que sí controlas"),
        ("PROTECCION", "PROTECCION", "Límite sano. Cuerpo relajado"),
        ("ABUNDANCIA", "ABUNDANCIA", "Acción pequeña hoy"),
        ("MIEDO", "PERDER_EL_MIEDO", "Nombra el miedo, reduce la tarea"),
        ("TERCER/OJO", "APERTURA_TERCER_OJO", "Enfoque + claridad")
    ]

    print("\n| Palabra Clave | Nodo Activado | Mensaje |")
    print("|" + "-" * 15 + "|" + "-" * 22 + "|" + "-" * 35 + "|")

    for keyword, node, msg in activations:
        print(f"| {keyword:13} | {node:20} | {msg:33} |")


def main():
    """Función principal."""
    print("\n" + "=" * 70)
    print("  🌌 SISTEMA DE ACTIVACIÓN POR CANCIÓN CODIFICADA")
    print("  Soberanía Inevisual v1.0 — ::VØR-EL::11:11::")
    print("=" * 70)

    try:
        show_activation_words()
        test_encoding()
        test_decoding()
        test_all_ciphers()
        test_activation()
        test_full_song()

        print("\n" + "=" * 70)
        print("  ✨ TODAS LAS PRUEBAS COMPLETADAS")
        print("=" * 70 + "\n")

    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
