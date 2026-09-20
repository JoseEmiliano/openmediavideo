# 🎬 Open Media Video Downloader (Self-Hosted Edition)

Herramienta web modular, segura y de código abierto desarrollada por **José Nuñez** para respaldar clases, conferencias y recursos educativos (ideal para materias de ingeniería y laboratorios) desde múltiples plataformas de video. 

El sistema está empaquetado mediante contenedores **Docker** para garantizar un despliegue aislado, reproducible y multiplataforma en cualquier entorno local (WSL, Linux, macOS, Windows o servidores Proxmox).

---

## 🏗️ Arquitectura y Estructura del Proyecto

```text
yt-downloader-lab/
│
├── app.py                # Interfaz web (Flask) en 2 pasos, telemetría y botón de donación.
├── downloader.py         # Motor lógico basado en yt-dlp, validaciones de seguridad y FFmpeg.
├── Dockerfile            # Imagen base (Python 3.11-slim + FFmpeg + Usuario no-root).
├── docker-compose.yml    # Orquestador local con volúmenes persistentes y seguridad.
├── requirements.txt      # Dependencias del ecosistema Python.
├── LICENSE               # Licencia MIT (Derechos de autor protegidos).
└── README.md             # Documentación técnica del proyecto.

📄 Contenido de los Archivos
app.py: Controla rutas HTTP, sondeo asíncrono de progreso y autolimpieza post-descarga.

downloader.py: Extrae metadatos con yt-dlp, aplica validaciones estrictas (URL_REGEX) contra ataques y fusiona streams con FFmpeg.

Dockerfile: Compila la imagen con FFmpeg ejecutándose bajo usuario seguro (appuser).

docker-compose.yml: Mapea el puerto 5000 y gestiona volúmenes y privilegios.

⚙️ Guía de Despliegue Local (Self-Hosted)
Clonar e ingresar:

Bash
git clone [https://github.com/tu-usuario/open-media-video-downloader.git](https://github.com/tu-usuario/open-media-video-downloader.git)
cd open-media-video-downloader
Levantar el servicio:

Bash
docker compose up --build -d
Acceso local:

En Linux / macOS: http://localhost:5000

En WSL (Windows): Ejecuta hostname -I en tu terminal y accede mediante http://<tu-ip-wsl>:5000.

⚖️ Licencia y Copyright
© 2026 José Nuñez. Distribuido bajo la Licencia MIT. Consulta el archivo LICENSE para más detalles.

☕ Apoya este Proyecto

