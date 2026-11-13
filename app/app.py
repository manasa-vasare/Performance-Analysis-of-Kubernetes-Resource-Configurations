
from flask import Flask, jsonify
import time

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({
        "message": "Kubernetes Performance Analysis",
        "status": "Running"
    })

@app.route("/work")
def work():
    start = time.time()

    result = 0
    for i in range(1, 1000000):
        result += i * i

    elapsed = time.time() - start

    return jsonify({
        "result": result,
        "processing_time": round(elapsed, 4)
    })

@app.route("/health")
def health():
    return jsonify({"status": "healthy"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
