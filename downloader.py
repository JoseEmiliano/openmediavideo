import os
import yt_dlp

def obtener_formatos_disponibles(url):
    """
    Inspecciona la URL y devuelve una lista de resoluciones y formatos disponibles.
    """
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
    }
    formatos = []
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])
            
            seen_res = set()
            for f in formats:
                if f.get('vcodec') != 'none' and f.get('height'):
                    res = f"{f.get('height')}p"
                    ext = f.get('ext', 'mp4')
                    format_id = f.get('format_id')
                    
                    key = (res, ext)
                    if key not in seen_res:
                        seen_res.add(key)
                        formatos.append({
                            'id': format_id,
                            'res': res,
                            'ext': ext
                        })
            formatos.sort(key=lambda x: int(x['res'].replace('p', '')), reverse=True)
    except Exception as e:
        print(f"[-] Error al inspeccionar formatos: {str(e)}")
    
    return formatos

def descargar_multimedia(url, format_id=None, modo="video", progress_hook=None):
    """
    Descarga multimedia con múltiples alternativas de respaldo para evitar fallos de formato.
    """
    output_dir = os.path.abspath("downloads")
    os.makedirs(output_dir, exist_ok=True)
    
    output_template = os.path.join(output_dir, "media_download_%(id)s.%(ext)s")
    
    def my_hook(d):
        if progress_hook:
            if d['status'] == 'downloading':
                p = d.get('_percent_str', '0%').strip()
                progress_hook(f"Descargando... {p}")
            elif d['status'] == 'finished':
                progress_hook("Finalizando archivo...")

    # Lista de esquemas de formato a probar (del más óptimo al más universal)
    if modo == "audio":
        formatos_a_probar = ['bestaudio/best']
    else:
        if format_id:
            formatos_a_probar = [
                f"{format_id}+bestaudio/best",
                f"{format_id}",
                'best'
            ]
        else:
            formatos_a_probar = [
                'bestvideo+bestaudio/best',
                'best[ext=mp4]/best',
                'best'
            ]

    filename = None
    for fmt in formatos_a_probar:
        ydl_opts = {
            'outtmpl': output_template,
            'progress_hooks': [my_hook],
            'noplaylist': True,
            'format': fmt,
            'merge_output_format': 'mp4' if modo != "audio" else None,
        }
        
        if modo == "audio":
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]

        try:
            print(f"[+] Intentando descarga con formato: {fmt}")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                
                if modo == "audio":
                    base, _ = os.path.splitext(filename)
                    filename = base + ".mp3"
                else:
                    base, _ = os.path.splitext(filename)
                    if os.path.exists(base + ".mp4"):
                        filename = base + ".mp4"
                
                if filename and os.path.exists(filename) and os.path.getsize(filename) > 50000:
                    print(f"[+] Descarga exitosa con formato: {fmt}")
                    return filename
        except Exception as e:
            print(f"[-] Falló el intento con formato {fmt}: {str(e)}")
            continue

    # Último recurso: buscar cualquier archivo válido reciente en la carpeta
    try:
        files = [os.path.join(output_dir, f) for f in os.listdir(output_dir) if not f.endswith('.part') and not f.endswith('.ytdl') and not f.endswith('.temp')]
        if files:
            valid = [f for f in files if os.path.getsize(f) > 50000]
            if valid:
                return max(valid, key=os.path.getctime)
    except:
        pass

    return None
