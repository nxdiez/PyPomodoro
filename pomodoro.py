import json
import time
from collections import defaultdict
from pathlib import Path

from ventana_activa import obtener_app_activa

RUTA_CONFIG = Path(__file__).parent / "config.json"

CONFIG_POR_DEFECTO = {
    "trabajo_min": 25,
    "descanso_min": 5,
    "ciclos": 4,
    "umbral_seg": 5,
    "apps_trabajo": ["Code.exe", "chrome.exe"],
    "apps_descanso": ["Spotify.exe", "vlc.exe"],
    "apps_ignoradas": ["explorer.exe"],
}

# categoría -> clave de config.json donde está su lista
CATEGORIAS = {
    "trabajo": "apps_trabajo",
    "descanso": "apps_descanso",
    "ignorada": "apps_ignoradas",
}


def guardar_config(config):
    with open(RUTA_CONFIG, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)


def cargar_config():
    if not RUTA_CONFIG.exists():
        guardar_config(CONFIG_POR_DEFECTO)
    with open(RUTA_CONFIG, "r", encoding="utf-8") as f:
        return {**CONFIG_POR_DEFECTO, **json.load(f)}


def categoria_de(config, clave):
    """Devuelve la categoría de la app (clave en minúsculas), o None si no está en ninguna lista."""
    for categoria, clave_config in CATEGORIAS.items():
        if clave in [a.lower() for a in config[clave_config]]:
            return categoria
    return None


def mostrar_resumen(por_app, apps):
    print("\n--- Tiempo efectivo por aplicación ---")
    ordenado = sorted(por_app.items(), key=lambda par: par[1], reverse=True)
    for clave, segundos in ordenado:
        info = apps[clave]
        categoria = info["categoria"] or "sin clasificar"
        print(f"{info['nombre']} [{categoria}]: {segundos / 60:.1f} min")


def clasificar_pendientes(config, pendientes):
    if not pendientes:
        return
    opciones = {"t": "apps_trabajo", "d": "apps_descanso", "i": "apps_ignoradas"}
    print("\n--- Aplicaciones sin clasificar ---")
    for nombre in pendientes.values():
        while True:
            respuesta = input(
                f"¿Dónde va {nombre}? [t]rabajo / [d]escanso / [i]gnorar / Enter = saltar: "
            ).strip().lower()
            if respuesta == "":
                break
            if respuesta in opciones:
                config[opciones[respuesta]].append(nombre)
                break
            print("Opción no válida.")
    guardar_config(config)


def main():
    config = cargar_config()
    ciclos = config["ciclos"]
    umbral = config["umbral_seg"]

    fase = "trabajo"
    ciclo = 1
    acumulado = 0.0                  # segundos efectivos de la fase actual
    por_app = defaultdict(float)     # segundos registrados por app
    apps = {}                        # clave -> {"nombre": ..., "categoria": ...}
    pendientes = {}                  # clave -> nombre de apps sin clasificar

    actual = None                    # clave de la app en primer plano
    categoria = None
    inicio_tramo = ultimo_credito = time.monotonic()
    superado = False                 # ¿el tramo actual ya superó el umbral?

    try:
        while True:
            time.sleep(1)
            ahora = time.monotonic()

            nombre_app, _ = obtener_app_activa()
            clave = nombre_app.lower() if nombre_app else None

            if clave != actual:      # empieza un tramo nuevo
                actual = clave
                categoria = categoria_de(config, clave) if clave else None
                inicio_tramo = ahora
                superado = False
                if clave and clave not in apps:
                    apps[clave] = {"nombre": nombre_app, "categoria": categoria}

            segundos = 0.0
            if actual and not superado and ahora - inicio_tramo >= umbral:
                superado = True
                ultimo_credito = inicio_tramo    # se acredita el tramo entero
            if actual and superado:
                segundos = ahora - ultimo_credito
                ultimo_credito = ahora

            if segundos:
                por_app[actual] += segundos
                if categoria is None and actual not in pendientes:
                    pendientes[actual] = nombre_app
                    print(f"\nApp sin clasificar: {nombre_app} (te preguntaré al cerrar)")
                if categoria == fase:
                    acumulado += segundos

            limite = int(config[f"{fase}_min"] * 60)
            restante = limite - acumulado

            if restante <= 0:
                if fase == "trabajo":
                    print("\n¡Bloque de trabajo completado! Toca descansar.")
                    fase = "descanso"
                else:
                    print("\nDescanso completado.")
                    if ciclo >= ciclos:
                        break
                    ciclo += 1
                    fase = "trabajo"
                acumulado = 0.0
                continue

            mins, segs = divmod(int(restante), 60)
            estado = "contando" if superado and categoria == fase else "en pausa"
            print(
                f"\r[{fase} {ciclo}/{ciclos}] {mins:02d}:{segs:02d} "
                f"({estado}) {nombre_app}      ",
                end="",
            )
        print("¡Sesión completada!")
    except KeyboardInterrupt:
        print("\nDetenido.")
    finally:
        mostrar_resumen(por_app, apps)
        clasificar_pendientes(config, pendientes)


if __name__ == "__main__":
    main()