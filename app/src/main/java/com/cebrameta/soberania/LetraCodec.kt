package com.cebrameta.soberania

/**
 * Codificador/decodificador de letras de canciones para el sistema de activación.
 *
 * Usa un cifrado PHI-shift: cada carácter se desplaza por un valor derivado
 * de la secuencia de Fibonacci/PHI y la posición en el verso.
 * La clave maestra es "1111" (el sello soberano).
 *
 * Flujo de activación:
 *   1. La letra de la canción se almacena CODIFICADA (versos cifrados).
 *   2. El usuario debe ingresar la frase-clave correcta para decodificar cada verso.
 *   3. Al decodificar todos los versos, se activa la resonancia completa.
 */
class LetraCodec(private val semilla: Int = 1111) {

    companion object {
        private const val CHARSET_SIZE = 256
    }

    /* Genera la secuencia de desplazamientos basada en Fibonacci + semilla */
    private fun generarDesplazamientos(longitud: Int): IntArray {
        val shifts = IntArray(longitud)
        var a = semilla % 13 + 1
        var b = semilla % 7 + 3
        for (i in 0 until longitud) {
            val next = (a + b) % CHARSET_SIZE
            shifts[i] = next
            a = b
            b = next
            if (b == 0) b = (semilla % 11) + 1
        }
        return shifts
    }

    /** Codifica un texto plano en texto cifrado (hex-encoded). */
    fun codificar(textoPlano: String): String {
        val bytes = textoPlano.toByteArray(Charsets.UTF_8)
        val shifts = generarDesplazamientos(bytes.size)
        val encoded = ByteArray(bytes.size)
        for (i in bytes.indices) {
            encoded[i] = ((bytes[i].toInt() and 0xFF) xor shifts[i]).toByte()
        }
        return encoded.joinToString("") { "%02x".format(it) }
    }

    /** Decodifica un texto cifrado (hex) al texto plano original. */
    fun decodificar(hexCifrado: String): String {
        val bytes = hexCifrado.chunked(2).map { it.toInt(16).toByte() }.toByteArray()
        val shifts = generarDesplazamientos(bytes.size)
        val decoded = ByteArray(bytes.size)
        for (i in bytes.indices) {
            decoded[i] = ((bytes[i].toInt() and 0xFF) xor shifts[i]).toByte()
        }
        return String(decoded, Charsets.UTF_8)
    }

    /**
     * Verifica si una frase-clave coincide con el verso decodificado.
     * Comparación insensible a mayúsculas y espacios extra.
     */
    fun verificarFrase(hexCifrado: String, intento: String): Boolean {
        val original = decodificar(hexCifrado).trim().lowercase()
        val prueba = intento.trim().lowercase()
        return original == prueba
    }
}

/**
 * Canción codificada para la activación soberana.
 *
 * Cada verso está cifrado con LetraCodec(1111).
 * El usuario debe descifrar/ingresar la frase correcta de cada verso
 * para desbloquear la activación completa.
 *
 * La letra original (en claro) es un himno de soberanía personal:
 *
 *   Verso 1: "Yo soy la frecuencia que despierta"
 *   Verso 2: "Mi voz resuena en cuatrocientos treinta y dos"
 *   Verso 3: "El miedo se disuelve en luz dorada"
 *   Verso 4: "Sello mi campo con el código once once"
 *   Verso 5: "Soberanía inevisual activada"
 *
 * Pista para cada verso: se muestra una pista parcial al usuario.
 */
data class VersoActivacion(
    val numero: Int,
    val hexCifrado: String,
    val pista: String,
    var desbloqueado: Boolean = false
)

object CancionSoberana {

    private val codec = LetraCodec(1111)

    /* Versos en texto plano — se codifican al inicializar */
    private val versosPlanos = listOf(
        "Yo soy la frecuencia que despierta",
        "Mi voz resuena en cuatrocientos treinta y dos",
        "El miedo se disuelve en luz dorada",
        "Sello mi campo con el codigo once once",
        "Soberania inevisual activada"
    )

    private val pistas = listOf(
        "Y_ s_y l_ fr_cu_nc_a qu_ d_sp_ _rta",
        "M_ v_z r_su_na _n cu_tr_ci_nt_s tr_ _nta y d_s",
        "El m_ _do s_ d_su_lv_ _n l_z d_r_da",
        "S_ll_ m_ c_mp_ c_n _l c_d_g_ _nc_ _nc_",
        "S_b_r_n_a _n_v_su_l _ct_v_da"
    )

    /** Genera la lista de versos codificados (estado fresco, todos bloqueados). */
    fun generarVersos(): List<VersoActivacion> {
        return versosPlanos.mapIndexed { i, texto ->
            VersoActivacion(
                numero = i + 1,
                hexCifrado = codec.codificar(texto),
                pista = pistas[i],
                desbloqueado = false
            )
        }
    }

    /** Intenta desbloquear un verso con la frase ingresada. */
    fun intentarDesbloqueo(verso: VersoActivacion, frase: String): Boolean {
        if (verso.desbloqueado) return true
        val ok = codec.verificarFrase(verso.hexCifrado, frase)
        if (ok) verso.desbloqueado = true
        return ok
    }

    /** Decodifica un verso (para mostrar al desbloquearse). */
    fun revelarVerso(verso: VersoActivacion): String {
        return codec.decodificar(verso.hexCifrado)
    }

    /** ¿Todos los versos desbloqueados? → activación completa. */
    fun activacionCompleta(versos: List<VersoActivacion>): Boolean {
        return versos.all { it.desbloqueado }
    }
}
