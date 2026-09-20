import os
import subprocess

def convertir_o_comprimir_video(input_path, formato_salida="mp4", preset_calidad="normal"):
    """
    Convierte y comprime un archivo de video local seleccionando 
    los códecs adecuados según el formato de salida (MP4/MKV o WebM).
    """
    if not os.path.exists(input_path):
        print("[-] Error: El archivo de entrada no existe.")
        return None
    
    output_dir = os.path.abspath("downloads")
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    output_path = os.path.join(output_dir, f"{base_name}_procesado.{formato_salida}")

    cmd = ["ffmpeg", "-y", "-i", input_path]

    # Configuración de códecs según el formato de salida elegido
    if formato_salida == "webm":
        # WebM requiere libvpx / libvorbis o libopus
        cmd.extend(["-c:v", "libvpx-vp9", "-pix_fmt", "yuv420p"])
        if preset_calidad == "comprimir":
            cmd.extend(["-crf", "32", "-b:v", "0"])
        elif preset_calidad == "alta":
            cmd.extend(["-crf", "15", "-b:v", "0"])
        else:
            cmd.extend(["-crf", "24", "-b:v", "0"])
        cmd.extend(["-c:a", "libopus"])
    else:
        # MP4 y MKV usan H.264 / AAC
        cmd.extend(["-c:v", "libx264", "-pix_fmt", "yuv420p"])
        if preset_calidad == "comprimir":
            cmd.extend(["-crf", "28", "-preset", "fast"])
        elif preset_calidad == "alta":
            cmd.extend(["-crf", "18", "-preset", "medium"])
        else:
            cmd.extend(["-crf", "23", "-preset", "medium"])
        cmd.extend(["-c:a", "aac", "-b:a", "192k"])

    cmd.append(output_path)

    print(f"[+] Ejecutando FFmpeg: {' '.join(cmd)}")

    try:
        resultado = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("[+] Conversión a WebM/MP4 finalizada correctamente.")
        return output_path
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.decode('utf-8', errors='ignore')
        print(f"[-] Error crítico de FFmpeg:\n{error_msg}")
        return None
    except Exception as ex:
        print(f"[-] Error inesperado en Python: {str(ex)}")
        return None
