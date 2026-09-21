# 🎬 Open Media Video Suite

Plataforma web *self-hosted* integral desarrollada con **Python, Flask, Docker, yt-dlp y FFmpeg** para la descarga de streams multimedia y el procesamiento local de videos.

Hecho con amor 💙 por **JoseEmiliano**  
Un proyecto de [GESTIONCLOUD.COM.AR](https://gestioncloud.com.ar)

---

## 🚀 Características Principales

1. **📥 Descargador Multimedia (YouTube y más):**
   - Inspección inteligente de enlaces multimedia.
   - Listado de resoluciones disponibles desde `144p` hasta `4K` (`MP4`/`WebM`) o extracción directa de audio en alta calidad (`MP3`).
   - Barra de progreso dinámica en tiempo real.

2. **🔄 Conversor y Compresor de Video:**
   - Subida de archivos locales de video.
   - Opciones de exportación universal (`MP4`, `MKV`, `WebM`).
   - Perfiles ajustables: *Comprimir (reducir tamaño)*, *Normal (balanceado)* y *Alta Calidad*.

3. **🧹 Mantenimiento Automático:**
   - Limpieza automática de la carpeta temporal de descargas tras completarse la transferencia al navegador, optimizando el espacio en disco.

---

## 🛠️ Tecnologías Utilizadas

* **Backend:** Python 3.11, Flask, yt-dlp, FFmpeg.
* **Frontend:** HTML5, CSS3, JavaScript (Fetch API asíncrona).
* **Despliegue:** Docker & Docker Compose (WSL).

---

## 📦 Instalación y Despliegue con Docker

1. Clona este repositorio o copia los archivos en tu servidor/WSL.
2. Asegúrate de tener instalado **Docker** y **Docker Compose**.
3. Levanta el contenedor ejecutando:

```bash
docker compose up --build -d

Accede a la aplicación desde tu navegador en: http://localhost:5000
