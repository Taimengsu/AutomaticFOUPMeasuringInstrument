from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
import time

# ==========================================
# 线程1：GEM状态机线程（SEMI E30）
# ==========================================
class GEMStateThread(QThread):
    stateChanged = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.state = "IDLE"
        self.running = True

    def run(self):
        while self.running:
            time.sleep(0.5)

    def change(self, s):
        self.state = s
        self.stateChanged.emit(s)

# ==========================================
# 线程2：MES心跳线程
# ==========================================
class MESHeartbeatThread(QThread):
    mesConnected = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.connected = False
        self.running = True

    def run(self):
        while self.running:
            try:
                self.connected = True
                self.mesConnected.emit(True)
            except:
                self.connected = False
                self.mesConnected.emit(False)
            time.sleep(2)

# ==========================================

# 线程3：RFID自动轮询线程
# ==========================================
class RFIDPollThread(QThread):
    foupArrived = pyqtSignal(str)
    foupRemoved = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.running = True
        self.last = None

    def run(self):
        while self.running:
            try:
                # 模拟读到RFID UID
                uid = "F0123456789ABCDEF"
                if uid != self.last:
                    self.last = uid
                    self.foupArrived.emit(uid)
            except:
                self.foupRemoved.emit()
            time.sleep(1)

# ==========================================
# 工作线程：读取 / 写入
# ==========================================
# class RFIDWorker(QThread):
#     result = pyqtSignal(dict)
#     log = pyqtSignal(str)

#     def __init__(self):
#         super().__init__()
#         self.cmd = ""
#         self.lot = ""
#         self.role = "operator"

#     def run(self):
#         try:
#             if self.cmd == "read":
#                 self.log.emit("读取 FOUP 中...")
#                 time.sleep(0.5)
#                 self.result.emit({
#                     "type": "read",
#                     "uid": "F0123456789ABCDEF",
#                     "msg": "OK"
#                 })

#             elif self.cmd == "write":
#                 self.log.emit("写入批次中...")
#                 time.sleep(0.5)
#                 self.result.emit({
#                     "type": "write",
#                     "ok": True,
#                     "msg": "SUCCESS"
#                 })

#         except Exception as e:
#             self.log.emit(f"异常：{str(e)}")

# ==========================================

# ==================== 多线程工作类 ====================
class RFIDWorker(QThread):
    result = pyqtSignal(dict)
    log = pyqtSignal(str)

    def __init__(self, service):
        super().__init__()
        self.service = service
        self.cmd = ""
        self.lot = ""
        self.role = "operator"

    def run(self):
        try:
            if self.cmd == "read":
                self.log.emit("读取 FOUP 中...")
                uid, msg = self.service.read_foup(self.role)
                self.result.emit({"type": "read", "uid": uid, "msg": msg})

            elif self.cmd == "write":
                self.log.emit("写入批次中...")
                ok, msg = self.service.write_foup(self.lot, self.role)
                self.result.emit({"type": "write", "ok": ok, "msg": msg})

        except Exception as e:
            self.log.emit(f"异常：{str(e)}")

# ==================== 主窗口 ====================
class MainWindow(QMainWindow):
    def __init__(self, service):
        super().__init__()
        self.setWindowTitle("FOUP RFID 控制系统")
        self.setGeometry(600, 600, 600, 500)

        # 业务服务
        self.service = service

        # 多线程
        self.thread = RFIDWorker(service)
        self.thread.result.connect(self.on_result)
        self.thread.log.connect(self.log)

        # # 正确创建线程（无内置关键字冲突）
        # self.gem_thread = GEMStateThread()
        # self.mes_thread = MESHeartbeatThread()
        # self.rfid_poll = RFIDPollThread()
        # self.worker = RFIDWorker()

        # # 绑定
        # self.worker.result.connect(self.on_result)
        # self.worker.log.connect(self.log)
        # self.gem_thread.stateChanged.connect(self.update_gem)
        # self.mes_thread.mesConnected.connect(self.update_mes)
        # self.rfid_poll.foupArrived.connect(lambda uid: self.foup_lbl.setText(f"FOUP: {uid}"))

        # # 启动线程
        # self.gem_thread.start()
        # self.mes_thread.start()
        # self.rfid_poll.start()

        # UI
        self.init_ui()

    def init_ui(self):
        w = QWidget()
        self.setCentralWidget(w)
        layout = QVBoxLayout(w)

        # 标题
        title = QLabel("12寸 FOUP RFID 读写台")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size:20px; font-weight:bold")
        layout.addWidget(title)

        # 状态
        self.status = QLabel("状态：空闲")
        self.uid = QLabel("FOUP ID：无")
        layout.addWidget(self.status)
        layout.addWidget(self.uid)


        # 状态栏
        self.gem_lbl = QLabel("GEM: IDLE")
        self.mes_lbl = QLabel("MES: 断开")
        self.foup_lbl = QLabel("FOUP: 无")
        layout.addWidget(self.gem_lbl)
        layout.addWidget(self.mes_lbl)
        layout.addWidget(self.foup_lbl)

        # 权限
        self.role = QComboBox()
        self.role.addItems(["operator", "engineer", "admin"])
        layout.addWidget(QLabel("权限："))
        layout.addWidget(self.role)

        # 按钮
        read_btn = QPushButton("读取 FOUP")
        write_btn = QPushButton("写入批次")
        read_btn.clicked.connect(self.run_read)
        write_btn.clicked.connect(self.run_write)
        layout.addWidget(read_btn)
        layout.addWidget(write_btn)

        # 批次输入
        self.lot_input = QLineEdit()
        self.lot_input.setPlaceholderText("输入批次号")
        layout.addWidget(QLabel("批次号："))
        layout.addWidget(self.lot_input)

        # 日志
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        layout.addWidget(QLabel("日志："))
        layout.addWidget(self.log_box)

    def log(self, msg):
        self.log_box.append(f"[{QDateTime.currentDateTime().toString()}] {msg}")

    def run_read(self):
        self.thread.cmd = "read"
        self.thread.role = self.role.currentText()
        self.thread.start()

    def run_write(self):
        self.thread.cmd = "write"
        self.thread.lot = self.lot_input.text()
        self.thread.role = self.role.currentText()
        self.thread.start()

    def on_result(self, d):
        if d["type"] == "read":
            self.uid.setText(f"FOUP ID：{d['uid']}")
            self.log(f"读取完成：{d['msg']}")
        else:
            self.log(f"写入结果：{d['msg']}")
        self.status.setText("状态：完成")

    def update_gem(self, s):
        self.gem_lbl.setText(f"GEM: {s}")

    def update_mes(self, c):
        self.mes_lbl.setText(f"MES: {'已连接' if c else '断开'}")



# ==================== 启动 ====================
def start_qt():
    from app.logic.foup_service import FoupService
    service = FoupService()

    app = QApplication(sys.argv)
    win = MainWindow(service)
    win.show()
    app.exec_()