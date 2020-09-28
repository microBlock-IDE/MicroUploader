# MicroUploader

Tool for upload MicroPython firmware to your Microcontroller. Now, Support only ESP32

## Device Support

Support device:

 * Generic ESP8266 Module
 * NodeMCU-32S
 * Node32 Lite
 * Node32s
 * Nano32
 * KidBright32
 * OpenKB
 * IPST-WiFi
 * Senses Weizen
 * M5Stack
 * LOLIN32 Lite
 * LOLIN D32 Pro

We tested this:

 * IOXESP32
 * IOXESP32U
 * IOXESP32PS
 * NodeMCU-32S
 * KidBright32
 * OpenKB
 * LOLIN32 Lite
 
## Using

### Use executable file

download program at Releases page and unzip file then open MicroUploader.exe and do three step

 1. Select your board - if your board is not in list, try select **ESP32 Dev Module**
 2. Select COM port
 3. Select MicroPython firmware version
 4. Click upload button

wait program upload firmware. After done you can try use MicroPython via microblock.app

**executable file have only Windows x64 and Ubuntu x64 and mac OS x64**

>For Ubuntu needs run via sudo

### Use Python file

Installing Python 3: https://docs.python-guide.org/starting/install3/linux/

Install pyserial and PySide2

```shell
pip3 install pyserial
pip3 install PySide2
```

Clone this project from master

```shell
wget -O MicroUploader.zip https://github.com/microBlock-IDE/MicroUploader/archive/master.zip
```

Unzip MicroUploader.zip

```shell
unzip MicroUploader.zip
```

Enter to MicroUploader folder

```shell
cd MicroUploader-master
```

chmod `esptool.py` for user can run

```shell
chmod 755 esptool/esptool.py
```

Run `MicroUploader.py` via Python3

```shell
sudo python3 ./MicroUploader.py
```

if you found error `libxcb-xinerama.so.0: cannot open shared object file: No such file or directory` install `libxcb-xinerama0`

```shell
apt-get install libxcb-xinerama0
```

MicroPython windows will open then do three step

 1. Select your board - if your board is not in list, try select **ESP32 Dev Module**
 2. Select COM port
 3. Select MicroPython firmware version
 4. Click upload button

wait program upload firmware. After done you can try use MicroPython via microblock.app

## License

GPL-3.0 same QT open source users


