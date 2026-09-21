import os
import subprocess
import traceback

def convertir_o_comprimir_video(input_path, formato_salida="mp4", preset_calidad="normal"):
    """
    Convierte y comprime un archivo de video local utilizando FFmpeg con mapeo completo de streams.
    """
    if not os.path.exists(input_path):
        print(f"[-] Error crítico: El archivo de entrada no existe en {input_path}")
        return None
    
    input_path = os.path.abspath(input_path)
    output_dir = os.path.abspath("downloads")
    os.makedirs(output_dir, exist_ok=True)

    base_name = os.path.splitext(os.path.basename(input_path))[0]
    output_path = os.path.join(output_dir, f"{base_name}_procesado.{formato_salida}")

    # Comando base asegurando mapeo completo de todos los streams de entrada (-map 0)
    cmd = ["ffmpeg", "-y", "-i", input_path, "-map", "0"]

    if formato_salida == "webm":
        cmd.extend(["-c:v", "libvpx-vp9", "-pix_fmt", "yuv420p", "-row-mt", "1", "-threads", "0"])
        if preset_calidad == "comprimir":
            cmd.extend(["-crf", "32", "-b:v", "0"])
        elif preset_calidad == "alta":
            cmd.extend(["-crf", "15", "-b:v", "0"])
        else:
            cmd.extend(["-crf", "24", "-b:v", "0"])
        cmd.extend(["-c:a", "libopus"])
    elif formato_salida == "mkv":
        cmd.extend(["-c:v", "libx264", "-pix_fmt", "yuv420p", "-threads", "0"])
        if preset_calidad == "comprimir":
            cmd.extend(["-crf", "28", "-preset", "fast"])
        elif preset_calidad == "alta":
            cmd.extend(["-crf", "18", "-preset", "medium"])
        else:
            cmd.extend(["-crf", "23", "-preset", "medium"])
        cmd.extend(["-c:a", "aac", "-b:a", "192k"])
    else: # mp4
        cmd.extend(["-c:v", "libx264", "-pix_fmt", "yuv420p", "-threads", "0"])
        if preset_calidad == "comprimir":
            cmd.extend(["-crf", "28", "-preset", "fast"])
        elif preset_calidad == "alta":
            cmd.extend(["-crf", "18", "-preset", "medium"])
        else:
            cmd.extend(["-crf", "23", "-preset", "medium"])
        cmd.extend(["-c:a", "aac", "-b:a", "192k"])

    cmd.append(output_path)

    print(f"[+] Ejecutando FFmpeg robusto: {' '.join(cmd)}")

    try:
        proceso = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        print("[+] Conversión finalizada con éxito.")
        return output_path
    except subprocess.CalledProcessError as e:
        print(f"[-] Error devuelto por FFmpeg:\n{e.stderr}")
        return None
    except Exception as ex:
        print(f"[-] Excepción inesperada:\n{str(ex)}")
        traceback.print_exc()
        return None
