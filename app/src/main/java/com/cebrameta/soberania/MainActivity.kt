package com.cebrameta.soberania

import android.content.Intent
import android.media.MediaPlayer
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.widget.ArrayAdapter
import androidx.appcompat.app.AppCompatActivity
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform
import com.cebrameta.soberania.databinding.ActivityMainBinding
import java.io.File
import java.io.FileOutputStream
import kotlin.concurrent.thread

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private val nucleo = NucleoSoberano()

    private var mediaPlayer: MediaPlayer? = null

    private val uiHandler = Handler(Looper.getMainLooper())
    private val ticker = object : Runnable {
        override fun run() {
            binding.vistaPhi.tick()
            uiHandler.postDelayed(this, 33) // ~30 fps
        }
    }

    private val nodos = listOf(
        "APERTURA_TERCER_OJO",
        "PROTECCION",
        "ABUNDANCIA",
        "LIBERTAD",
        "PERDER_EL_MIEDO"
    )

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        // Spinner nodos
        binding.spinnerNodo.adapter = ArrayAdapter(
            this,
            android.R.layout.simple_spinner_dropdown_item,
            nodos
        )

        binding.btnActivar.setOnClickListener {
            // audio (Kotlin) en hilo aparte para no congelar UI
            thread(start = true) {
                registrarUsoEnBitacora(432.0, "PORTAL_ACTIVO_1111")
                nucleo.activarResonancia(432.0, 11)
            }
            uiHandler.removeCallbacks(ticker)
            uiHandler.post(ticker)
        }

        binding.btnDetener.setOnClickListener {
            nucleo.detener()
            detenerMediaPlayer()
            uiHandler.removeCallbacks(ticker)
        }

        binding.btnDashboard.setOnClickListener {
            startActivity(Intent(this, DashboardActivity::class.java))
        }

        binding.btnActivacionLetra.setOnClickListener {
            startActivity(Intent(this, ActivacionLetraActivity::class.java))
        }

        // Ping rápido de Python
        binding.btnPython.setOnClickListener {
            thread(start = true) {
                val py = getPython()
                val result = py.getModule("soberania").callAttr("ping").toString()
                runOnUiThread {
                    binding.pythonOutput.text = "Python: $result"
                }
            }
        }

        // Correr nodo (Python + bitácora JSONL)
        binding.btnRunNode.setOnClickListener {
            val node = binding.spinnerNodo.selectedItem?.toString() ?: "NODO"
            thread(start = true) {
                val py = getPython()
                val logPath = getLogFile().absolutePath
                val metaJson = """{"source":"ui","kind":"node_button"}"""
                val result = py.getModule("soberania")
                    .callAttr("run_node", node, logPath, metaJson)
                    .toString()

                runOnUiThread {
                    binding.pythonOutput.text = "Nodo: $result"
                }
            }
        }

        // Generar WAV con Python y reproducirlo
        binding.btnGenAudioPy.setOnClickListener {
            thread(start = true) {
                val py = getPython()
                val outFile = File(getAudioDir(), "tono_432_python.wav")
                val result = py.getModule("soberania")
                    .callAttr("generate_tone_wav", outFile.absolutePath, 432.0, 11.0, 44100, 0.6)

                runOnUiThread {
                    binding.pythonOutput.text = "Audio (Python): $result"
                    reproducirWav(outFile)
                }
            }
        }

        // Leer archivo (copiamos un asset a almacenamiento interno y lo leemos con Python)
        binding.btnLeerArchivo.setOnClickListener {
            thread(start = true) {
                val py = getPython()
                val local = File(getCacheDirInternal(), "comandos.txt")
                copyAssetIfNeeded("comandos.txt", local)

                val result = py.getModule("soberania")
                    .callAttr("read_text_file", local.absolutePath, 2500)
                    .toString()

                runOnUiThread {
                    binding.pythonOutput.text = "Archivo: $result"
                }
            }
        }

        // QRNG (ANU si hay internet; fallback offline)
        binding.btnQrng.setOnClickListener {
            thread(start = true) {
                val py = getPython()
                val result = py.getModule("soberania")
                    .callAttr("qrng_bytes", 16, "anu")
                    .toString()

                // también lo registramos
                py.getModule("soberania").callAttr(
                    "log_event",
                    getLogFile().absolutePath,
                    mapOf("type" to "qrng", "result" to result)
                )

                runOnUiThread {
                    binding.pythonOutput.text = "QRNG: $result"
                }
            }
        }

        // Ver bitácora (últimas líneas)
        binding.btnVerBitacora.setOnClickListener {
            thread(start = true) {
                val py = getPython()
                val logTail = py.getModule("soberania")
                    .callAttr("read_log_tail", getLogFile().absolutePath, 60)
                    .toString()

                runOnUiThread {
                    binding.pythonOutput.text = if (logTail.isBlank()) "Bitácora: (vacía)" else "Bitácora:\n$logTail"
                }
            }
        }
    }

    override fun onStop() {
        super.onStop()
        nucleo.detener()
        detenerMediaPlayer()
        uiHandler.removeCallbacks(ticker)
    }

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

    private fun getAudioDir(): File {
        val dir = File(filesDir, "audio_py")
        if (!dir.exists()) dir.mkdirs()
        return dir
    }

    private fun getCacheDirInternal(): File {
        val dir = File(filesDir, "assets_cache")
        if (!dir.exists()) dir.mkdirs()
        return dir
    }

    private fun copyAssetIfNeeded(assetName: String, dest: File) {
        if (dest.exists() && dest.length() > 0) return
        assets.open(assetName).use { input ->
            FileOutputStream(dest).use { output ->
                input.copyTo(output)
            }
        }
    }

    private fun reproducirWav(file: File) {
        try {
            detenerMediaPlayer()
            mediaPlayer = MediaPlayer().apply {
                setDataSource(file.absolutePath)
                prepare()
                start()
            }
        } catch (e: Exception) {
            binding.pythonOutput.text = "Error reproduciendo WAV: ${e.message}"
        }
    }

    private fun detenerMediaPlayer() {
        mediaPlayer?.run {
            try {
                stop()
            } catch (_: Exception) {
            }
            release()
        }
        mediaPlayer = null
    }

    private fun registrarUsoEnBitacora(hz: Double, tag: String) {
        // Dejamos este registro simple y además registramos en JSONL con Python cuando esté disponible.
        val prefs = getSharedPreferences("bitacora", MODE_PRIVATE)
        val prev = prefs.getString("log", "") ?: ""
        val now = System.currentTimeMillis()
        val line = "$now | $hz Hz | $tag\n"
        prefs.edit().putString("log", prev + line).apply()

        // Mejor: JSONL (si Python ya está listo)
        try {
            val py = getPython()
            py.getModule("soberania").callAttr(
                "log_event",
                getLogFile().absolutePath,
                mapOf("type" to "tone_kotlin", "hz" to hz, "tag" to tag)
            )
        } catch (_: Exception) {
        }
    }
}
