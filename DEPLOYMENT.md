# 🚀 Guía Completa de Despliegue — Open Media Video Suite

Esta guía detalla los pasos de instalación, configuración y acceso para **Open Media Video Suite** en distintos entornos de trabajo: Windows (Docker Desktop / WSL2), Linux nativo y Servidores Cloud / VPS.

---

## 📋 Requisitos Previos Generales

Independientemente del entorno, necesitarás:
- **Git** instalado.
- **Docker Engine** (v20.10 o superior) y **Docker Compose** (v2.0 o superior).
- Mínimo recomendado: 2 vCPU y 2 GB de RAM (FFmpeg se beneficia de mayor potencia de CPU).
- Espacio libre en disco suficiente para procesamiento de video (mínimo 10–20 GB recomendados).

---

## 💻 1. Windows con WSL2 (Windows Subsystem for Linux)

Este entorno es ideal para desarrollo y pruebas en sistemas Windows.

### Pasos:
1. Abre tu terminal de WSL (Ubuntu/Debian).
2. Clona el repositorio e ingresa a la carpeta:
   ```bash
   git clone [https://github.com/JoseEmiliano/openmediavideo.git](https://github.com/JoseEmiliano/openmediavideo.git)
   cd openmediavideo

Inicia el contenedor con Docker Compose:

Bash
docker compose up --build -d
Acceso:

Generalmente puedes acceder desde el navegador de Windows en: http://localhost:5000

Si Windows no resuelve localhost hacia WSL2, obtén la IP interna asignada al contenedor:

Bash
docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' wsl_yt_downloader
Accede ingresando en tu navegador a: http://<IP_OBTENIDA>:5000

🖥️ 2. Windows con Docker Desktop
Si utilizas Docker Desktop integrado sin consola interactiva de WSL:

Abre PowerShell o Windows Terminal.

Clona el repositorio y entra al directorio:

PowerShell
git clone [https://github.com/JoseEmiliano/openmediavideo.git](https://github.com/JoseEmiliano/openmediavideo.git)
cd openmediavideo
Levanta la suite:

PowerShell
docker compose up --build -d
Acceso:

Ingresa directamente en tu navegador web a:

👉 http://localhost:5000

🐧 3. Servidor o Estación de Trabajo Linux Nativo (Ubuntu, Debian, etc.)
Ideal para homelabs o servidores dedicados locales.

Pasos:
Clona el repositorio:

Bash
git clone [https://github.com/JoseEmiliano/openmediavideo.git](https://github.com/JoseEmiliano/openmediavideo.git)
cd openmediavideo
Asegúrate de que el usuario tenga permisos para ejecutar Docker (o usa sudo):

Bash
docker compose up --build -d
Acceso:

En local: http://localhost:5000

Desde otra máquina en la misma red LAN: http://<IP_PRIVADA_DEL_SERVIDOR>:5000

☁️ 4. Servidor VPS en la Nube (DigitalOcean, AWS, Hetzner, Linode, etc.)
Para desplegar la herramienta en un servidor accesible públicamente por ti o tu equipo.

Pasos recomendados:
Conéctate por SSH a tu VPS:

Bash
ssh usuario@IP_DEL_VPS
Clona el repositorio e inicia el contenedor:

Bash
git clone [https://github.com/JoseEmiliano/openmediavideo.git](https://github.com/JoseEmiliano/openmediavideo.git)
cd openmediavideo
docker compose up --build -d
Configuración de Firewall:

Asegúrate de permitir el tráfico en el puerto 5000 (o el puerto configurado):

Bash
sudo ufw allow 5000/tcp
Acceso:

Accede vía: http://<IP_PUBLICA_VPS>:5000

🔒 Recomendación de Producción en VPS (Reverse Proxy & HTTPS):
Para despliegues públicos en Internet, se recomienda colocar un proxy inverso como Nginx o Caddy delante del contenedor y configurar certificados SSL con Let's Encrypt:

Configurar en Nginx la directiva client_max_body_size 2048M; para no limitar la subida de videos grandes.

Configurar tiempos de espera largos (proxy_read_timeout 600s;) para evitar interrupciones en procesos largos de codificación de FFmpeg.

🛠️ Comandos de Mantenimiento Útiles
Ver logs en tiempo real:

Bash
docker compose logs -f
Reiniciar el servicio:

Bash
docker compose restart
Detener los servicios:

Bash
docker compose down
Actualizar extractor de fuentes (yt-dlp) en caliente:

Bash
docker exec -it wsl_yt_downloader pip install --upgrade yt-dlp
docker compose restart
