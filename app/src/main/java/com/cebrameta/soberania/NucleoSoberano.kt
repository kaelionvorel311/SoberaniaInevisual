package com.cebrameta.soberania

import android.media.AudioAttributes
import android.media.AudioFormat
import android.media.AudioManager
import android.media.AudioTrack
import kotlin.math.PI
import kotlin.math.sin

/**
 * Núcleo de resonancia: genera tono senoidal simple (p.ej. 432Hz) con AudioTrack.
 * Nota: esto es audio "real" (sonido), no una afirmación de efectos médicos o místicos.
 */
class NucleoSoberano {

    private var audioTrack: AudioTrack? = null
    @Volatile private var running: Boolean = false

    fun activarResonancia(hz: Double, duracionSeg: Int) {
        detener()

        val sampleRate = 44100
        val totalSamples = (duracionSeg * sampleRate).coerceAtLeast(1)
        val buffer = ShortArray(totalSamples)

        val amp = 0.2 // volumen relativo (0..1) para evitar saturación
        for (i in 0 until totalSamples) {
            val t = i.toDouble() / sampleRate.toDouble()
            val s = (sin(2.0 * PI * hz * t) * Short.MAX_VALUE * amp).toInt()
            buffer[i] = s.toShort()
        }

        val minBuf = AudioTrack.getMinBufferSize(
            sampleRate,
            AudioFormat.CHANNEL_OUT_MONO,
            AudioFormat.ENCODING_PCM_16BIT
        ).coerceAtLeast(2048)

        val track = AudioTrack(
            AudioAttributes.Builder()
                .setUsage(AudioAttributes.USAGE_MEDIA)
                .setContentType(AudioAttributes.CONTENT_TYPE_MUSIC)
                .build(),
            AudioFormat.Builder()
                .setEncoding(AudioFormat.ENCODING_PCM_16BIT)
                .setSampleRate(sampleRate)
                .setChannelMask(AudioFormat.CHANNEL_OUT_MONO)
                .build(),
            minBuf,
            AudioTrack.MODE_STREAM,
            AudioManager.AUDIO_SESSION_ID_GENERATE
        )

        audioTrack = track
        running = true
        track.play()

        // Escribimos en chunks para no bloquear demasiado.
        var offset = 0
        val chunk = 2048
        while (running && offset < buffer.size) {
            val len = minOf(chunk, buffer.size - offset)
            track.write(buffer, offset, len)
            offset += len
        }

        detener()
    }

    fun detener() {
        running = false
        audioTrack?.let { t ->
            try { t.pause() } catch (_: Throwable) {}
            try { t.flush() } catch (_: Throwable) {}
            try { t.stop() } catch (_: Throwable) {}
            try { t.release() } catch (_: Throwable) {}
        }
        audioTrack = null
    }
}
