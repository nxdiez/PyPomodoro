import time

import psutil
import win32gui
import win32process


def obtener_app_activa():
    """Devuelve (nombre_del_proceso, titulo_de_la_ventana) de la ventana en primer plano."""
    hwnd = win32gui.GetForegroundWindow()
    if not hwnd:
        return None, None

    titulo = win32gui.GetWindowText(hwnd)
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    try:
        nombre = psutil.Process(pid).name()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        nombre = None
    return nombre, titulo


def main():
    anterior = None
    try:
        while True:
            actual = obtener_app_activa()
            if actual != anterior:
                nombre, titulo = actual
                print(f"{nombre} | {titulo}")
                anterior = actual
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nDetenido.")


if __name__ == "__main__":
    main()