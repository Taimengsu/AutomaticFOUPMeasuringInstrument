# import serial
import time

class RfidISO15693:
    def __init__(self, port="/dev/ttyTHS0", baud=9600):
        # self.ser = serial.Serial(
        #     port=port,
        #     baudrate=baud,
        #     parity=serial.PARITY_NONE,
        #     stopbits=serial.STOPBITS_ONE,
        #     bytesize=serial.EIGHTBITS,
        #     timeout=0.3
        # )
        self.ser=1
        self.retry = 2

    def _send_cmd(self, cmd):
        for _ in range(self.retry):
            self.ser.flushInput()
            self.ser.write(cmd)
            time.sleep(0.05)
            res = self.ser.read(64)
            if len(res) > 4 and res[0] == 0x01:
                return res
            time.sleep(0.03)
        return None

    def read_uid(self):
        cmd = bytes([0x01, 0x02, 0x01, 0x00, 0x04])
        res = self._send_cmd(cmd)
        if res and len(res) >= 10:
            uid = res[4:12].hex().upper()
            return uid if len(uid) == 16 else None
        return None

    def read_block(self, block=0):
        cmd = bytes([0x01, 0x02, 0x03, block, 0x00, 0x06])
        res = self._send_cmd(cmd)
        if res:
            return res[4:-1].hex()
        return None

    def write_block(self, block=0, data=b"\x00\x00\x00\x00"):
        cmd = bytes([0x01, 0x02, 0x04, block]) + data + bytes([0x00])
        res = self._send_cmd(cmd)
        return res is not None