package com.cebrameta.soberania

import android.content.Context
import android.graphics.Canvas
import android.graphics.Paint
import android.graphics.Path
import android.util.AttributeSet
import android.view.View
import kotlin.math.cos
import kotlin.math.sin

/**
 * Visualización tipo espiral/phi (decorativa).
 */
class VistaPhi(context: Context, attrs: AttributeSet?) : View(context, attrs) {

    private val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.STROKE
        strokeWidth = 6f
    }

    private var phase = 0.0

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)

        val w = width.toFloat()
        val h = height.toFloat()
        val cx = w / 2f
        val cy = h / 2f
        val rMax = minOf(cx, cy) * 0.9f

        val path = Path()
        val turns = 6
        val steps = 900
        for (i in 0..steps) {
            val t = i.toDouble() / steps.toDouble()
            val angle = (turns * 2.0 * Math.PI * t) + phase
            val radius = (rMax * t).toFloat()
            val x = cx + (radius * cos(angle)).toFloat()
            val y = cy + (radius * sin(angle)).toFloat()
            if (i == 0) path.moveTo(x, y) else path.lineTo(x, y)
        }

        canvas.drawPath(path, paint)
    }

    fun tick() {
        phase += 0.08
        invalidate()
    }
}
