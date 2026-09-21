from flask import Flask, render_template_string, request, send_file, session, abort, redirect, url_for, jsonify
from downloader import obtener_formatos_disponibles, descargar_multimedia
from toolbox import convertir_o_comprimir_video
import os
import threading
import glob

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = os.path.abspath("downloads")
app.config['MAX_CONTENT_LENGTH'] = 2048 * 1024 * 1024
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

descarga_estado = {"mensaje": "Esperando inicio...", "archivo": None, "completado": False}
conversion_estado = {"mensaje": "Esperando archivo...", "archivo": None, "completado": False}

MODERN_STYLE = """
    :root {
        --bg-main: #0b0f19;
        --card-bg: #111827;
        --border-color: #1f2937;
        --accent: #38bdf8;
        --accent-hover: #0ea5e9;
        --text-main: #f9fafb;
        --text-muted: #9ca3af;
        --danger: #ef4444;
        --danger-hover: #dc2626;
        --success: #10b981;
    }
    body {
        font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
        background: var(--bg-main);
        color: var(--text-main);
        margin: 0;
        min-height: 100vh;
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 20px;
    }
    .container {
        width: 100%;
        max-width: 580px;
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        padding: 2.5rem;
        border-radius: 16px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6);
        box-sizing: border-box;
    }
    h2 {
        text-align: center;
        color: var(--accent);
        margin-top: 0;
        font-size: 1.5rem;
        font-weight: 700;
        letter-spacing: -0.025em;
    }
    .subtitle {
        text-align: center;
        color: var(--text-muted);
        font-size: 0.85rem;
        margin-bottom: 1.5rem;
    }
    label {
        font-size: 0.85rem;
        color: var(--text-muted);
        display: block;
        margin-top: 12px;
        font-weight: 500;
    }
    input[type="text"], select, input[type="file"] {
        width: 100%;
        padding: 12px;
        margin-top: 6px;
        border-radius: 8px;
        border: 1px solid var(--border-color);
        background: #1f2937;
        color: var(--text-main);
        box-sizing: border-box;
        font-size: 0.95rem;
    }
    input[type="file"]::file-selector-button {
        background: var(--accent);
        color: #000;
        border: none;
        padding: 6px 12px;
        border-radius: 4px;
        font-weight: bold;
        cursor: pointer;
    }
    button, .btn-primary {
        width: 100%;
        padding: 12px;
        margin-top: 18px;
        border-radius: 8px;
        border: none;
        background: var(--accent);
        color: #0b0f19;
        font-weight: 700;
        cursor: pointer;
        font-size: 0.95rem;
        text-align: center;
        text-decoration: none;
        display: block;
        box-sizing: border-box;
        transition: background 0.2s;
    }
    button:hover, .btn-primary:hover {
        background: var(--accent-hover);
    }
    .tool-card {
        background: rgba(31, 41, 55, 0.4);
        border: 1px solid var(--border-color);
        padding: 18px;
        border-radius: 12px;
        margin-top: 16px;
        transition: border-color 0.2s;
    }
    .tool-card:hover {
        border-color: var(--accent);
    }
    .tool-card h3 {
        margin: 0 0 6px 0;
        font-size: 1.05rem;
        color: var(--accent);
    }
    .tool-card p {
        margin: 0 0 12px 0;
        font-size: 0.82rem;
        color: var(--text-muted);
        line-height: 1.4;
    }
    .btn-danger {
        background: var(--danger);
        color: white;
    }
    .btn-danger:hover {
        background: var(--danger-hover);
    }
    .error {
        color: #f87171;
        text-align: center;
        font-size: 0.85rem;
        margin-top: 12px;
    }
    .success-msg {
        color: var(--success);
        text-align: center;
        font-size: 0.85rem;
        margin-top: 12px;
        font-weight: bold;
    }
    .progress-container {
        margin-top: 16px;
        background: #0b0f19;
        padding: 14px;
        border-radius: 8px;
        border: 1px solid var(--accent);
        text-align: center;
        display: none;
    }
    .progress-bar-bg {
        width: 100%;
        background: #1f2937;
        border-radius: 6px;
        height: 8px;
        margin-top: 10px;
        overflow: hidden;
    }
    .progress-bar-fill {
        width: 0%;
        height: 100%;
        background: var(--accent);
        transition: width 0.4s ease;
    }
    #status-text, #conv-status-text {
        font-size: 0.85rem;
        color: var(--accent);
        font-family: monospace;
        margin: 0;
        word-break: break-all;
    }
    .temp-files-box {
        margin-top: 20px;
        background: #161e2e;
        border: 1px dashed var(--border-color);
        padding: 12px;
        border-radius: 8px;
        font-size: 0.8rem;
    }
    .temp-files-box h4 {
        margin: 0 0 8px 0;
        color: var(--text-muted);
        font-size: 0.85rem;
    }
    .temp-file-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 6px 0;
        border-bottom: 1px solid #1f2937;
    }
    .temp-file-item:last-child {
        border-bottom: none;
    }
    .temp-file-actions a {
        font-size: 0.75rem;
        margin-left: 8px;
        padding: 3px 8px;
        border-radius: 4px;
        text-decoration: none;
        display: inline-block;
    }
    .btn-sm-download { background: var(--success); color: white; }
    .btn-sm-delete { background: var(--danger); color: white; }
    .back-link {
        display: block;
        text-align: center;
        margin-top: 18px;
        color: var(--accent);
        text-decoration: none;
        font-size: 0.85rem;
    }
    .footer-brand {
        margin-top: 20px;
        text-align: center;
        font-size: 0.75rem;
        color: var(--text-muted);
        border-top: 1px solid var(--border-color);
        padding-top: 12px;
    }
    .footer-brand a {
        color: var(--accent);
        text-decoration: none;
        font-weight: bold;
    }
"""

