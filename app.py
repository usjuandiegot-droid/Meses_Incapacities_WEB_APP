from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import os
import zipfile

from procesador import procesar_colombia, procesar_peru

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


@app.route("/")
def home():
    return {
        "status": "ok",
        "mensaje": "API Globant Incapacidades Wide funcionando"
    }


@app.route("/procesar", methods=["POST"])
def procesar():

    colombia = request.files.get("colombia")
    peru = request.files.get("peru")

    archivos_generados = []

    # ---------------- COLOMBIA ----------------

    if colombia:

        ruta_colombia = os.path.join(
            UPLOAD_FOLDER,
            colombia.filename
        )

        colombia.save(ruta_colombia)

        salida = procesar_colombia(ruta_colombia)

        archivos_generados.append(salida)

    # ---------------- PERÚ ----------------

    if peru:

        ruta_peru = os.path.join(
            UPLOAD_FOLDER,
            peru.filename
        )

        peru.save(ruta_peru)

        salida = procesar_peru(ruta_peru)

        archivos_generados.append(salida)

    if len(archivos_generados) == 0:

        return jsonify({
            "error": "No se recibió ningún archivo."
        }), 400

    # Si solo hay uno

    if len(archivos_generados) == 1:

        return send_file(
            archivos_generados[0],
            as_attachment=True
        )

    # Si hay dos -> ZIP

    ruta_zip = os.path.join(
        OUTPUT_FOLDER,
        "Resultado.zip"
    )

    with zipfile.ZipFile(
        ruta_zip,
        "w",
        zipfile.ZIP_DEFLATED
    ) as zipf:

        for archivo in archivos_generados:

            zipf.write(
                archivo,
                arcname=os.path.basename(archivo)
            )

    return send_file(
        ruta_zip,
        as_attachment=True
    )


if __name__ == "__main__":
    app.run(debug=True)
