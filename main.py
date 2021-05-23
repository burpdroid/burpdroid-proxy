from _thread import start_new_thread
from BurpDroid import HTTPSPROXY
import socketio
from flask import Flask, render_template, Response, send_file
import os
from gevent.pywsgi import WSGIServer

app = Flask(__name__)
sio = socketio.Server(async_mode='threading')
app.wsgi_app = socketio.WSGIApp(sio, app.wsgi_app)
Proxy = HTTPSPROXY(sio)
INSTALLED_DIR = "/data/data/com.termux/files/usr/var/burpdroid-proxy/"
cert_dir = INSTALLED_DIR + "cert"


@app.route("/style.css")
def read_css():
    with open(INSTALLED_DIR + "templates/bootstrap.min-lux.css", "r") as file:
        return Response(file.read(), mimetype='text/css')


@app.route("/manifest.json")
def read_manifest():
    return Response("""{
  "short_name": "BurpDroid",
  "name": "BurpDroid",
  "icons": [
    {
      "src": "favicon.ico",
      "sizes": "64x64 32x32 24x24 16x16",
      "type": "image/x-icon"
    },
    {
      "src": "logo192.png",
      "type": "image/png",
      "sizes": "192x192"
    },
    {
      "src": "logo512.png",
      "type": "image/png",
      "sizes": "512x512"
    }
  ],
  "start_url": ".",
  "display": "standalone",
  "theme_color": "#000000",
  "background_color": "#000000"
}
""", mimetype='application/json')


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/About')
def About():
    return render_template("About.html")


@app.route('/Intruder')
def Intruder():
    return render_template("Intruder.html")


@app.route('/Repeater')
def Repeater():
    return render_template("Repeater.html")


@app.route('/ca')
def ca():
    return render_template("ca.html")


@app.route('/ca/Ndroid.pem')
def ca_download():
    return send_file(INSTALLED_DIR + "cert/ca/Ndroid.pem")


@sio.on('message')
def handleMessage(namespace, event):
    print('Message: ' + event, namespace)


@sio.on('Capture')
def handleMessage(namespace, event):
    print('Message: ' + str(event), namespace)
    Proxy.setCapture()
    print(Proxy.Capture)


@sio.on('ProxyResponse')
def handleMessage(namespace, event):
    print(event)
    Proxy.HTTPPROXY.setData(event)
    Proxy.setData(event)
    print('Message: ' + event, namespace)


def Start_Proxy():
    Proxy.start_server()


def remove_old_cert():
    files_in_directory = os.listdir(cert_dir)
    filtered_files = [
        file for file in files_in_directory if file.endswith(".key") or file.endswith(".cert")]
    for file in filtered_files:
        path_to_file = os.path.join(cert_dir, file)
        os.remove(path_to_file)


if __name__ == '__main__':
    start_new_thread(Start_Proxy, ())
    app.run(host="127.0.0.1", port=5000, threaded=True)
