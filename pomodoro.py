import json
import time
from pathlib import Path

RUTA_CONFIG = Path(__file__).parent / "config.json"

CONFIG_POR_DEFECTO = {
    "trabajo_min": 25,
    "descanso_min": 5,
    "ciclos": 4,
}


def guardar_config(config):
    with open(RUTA_CONFIG, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)


def cargar_config():
    if not RUTA_CONFIG.exists():
        guardar_config(CONFIG_POR_DEFECTO)
        return CONFIG_POR_DEFECTO.copy()
    with open(RUTA_CONFIG, "r", encoding="utf-8") as f:
        return json.load(f)


def temporizador(minutos, etiqueta):
    segundos_totales = int(minutos * 60)
    for restantes in range(segundos_totales, 0, -1):
        mins, segs = divmod(restantes, 60)
        print(f"\r{etiqueta}: {mins:02d}:{segs:02d}", end="")
        time.sleep(1)
    print(f"\r{etiqueta}: 00:00  ¡Tiempo!")


def main():
    config = cargar_config()
    try:
        for ciclo in range(1, config["ciclos"] + 1):
            print(f"--- Ciclo {ciclo} de {config['ciclos']} ---")
            temporizador(config["trabajo_min"], "Trabajo")
            temporizador(config["descanso_min"], "Descanso")
        print("¡Sesión completada!")
    except KeyboardInterrupt:
        print("\nTemporizador detenido.")


if __name__ == "__main__":
    main()