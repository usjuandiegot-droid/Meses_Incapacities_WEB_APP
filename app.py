from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return {
        "status": "ok",
        "mensaje": "API Globant Incapacidades Wide funcionando"
    }

if __name__ == "__main__":
    app.run(debug=True)
