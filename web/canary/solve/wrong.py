from flask import Flask, redirect

app = Flask(__name__)

@app.route("/")
def hello_world():
    return redirect("http://localhost:8080/canary/f821872d-f764-45c3-8710-76c0c0d7ee13", code=302)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
