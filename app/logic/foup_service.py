from app.scheduler.foup_state_machine import FoupStateMachine
from app.comm.tcp_mes_client import TcpMesClient
from app.db.history import insert_log
import time

USER_ROLES = {
    "operator": ["read"],
    "engineer": ["read", "write"],
    "admin": ["read", "write", "delete"]
}

class FoupService:
    def __init__(self):
        self.sm = FoupStateMachine()
        self.mes = TcpMesClient("192.168.1.100", 8080)
        self.last_uid = None
        self.last_write_time = 0

    def auth(self, role, action):
        return action in USER_ROLES.get(role, [])

    def read_foup(self, role="operator"):
        if not self.auth(role, "read"):
            return None, "NO_PERMISSION"
        ok = self.sm.scan_read()
        if not ok:
            return None, self.sm.last_error
        insert_log(self.sm.current_uid, "READ", role)
        self.mes.send({"uid": self.sm.current_uid, "action": "READ"})
        return self.sm.current_uid, "OK"

    def write_foup(self, lot_id, role="engineer"):
        if not self.auth(role, "write"):
            return False, "NO_PERMISSION"
        if self.sm.current_uid == self.last_uid and time.time() - self.last_write_time < 5:
            return False, "REPEAT_WRITE"
        data = lot_id.encode().ljust(4, b'\x00')[:4]
        ok = self.sm.write_with_verify(data)
        if ok:
            self.last_uid = self.sm.current_uid
            self.last_write_time = time.time()
            insert_log(self.sm.current_uid, "WRITE", role)
            self.mes.send({"uid": self.sm.current_uid, "action": "WRITE", "lot": lot_id})
        return ok, "OK" if ok else self.sm.last_error