from flask import Flask
from threading import Thread

app = Flask(' ')


@app.route('/')
def home():
    return "我是人气最旺探员-老K!!!!"


def run():
    app.run(host='0.0.0.0', port=8000)


def keep_alive():
    t = Thread(target=run)
    t.start()
