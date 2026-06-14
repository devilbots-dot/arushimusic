from flask import Flask
import threading
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "Devils Arushi Music Bot Running"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

def start_keep_alive():
    threading.Thread(target=run, daemon=True).start()
