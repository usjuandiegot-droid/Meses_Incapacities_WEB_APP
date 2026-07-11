from flask import Flask, request

app = Flask(__name__)

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

    return {
        "status": "ok",
        "archivo_colombia": colombia.filename if colombia else None,
        "archivo_peru": peru.filename if peru else None
    }

if __name__ == "__main__":
    app.run(debug=True)
