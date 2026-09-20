from flask import Flask, render_template_string, request, send_file, session, abort, redirect, url_for, jsonify
from downloader import obtener_formatos_disponibles, descargar_multimedia
from toolbox import convertir_o_comprimir_video
import os
import threading

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = os.path.abspath("downloads")
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

descarga_estado = {"mensaje": "Esperando inicio...", "archivo": None, "completado": False}

COMMON_STYLE = """
    body { font-family: Arial, sans-serif; background: #0f172a; color: #f8fafc; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
    .card { background: #1e293b; padding: 2rem; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.5); width: 460px; box-sizing: border-box; }
    h2 { text-align: center; color: #38bdf8; margin-top: 0; }
    label { font-size: 13px; color: #cbd5e1; display: block; margin-top: 10px; }
    input, select, button { width: 100%; padding: 10px; margin-top: 6px; border-radius: 6px; border: none; box-sizing: border-box; }
    input, select { background: #334155; color: white; }
    button { background: #0ea5e9; color: white; font-weight: bold; cursor: pointer; margin-top: 15px; }
    button:hover { background: #0284c7; }
    a { display: block; text-align: center; margin-top: 15px; color: #38bdf8; text-decoration: none; font-size: 14px; }
    .btn-tool { background: #334155; color: #38bdf8; border: 1px solid #38bdf8; text-align: center; padding: 12px; border-radius: 6px; margin-top: 10px; display: block; text-decoration: none; font-weight: bold; }
    .btn-tool:hover { background: #0ea5e9; color: white; }
    .error { color: #f87171; text-align: center; font-size: 14px; margin-top: 10px; }
    .progress-box { margin-top: 15px; background: #0f172a; padding: 12px; border-radius: 6px; border: 1px solid #38bdf8; }
    #status-text { font-size: 13px; color: #38bdf8; font-family: monospace; text-align: center; margin: 0; word-break: break-all; }
    .donation-box { margin-top: 18px; text-align: center; border-top: 1px solid #334155; padding-top: 12px; }
    .donation-box p { font-size: 12px; color: #94a3b8; margin-bottom: 6px; }
    .donation-box img { height: 32px; }
    .footer-brand { margin-top: 15px; text-align: center; font-size: 11px; color: #64748b; border-top: 1px dashed #334155; padding-top: 10px; }
    .footer-brand a { color: #38bdf8; text-decoration: none; font-weight: bold; font-size: 11px; margin-top: 2px; display: inline; }
"""

HTML_HOME = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Open Media Video Suite</title>
    <style>""" + COMMON_STYLE + """</style>
</head>
<body>
    <div class="card">
        <h2>🎬 Open Media Suite</h2>
        <p style="text-align:center; color:#94a3b8; font-size:13px;">Selecciona una herramienta multimedia:</p>
        
        <a href="/downloader" class="btn-tool">📥 Descargador Multimedia</a>
        <a href="/convert-tools" class="btn-tool">🔄 Conversor y Compresor de Video</a>

        <div class="donation-box" style="margin-top:25px;">
            <p>¿Te gusta esta herramienta Open Source?</p>
            <a href="https://buymeacoffee.com/josenunez1t" target="_blank">
                <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee">
            </a>
        </div>

        <div class="footer-brand">
            Hecho con amor 💙 por José Emiliano<br>
            <a href="https://gestioncloud.com.ar" target="_blank">GESTIONCLOUD.COM.AR</a>
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
    <title>Descargador - Open Media</title>
    <style>""" + COMMON_STYLE + """</style>
</head>
<body>
    <div class="card">
        <h2>📥 Descargador</h2>
        <form method="POST" action="/inspect">
            <label>URL del enlace multimedia:</label>
            <input type="text" name="url" required placeholder="https://...">
            <button type="submit">Inspeccionar Calidades</button>
        </form>
        {% if error %}
            <p class="error">{{ error }}</p>
        {% endif %}
        <a href="/">⬅ Volver al menú principal</a>
        <div class="footer-brand">
            Hecho con amor 💙 por José Emiliano<br><a href="https://gestioncloud.com.ar" target="_blank">GESTIONCLOUD.COM.AR</a>
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
    <title>Seleccionar Calidad - Open Media</title>
    <style>""" + COMMON_STYLE + """</style>
    <script>
        function iniciarDescarga(event) {
            event.preventDefault();
            let btn = document.getElementById('btn-descargar');
            btn.disabled = true;
            btn.innerText = "Procesando...";
            let formData = new FormData(document.getElementById('download-form'));
            fetch('/download-async', { method: 'POST', body: formData }).then(r => r.json()).then(data => {
                if (data.status === 'started') verificarProgreso();
            });
        }
        function verificarProgreso() {
            let interval = setInterval(() => {
                fetch('/progress').then(res => res.json()).then(data => {
                    document.getElementById('status-text').innerText = data.mensaje;
                    if (data.completado) {
                        clearInterval(interval);
                        document.getElementById('status-text').innerText = "¡Proceso finalizado! Descargando...";
                        window.location.href = '/download-file';
                        setTimeout(() => { btn = document.getElementById('btn-descargar'); btn.disabled = false; btn.innerText = "Descargar a mi PC"; }, 3000);
                    }
                });
            }, 800);
        }
    </script>
