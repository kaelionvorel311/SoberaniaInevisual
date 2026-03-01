# Soberanía Inevisual — Proyecto Android (APK)

Este ZIP contiene un proyecto **Android Studio** listo para abrir y compilar.

## Requisitos
- Android Studio (cualquier versión reciente).
- JDK 17 (Android Studio ya lo incluye).
- Internet solo para que Gradle descargue dependencias la primera vez.

## Cómo compilar e instalar en tu Android
1. Descomprime el ZIP.
2. Abre **Android Studio** → **Open** → elige la carpeta `SoberaniaInevisual`.
3. Espera a que termine **Gradle Sync**.
4. Conecta tu teléfono por USB y activa:
   - Ajustes → Acerca del teléfono → toca “Número de compilación” 7 veces
   - Opciones de desarrollador → **Depuración USB**
5. En Android Studio, presiona **Run ▶** (Debug). Se instalará en tu dispositivo.

## Generar el APK (para compartir/instalar manual)
- Build → **Build Bundle(s) / APK(s)** → **Build APK(s)**
- Android Studio te mostrará la ruta del APK generado.

## Qué incluye la app
- Botón “Activar 432Hz” (tono simple con AudioTrack, 11s).
- Visualización PHI (decorativa).
- “Dashboard” abre `dashboard_soberano.html` desde assets.
- En `assets/` también van tus scripts `.py` y audio `.mp3` como referencia.

> Nota: los scripts Python no se ejecutan dentro de Android en esta versión.
> Si quieres que sí, se puede integrar con **Chaquopy** (requiere cambios).