HTML_HOME = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Open Media Video Suite</title>
    <style>""" + MODERN_STYLE + """</style>
</head>
<body>
    <div class="container">
        <h2>🎬 Open Media Video Suite</h2>
        <p class="subtitle">Plataforma self-hosted avanzada para gestión multimedia.</p>

        <div class="tool-card">
            <h3>📥 Descargador Multimedia</h3>
            <p>Inspecciona enlaces de portales de video, lista calidades desde 144p hasta 4K (MP4/WebM) o extrae audio en alta calidad (MP3).</p>
            <a href="/downloader" class="btn-primary" style="margin-top:0;">Acceder al Descargador</a>
        </div>

        <div class="tool-card">
            <h3>🔄 Conversor y Compresor</h3>
            <p>Sube archivos locales y optimiza su tamaño o formato (MP4, MKV, WebM) con compresión inteligente asistida por FFmpeg.</p>
            <a href="/convert-tools" class="btn-primary" style="margin-top:0;">Acceder al Conversor</a>
        </div>

        <div class="tool-card" style="border-color: rgba(239, 68, 68, 0.4);">
            <h3 style="color: #f87171;">🛡️ Control de Archivos Temporales</h3>
            <p>Los archivos se descargan directo a tu navegador y se limpian solos. Si algo quedara retenido, puedes gestionarlos aquí.</p>
            <a href="/clean-cache" class="btn-primary btn-danger" style="margin-top:5px;">🗑️ Limpiar Todos los Temporales</a>
        </div>

        {% if temp_files %}
        <div class="temp-files-box">
            <h4>Archivos Temporales Activos en Servidor:</h4>
            {% for file in temp_files %}
            <div class="temp-file-item">
                <span style="overflow:hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 240px;" title="{{ file }}">{{ file }}</span>
                <div class="temp-file-actions">
                    <a href="/download-direct/{{ file }}" class="btn-sm-download">📥 Bajar</a>
                    <a href="/delete-file/{{ file }}" class="btn-sm-delete">❌ Borrar</a>
                </div>
            </div>
            {% endfor %}
        </div>
        {% endif %}

        {% if msg %}
            <p class="success-msg">{{ msg }}</p>
        {% endif %}

        <div class="donation-box" style="margin-top:16px; text-align:center; border-top: 1px solid var(--border-color); padding-top:12px;">
            <p style="font-size: 0.75rem; color: var(--text-muted); margin-bottom:6px;">¿Te gusta esta herramienta Open Source?</p>
            <a href="https://buymeacoffee.com/josenunez1t" target="_blank">
                <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height:28px;">
            </a><a href='https://cafecito.app/kempcloud' rel='noopener' target='_blank'><img srcset='https://cdn.cafecito.app/imgs/buttons/button_1.png 1x, https://cdn.cafecito.app/imgs/buttons/button_1_2x.png 2x, https://cdn.cafecito.app/imgs/buttons/button_1_3.75x.png 3.75x' src='https://cdn.cafecito.app/imgs/buttons/button_1.png' alt='Invitame un café en cafecito.app' /></a>
            
        </div>

        <div class="footer-brand">
            Hecho con amor 💙 por JoseEmiliano<br>
            Un proyecto de <a href="https://gestioncloud.com.ar" target="_blank">GESTIONCLOUD.COM.AR</a>
        </div>
    </div>
