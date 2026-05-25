from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "<h1>Projekt Leo zije!</h1><p>Tu bude bezat web scraper.</p>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)