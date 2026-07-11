import os
import shutil

OUTPUT_FOLDER = "outputs"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def procesar_colombia(ruta_entrada):
    nombre = "GLOBANT COLOMBIA Wide.xlsx"
    ruta_salida = os.path.join(OUTPUT_FOLDER, nombre)

    shutil.copy(ruta_entrada, ruta_salida)

    return ruta_salida


def procesar_peru(ruta_entrada):
    nombre = "GLOBANT PERU Wide.xlsx"
    ruta_salida = os.path.join(OUTPUT_FOLDER, nombre)

    shutil.copy(ruta_entrada, ruta_salida)

    return ruta_salida
