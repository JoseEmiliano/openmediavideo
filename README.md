# 🎬 Open Media Video Suite

Plataforma web *self-hosted* integral desarrollada con **Python, Flask, Docker, yt-dlp y FFmpeg** diseñada para la descarga eficiente de streams multimedia desde portales de video y el procesamiento, compresión y conversión local de archivos de video.

Hecho con amor 💙 por **JoseEmiliano**  
Un proyecto de [GESTIONCLOUD.COM.AR](https://gestioncloud.com.ar)

---

## 🚀 Características Principales

1. **📥 Descargador Multimedia Avanzado:**
   - Inspección inteligente de enlaces multimedia.
   - Listado dinámico de resoluciones disponibles (desde `144p` hasta `4K` en formatos `MP4` y `WebM`) o extracción directa de audio en alta calidad (`MP3`).
   - Estrategia de reintentos múltiples y respaldo de formatos para garantizar la compatibilidad con plataformas de streaming fragmentado (Youtub, Daily, etc.).

2. **🔄 Conversor y Compresor de Video:**
   - Soporte para subida de archivos locales de video (`MP4`, `MKV`, `WebM`).
   - Opciones de exportación versátiles con compresión inteligente asistida por FFmpeg y mapeo robusto de streams (`-map 0`).
   - Perfiles ajustables: *Comprimir (reducir tamaño)*, *Normal (balanceado)* y *Alta Calidad*.

3. **🧹 Gestión Transparente de Temporales y Autolimpieza:**
   - Los archivos procesados se descargan de forma limpia y directa al navegador del cliente mediante streaming HTTP, eliminándose del servidor automáticamente al finalizar la transferencia.
   - Panel de control y resguardo en la interfaz principal que lista los archivos temporales activos con opciones para descargarlos o eliminarlos de forma individual, además de un botón general de limpieza manual en caso de interrupciones de red.

---

## 🛠️ Tecnologías Utilizadas

* **Backend:** Python 3.11, Flask, yt-dlp, FFmpeg.
* **Frontend:** HTML5, CSS3, JavaScript (Fetch API asíncrona, diseño moderno en tonos oscuros).
* **Despliegue:** Docker & Docker Compose (Optimizado para entornos WSL / Linux).

---

## 📦 Guía de Implementación y Despliegue

### 1. Clonar o preparar el proyecto
Asegúrate de contar con los archivos principales del proyecto en tu directorio de trabajo (por ejemplo, en `~/openmediavideo`):
- `app.py`
- `downloader.py`
- `toolbox.py`
- `requirements.txt`
- `Dockerfile`
- `docker-compose.yml`

### 2. Levantar el contenedor con Docker Compose
Abre tu terminal en la carpeta del proyecto y ejecuta el siguiente comando para compilar y levantar los servicios en segundo plano:

```bash
docker compose up --build -d
```

### 3. Acceso mediante la IP interna del contenedor
Si necesitas interactuar directamente utilizando la dirección IP asignada por la red interna de Docker (ideal para pruebas en WSL):

1. **Obtener la IP interna:**
   ```bash
   docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' wsl_yt_downloader
   ```
2. **Acceder desde el navegador:**
   Ingresa usando la IP obtenida junto al puerto `5000` (por ejemplo, `http://172.18.225.63:5000`).

---

## ⚠️ Limitaciones y Restricciones Técnicas

Para garantizar la estabilidad del sistema, ten en cuenta las siguientes consideraciones:

1. **Límite de tamaño de subida:** Configurado por defecto para aceptar archivos locales de hasta **2 GB** (`MAX_CONTENT_LENGTH`).
2. **Uso de CPU:** La codificación de video mediante FFmpeg (especialmente en perfiles WebM / alta definición) demanda un alto uso de procesamiento. Los videos muy extensos requerirán mayor tiempo de conversión.
3. **Restricciones de fuentes externas:** Algunas plataformas implementan restricciones geográficas, sistemas anti-bot estrictos o requieren autenticación por cookies que pueden provocar fallas intermitentes en la descarga de determinados enlaces.

---

## 🤝 Contribuciones y Comunidad

¡Las contribuciones, comentarios e ideas de la comunidad son totalmente bienvenidas! Si deseas proponer mejoras, reportar problemas o participar en el desarrollo, puedes abrir un *Pull Request* o un *Issue* en el repositorio oficial del proyecto.

---

<div align="center">
    <p>¿Te gusta esta herramienta Open Source?</p>
    <a href="https://buymeacoffee.com/josenunez1t" target="_blank">
        <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height:36px;">
    </a>
    <br><br>
    Made with 💙 por JoseEmiliano — Un proyecto tambien apoyado por <a href="https://gestioncloud.com.ar" target="_blank">GESTIONCLOUD.COM.AR</a>
</div>
