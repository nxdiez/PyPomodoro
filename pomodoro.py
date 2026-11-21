import json
import time
from pathlib import Path

from ventana_activa import obtener_app_activa

RUTA_CONFIG = Path(__file__).parent / "config.json"

CONFIG_POR_DEFECTO = {
    "por_defecto": {"trabajo_min": 25, "descanso_min": 5, "ciclos": 4},
    "perfiles": {
        "Code.exe": {"trabajo_min": 50, "descanso_min": 10},
        "chrome.exe": {"trabajo_min": 15},
    },
}


def guardar_config(config):
    with open(RUTA_CONFIG, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)


def cargar_config():
    if not RUTA_CONFIG.exists():
        guardar_config(CONFIG_POR_DEFECTO)
    with open(RUTA_CONFIG, "r", encoding="utf-8") as f:
        return json.load(f)


def ajustes_para(config, nombre_app):
    """Devuelve los ajustes por defecto, sobrescritos por el perfil de la app si existe."""
    ajustes = dict(config["por_defecto"])
    if nombre_app:
        perfiles = {k.lower(): v for k, v in config["perfiles"].items()}
        ajustes.update(perfiles.get(nombre_app.lower(), {}))
    return ajustes


def temporizador(minutos, etiqueta):
    segundos_totales = int(minutos * 60)
    for restantes in range(segundos_totales, 0, -1):
        mins, segs = divmod(restantes, 60)
        print(f"\r{etiqueta}: {mins:02d}:{segs:02d}", end="")
        time.sleep(1)
    print(f"\r{etiqueta}: 00:00  ¡Tiempo!")


def main():
    config = cargar_config()
    ciclos = config["por_defecto"]["ciclos"]
    try:
        for ciclo in range(1, ciclos + 1):
            nombre_app, _ = obtener_app_activa()
            ajustes = ajustes_para(config, nombre_app)
            print(f"--- Ciclo {ciclo} de {ciclos} | App: {nombre_app} ---")
            temporizador(ajustes["trabajo_min"], "Trabajo")
            temporizador(ajustes["descanso_min"], "Descanso")
        print("¡Sesión completada!")
     
    except KeyboardInterrupt:
        print("\nTemporizador detenido.")
        
        

if __name__ == "__main__":
    main()