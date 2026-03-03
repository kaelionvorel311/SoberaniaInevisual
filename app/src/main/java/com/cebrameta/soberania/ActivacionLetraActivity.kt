package com.cebrameta.soberania

import android.os.Bundle
import android.view.View
import android.view.inputmethod.EditorInfo
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform
import com.cebrameta.soberania.databinding.ActivityActivacionLetraBinding
import java.io.File
import kotlin.concurrent.thread

/**
 * Activación a través de la letra de una canción codificada.
 *
 * Flujo:
 *   1. Se muestran 5 versos cifrados (hex) con pistas parciales.
 *   2. El usuario escribe la frase correcta de cada verso.
 *   3. Al acertar, el verso se revela y se avanza al siguiente.
 *   4. Al completar los 5 versos, se desbloquea la activación de resonancia
 *      completa (432 Hz + registro en bitácora).
 */
class ActivacionLetraActivity : AppCompatActivity() {

    private lateinit var binding: ActivityActivacionLetraBinding

    private lateinit var versos: List<VersoActivacion>
    private var indiceActual = 0

    private val nucleo = NucleoSoberano()

    /* Indicadores de progreso (barras) */
    private val indicadores: Array<View> by lazy {
        arrayOf(
            binding.indicador1,
            binding.indicador2,
            binding.indicador3,
            binding.indicador4,
            binding.indicador5
        )
    }

    // Colores
    private val colorBloqueado = 0xFF333355.toInt()
    private val colorDesbloqueado = 0xFFE0C878.toInt()
    private val colorCompleto = 0xFFFFD700.toInt()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityActivacionLetraBinding.inflate(layoutInflater)
        setContentView(binding.root)

        versos = CancionSoberana.generarVersos()
        indiceActual = 0

        mostrarVersoActual()
        actualizarIndicadores()

        // Verificar al pulsar botón
        binding.btnVerificar.setOnClickListener {
            verificarIntento()
        }

        // Verificar al pulsar "Done" en teclado
        binding.inputFrase.setOnEditorActionListener { _, actionId, _ ->
            if (actionId == EditorInfo.IME_ACTION_DONE) {
                verificarIntento()
                true
            } else false
        }

        // Activar resonancia completa (solo visible al completar todos los versos)
        binding.btnActivarResonancia.setOnClickListener {
            activarResonanciaCompleta()
        }

