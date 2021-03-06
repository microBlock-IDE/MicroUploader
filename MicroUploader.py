# This Python file uses the following encoding: utf-8
import sys
import os
import serial.tools.list_ports
import json
import subprocess
import threading
import io
import re
import shlex
import esptool

from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtUiTools import *
from PySide2 import QtXml, QtCore

if getattr(sys, 'frozen', False):
    scriptPath = os.path.dirname(sys.executable)
elif __file__:
    scriptPath = os.path.dirname(__file__)

signals = None

class Main(QWidget):
    def __init__(self):
        super(Main, self).__init__()
        self.load_ui()

    def load_ui(self):
        loader = QUiLoader()
        path = os.path.join(scriptPath, "form.ui")
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

    firmwarePath = os.path.join(scriptPath, "firmware", firmware)

    esptool = os.path.join(scriptPath, "esptool/esptool")
    if sys.platform == "win32":
        esptool = esptool + ".exe"
    elif sys.platform == "darwin":
        esptool = esptool
    else:
        esptool = esptool + "-ubuntu-x64"

    esptool = os.path.abspath(esptool)

    deviceInfo = devices[boardCombo.currentIndex()]

    global worker
    worker = UploadWorker(esptool, port, firmwarePath, deviceInfo)
    signals.progress.connect(onProgressUpdateHandle)
    signals.result.connect(onResultHandle)
    signals.finished.connect(onUploadEndHandle)

    threading.Thread(target=worker.run).start()

class UploadWorkerSignals(QObject):
    finished = Signal(object)
    result = Signal(object)
    progress = Signal(int)

class UploadWorker(QRunnable):
    def __init__(self, esptool, port, bin, deviceInfo):
        super(UploadWorker, self).__init__()

        global signals
        signals = UploadWorkerSignals()    
        self.esptool = esptool
        self.port = port
        self.bin = bin
        self.deviceInfo = deviceInfo

    @Slot()
    def run(self):
        error = uploadBin(signals, self.port, self.bin, self.deviceInfo)
        signals.finished.emit(error)


def onProgressUpdateHandle(i):
    progressBar.setValue(i)

def onResultHandle(line):
    logLabel.setText(line)

def onUploadEndHandle(error):
    uploadButton.setEnabled(True)
    msg = QMessageBox()
    if error == None:
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Upload successful")
        msg.setText("Upload successful")
    else:
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Upload error")
        msg.setText(error)
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec_()

def esptool_print(message, last_line=False, end="\n"):
    # if sys.stdout.isatty():
    #     print("\r%s" % message, end='\n' if last_line else '')
    # else:
    #     print(message, end=end)
    
    signals.result.emit(message)
    if message.startswith("Writing at"):
        i = int(message[message.find("(") + 1 : message.find("%")].strip())
        signals.progress.emit(i)

esptool.print_overwrite = esptool_print

def uploadBin(signals, port, binFile, deviceInfo):
    command = [ ]
    command.append("--chip"); command.append(deviceInfo["chip"])
    command.append("--port"); command.append(port)
    command.append("--baud"); command.append(str(deviceInfo["speed"]))
    command.append("write_flash"); command.append("-z")
    command.append("--erase-all")
    command.extend(shlex.split(deviceInfo["flag"]))
    command.append("0x1000" if deviceInfo["chip"] == "esp32" else "0x0000"); command.append(binFile)

    try:
        esptool.main(command)
        return None
    except Exception as e:
        return str(e)

def updatePortTimerCB():
    ports = serial.tools.list_ports.comports()
    if portCombo.count() != len(ports):
        portCombo.clear()
        for port, desc, hwid in sorted(ports):
            portCombo.addItem(port)

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
    widget.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.WindowMinimizeButtonHint)
    widget.show()

    boardCombo = widget.ui.boardCombo
    portCombo = widget.ui.portCombo
    firmwareCombo = widget.ui.firmwareCombo
    uploadButton = widget.ui.uploadButton
    logLabel = widget.ui.logLabel
    progressBar = widget.ui.progressBar
    
    logLabel.setFixedSize(530, 40)

    updatePortTimerCB()

    devices = json.loads(open(os.path.join(scriptPath, "devices.json")).read())
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
