from flask import Flask, render_template_string, request, send_file, session, abort, redirect, url_for, jsonify
from downloader import obtener_formatos_disponibles, descargar_multimedia
import os
import threading

app = Flask(__name__)
app.secret_key = os.urandom(24)

descarga_estado = {"mensaje": "Esperando inicio...", "archivo": None, "completado": False}

COMMON_STYLE = """
    body { font-family: Arial, sans-serif; background: #0f172a; color: #f8fafc; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
    .card { background: #1e293b; padding: 2rem; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.5); width: 440px; box-sizing: border-box; }
    h2 { text-align: center; color: #38bdf8; margin-top: 0; }
    label { font-size: 14px; color: #cbd5e1; }
    input, select, button { width: 100%; padding: 10px; margin-top: 8px; border-radius: 6px; border: none; box-sizing: border-box; }
    input, select { background: #334155; color: white; }
    button { background: #0ea5e9; color: white; font-weight: bold; cursor: pointer; margin-top: 15px; }
    button:hover { background: #0284c7; }
    a { display: block; text-align: center; margin-top: 15px; color: #38bdf8; text-decoration: none; font-size: 14px; }
    .error { color: #f87171; text-align: center; font-size: 14px; margin-top: 10px; }
    .progress-box { margin-top: 15px; background: #0f172a; padding: 12px; border-radius: 6px; border: 1px solid #38bdf8; }
    #status-text { font-size: 13px; color: #38bdf8; font-family: monospace; text-align: center; margin: 0; word-break: break-all; }
    .donation-box { margin-top: 18px; text-align: center; border-top: 1px solid #334155; padding-top: 12px; }
    .donation-box p { font-size: 12px; color: #94a3b8; margin-bottom: 6px; }
    .donation-box img { height: 32px; }
    .footer-brand { margin-top: 15px; text-align: center; font-size: 11px; color: #64748b; border-top: 1px dashed #334155; padding-top: 10px; }
    .footer-brand a { color: #38bdf8; text-decoration: none; font-weight: bold; font-size: 11px; margin-top: 2px; display: inline; }
"""

HTML_INDEX = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Open Media Video - Paso 1</title>
    <style>""" + COMMON_STYLE + """</style>
</head>
<body>
    <div class="card">
        <h2>🎬 Open Media Video</h2>
        <form method="POST" action="/inspect">
            <label>URL del enlace multimedia:</label>
            <input type="text" name="url" required placeholder="https://...">
            <button type="submit">Inspeccionar Calidades</button>
        </form>
        {% if error %}
            <p class="error">{{ error }}</p>
        {% endif %}
        
        <div class="donation-box">
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

HTML_SELECT = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Open Media Video - Paso 2</title>
    <style>""" + COMMON_STYLE + """</style>
    <script>
        function iniciarDescarga(event) {
            event.preventDefault();
            let btn = document.getElementById('btn-descargar');
            btn.disabled = true;
            btn.innerText = "Procesando...";

            let formData = new FormData(document.getElementById('download-form'));

            fetch('/download-async', {
                method: 'POST',
                body: formData
            }).then(response => response.json()).then(data => {
                if (data.status === 'started') {
                    verificarProgreso();
                }
            });
        }

        function verificarProgreso() {
            let interval = setInterval(() => {
                fetch('/progress').then(res => res.json()).then(data => {
                    document.getElementById('status-text').innerText = data.mensaje;
                    if (data.completado) {
                        clearInterval(interval);
                        document.getElementById('status-text').innerText = "¡Proceso finalizado! Descargando archivo...";
                        
                        window.location.href = '/download-file';
                        
                        setTimeout(() => {
                            let btn = document.getElementById('btn-descargar');
                            btn.disabled = false;
                            btn.innerText = "Descargar a mi PC";
                        }, 3000);
                    }
                });
            }, 800);
        }
    </script>
</head>
<body>
    <div class="card">
        <h2>Open Media Video</h2>
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
        
        <div class="progress-box">
            <p id="status-text">Estado: Esperando acción...</p>
        </div>

        <a href="/">⬅ Volver al inicio</a>

        <div class="donation-box">
            <p>Apoya el desarrollo de código abierto</p>
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

@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML_INDEX)

@app.route('/inspect', methods=['GET', 'POST'])
def inspect():
    if request.method == 'GET':
        return redirect(url_for('index'))
        
    url = request.form.get('url', '').strip()
    try:
        formatos = obtener_formatos_disponibles(url)
        if not formatos:
            return render_template_string(HTML_INDEX, error="No se encontraron formatos para esta URL.")
        session['url'] = url
        return render_template_string(HTML_SELECT, formatos=formatos)
    except Exception as e:
        return render_template_string(HTML_INDEX, error=f"Error al analizar: {str(e)}")

@app.route('/download-async', methods=['POST'])
def download_async():
    url = session.get('url')
    if not url:
        return jsonify({"status": "error"}), 403
        
    format_id = request.form.get('format_id', '').strip()
    modo = "audio" if format_id == "audio" else "video"
    fid = None if modo == "audio" else format_id
    
    global descarga_estado
    descarga_estado = {"mensaje": "Iniciando descarga de streams...", "archivo": None, "completado": False}

    def tarea_en_segundo_plano():
        global descarga_estado
        def actualizar_progreso(msg):
            descarga_estado["mensaje"] = msg

        file_path = descargar_multimedia(url, format_id=fid, modo=modo, progress_hook=actualizar_progreso)
        if file_path and os.path.exists(file_path):
            descarga_estado["archivo"] = file_path
            descarga_estado["mensaje"] = "¡Fusión y procesamiento completados!"
            descarga_estado["completado"] = True
        else:
            descarga_estado["mensaje"] = "Error en el procesamiento."

    threading.Thread(target=tarea_en_segundo_plano).start()
    return jsonify({"status": "started"})

@app.route('/progress', methods=['GET'])
def progress():
    global descarga_estado
    return jsonify(descarga_estado)

@app.route('/download-file', methods=['GET'])
def download_file():
    global descarga_estado
    file_path = descarga_estado.get("archivo")
    
    if file_path and os.path.exists(file_path):
        def generate():
            try:
                with open(file_path, "rb") as f:
                    yield from f
            finally:
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"[-] Error al eliminar el archivo temporal: {e}")

        filename = os.path.basename(file_path)
        return app.response_class(generate(), mimetype="application/octet-stream", headers={"Content-Disposition": f"attachment; filename={filename}"})
        
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
