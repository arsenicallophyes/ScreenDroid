# **ScreenDroid**

ScreenDroid is an Android debugger that allows you to share your Android device's screen wirelessly or via USB. It has a CLI interface in version 1 and a GUI interface in version 2.

## Preview

![ScreenDroid Preview](preview.png)

## Features

- Version 1 (Deprecated): Supports one device at a time and has a limited set of features.
- Version 2: Supports multiple devices, routing traffic to a specific adapter, and has a full feature set. It also has a startup animation and prevents multiple instances of the process from running. It has keybinds for refreshing, killing processes, and exiting the application.
- **New Feature**: QR Code Pairing with Zeroconf for seamless device pairing over the network.
- **New Feature**: Window Resizing (Beta): Resizing the window is now enabled. This feature is currently in beta and not fully implemented, so some issues might occur. Using the default size should not have any issues.

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
- Samsung Galaxy J5 2016 (Android 10, Lineage OS 17)
- Samsung Galaxy Tab 4 (Android 4.4.2)
- Samsung Galaxy Note 10.1 (Android 9, Lineage OS 16)

On the latest version, the app has only been tested on the Samsung Galaxy S10 (Android 12).

## Development

Our app was developed and tested on Python 3.12.0.
We welcome contributions and feedback from the community to improve and stabilize the application.

## Known Issues

We are aware of the following issues with our app:

- There is a minor issue with the new QR code pairing via Zeroconf, where the app occasionally fails to connect to the phone. This happens because the phone may stop sending mDNS requests at regular intervals, preventing the app from detecting it. To avoid this problem, turn on wireless debugging only when you need to use the QR code pairing feature and turn it off when not in use, rather than leaving it on all the time.

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
- **PIN Pairing with Autodetect**: We've introduced PIN pairing alongside QR code pairing. When attempting to connect via PIN, the app will automatically detect the IP address, port, and PIN to auto-complete the input section for convenience.
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