</body>
</html>
"""

HTML_DOWNLOADER = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Descargador - Open Media Video Suite</title>
    <style>""" + MODERN_STYLE + """</style>
</head>
<body>
    <div class="container">
        <h2>📥 Descargador Multimedia</h2>
        <form method="POST" action="/inspect">
            <label>URL del enlace multimedia:</label>
            <input type="text" name="url" required placeholder="https://...">
            <button type="submit">Inspeccionar Calidades</button>
        </form>
        {% if error %}
            <p class="error">{{ error }}</p>
        {% endif %}
        <a href="/" class="back-link">⬅ Volver al menú principal</a>
        <div class="footer-brand">
            Hecho con amor 💙 por JoseEmiliano<br>Un proyecto de <a href="https://gestioncloud.com.ar" target="_blank">GESTIONCLOUD.COM.AR</a>
        </div>
    </div>
</body>
</html>
"""

HTML_SELECT = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Seleccionar Calidad - Open Media Video Suite</title>
    <style>""" + MODERN_STYLE + """</style>
    <script>
        function iniciarDescarga(event) {
            event.preventDefault();
            let btn = document.getElementById('btn-descargar');
            btn.style.display = 'none';
            document.getElementById('progress-box').style.display = 'block';
            let formData = new FormData(document.getElementById('download-form'));
            fetch('/download-async', { method: 'POST', body: formData }).then(r => r.json()).then(data => {
                if (data.status === 'started') verificarProgreso();
            });
        }
        function verificarProgreso() {
            let interval = setInterval(() => {
                fetch('/progress').then(res => res.json()).then(data => {
                    document.getElementById('status-text').innerText = data.mensaje;
                    let match = data.mensaje.match(/([0-9.]+)%/);
                    if (match) {
                        document.getElementById('bar-fill').style.width = match[1] + '%';
                    }
                    if (data.completado && data.archivo_descarga) {
                        clearInterval(interval);
                        document.getElementById('bar-fill').style.width = '100%';
                        // Disparar descarga limpia directa al navegador mediante enlace temporal
                        window.location.href = '/download-direct/' + encodeURIComponent(data.archivo_descarga);
                        document.getElementById('status-text').innerHTML = "¡Descarga iniciada en tu navegador!<br><br><a href='/' class='btn-primary'>🏠 Volver al inicio</a>";
                    }
                });
            }, 800);
        }
    </script>
</head>
<body>
    <div class="container">
        <h2>⚙️ Procesando Stream</h2>
        <form id="download-form" onsubmit="iniciarDescarga(event)">
            <label>Seleccionar formato / resolución:</label>
            <select name="format_id">
                <option value="audio">🎧 Solo Audio (MP3)</option>
                {% for f in formatos %}
                    <option value="{{ f.id }}">📺 {{ f.res }} ({{ f.ext }})</option>
                {% endfor %}
            </select>
            <button type="submit" id="btn-descargar">Procesar Descarga</button>
        </form>
        <div id="progress-box" class="progress-container">
            <p id="status-text">Iniciando procesamiento...</p>
            <div class="progress-bar-bg"><div id="bar-fill" class="progress-bar-fill"></div></div>
        </div>
        <a href="/downloader" class="back-link">⬅ Volver</a>
    </div>
