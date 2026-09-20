import os
import sys
import re
try:
    import yt_dlp
except ImportError:
    print("Error: yt-dlp no está instalado.")
    sys.exit(1)

URL_REGEX = re.compile(
    r'^(https?://)?(www\.)?'
    r'(youtube\.com|youtu\.be|vimeo\.com|twitch\.tv|dailymotion\.com|tiktok\.com)'
    r'/.+$', re.IGNORECASE
)

def validar_url(url):
    if not url or len(url) > 500:
        return False
    if not URL_REGEX.match(url):
        if re.search(r'[;&|`$<>\\:]', url):
            return False
        if not url.startswith(('http://', 'https://')):
            return False
    return True

def obtener_formatos_disponibles(url):
    if not validar_url(url):
        raise ValueError("URL inválida.")
    
    ydl_opts = {'quiet': True, 'no_warnings': True, 'socket_timeout': 10}
    formatos = []
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            for f in info.get('formats', []):
                if f.get('vcodec') != 'none' and f.get('height'):
                    res = f"{f.get('height')}p"
                    ext = f.get('ext')
                    format_id = f.get('format_id')
                    item = {'id': format_id, 'res': res, 'ext': ext}
                    if item not in formatos:
                        formatos.append(item)
            formatos = sorted(formatos, key=lambda x: int(x['res'].replace('p','')), reverse=True)
    except Exception as e:
        print(f"Error: {e}")
    return formatos

def descargar_multimedia(url, format_id=None, modo="video", progress_hook=None):
    if not validar_url(url):
        raise ValueError("URL inválida o bloqueada por seguridad.")

    output_dir = os.path.abspath("downloads")
    os.makedirs(output_dir, exist_ok=True)

    def my_hook(d):
        if d['status'] == 'downloading':
            p = d.get('_percent_str', '0.0%').strip()
            speed = d.get('_speed_str', 'N/A').strip()
            eta_raw = d.get('eta')
            eta_str = f"{eta_raw}s" if eta_raw is not None else d.get('_eta_str', 'Calculando...').strip()
            msg = f"Descargando: {p} | Vel: {speed} | Restante: {eta_str}"
            if progress_hook:
                progress_hook(msg)
        elif d['status'] == 'finished':
            msg = "⚡ Descarga finalizada. Fusionando video y audio con FFmpeg..."
            if progress_hook:
                progress_hook(msg)

    ydl_opts = {
        'outtmpl': os.path.join(output_dir, '%(title)s [%(resolution)s] [%(id)s].%(ext)s'),
        'restrictfilenames': True,
        'socket_timeout': 15,
        'noplaylist': True,
        'progress_hooks': [my_hook],
    }

    if modo == "audio":
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        })
    elif format_id and re.match(r'^[a-zA-Z0-9_-]+$', format_id):
        ydl_opts.update({
            'format': f'{format_id}+bestaudio/best',
            'merge_output_format': 'mp4',
        })
    else:
        ydl_opts.update({
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
        })

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info_dict)
            if modo == "audio":
                base, _ = os.path.splitext(filename)
                filename = base + ".mp3"
                
        if not os.path.abspath(filename).startswith(output_dir):
            raise Exception("Intento de Path Traversal bloqueado.")
            
        return filename
    except Exception as e:
        print(f"Error: {e}")
        return None
