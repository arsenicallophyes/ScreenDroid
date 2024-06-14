# **ScreenDroid**

ScreenDroid is an Android debugger that allows you to share your Android device's screen wirelessly or via USB. It has a CLI interface in version 1 and a GUI interface in version 2.

## Features

- Version 1 (Deprecated): Supports one device at a time and has a limited set of features.
- Version 2: Supports multiple devices, routing traffic to a specific adapter, and has a full feature set. It also has a startup animation and prevents multiple instances of the process from running. It has keybinds for refreshing, killing processes, and exiting the application.
- **New Feature**: QR Code Pairing with Zeroconf for seamless device pairing over the network.
- **New Feature**: Window Resizing (Beta): Resizing the window is now enabled. This feature is currently in beta and not fully implemented, so some issues might occur. Using the default size should not have any issues.

## Preview

![ScreenDroid Preview](https://github.com/arsenicallophyes/ScreenDroid/assets/120115529/643da152-902b-48d4-b0f1-1bcc2baeab25)

## Built With

- [ADB](https://developer.android.com/studio/command-line/adb) - Automate this tool
- [Scrcpy](https://github.com/Genymobile/scrcpy) - Automate this tool
- [Tkinter](https://docs.python.org/3/library/tkinter.html) - Graphical User Interface
- [Pillow](https://pillow.readthedocs.io/en/stable/) - Extract each frame from a .mp4 file
- [Imageio](https://imageio.readthedocs.io/en/stable/) - Read .mp4 files
- [Subprocess](https://docs.python.org/3/library/subprocess.html) - Run commands and capture their output
- [Re](https://docs.python.org/3/library/re.html) - Filter command outputs and extract data
- [Zeroconf](https://pypi.org/project/zeroconf/) - QR Code Pairing and network service discovery

## Compatibility

In order to use our app, the following requirements must be met:

- Your device must have USB debugging enabled in the developer options.
- Android 11 and higher officially support wireless screen sharing (it may also work on older versions).
- Android 5 and higher officially support wired screen sharing.
- Your device and PC must be on the same LAN.

## Tested Devices

We have tested our app on the following devices:

- Samsung Galaxy S10 (Android 12)
- Samsung Galaxy A73 (Android 14)
- Samsung Galaxy Tab S7 FE (Android 14)
- Samsung Galaxy A20s (Android 12)


## Development

Our app was developed and tested on Python 3.12.0.
We welcome feedback from the community to improve and stabilize the application.

## Known Issues

We are aware of the following issues with our app:

- There is a minor issue with the new QR code pairing via Zeroconf, where the app occasionally fails to connect to the phone. This happens because the phone may stop sending mDNS requests at regular intervals, preventing the app from detecting it. To avoid this problem, turn on wireless debugging only when you need to use the QR code pairing feature and turn it off when not in use, rather than leaving it on all the time.
- Certain elements will not resize properly. As mentioned earlier, resizing is in beta, and this is a known issue.

## Fixed Issues

- Slow Startup (Improved in the latest version)
- Low Quality UI and Old Design (The design is now more modern and up to date)
- The bug preventing the device's name from disappearing from the list box when running a task has been fixed.
- The `ADBV2.lock` file is no longer used. We now use a socket IPC method to prevent multiple instances. Here is the updated implementation:

```python
def multiple_instances_eliminator():
    try:
        client_side.connect(IPC_ADDRESS)
        os.kill(os.getpid(), 9)
    except ConnectionRefusedError:
        global server_side
        server_side = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_side.bind(IPC_ADDRESS)
        server_side.listen(20)
        while True:
            conn, addr = server_side.accept()
            threading.Thread(target=conn.close).start()

threading.Thread(target=multiple_instances_eliminator).start()
```
## New Features

- **Window Resizing**: Resizing the window is now enabled. This feature is currently in beta and not fully implemented, so some issues might occur. Using the default size should not have any issues.
- **QR Code Pairing with Zeroconf**: We have added a new feature that allows for seamless device pairing over the network using QR codes and Zeroconf. This feature requires the Bonjour service to be installed, and the app will prompt for admin privileges during the first startup to install the necessary files. Here’s how it works:
  1. **Zeroconf Service Discovery**: The app uses Zeroconf to broadcast its presence on the local network, making it discoverable by other devices.
  2. **QR Code Generation**: A QR code is generated to encode the service information. This QR code can be scanned by the Android device to pair with the app.
  3. **Automatic Bonjour Installation**: If Bonjour is not installed, the app will request admin privileges to install it, ensuring smooth operation.
  4. **Admin Privileges Request**: The app will ask for admin privileges automatically during the first startup to install the necessary files.
- **PIN Pairing with Autodetect**: We've introduced PIN pairing alongside QR code pairing. When attempting to connect via PIN, the app will automatically detect the IP address, and port to auto-complete the input section for convenience.
- **Network Verification**: All network operations involving connecting a phone will now verify the IP address within the network range and attempt to ping the device. Connection will only be established if both tests are successful. These options can be disabled from settings.
- **Screen Off Option**: Users can now choose to turn off their phone screen while sharing the screen with their PC.
- **Preferred Connection Method**:
  - Defaults to Any: Allows the app to use any available connection method.
  - Wired Mode: Disconnects all wireless connections that are connected both with wire and wireless. If a device is connected wirelessly only, it will not get disconnected.
  - Wireless Mode: Hides the wired devices from the devices selection list. If a device is connected via both wire and wireless, wired-only devices will not be hidden.


## Upcoming Features

We have a number of exciting features in the pipeline for our app. Here's a sneak peek at what you can expect:

- **File Transfer and Progress Monitoring**: Our app will allow you to easily download and upload files, both over wired and wireless connections, and keep track of the progress of your file transfers with our built-in progress monitor.
- **Custom Refresh Time**: Set the refresh time for the app to suit your needs.
- **User Settings**: Customize your experience with the ability to save your preferred settings.
- **Update Mechanism**: An update mechanism will be added.

Stay tuned for updates on these exciting new features!


## Modules Used

Here is the full list of modules used in our app:

```python
from tkinter import *
import subprocess, os, threading, random, imageio, re, socket, qrcode, hashlib, ctypes, time, ipaddress
from tkinter import messagebox
from uuid import uuid4
from PIL import Image, ImageTk
from zeroconf import ServiceBrowser, Zeroconf
from io import BytesIO
from collections import Counter
```
## Running the Script
To run the script, follow these steps:
  1. Install the required dependencies using the `requirements.txt` file included in the GitHub repository:
```bash
pip install -r requirements.txt
```
  2. Move the `ScreenDroid.py` file into the `addons` folder.

After completing these steps, you can run the script as usual.

## How to Compile

To compile the ScreenDroid application, you will need the following dependencies:

- Pillow>=10.0.1
- imageio==2.4.1
- qrcode>=7.4.2
- zeroconf==0.119.0
- imageio-ffmpeg==0.4.9
- Nuitka==2.3

You can install these dependencies using pip:

```bash
pip install Pillow>=10.0.1 imageio==2.4.1 qrcode>=7.4.2 zeroconf==0.119.0 imageio-ffmpeg==0.4.9 Nuitka==2.3
```
Make sure to use `Python 3.12.0` for compiling. It may work with newer versions of Python, but it has not been tested.

You also need to modify a line in the `ScreenDroid.py` file. Change this line:
```python
os.environ['PATH'] = rf"{os.path.dirname(__file__)}\lib" + os.pathsep + os.environ['PATH']
```
to:
```python
os.environ['PATH'] = os.path.dirname(__file__) + os.pathsep + os.environ['PATH']
```
Next, move the `lib` folder from `addons/lib` to the parent directory and download and extract the [`bin`](https://github.com/BtbN/FFmpeg-Builds/releases/download/autobuild-2023-05-31-12-47/ffmpeg-N-110946-g859c34706d-win64-gpl.zip) folder into the parent directory.

You should have the following folder tree structure:
```
.
├── ScreenDroid.py
├── lib/
│   └── *.dll
├── addons/
│   ├── vids/
│   ├── Android.ico
│   └── *.*
└── bin/
    └── ffmpeg.exe
```

Once you have installed the dependencies, made the necessary code modification, and moved the required folders, use the following command to compile the application with Nuitka:


```bash
nuitka "ScreenDroid.py" --standalone --onefile --enable-plugin=tk-inter --include-data-dir="addons"=./ --windows-icon-from-ico="addons\Android.ico" --include-module=imageio_ffmpeg --include-data-file="bin\\ffmpeg.exe"=./ --include-module=threading --include-module=PIL._imagingtk --include-module=tkinter --windows-console-mode=disable --include-data-file="lib\libbrotlicommon.dll"=./ --include-data-file="lib\libbrotlidec.dll"=./ --include-data-file="lib\libbz2-1.dll"=./ --include-data-file="lib\libcairo-2.dll"=./ --include-data-file="lib\libexpat-1.dll"=./ --include-data-file="lib\libfontconfig-1.dll"=./ --include-data-file="lib\libfreetype-6.dll"=./ --include-data-file="lib\libgcc_s_seh-1.dll"=./ --include-data-file="lib\libglib-2.0-0.dll"=./ --include-data-file="lib\libgraphite2.dll"=./ --include-data-file="lib\libharfbuzz-0.dll"=./ --include-data-file="lib\libiconv-2.dll"=./ --include-data-file="lib\libintl-8.dll"=./ --include-data-file="lib\libpcre-1.dll"=./ --include-data-file="lib\libpixman-1-0.dll"=./ --include-data-file="lib\libpng16-16.dll"=./ --include-data-file="lib\libstdc++-6.dll"=./ --include-data-file="lib\libwinpthread-1.dll"=./ --include-data-file="lib\zlib1.dll"=./lib
```
This command will compile ScreenDroid.py into a standalone executable with all necessary dependencies included.








