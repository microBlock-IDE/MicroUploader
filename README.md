# MicroUploader

Tool for upload MicroPython firmware to your Microcontroller. Now, Support only ESP32

## Device Support

We tested this:

 * IOXESP32
 * IOXESP32U
 * IOXESP32PS
 
## Using

### for Windows user

download program at Releases page and unzip file then open MicroUploader.exe and do three step

 1. Select your board - if your board is not in list, try select **ESP32 Dev Module**
 2. Select COM port
 3. Select MicroPython firmware version
 4. Click upload button

wait program upload firmware. After done you can try use MicroPython via microblock.app


### for Linux and mac OS user

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

Run `MicroUploader.py` via Python3

```shell
sudo python3 ./MicroUploader.py
```

if you found error `libxcb-xinerama.so.0: cannot open shared object file: No such file or directory` install `libxcb-xinerama`

```shell
apt-get install libxcb-xinerama
```

MicroPython windows will open then do three step

 1. Select your board - if your board is not in list, try select **ESP32 Dev Module**
 2. Select COM port
 3. Select MicroPython firmware version
 4. Click upload button

wait program upload firmware. After done you can try use MicroPython via microblock.app

## License

GPL-3.0 same QT open source users


