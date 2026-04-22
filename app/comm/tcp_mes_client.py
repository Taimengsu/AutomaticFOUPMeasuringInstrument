import socket
import threading
import time
import json

class TcpMesClient:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.sock = None
        self.connected = False
        self.buffer = []
        threading.Thread(target=self._heartbeat, daemon=True).start()

    def connect(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(2)
            self.sock.connect((self.ip, self.port))
            self.connected = True
        except:
            self.connected = False

    def _heartbeat(self):
        while True:
            if self.connected:
                try:
                    self.sock.send(b'#HB#')
                except:
                    self.connected = False
            else:
                self.connect()
            time.sleep(3)

    def send(self, data):
        if not self.connected:
            self.buffer.append(data)
            return False
        try:
            self.sock.send(json.dumps(data).encode())
            while self.buffer:
                self.sock.send(json.dumps(self.buffer.pop(0)).encode())
            return True
        except:
            self.connected = False
            self.buffer.append(data)
            return False