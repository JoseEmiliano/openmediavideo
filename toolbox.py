import os
import subprocess

def convertir_o_comprimir_video(input_path, formato_salida="mp4", preset_calidad="normal"):
    """
    Convierte y comprime un archivo de video local utilizando FFmpeg.
    preset_calidad: 'comprimir' (reduce tamaño), 'alta' (mantiene calidad), 'normal' (balanceado).
    """
    if not os.path.exists(input_path):
        return None
    
    output_dir = os.path.abspath("downloads")
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    output_path = os.path.join(output_dir, f"{base_name}_procesado.{formato_salida}")

    # Definir parámetros de compresión/calidad con FFmpeg
    cmd = ["ffmpeg", "-y", "-i", input_path]

    if preset_calidad == "comprimir":
        # Reducir tasa de bits de video y audio para comprimir tamaño significativamente
        cmd.extend(["-c:v", "libx264", "-crf", "28", "-preset", "fast", "-c:a", "aac", "-b:a", "128k"])
    elif preset_calidad == "alta":
        # Mantener alta calidad de codificación
        cmd.extend(["-c:v", "libx264", "-crf", "18", "-preset", "medium", "-c:a", "aac", "-b:a", "192k"])
    else:
        # Configuración estándar / normal
        cmd.extend(["-c:v", "libx264", "-crf", "23", "-preset", "medium", "-c:a", "aac", "-b:a", "192k"])

    cmd.append(output_path)

    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return output_path
    except subprocess.CalledProcessError as e:
        print(f"Error en FFmpeg (Conversión): {e.stderr.decode()}")
        return None
