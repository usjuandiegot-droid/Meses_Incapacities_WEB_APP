import os
import shutil

OUTPUT_FOLDER = "outputs"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def procesar_colombia(ruta_entrada):

    nombre = "GLOBANT COLOMBIA Wide.xlsx"
    ruta_salida = os.path.join(OUTPUT_FOLDER, nombre)

    shutil.copy(ruta_entrada, ruta_salida)

    print("========== COLOMBIA ==========")
    print("Entrada:", ruta_entrada)
    print("Salida:", ruta_salida)
    print("Existe:", os.path.exists(ruta_salida))
    print("Tamaño:", os.path.getsize(ruta_salida))

    return ruta_salida


def procesar_peru(ruta_entrada):

    nombre = "GLOBANT PERU Wide.xlsx"
    ruta_salida = os.path.join(OUTPUT_FOLDER, nombre)

    shutil.copy(ruta_entrada, ruta_salida)

    print("========== PERÚ ==========")
    print("Entrada:", ruta_entrada)
    print("Salida:", ruta_salida)
    print("Existe:", os.path.exists(ruta_salida))
    print("Tamaño:", os.path.getsize(ruta_salida))

    return ruta_salida