</head>
<body>
    <div class="card">
        <h2>⚙️ Procesando Stream</h2>
        <form id="download-form" onsubmit="iniciarDescarga(event)">
            <label>Seleccionar formato / resolución:</label>
            <select name="format_id">
                <option value="audio">🎧 Solo Audio (MP3)</option>
                {% for f in formatos %}
                    <option value="{{ f.id }}">📺 {{ f.res }} ({{ f.ext }})</option>
                {% endfor %}
            </select>
            <button type="submit" id="btn-descargar">Descargar a mi PC</button>
        </form>
        <div class="progress-box"><p id="status-text">Estado: Esperando acción...</p></div>
        <a href="/downloader">⬅ Volver</a>
    </div>
</body>
</html>
"""

HTML_CONVERT = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Conversor y Compresor - Open Media</title>
    <style>""" + COMMON_STYLE + """</style>
</head>
<body>
    <div class="card">
        <h2>🔄 Conversor y Compresor</h2>
        <form method="POST" action="/convert-action" enctype="multipart/form-data">
            <label>Sube tu archivo de video local:</label>
            <input type="file" name="video_file" accept="video/*" required style="padding: 6px; background:#334155;">
            
            <label>Formato de salida:</label>
            <select name="format_out">
                <option value="mp4">MP4 (Estándar Universal)</option>
                <option value="mkv">MKV (Alta Compatibilidad)</option>
                <option value="webm">WebM (Optimizado Web)</option>
            </select>

            <label>Nivel de compresión / calidad:</label>
            <select name="preset">
                <option value="comprimir">📉 Comprimir (Reducir tamaño de archivo)</option>
                <option value="normal" selected>⚖️ Normal (Balanceado)</option>
                <option value="alta">📈 Alta Calidad (Conservar definición)</option>
            </select>

            <button type="submit">Procesar Archivo</button>
        </form>
        {% if error %}
            <p class="error">{{ error }}</p>
        {% endif %}
        <a href="/">⬅ Volver al menú principal</a>
        <div class="footer-brand">
            Hecho con amor 💙 por José Emiliano<br><a href="https://gestioncloud.com.ar" target="_blank">GESTIONCLOUD.COM.AR</a>
        </div>
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML_HOME)

@app.route('/downloader', methods=['GET'])
def downloader_ui():
    return render_template_string(HTML_DOWNLOADER)

@app.route('/convert-tools', methods=['GET'])
def convert_tools():
    return render_template_string(HTML_CONVERT)

@app.route('/convert-action', methods=['POST'])
def convert_action():
    if 'video_file' not in request.files:
        return render_template_string(HTML_CONVERT, error="No se adjuntó ningún archivo.")
    
    file = request.files['video_file']
    if file.filename == '':
        return render_template_string(HTML_CONVERT, error="Nombre de archivo vacío.")

    format_out = request.form.get('format_out', 'mp4')
    preset = request.form.get('preset', 'normal')

    input_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(input_path)

    output_path = convertir_o_comprimir_video(input_path, formato_salida=format_out, preset_calidad=preset)

    # Limpiar archivo original subido
    try:
        os.remove(input_path)
    except:
        pass

    if output_path and os.path.exists(output_path):
        def generate():
            try:
                with open(output_path, "rb") as f: yield from f
            finally:
                try: os.remove(output_path)
                except: pass
        return app.response_class(generate(), mimetype="application/octet-stream", headers={"Content-Disposition": f"attachment; filename={os.path.basename(output_path)}"})
    
    return render_template_string(HTML_CONVERT, error="Error al procesar el video con FFmpeg.")

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
    descarga_estado = {"mensaje": "Iniciando descarga...", "archivo": None, "completado": False}

    def tarea():
        global descarga_estado
        def hook(msg): descarga_estado["mensaje"] = msg
        fp = descargar_multimedia(url, format_id=fid, modo=modo, progress_hook=hook)
        if fp and os.path.exists(fp):
            descarga_estado["archivo"] = fp
            descarga_estado["mensaje"] = "¡Procesamiento completado!"
            descarga_estado["completado"] = True
        else:
            descarga_estado["mensaje"] = "Error en el procesamiento."

    threading.Thread(target=tarea).start()
    return jsonify({"status": "started"})

@app.route('/progress', methods=['GET'])
def progress():
    global descarga_estado
    return jsonify(descarga_estado)

@app.route('/download-file', methods=['GET'])
def download_file():
    global descarga_estado
    fp = descarga_estado.get("archivo")
    if fp and os.path.exists(fp):
        def generate():
            try:
                with open(fp, "rb") as f: yield from f
            finally:
                try: os.remove(fp)
                except: pass
        return app.response_class(generate(), mimetype="application/octet-stream", headers={"Content-Disposition": f"attachment; filename={os.path.basename(fp)}"})
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
