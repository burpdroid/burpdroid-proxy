from _thread import start_new_thread
from BurpDroid import HTTPSPROXY
import eel
# from flask import Flask, render_template, Response, send_file
import os
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

INSTALLED_DIR = "/data/data/com.termux/files/usr/var/burpdroid-proxy/templates"
cert_dir = INSTALLED_DIR + "/cert"
eel.init(INSTALLED_DIR)
Proxy = HTTPSPROXY(eel)


@eel.expose
def changeCapture():
    Proxy.setCapture()
    print(Proxy.Capture)


@eel.expose
def getData(event):
    Proxy.HTTPPROXY.setData(event)
    Proxy.setData(event)
    print("New data coming")


@eel.expose
def getCapture():
    return Proxy.Capture


@eel.expose
def getCert():
    return Proxy.CERT_DIR + "/ca/" + Proxy.CA_CERT_NAME


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
    eel.start('index.html', port=5000, mode=None)
    # app.run(host="127.0.0.1", port=5000)