</body>
</html>
"""

HTML_CONVERT = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Conversor y Compresor - Open Media Video Suite</title>
    <style>""" + MODERN_STYLE + """</style>
    <script>
        function iniciarConversion(event) {
            event.preventDefault();
            let btn = document.getElementById('btn-convertir');
            btn.style.display = 'none';
            document.getElementById('progress-box').style.display = 'block';
            
            let fill = document.getElementById('conv-bar-fill');
            let text = document.getElementById('conv-status-text');
            
            let progresoVisual = 10;
            fill.style.width = progresoVisual + '%';
            text.innerText = "Codificando con FFmpeg...";

            let fakeProgress = setInterval(() => {
                if (progresoVisual < 90) {
                    progresoVisual += 4;
                    fill.style.width = progresoVisual + '%';
                }
            }, 1000);

            let formData = new FormData(document.getElementById('convert-form'));
            fetch('/convert-async', { method: 'POST', body: formData }).then(res => res.json()).then(data => {
                if (data.status === 'started') {
                    verificarProgresoConversion(fakeProgress);
                } else {
                    clearInterval(fakeProgress);
                    alert("Error: " + data.message);
                    btn.style.display = 'block';
                }
            });
        }
        function verificarProgresoConversion(fakeProgress) {
            let fill = document.getElementById('conv-bar-fill');
            let interval = setInterval(() => {
                fetch('/convert-progress').then(res => res.json()).then(data => {
                    document.getElementById('conv-status-text').innerText = data.mensaje;
                    if (data.completado && data.archivo_descarga) {
                        clearInterval(interval);
                        clearInterval(fakeProgress);
                        fill.style.width = '100%';
                        // Disparar descarga limpia directa al navegador
                        window.location.href = '/download-direct/' + encodeURIComponent(data.archivo_descarga);
                        document.getElementById('conv-status-text').innerHTML = "¡Conversión exitosa y descargada!<br><br><a href='/' class='btn-primary'>🏠 Volver al inicio</a>";
                    }
                });
            }, 800);
        }
    </script>
</head>
<body>
    <div class="container">
        <h2>🔄 Conversor y Compresor</h2>
        <form id="convert-form" onsubmit="iniciarConversion(event)">
            <label>Sube tu archivo de video local:</label>
            <input type="file" name="video_file" accept="video/*" required>
            
            <label>Formato de salida:</label>
            <select name="format_out">
                <option value="mp4">MP4 (Estándar Universal)</option>
                <option value="mkv">MKV (Alta Compatibilidad)</option>
                <option value="webm">WebM (Optimizado Web)</option>
            </select>

            <label>Nivel de compresión / calidad:</label>
            <select name="preset">
                <option value="comprimir">📉 Comprimir (Reducir tamaño)</option>
                <option value="normal" selected>⚖️ Normal (Balanceado)</option>
                <option value="alta">📈 Alta Calidad (Definición máxima)</option>
            </select>

            <button type="submit" id="btn-convertir">Procesar Archivo</button>
        </form>

        <div id="progress-box" class="progress-container">
            <p id="conv-status-text">Preparando...</p>
            <div class="progress-bar-bg"><div id="conv-bar-fill" class="progress-bar-fill"></div></div>
        </div>

        <a href="/" class="back-link">⬅ Volver al menú principal</a>
        <div class="footer-brand">
            Hecho con amor 💙 por JoseEmiliano<br>Un proyecto de <a href="https://gestioncloud.com.ar" target="_blank">GESTIONCLOUD.COM.AR</a>
        </div>
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET'])
def index():
    msg = request.args.get('msg', '')
    files = glob.glob(os.path.join(app.config['UPLOAD_FOLDER'], '*'))
    temp_files = [os.path.basename(f) for f in files]
    return render_template_string(HTML_HOME, msg=msg, temp_files=temp_files)

@app.route('/clean-cache', methods=['GET'])
def clean_cache():
    try:
        files = glob.glob(os.path.join(app.config['UPLOAD_FOLDER'], '*'))
        for f in files:
            try: os.remove(f)
            except: pass
        return redirect(url_for('index', msg="¡Caché de temporales limpiada con éxito!"))
    except Exception as e:
        return redirect(url_for('index', msg=f"Error al limpiar: {str(e)}"))

@app.route('/delete-file/<filename>', methods=['GET'])
def delete_file(filename):
    try:
        fp = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(fp):
            os.remove(fp)
        return redirect(url_for('index', msg=f"Archivo {filename} eliminado."))
    except:
        return redirect(url_for('index', msg="No se pudo eliminar el archivo."))

@app.route('/download-direct/<filename>', methods=['GET'])
def download_direct(filename):
    fp = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(fp):
        def generate():
            try:
                with open(fp, "rb") as f:
                    yield from f
            finally:
                try:
                    if os.path.exists(fp):
                        os.remove(fp)
                except:
                    pass
        return app.response_class(
            generate(),
            mimetype="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    return redirect(url_for('index'))

@app.route('/downloader', methods=['GET'])
def downloader_ui():
    return render_template_string(HTML_DOWNLOADER)

@app.route('/convert-tools', methods=['GET'])
def convert_tools():
    return render_template_string(HTML_CONVERT)

@app.route('/convert-async', methods=['POST'])
def convert_async():
    if 'video_file' not in request.files:
        return jsonify({"status": "error", "message": "No se adjuntó archivo."})
    
    file = request.files['video_file']
    if file.filename == '':
        return jsonify({"status": "error", "message": "Nombre de archivo vacío."})

    format_out = request.form.get('format_out', 'mp4')
    preset = request.form.get('preset', 'normal')

    input_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(input_path)

    global conversion_estado
    conversion_estado = {"mensaje": "Codificando con FFmpeg...", "archivo": None, "completado": False, "archivo_descarga": None}

    def tarea_conversion():
        global conversion_estado
        try:
            output_path = convertir_o_comprimir_video(input_path, formato_salida=format_out, preset_calidad=preset)
            if output_path and os.path.exists(output_path):
                conversion_estado["archivo"] = output_path
                conversion_estado["archivo_descarga"] = os.path.basename(output_path)
                conversion_estado["mensaje"] = "¡Conversión finalizada!"
                conversion_estado["completado"] = True
            else:
                conversion_estado["mensaje"] = "Error en motor FFmpeg."
        except Exception as e:
            conversion_estado["mensaje"] = f"Error: {str(e)}"
        finally:
            try: os.remove(input_path)
            except: pass

    threading.Thread(target=tarea_conversion).start()
    return jsonify({"status": "started"})

@app.route('/convert-progress', methods=['GET'])
def convert_progress():
    global conversion_estado
    if not conversion_estado.get("completado"):
        # Resguardo si el archivo procesado ya existe físicamente
        files = glob.glob(os.path.join(app.config['UPLOAD_FOLDER'], '*_procesado.*'))
        if files:
            latest = max(files, key=os.path.getctime)
            conversion_estado["archivo"] = latest
            conversion_estado["archivo_descarga"] = os.path.basename(latest)
            conversion_estado["completado"] = True
            conversion_estado["mensaje"] = "¡Conversión finalizada!"
    return jsonify(conversion_estado)

@app.route('/inspect', methods=['POST'])
def inspect():
    url = request.form.get('url', '').strip()
    try:
        formatos = obtener_formatos_disponibles(url)
        if not formatos:
            return render_template_string(HTML_DOWNLOADER, error="No se encontraron formatos para esta URL.")
        session['url'] = url
        return render_template_string(HTML_SELECT, formatos=formatos)
    except Exception as e:
        return render_template_string(HTML_DOWNLOADER, error=f"Error al analizar: {str(e)}")

@app.route('/download-async', methods=['POST'])
def download_async():
    url = session.get('url')
    if not url: return jsonify({"status": "error"}), 403
    format_id = request.form.get('format_id', '').strip()
    modo = "audio" if format_id == "audio" else "video"
    fid = None if modo == "audio" else format_id
    
    global descarga_estado
    descarga_estado = {"mensaje": "Iniciando descarga...", "archivo": None, "completado": False, "archivo_descarga": None}

    def tarea():
        global descarga_estado
        def hook(msg): descarga_estado["mensaje"] = msg
        fp = descargar_multimedia(url, format_id=fid, modo=modo, progress_hook=hook)
        if fp and os.path.exists(fp):
            descarga_estado["archivo"] = fp
            descarga_estado["archivo_descarga"] = os.path.basename(fp)
            descarga_estado["mensaje"] = "¡Procesamiento completado!"
            descarga_estado["completado"] = True
        else:
            descarga_estado["mensaje"] = "Error en procesamiento."

    threading.Thread(target=tarea).start()
    return jsonify({"status": "started"})

@app.route('/progress', methods=['GET'])
def progress():
    global descarga_estado
    if not descarga_estado.get("completado"):
        files = glob.glob(os.path.join(app.config['UPLOAD_FOLDER'], '*'))
        # Excluir carpetas
        files = [f for f in files if os.path.isfile(f)]
        if files:
            latest = max(files, key=os.path.getctime)
            descarga_estado["archivo"] = latest
            descarga_estado["archivo_descarga"] = os.path.basename(latest)
            descarga_estado["completado"] = True
            descarga_estado["mensaje"] = "¡Procesamiento completado!"
    return jsonify(descarga_estado)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
