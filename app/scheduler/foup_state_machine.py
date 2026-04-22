from app.driver.rfid_driver import RfidISO15693
from app.driver.led_driver import LedDriver

class FoupStateMachine:
    def __init__(self):
        self.rfid = RfidISO15693()
        self.led = LedDriver()
        self.state = "IDLE"
        self.current_uid = None
        self.current_data = None
        self.last_error = None

    def reset(self):
        self.state = "IDLE"
        self.current_uid = None
        self.current_data = None
        self.last_error = None

    def scan_read(self):
        self.state = "SCAN"
        uid = self.rfid.read_uid()
        if not uid:
            self.state = "ERROR"
            self.last_error = "NO_TAG"
            self.led.red()
            return False

        self.current_uid = uid
        self.state = "READ"
        self.current_data = self.rfid.read_block(0)
        self.state = "DONE"
        self.led.green()
        return True

    def write_with_verify(self, data_bytes):
        if not self.current_uid:
            self.state = "ERROR"
            self.last_error = "NO_UID"
            return False

        self.state = "WRITE"
        ok = self.rfid.write_block(0, data_bytes[:4])
        if not ok:
            self.state = "ERROR"
            self.led.red()
            return False

        self.state = "VERIFY"
        verify = self.rfid.read_block(0)
        if verify[:8] != data_bytes.hex()[:8]:
            self.state = "ERROR"
            self.last_error = "VERIFY_FAIL"
            self.led.red()
            return False

        self.state = "DONE"
        self.led.green()
        return True