# This Python file uses the following encoding: utf-8
import sys
import os
import serial.tools.list_ports
import json
import subprocess
import threading
import io
import re

from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtUiTools import *
from PySide2 import QtXml


class Main(QWidget):
    def __init__(self):
        super(Main, self).__init__()
        self.load_ui()

    def load_ui(self):
        loader = QUiLoader()
        path = os.path.join(os.path.dirname(__file__), "form.ui")
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        self.ui = loader.load(ui_file, self)
        ui_file.close()

def onBoardChangedHandle(index):
    # print(devices[index])
    firmwareCombo.clear()
    for firmware in devices[index]['firmware']:
        firmwareCombo.addItem(firmware)

def chackValue():
    if boardCombo.currentIndex() == -1:
        raise Exception("Board not select")

    if portCombo.currentIndex() == -1:
        raise Exception("COM port not select")

    if firmwareCombo.currentIndex() == -1:
        raise Exception("Firmware not select")

def onUploadBtnClickHandle():
    try:
        chackValue()
    except Exception as e:
        e = str(e)
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Upload error")
        msg.setText(e)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
        return

    progressBar.setValue(0)
    uploadButton.setEnabled(False)

    port = portCombo.currentText()
    firmware = firmwareCombo.currentText()

    firmwarePath = "{}/firmware/{}".format(os.getcwd(), firmware)
    print(firmwarePath)

    esptool = "{}/esptool/esptool".format(os.getcwd())
    if sys.platform == "win32":
        esptool = esptool + ".exe"
    elif sys.platform == "darwin":
        esptool = esptool
    else:
        esptool = "python " + esptool + ".py"

    esptool = os.path.abspath(esptool)

    global worker
    worker = UploadWorker(esptool, port, firmwarePath)
    worker.signals.progress.connect(onProgressUpdateHandle)
    worker.signals.result.connect(onResultHandle)
    worker.signals.finished.connect(onUploadEndHandle)

    threading.Thread(target=worker.run).start()

# def QThreadPoolTaskCB():
#     threadpool = QThreadPool()
#     threadpool.start(worker) 

class UploadWorkerSignals(QObject):
    finished = Signal(int)
    result = Signal(object)
    progress = Signal(int)

class UploadWorker(QRunnable):
    def __init__(self, esptool, port, bin):
        super(UploadWorker, self).__init__()

        self.signals = UploadWorkerSignals()    
        self.esptool = esptool
        self.port = port
        self.bin = bin

    @Slot()
    def run(self):
        eraseFlash(self.signals, self.esptool, self.port)
        uploadBin(self.signals, self.esptool, self.port, self.bin)
        self.signals.finished.emit(0)


def onProgressUpdateHandle(i):
    progressBar.setValue(i)

def onResultHandle(line):
    logLabel.setText(line)

def onUploadEndHandle():
    print("Upload END")
    uploadButton.setEnabled(True)
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setWindowTitle("Upload successful")
    msg.setText("Upload successful")
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec_()

def eraseFlash(signals, esptool, port):
    command = [
        esptool,
        "--chip", "esp32",
        "--port", port,
        "--baud", "1152000",
        "erase_flash"
    ]
    print(" ".join(command))
    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    for line in io.TextIOWrapper(process.stdout, encoding="utf-8"):
        sys.stdout.write("erase>" + line)
        signals.result.emit(re.sub(r'[\n\r]+', '', line))

def uploadBin(signals, esptool, port, bin):
    command = [
        esptool,
        "--chip", "esp32",
        "--port", port,
        "--baud", "1152000",
        "write_flash", "-z",
        "0x1000", bin
    ]
    print(" ".join(command))
    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    for line in io.TextIOWrapper(process.stdout, encoding="utf-8"):
        sys.stdout.write("upload>" + line)
        signals.result.emit(re.sub(r'[\n\r]+', '', line))
        if line.startswith("Writing at"):
            i = int(line[line.find("(") + 1 : line.find("%")].strip())
            signals.progress.emit(i)

def updatePortTimerCB():
    ports = serial.tools.list_ports.comports()
    if portCombo.count() != len(ports):
        portCombo.clear()
        for port, desc, hwid in sorted(ports):
            portCombo.addItem(port)
        # portCombo.setCurrentIndex(-1)

if __name__ == "__main__":
    global widget
    global boardCombo, portCombo, firmwareCombo
    global uploadButton
    global logLabel
    global progressBar
    global devices
    
    app = QApplication([])
    widget = Main()
    widget.setWindowTitle("MicroUploader")
    widget.show()

    boardCombo = widget.ui.boardCombo
    portCombo = widget.ui.portCombo
    firmwareCombo = widget.ui.firmwareCombo
    uploadButton = widget.ui.uploadButton
    logLabel = widget.ui.logLabel
    progressBar = widget.ui.progressBar
    
    logLabel.setFixedSize(530, 40)

    updatePortTimerCB()

    devices = json.loads(open("{}/devices.json".format(os.getcwd())).read())
    for device in devices:
        boardCombo.addItem(device["name"])
    
    boardCombo.setCurrentIndex(-1)
    boardCombo.currentIndexChanged.connect(onBoardChangedHandle)

    widget.ui.uploadButton.clicked.connect(onUploadBtnClickHandle)

    updatePortTimer = QTimer()
    updatePortTimer.setInterval(100)
    updatePortTimer.timeout.connect(updatePortTimerCB)
    updatePortTimer.start()

    sys.exit(app.exec_())
