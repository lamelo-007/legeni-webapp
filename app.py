import os
import socket

from flask import Flask, jsonify

APP_VERSION = os.environ.get("APP_VERSION", "dev")
APP_ENV = os.environ.get("APP_ENV", "dev")
APP_COLOR = os.environ.get("APP_COLOR", "#1f6feb")

app = Flask(__name__)

PAGE = """<!doctype html>
<html><head><title>Legeni WebApp</title></head>
<body style="font-family:sans-serif;margin:0">
<div style="background:{color};color:white;padding:24px">
<h1>Legeni WebApp</h1><p>Environnement : {env}</p></div>
<p style="padding:24px">Version {version}</p>
</body></html>"""


@app.route("/")
def index():
    return PAGE.format(color=APP_COLOR, env=APP_ENV, version=APP_VERSION)


@app.route("/health")
def health():
    return jsonify(status="ko")


@app.route("/ready")
def ready():
    return jsonify(status="ready")


@app.route("/api/info")
def info():
    return jsonify(env=APP_ENV, version=APP_VERSION,
                   hostname=socket.gethostname(), color=APP_COLOR)
