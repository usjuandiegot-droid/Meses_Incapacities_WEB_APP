from flask import Flask, request, send_file
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


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

    if colombia:

        ruta = os.path.join(
            UPLOAD_FOLDER,
            colombia.filename
        )

        colombia.save(ruta)

        return send_file(
            ruta,
            as_attachment=True,
            download_name=colombia.filename
        )

    if peru:

        ruta = os.path.join(
            UPLOAD_FOLDER,
            peru.filename
        )

        peru.save(ruta)

        return send_file(
            ruta,
            as_attachment=True,
            download_name=peru.filename
        )

        return {
        "error": "No se recibió ningún archivo."
    }, 400


if __name__ == "__main__":
    app.run(debug=True)
