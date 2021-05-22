import socket
import ssl
from _thread import start_new_thread
from certauth.certauth import CertificateAuthority
from OpenSSL import crypto
from OpenSSL.SSL import FILETYPE_PEM
# from HttpProxy import HTTPPROXY
from os import lseek, path, makedirs, getcwd
from cprint import *
from json import loads
from sys import exit
import time


class HTTPPROXY:
    def __init__(self, websocket):
        self.buffer_size = 4096
        self.websocket = websocket
        self.ModifedResponse = ""
        self.Capture = False

    def handle_request(self, client, firstrequest, host):
        head = self.parse_head(firstrequest)
        headers = head["headers"]
        request = "{}\r\n".format(head["meta"])
        for key, value in headers.items():
            request += "{}: {}\r\n".format(key, value)
        request += "\r\n"
        if "content-length" in headers:
            while len(head["chunk"]) < int(headers["content-length"]):
                head["chunk"] += client.recv(self.buffer_size)

        request = request.encode() + head["chunk"]
        port = 80
        response = self.send_to_server(host, port, request)
        if response == "drop":
            client.close()
            return False
        client.sendall(response)
        client.close()

    def ReciveModifedRequestHTTP(self, data):
        self.websocket.emit("MyResponse", data)
        while True:
            if self.ModifedResponse != "" and self.ModifedResponse != "drop":
                return self.ModifedResponse.encode()
            elif self.ModifedResponse == "drop":
                return "drop"

    def setData(self, data):
        self.ModifedResponse = data

    def resetReponse(self):
        self.ModifedResponse = ""

    def send_to_server(self, host, port, data):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.connect((socket.gethostbyname(host), port))
        if self.Capture:
            formated_request = ""
            str_req = str(data).split("\\r\\n")
            for i in str_req:
                cprint.ok(i)
                formated_request = formated_request + i + "\n"
            new_request = self.ReciveModifedRequestHTTP(formated_request)
            if new_request == "drop":
                return "drop"
            server.sendall(new_request)
            self.resetReponse()
        else:
            server.sendall(data)
        head = self.parse_head(server.recv(4096))
        headers = head["headers"]
        response = "{}\r\n".format(head["meta"])
        for key, value in headers.items():
            response += "{}: {}\r\n".format(key, value)
        response += "\r\n"

        if "content-length" in headers:
            while len(head["chunk"]) < int(headers["content-length"]):
                head["chunk"] += server.recv(self.buffer_size)

        response = response.encode() + head["chunk"]
        server.close()
        return response

    def parse_head(self, head_request):
        nodes = head_request.split(b"\r\n\r\n")
        heads = nodes[0].split(b"\r\n")
        meta = heads.pop(0).decode("utf-8")
        data = {
            "meta": meta,
            "headers": {},
            "chunk": b""
        }

        if len(nodes) >= 2:
            data["chunk"] = nodes[1]

        for head in heads:
            pieces = head.split(b": ")
            key = pieces.pop(0).decode("utf-8")
            if key.startswith("Connection: "):
                data["headers"][key.lower()] = "close"
            else:
                data["headers"][key.lower()] = b": ".join(
                    pieces).decode("utf-8")
        return data