        binding.btnVolver.setOnClickListener {
            finish()
        }
    }

    override fun onStop() {
        super.onStop()
        nucleo.detener()
    }

    // ─── Lógica principal ───────────────────────────────────────────

    private fun verificarIntento() {
        if (indiceActual >= versos.size) return

        val frase = binding.inputFrase.text?.toString() ?: ""
        if (frase.isBlank()) {
            binding.txtResultado.text = getString(R.string.escribe_la_frase)
            binding.txtResultado.setTextColor(0xFFCC6666.toInt())
            return
        }

        val verso = versos[indiceActual]
        val exito = CancionSoberana.intentarDesbloqueo(verso, frase)

        if (exito) {
            // Verso desbloqueado
            val textoRevelado = CancionSoberana.revelarVerso(verso)
            binding.txtResultado.text = getString(R.string.verso_desbloqueado)
            binding.txtResultado.setTextColor(0xFF66EEBB.toInt())

            binding.txtVersoRevelado.text = "\"$textoRevelado\""
            binding.txtVersoRevelado.visibility = View.VISIBLE

            actualizarIndicadores()
            registrarDesbloqueo(verso, textoRevelado)

            // Avanzar al siguiente verso tras un breve delay
            binding.btnVerificar.postDelayed({
                indiceActual++
                binding.inputFrase.text?.clear()
                binding.txtVersoRevelado.visibility = View.GONE
                binding.txtResultado.text = ""

                if (CancionSoberana.activacionCompleta(versos)) {
                    mostrarActivacionCompleta()
                } else {
                    mostrarVersoActual()
                }
            }, 1800)

        } else {
            // Frase incorrecta
            binding.txtResultado.text = getString(R.string.frase_incorrecta)
            binding.txtResultado.setTextColor(0xFFCC6666.toInt())
            binding.txtVersoRevelado.visibility = View.GONE

            // Animación sutil de shake
            binding.inputFrase.animate()
                .translationX(12f).setDuration(60)
                .withEndAction {
                    binding.inputFrase.animate()
                        .translationX(-12f).setDuration(60)
                        .withEndAction {
                            binding.inputFrase.animate()
                                .translationX(0f).setDuration(60)
                                .start()
                        }.start()
                }.start()
        }
    }

    private fun mostrarVersoActual() {
        if (indiceActual >= versos.size) return

        val verso = versos[indiceActual]
        binding.labelVersoNum.text = getString(R.string.verso_n_de_total, verso.numero, versos.size)
        binding.txtPista.text = verso.pista
        binding.txtCifrado.text = verso.hexCifrado
        binding.inputFrase.isEnabled = true
        binding.btnVerificar.isEnabled = true
    }

    private fun actualizarIndicadores() {
        for (i in indicadores.indices) {
            val color = if (i < versos.size && versos[i].desbloqueado) colorDesbloqueado else colorBloqueado
            indicadores[i].setBackgroundColor(color)
        }
    }

    private fun mostrarActivacionCompleta() {
        // Ocultar controles de verso
        binding.labelVersoNum.text = getString(R.string.todos_versos_desbloqueados)
        binding.txtPista.visibility = View.GONE
        binding.txtCifrado.visibility = View.GONE
        binding.inputFrase.isEnabled = false
        binding.btnVerificar.isEnabled = false
        binding.txtResultado.text = ""

        // Pintar todos los indicadores en dorado
        for (ind in indicadores) {
            ind.setBackgroundColor(colorCompleto)
        }

        // Mostrar panel de activación completa con la letra entera
        binding.panelActivacionCompleta.visibility = View.VISIBLE
        val letraCompleta = versos.joinToString("\n") { "\"${CancionSoberana.revelarVerso(it)}\"" }
        binding.txtLetraCompleta.text = letraCompleta
    }

    // ─── Resonancia final ───────────────────────────────────────────

    private fun activarResonanciaCompleta() {
        binding.txtEstadoResonancia.text = getString(R.string.resonancia_activando)
        binding.btnActivarResonancia.isEnabled = false

        thread(start = true) {
            // Registrar activación completa en bitácora
            registrarActivacionCompleta()

            // Generar resonancia 432 Hz por 22 segundos (11 × 2, sello doble)
            nucleo.activarResonancia(432.0, 22)

            runOnUiThread {
                binding.txtEstadoResonancia.text = getString(R.string.resonancia_completada)
                binding.btnActivarResonancia.isEnabled = true
            }
        }
    }

    // ─── Bitácora (Python) ──────────────────────────────────────────

    private fun getPython(): Python {
        if (!Python.isStarted()) {
            Python.start(AndroidPlatform(this))
        }
        return Python.getInstance()
    }

    private fun getLogFile(): File {
        val dir = File(filesDir, "bitacora")
        if (!dir.exists()) dir.mkdirs()
        return File(dir, "bitacora.jsonl")
    }

    private fun registrarDesbloqueo(verso: VersoActivacion, textoRevelado: String) {
        thread(start = true) {
            try {
                val py = getPython()
                py.getModule("soberania").callAttr(
                    "log_event",
                    getLogFile().absolutePath,
                    mapOf(
                        "type" to "letra_verso_desbloqueado",
                        "verso" to verso.numero,
                        "texto" to textoRevelado
                    )
                )
            } catch (_: Exception) {
            }
        }
    }

    private fun registrarActivacionCompleta() {
        try {
            val py = getPython()
            val letraCompleta = versos.joinToString(" | ") { CancionSoberana.revelarVerso(it) }
            py.getModule("soberania").callAttr(
                "log_activacion_letra",
                getLogFile().absolutePath,
                letraCompleta,
                versos.size
            )
        } catch (_: Exception) {
        }
    }
}
