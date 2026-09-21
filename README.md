# 🎬 Open Media Video Suite

<div align="center">

![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Python](https://img.shields.io/badge/Python_3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![FFmpeg](https://img.shields.io/badge/FFmpeg-007808?style=for-the-badge&logo=ffmpeg&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)

**Plataforma web *self-hosted* integral diseñada para la inspección, descarga de streams multimedia y el procesamiento, compresión y conversión local de video.**

Hecho con amor 💙 por **JoseEmiliano**  
Un proyecto impulsado por [GESTIONCLOUD.COM.AR](https://gestioncloud.com.ar)

[Características](#-características-principales) • [Arquitectura](#-estructura-del-proyecto) • [Instalación](#-guía-de-implementación-y-despliegue) • [Limitaciones](#️-limitaciones-y-restricciones-técnicas) • [Comunidad](#-contribuciones-y-comunidad)

</div>

---

## 🚀 Características Principales

1. **📥 Descargador Multimedia Avanzado:**
   - **Inspección de Streams:** Analiza enlaces en tiempo real y detecta pistas de audio y resoluciones de video disponibles.
   - **Múltiples Calidades:** Soporta selecciones desde `144p` hasta `4K` en contenedores `MP4` y `WebM`, además de extracción directa de audio a `MP3` en 192 kbps.
   - **Estrategia Fallback:** Algoritmo de reintentos secuenciales para sortear limitaciones en plataformas con streaming fragmentado o adaptativo (DASH/HLS).

2. **🔄 Conversor y Compresor de Video:**
   - **Formatos Soportados:** Conversión flexible entre `MP4`, `MKV` y `WebM`.
   - **Perfiles Predefinidos:**
     - 📉 **Comprimir:** Optimizado para reducir tamaño de archivo sacrificando el mínimo de nitidez.
     - ⚖️ **Normal (Balanceado):** Ajuste estándar ideal para distribución web.
     - 📈 **Alta Calidad:** Preserva la tasa de bits y definición original.
   - **Mapeo Robusto (`-map 0`):** Integración estricta con FFmpeg para asegurar que ninguna pista de audio o video quede huérfana en el contenedor de salida.

3. **🧹 Descarga Limpia y Gestión de Temporales:**
   - **Streaming Directo al Navegador:** El cliente recibe el archivo procesado mediante streaming HTTP (`Content-Disposition: attachment`), eliminando la dependencia de rutas internas de almacenamiento.
   - **Autolimpieza Automática:** El servidor purga los archivos procesados tan pronto concluye la transferencia hacia el cliente.
   - **Panel de Resguardo:** Interfaz interactiva en la página de inicio que lista archivos temporales activos con opciones para descarga directa o eliminación manual individual/global ante cortes de red imprevistos.

---

## 📁 Estructura del Proyecto

```text
openmediavideo/
├── app.py                 # Servidor Flask, rutas web y streaming HTTP
├── downloader.py          # Lógica de inspección y descarga con yt-dlp
├── toolbox.py             # Módulo de procesamiento y transcodificación con FFmpeg
├── requirements.txt       # Dependencias de Python
├── Dockerfile             # Imagen base con Python 3.11 y binarios de FFmpeg
├── docker-compose.yml     # Orquestación de servicios y montaje de volúmenes
└── downloads/             # Directorio de trabajo y caché temporal

[![Invitame un café en cafecito.app](https://cdn.cafecito.app/imgs/buttons/button_1.svg)](https://cafecito.app/kempcloud)