class HTTPSPROXY:
    def __init__(self, websocket):
        self.CERT_DIR = getcwd() + "\\cert\\"
        self.CA_CERT_NAME = "Ndroid.pem"
        self.config = ""
        self.isDev = True
        self.websocket = websocket
        self.ModifedResponse = ""
        self.HTTPPROXY = HTTPPROXY(websocket)
        self.Capture = False

    def set_config(self, config_path="config.json"):
        self.config = loads(config_path)

    def check_ca_auth(self):
        ca_file = self.CERT_DIR + "ca\\"
        if path.isdir(ca_file):
            pass
        else:
            makedirs(ca_file)
        cprint.info("Your can find your ca cert here: " +
                    ca_file + self.CA_CERT_NAME)
        return CertificateAuthority(
            'Nsecurity', ca_file + self.CA_CERT_NAME)

    def check_cert(self, ca, host):
        certpath = self.CERT_DIR + host + ".cert"
        keypath = self.CERT_DIR + host + ".key"
        if path.isfile(certpath) and path.isfile(keypath):
            return certpath, keypath
        else:
            cert, key = ca.load_cert(host, wildcard=True)
            with open(certpath, "w") as file:
                file.write(crypto.dump_certificate(
                    crypto.FILETYPE_PEM, cert).decode("utf-8"))
            with open(keypath, "w") as file:
                file.write(crypto.dump_privatekey(
                    crypto.FILETYPE_PEM, key).decode("utf-8"))
            return certpath, keypath

    def recv_timeout(self, the_socket, timeout=1):
        the_socket.setblocking(0)
        data = b''
        begin = time.time()
        while True:
            if data and time.time()-begin > timeout:
                break
            elif time.time()-begin > timeout*2:
                break
            try:
                datax = the_socket.recv(8192)
                if datax:
                    data += datax
                    begin = time.time()
                else:
                    time.sleep(0.1)
            except:
                pass
        return data

    def setData(self, data):
        self.ModifedResponse = data

    def setCapture(self):
        if self.Capture:
            self.HTTPPROXY.Capture = False
            self.Capture = False
        else:
            self.HTTPPROXY.Capture = True
            self.Capture = True

    def resetReponse(self):
        self.ModifedResponse = ""

    def ReciveModifedRequest(self, formated_request):
        self.websocket.emit("MyResponse", formated_request)
        while True:
            if self.ModifedResponse != "" and self.ModifedResponse != "drop":
                return self.ModifedResponse.encode()
            elif self.ModifedResponse == "drop":
                return "drop"

    def request_handler(self, conn, tunn, request):
        while True:
            data = self.recv_timeout(conn)
            if data:
                try:
                    if request and self.Capture:
                        formated_request = ""
                        str_req = str(data).split("\\r\\n")
                        for i in str_req:
                            # cprint.ok(i)
                            formated_request = formated_request + i + "\n"
                        moddeddata = self.ReciveModifedRequest(
                            formated_request)
                        if moddeddata == "drop":
                            conn.close()
                            return False
                        tunn.sendall(moddeddata)
                        self.resetReponse()
                        break
                    else:
                        tunn.sendall(data)
                        break
                except Exception as e:
                    cprint.fatal(e)
            else:
                break

    def request_to_host(self, request):
        host, port = "", 443
        str_req = str(request).split("\\r\\n")
        for i in str_req:
            if "Host:" in i:
                host = i.split(" ")[1]
        host_info = host.split(":")
        if len(host_info) == 2 and host_info[1] == 443:
            port = int(443)
        elif len(host_info) == 1 and host_info[0] != "":
            port = int(80)
        host = host_info[0]
        return host, port

    def create_encrypted_socket(self, host, port):
        tunn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        wrappedSocket = ssl.create_default_context().wrap_socket(tunn, server_hostname=host)
        wrappedSocket.connect((host, port))
        return wrappedSocket

    def encrypt_socket(self, socket, ca, host):
        certfile, keyfile = self.check_cert(ca, host)
        try:
            conn_s = ssl.wrap_socket(
                socket, keyfile=keyfile, certfile=certfile, server_side=True)
            conn_s.do_handshake()
            return conn_s
        except:
            return None

    def handle(self, conn, ca):
        conn_s = ""
        request = conn.recv(40960)
        host, port = self.request_to_host(request)
        if host == "":
            return 0
        if port == 443:
            conn.sendall(b'HTTP/1.1 200 Connection Established\r\n\r\n')
            wrappedSocket = self.create_encrypted_socket(host, port)
            conn_s = self.encrypt_socket(conn, ca, host)
            if conn_s == None:
                return False
            self.request_handler(conn_s, wrappedSocket, True)
            self.request_handler(wrappedSocket, conn_s, False)
        else:
            self.HTTPPROXY.handle_request(conn, request, host)

    def start_server(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('127.0.0.1', 8080))
        sock.listen(1)
        ca = self.check_ca_auth()
        while True:
            conn, addr = sock.accept()
            conn.settimeout(2)
            cprint.info("connected ===> " + str(addr))
            try:
                self.handle(conn, ca)
            except Exception as e:
                conn.close()
                print(e)


if __name__ == "__main__":
    print("You can't run this module dirctly")
