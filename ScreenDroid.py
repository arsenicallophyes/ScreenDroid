"""
    ScreenDroid: Share and debug your Android device's screen wirelessly or via USB, with support for additional functions through USB debugging.
    Copyright (C) 2023  arsenicallophyes

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

For any inquiries or questions, you can reach out to me via electronic mail at "arsenicallophyes@tutanota.com".
"""

from tkinter import *
import subprocess, os, threading, random, imageio, re, socket, qrcode, hashlib, ctypes, time, ipaddress
from tkinter import messagebox
from uuid import uuid4
from PIL import Image, ImageTk
from zeroconf import ServiceBrowser, Zeroconf
from io import BytesIO
from collections import Counter
os.environ['PATH'] = rf"{os.path.dirname(__file__)}\lib" + os.pathsep + os.environ['PATH']
ctypes.windll.shcore.SetProcessDpiAwareness(True) # increases DPI for better image

try:
    import cairosvg
except OSError as e:
    messagebox.showerror("Missing Libaries",message=str(e))
    os.kill(os.getpid(),9)

VBS_KILL_PATH = '\\'.join([os.environ['TEMP'],'bj-serv-kill.vbs'])
VBS_START_PATH = '\\'.join([os.environ['TEMP'],'bj-serv-start.vbs'])
VBS_MD5_HASH_KILL = b'\xda6\xcd\xc2<\xd27\xee\x01\x1e1\xb2\xf3N\x94\xea'
VBS_MD5_HASH_START = b'##\x84S\x9eE\x99\xb0%\xc9_;\xbaF\xf8\xed'
VBS_CONTENT_KILL = '''Set objShell = CreateObject("Shell.Application")\nobjShell.ShellExecute "cmd.exe", "/c net stop ""Bonjour Service""", "", "runas", 0'''
VBS_CONTENT_START = '''Set objShell = CreateObject("Shell.Application")\nobjShell.ShellExecute "cmd.exe", "/c net start ""Bonjour Service""", "", "runas", 0'''
RESIZE_AND_PLACE_QR_CODE_LABEL = True
bg_color_main = "#1f1f1f"
Running_tasks_pid = {}
kill_process_running = False
re_checkup_running = False
time_list = list(range(0, 31))
time_list.reverse()
aspect_ratio = 2/3
UNAUTHORIZED_BUTTON_PLACEMENT = False
OFFLINE_BUTTON_PLACEMENT = False
PERMISSION_ERROR_PLACEMENT = False
RESTART_TIMER = False
STARTUP_CHECK = None
RESIZING = False
vid_playback_wireless = None
vid_playback_downloading = None
attached_adapters = []
network_devices_info = {}
active_color = "#182129"
WIRELESS_QR_PAIRING_STATE = False
WIRELESS_BUTTON_NETWORK_STATE = True
WIFI_PAIRING_SSID = uuid4()
WIFI_PAIRING_PASSWORD = str(random.getrandbits(6))
CURRENT_MENU = "Main_Menu"
Active_Routes : list[dict] = [] 
vid_playback_startup = True
ip_addr_qr_pairing = None
IPC_ADDRESS = ('127.0.168.3',45222)
AUTO_COMPLETE_ADDRESS_BOX_PIN_PAIR = False
PIN_BOX_PAIR_HINT = False
PORT_BOX_PAIR_HINT= False
PORT_BOX_PAIR_STATUS = False
PIN_BOX_PAIR_STATUS = False
IP_ADDRESS_BOX_PAIR_STATUS = False
WIRELESS_CONNECTION_MDNS_STATUS = False
CONNECTION_SERVICE_INITIALIZED = False
PAIRING_SERVICE_INITIALIZED = False
zeroconf = Zeroconf()
client_side = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

os.chdir(os.path.dirname(__file__))

def multiple_instances_eliminator():
    try:
        client_side.connect(IPC_ADDRESS)
        os.kill(os.getpid(),9)
    except ConnectionRefusedError:
        global server_side
        server_side = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        server_side.bind(IPC_ADDRESS)
        server_side.listen(20)
        while True:
            conn, addr = server_side.accept()
            threading.Thread(target=conn.close).start()

threading.Thread(target=multiple_instances_eliminator).start()

subprocess.run(["adb", "kill-server"], shell=True, capture_output=True)

def network_check():
    global attached_adapters, network_devices_info
    attached_adapters = []
    network_devices_info = {}
    network_info_addr = subprocess.run(["powershell", "Get-NetIPConfiguration"], shell=True, capture_output=True).stdout.decode().split("\r\n\r\n")
    network_info_subnet = subprocess.run(["wmic", "NICCONFIG"],shell=True,capture_output=True,).stdout.decode().split("""\r\r\n                                       """)
    for i in subprocess.run(["powershell","" "Get-NetAdapter -physical | where status -eq 'up' | Format-List" "",],shell=True,capture_output=True,).stdout.decode().split("\r\n\r\n"):
        if len(i) != 0:
            Interface_description = re.findall("InterfaceDescription       : (.*)", i)[0].replace("\r", "")
            Interface_MAC = re.findall("MacAddress                 : (.*)", i)[0].replace("\r", "")
            Interface_Name = re.findall("Name                       : (.*)", i)[0].replace("\r", "")
            Interface_Index = re.findall("InterfaceIndex             : (.*)",i)[0].replace("\r", "")
            for x in network_info_addr:
                if len(x) != 0:
                    if Interface_Name == re.findall("InterfaceAlias       : ([^\r]*)", x)[0]:
                        if len(re.findall("IPv4DefaultGateway   : (.*)", x)) != 0:
                            IPv4_gate = re.findall("IPv4DefaultGateway   : (.*)", x)[0].replace("\r", "")
                            try:
                                for p in network_info_subnet:
                                    if Interface_description in p:
                                        Interface_subnet = re.findall('}                   {"(.*?")',p)[0].strip('"')
                                        network_devices_info[Interface_Name] = (Interface_MAC,Interface_description,IPv4_gate,Interface_subnet,Interface_Index)
                            except IndexError:
                                pass
    if len(network_devices_info) != 0: 
        for i in network_devices_info.values():
            attached_adapters.append(i[1])
        wireless_tcpip_btn.configure(state="normal")
        wireless_pairing_btn.configure(state="normal")
    else:
        attached_adapters = ["Couldn't Detect Any Adapter"]
        wireless_tcpip_btn.configure(state="disabled")
        wireless_pairing_btn.configure(state="disabled")
        global WIRELESS_BUTTON_NETWORK_STATE
        WIRELESS_BUTTON_NETWORK_STATE = False

def vid_playback_4_startup():
    global vid_playback_startup, window_size
    frame_data_part_1 = imageio.get_reader(r"vids\\startup_part1.mp4")
    frame_data_part_2 = imageio.get_reader(r"vids\\startup_part2.mp4")
    window_size = (window_width, window_height)
    for image in frame_data_part_1.iter_data():
        frame_image = ImageTk.PhotoImage(Image.fromarray(image).resize(window_size))
        startup_label.config(image=frame_image)
        startup_label.image = frame_image
        if vid_playback_startup != True:
            main_page.pack()
            startup_label.pack_forget()
        time.sleep(0.00_00_8)
    while True:
        for image in frame_data_part_2.iter_data():
            frame_image = ImageTk.PhotoImage(Image.fromarray(image).resize(window_size))
            startup_label.config(image=frame_image)
            startup_label.image = frame_image
            if vid_playback_startup != True:
                main_page.pack()
                startup_label.pack_forget()
                return
            time.sleep(0.00_00_8)


def vid_playback_4_wireless(path):
    global vid_playback_wireless, window_size
    frame_data = imageio.get_reader(path)
    window_size = (window_width, window_height)
    while vid_playback_wireless:
        for image in frame_data.iter_data():
            frame_image = ImageTk.PhotoImage(Image.fromarray(image).resize(window_size))
            vid_label_wireless.config(image=frame_image)
            vid_label_wireless.image = frame_image
            if vid_playback_wireless != True:
                break
            time.sleep(0.001)

# def vid_playback_4_downloading(path):
#     global vid_playback_downloading
#     frame_data = imageio.get_reader(path)
#     size = (48, 48)
#     while vid_playback_downloading:
#         for image in frame_data.iter_data():
#             frame_image = ImageTk.PhotoImage(Image.fromarray(image).resize(size))
#             file_downloading_btn.config(image=frame_image)
#             file_downloading_btn.image = frame_image
#             if vid_playback_downloading == False:
#                 break
#             time.sleep(0.03)
#     else:
#         file_downloading_btn.config(image=file_downloading_btn_complete_png)

class Pairer:
    def remove_service(self, zeroconf, type, name):
        pass

    def update_service(self, zeroconf, type, name):
        pass

    def validate_phone_ip(self, zeroconf, type, name, phone_ip : str, device_id):
        preferred_interface = preferred_adapter.get()
        for key,value in network_devices_info.items():
            if value[1] == preferred_interface:
                Interface_MAC,IPv4_gate,Interface_subnet,Interface_Index = value[0],value[2],value[3],value[4]
                break
        
        if len(attached_adapters) > 1:
            Route_Traffic = True
        else:
            Route_Traffic = False

        if len(Active_Routes) != 0:
            try:
                for index, active_routes_dict in enumerate(Active_Routes):
                    active_routes_dict : dict
                    if active_routes_dict.values()[0] == f"route delete {phone_ip}":
                        subprocess.run(f"route delete {phone_ip}".split(" "),shell=True,capture_output=True)
                        Active_Routes.pop(index)
                        break
            except TypeError as e:
                print("LINE 210 "*10)
                print(e)
                print("LINE 210 "*10)
                print(f"List: {Active_Routes}")
                print(f"Index: {index}")
                print(f"Dictionary: {active_routes_dict}")

        ping_check, route_status = route_n_ping(Route_Traffic,phone_ip,IPv4_gate,Interface_Index,device_id)
        if not ip_validation(IPv4_gate,Interface_subnet, phone_ip):
            threading.Thread(target=messagebox.showerror,args=("Network Error",f"{phone_ip} is connected to a different network")).start()
            return False
        elif route_status == "ROUTE_FAILED":
            threading.Thread(target=messagebox.showerror,args=("Network Error",f"Routing Error:\n{ping_check}")).start()
            return False
        elif ping_check.returncode != 0:
            threading.Thread(target=messagebox.showerror,args=("Network Error",f"{phone_ip} didn't respond to a ping")).start()
            return False
        else:
            return True 

    def add_service(self, zeroconf:Zeroconf, type, name):
        servc_info = zeroconf.get_service_info(type, name, 1)
        ip_addr_qr_pairing = '.'.join([str(byte) for byte in bytearray(servc_info.addresses[0])])
        if CURRENT_MENU == "QR_CODE_PAIRING_MENU":
            if self.validate_phone_ip(zeroconf, type, name, ip_addr_qr_pairing, servc_info.server):
                process = subprocess.run(["adb","pair" ,f"{servc_info.server}:{servc_info.port}" ,WIFI_PAIRING_PASSWORD], shell=True,capture_output=True)
                if "Successfully paired" in process.stdout.decode():
                    wireless_back_btn.configure(state='disabled')
                    device_name = re.findall(r"guid=adb-(.*)-",process.stdout.decode())[0]
                    threading.Thread(target=messagebox.showinfo, args=("Pairing Successful",f"Successfully paired to {device_name}\n{ip_addr_qr_pairing}")).start() # replace with Entry/Label
                    threading.Thread(target=connecting_service,args=(device_name,servc_info.server),daemon=True).start()
                else:
                    threading.Thread(target=messagebox.showerror, args=("Pairing Error",process.stderr.decode("utf-8"))).start()
                    back_btn_wireless_pairing()  
            else:
                back_btn_wireless_pairing()
        elif CURRENT_MENU == "PIN_PAIRING_MENU":
            PIN_devies_IP_label_string_var.set(f"{ip_addr_qr_pairing}:{servc_info.port}")
            PIN_devices_label.place(x=30,y=150)




class Connector:
    global WIRELESS_CONNECTION_MDNS_STATUS
    def __init__(self,mode:str,pin_pair,device_name) -> None:
        
        self.mode = mode
        self.pin_pair = pin_pair
        self.device_name :str = device_name
        WIRELESS_CONNECTION_MDNS_STATUS = False
        # print("class initialized")

    def remove_service(self, zeroconf, type, name):
        pass

    def update_service(self, zeroconf, type, name):
        pass

    def add_service(self, zeroconf : Zeroconf, type, name):
        global WIRELESS_CONNECTION_MDNS_STATUS
        servc_info = zeroconf.get_service_info(type, name, 1)
        phone_ip = '.'.join([str(byte) for byte in bytearray(servc_info.addresses[0])])
        WIRELESS_CONNECTION_MDNS_STATUS = True
        if self.mode == 'background':
            subprocess.run(f'adb connect {servc_info.server}:{servc_info.port}',shell=True)
        elif self.mode == 'foreground':
            # print(phone_ip,":",servc_info.port,self.device_name)
            connection_process = subprocess.run(["adb","connect",f"{phone_ip}:{servc_info.port}"],shell=True,capture_output=True)
            # print('done')
            wireless_back_btn.configure(state='normal')
            threading.Thread(target=re_checkup,daemon=True).start()
            if connection_process.returncode == 0:
                threading.Thread(target=messagebox.showinfo, args= ('Sucessfully Connected',f"Connected to {self.device_name}")).start()
                if self.pin_pair:
                    Active_Routes.append({self.device_name:f"route delete {phone_ip}"}) # fix this, key should be serial number not server info
            elif connection_process.returncode == 1:
                threading.Thread(target=messagebox.showinfo, args=('Failed To Connect',connection_process.stdout.replace(servc_info.server.encode('utf-8'),self.device_name.encode('utf-8')).decode('utf-8')) ).start()
                if self.pin_pair:
                    subprocess.run(f"route delete {phone_ip}".split(" "),shell=True,capture_output=True) # fix this, key should be serial number not server info
            back_btn_wireless_pairing()

def connecting_service(device_name,device_id,pin_pair=False):
    kill_bonjour_service()
    global connecter_service, CONNECTION_SERVICE_INITIALIZED
    CONNECTION_SERVICE_INITIALIZED = True
    connecter = Connector('foreground',pin_pair,device_name)
    start_bonjour_service()
    connecter_service = ServiceBrowser(zeroconf,"_adb-tls-connect._tcp.local.",connecter)
    n = 0            
    while True:
        time.sleep(1)
        n+=1
        if not any(device_id in i for i in devices.keys()) and (CURRENT_MENU == "QR_CODE_PAIRING_MENU" or CURRENT_MENU == "PIN_PAIRING_MENU"):
            if n != 120:
                if n%30 == 0:
                    if messagebox.askyesno("Longer Than Expected?",message = "Recommendations:\n  • Disable WiFi Throttling.\n  • Try turning Wireless Debugging OFF and then ON.\nClick Yes to abort the auto-connection"):
                        # print('aborting')
                        if CURRENT_MENU == "QR_CODE_PAIRING_MENU" or CURRENT_MENU == "PIN_PAIRING_MENU":
                            # print('aborted')
                            back_btn_wireless_pairing()
                            # print("abortion complete")
                            break
            else:
                threading.Thread(target=messagebox.showinfo,args=("Connection Aborted","The connection was automatically stopped because it took more than 2 minutes. Please check your device and try again.")).start()
                if CURRENT_MENU == "QR_CODE_PAIRING_MENU" or CURRENT_MENU == "PIN_PAIRING_MENU":
                    back_btn_wireless_pairing()
def pin_pair_address_completion(event: Event):
    global AUTO_COMPLETE_ADDRESS_BOX_PIN_PAIR, PORT_BOX_PAIR_STATUS, IP_ADDRESS_BOX_PAIR_STATUS
    AUTO_COMPLETE_ADDRESS_BOX_PIN_PAIR = True
    on_entry_click_port(None)
    ip_addr , port = PIN_devies_IP_label_string_var.get().split(":")
    address_box_pairing_address.delete(0,END)
    address_box_pairing_address.insert(0,ip_addr)
    address_box_pairing_port.delete(0,END)
    address_box_pairing_port.insert(0,port)
    AUTO_COMPLETE_ADDRESS_BOX_PIN_PAIR = False
    PORT_BOX_PAIR_STATUS = True
    IP_ADDRESS_BOX_PAIR_STATUS = True

def PIN_pair_menu():
    global RESIZE_AND_PLACE_QR_CODE_LABEL, CURRENT_MENU
    RESIZE_AND_PLACE_QR_CODE_LABEL = False
    CURRENT_MENU = "PIN_PAIRING_MENU"
    PIN_pair_option_btn.configure(fg="#d3d3d3",state="disabled",)
    QR_pair_option_btn.configure(fg="#ffffff",state="normal",)
    QR_code_label.place_forget()
    connect_pairing_btn.place(x=140,y=460)
    address_box_pairing_address.place(x=50,y=330)
    address_box_pairing_port.place(x=270,y=330)
    pin_box_pairing.place(x=50, y=370)
    if not WIRELESS_QR_PAIRING_STATE:
        bonjour_install_btn.place_forget()
    auto_complete_address_box()

def auto_complete_address_box():
    if ip_validation_check_state_int.get() == 0:
        preferred_interface = preferred_adapter.get()
        for key,value in network_devices_info.items():
            if value[1] == preferred_interface:
                Interface_MAC,IPv4_gate,Interface_subnet,Interface_Index = value[0],value[2],value[3],value[4]
                break
        global auto_complete_gateway, network_address_lower_limit, broadcast_address_upper_limit
        auto_complete_gateway, network_address_lower_limit, broadcast_address_upper_limit = ip_validation_pin_pair(IPv4_gate,Interface_subnet)
        if auto_complete_gateway is not None:
            address_box_pairing_address.insert(0,auto_complete_gateway)

def ip_validation_pin_pair(default_gateway,subnet_mask,):
    if ip_validation_check_state_int.get() == 1:
        return None
    network = ipaddress.IPv4Network(f"{default_gateway}/{subnet_mask}", strict=False)
    network_address = str(network.network_address)
    broadcast_address = str(network.broadcast_address)
    broadcast_address = broadcast_address.split(".")
    broadcast_address.reverse()
    splitting_count = subnet_mask.split(".").count("255")
    network_address = network_address.split(".")
    network_address.reverse()
    auto_complete_gateway = []
    for i in range(splitting_count):
        auto_complete_gateway.append(network_address.pop(-1))
        broadcast_address.pop(-1)
    if len(auto_complete_gateway):
        network_address.reverse()
        broadcast_address.reverse()
        return ".".join(auto_complete_gateway)+".", network_address,broadcast_address
    else:
        return None


def QR_pair_menu():
    global RESIZE_AND_PLACE_QR_CODE_LABEL, CURRENT_MENU
    RESIZE_AND_PLACE_QR_CODE_LABEL = True
    CURRENT_MENU = "QR_CODE_PAIRING_MENU"
    QR_pair_option_btn.configure(fg="#d3d3d3",state="disabled",)
    PIN_pair_option_btn.configure(fg="#ffffff",state="normal",)
    PIN_devices_label.place_forget()
    QR_code_label.place(x=window_size[0]*0.1875,y=window_size[1]/3)
    connect_pairing_btn.place_forget()
    address_box_pairing_address.place_forget()
    address_box_pairing_port.place_forget()
    pin_box_pairing.place_forget()
    if not WIRELESS_QR_PAIRING_STATE:
        bonjour_install_btn.place(x=window_size[0]/4,y=window_size[1]/1.2)
    address_box_pairing_address.delete(0,END)

def wireless_pairing():
    global CURRENT_MENU
    # CURRENT_MENU = "QR_CODE_PAIRING_MENU"
    wireless_pairing_btn.configure(command=lambda: ...)
    QR_pair_menu()
    placements = list(range(window_size[0]*-1,0+1))
    for i in placements:
        wireless_pairing_frame.place(x=i,y=0)
        time.sleep(0.00_00_08)
        if i % 10 ==0:
            wireless_pairing_frame.update()
    main_page.pack_forget()
    if WIRELESS_QR_PAIRING_STATE:
        kill_bonjour_service()
        start_bonjour_service()
        global pairing_service, PAIRING_SERVICE_INITIALIZED
        PAIRING_SERVICE_INITIALIZED = True
        pairer = Pairer()
        pairing_service = ServiceBrowser(zeroconf,"_adb-tls-pairing._tcp.local.",pairer)

def back_btn_wireless_pairing():
    global CURRENT_MENU, CONNECTION_SERVICE_INITIALIZED, PAIRING_SERVICE_INITIALIZED
    CURRENT_MENU = "Main_Menu"
    if WIRELESS_QR_PAIRING_STATE:
        if PAIRING_SERVICE_INITIALIZED:
            PAIRING_SERVICE_INITIALIZED = False
            try:
                pairing_service.cancel()
            except RuntimeError:
                pass
            except KeyError:
                pass
        if CONNECTION_SERVICE_INITIALIZED:
            CONNECTION_SERVICE_INITIALIZED = False
            try:
                connecter_service.cancel()
            except RuntimeError:
                pass
            except NameError:
                pass
            except KeyError:
                pass
    main_page.pack()
    placements = list(range(window_size[0]*-1,0+1))
    placements.reverse()
    for i in placements:
        wireless_pairing_frame.place(x=i,y=0)
        time.sleep(0.00_00_08)
        if i % 10 ==0:
            wireless_pairing_frame.update()
    PIN_devices_label.place_forget()
    wireless_pairing_frame.place_forget()
    wireless_pairing_btn.configure(command=wireless_pairing)

def ask_4_exit(event):
    if messagebox.askyesno("Exiting", message="Do you wish to exit?"):
        exiting()

def keep_flat(event:Event):
    if any(event.widget is btn for btn in (screen_share_scrcpy_btn,wireless_tcpip_btn,shell_btn,wireless_pairing_btn,file_download_btn,file_upload_btn,file_downloading_btn,kill_btn,background_color_btn,devices_refresh_btn,unauthorized_noti_btn,offline_noti_btn,permission_error_btn,running_with_errors_btn,settings_btn,preferred_interface_info_btn,pairing_info_btn,settings_back_btn,wireless_back_btn,network_refresh_btn)):
        event.widget.configure(relief="flat")
    elif any(event.widget is btn for btn in (PIN_pair_option_btn,QR_pair_option_btn,connect_pairing_btn)):
        event.widget.configure(relief="raised")
    

def not_implemented_message():
    messagebox.showinfo("Under Development",message="Under Development")

def hover_highlight(event :Event):
    event.widget.configure(background="#333333")


def hover_unhighlight(event :Event):
    event.widget.configure(background="#1f1f1f")

def recheck_network_adapters():
    network_check()
    txt_width = round(window_size[0]*0.11)
    preferred_adapter.set(attached_adapters[-1])
    menu = adapters_list_option['menu']
    menu.delete(0, "end")
    for string in attached_adapters:
        string = f"•  {string:<{txt_width}}"
        menu.add_command(label=string, command=lambda value=string: preferred_adapter.set(value))
    settings_back_btn.configure(state="normal")
    adapters_list_option.configure(state='normal')
    network_refresh_btn.configure(state="normal")

def create_bonjour_kill_service(restart=False):
    global WIRELESS_QR_PAIRING_STATE
    task_query = subprocess.run(['schtasks',"/query","/tn",'ScreenDroid_BONJOUR_SERVICE_KILLER','/FO','LIST'],shell=True,capture_output=True)
    if "ERROR: The system cannot find the file specified." in task_query.stderr.decode():
        with open(VBS_KILL_PATH,'w') as file:
            file.write(VBS_CONTENT_KILL)
        task_creation = subprocess.run(["powershell","-NoLogo","-WindowStyle","hidden","-Command","Start-Process","-FilePath","schtasks","-ArgumentList",rf'''"/Create", "/F", "/RL", "HIGHEST", "/TN", "ScreenDroid_BONJOUR_SERVICE_KILLER","/TR", '"wscript {VBS_KILL_PATH}"', "/SC", "ONCE", "/ST", "00:00", "/SD", "01/01/2015"''',"-Verb","RunAs",],shell=True,capture_output=True)
        if task_creation.returncode != 0:
            messagebox.showerror("Failed to create scheduled task",message=task_creation.stderr.decode())
            WIRELESS_QR_PAIRING_STATE = False
            wireless_pairing_btn.configure(state='disabled')
    else:
        if not os.path.exists(VBS_KILL_PATH):
            with open(VBS_KILL_PATH,'ab+') as file:
                if hashlib.file_digest(file,'md5').digest() != VBS_MD5_HASH_KILL:
                    file.truncate(0)
                    file.seek(0)
                    file.write(VBS_CONTENT_KILL.encode('utf-8'))
    if restart:
        kill_bonjour_service()


def create_bonjour_start_service():
    global WIRELESS_QR_PAIRING_STATE
    task_query = subprocess.run(['schtasks',"/query","/tn",'ScreenDroid_BONJOUR_SERVICE_STARTER','/FO','LIST'],shell=True,capture_output=True)
    if "ERROR: The system cannot find the file specified." in task_query.stderr.decode():
        with open(VBS_START_PATH,'w') as file:
            file.write(VBS_CONTENT_START)
        task_creation = subprocess.run(["powershell","-NoLogo","-WindowStyle","hidden","-Command","Start-Process","-FilePath","schtasks","-ArgumentList",rf'''"/Create", "/F", "/RL", "HIGHEST", "/TN", "ScreenDroid_BONJOUR_SERVICE_STARTER","/TR", '"wscript {VBS_START_PATH}"', "/SC", "ONCE", "/ST", "00:00", "/SD", "01/01/2015"''',"-Verb","RunAs",],shell=True,capture_output=True)
        if task_creation.returncode != 0:
            messagebox.showerror("Failed to create scheduled task",message=task_creation.stderr.decode())
            WIRELESS_QR_PAIRING_STATE = False
            wireless_pairing_btn.configure(state='disabled')
    else:
        if not os.path.exists(VBS_START_PATH):
            with open(VBS_START_PATH,'ab+') as file:
                if hashlib.file_digest(file,'md5').digest() != VBS_MD5_HASH_START:
                    file.truncate(0)
                    file.seek(0)
                    file.write(VBS_CONTENT_START.encode('utf-8'))

def install_bonjour():
    PIN_pair_option_btn.configure(state='disabled')
    bonjour_install_btn.configure(state='disabled')
    wireless_back_btn.configure(state='disabled')
    command = '''msiexec /i "Bonjour64.msi" /passive /log bonjour-install.log'''
    proc = subprocess.run(command,shell=True,capture_output=True)
    if proc.returncode == 0:
        create_bonjour_kill_service()
        create_bonjour_start_service()
        messagebox.showinfo("Installation Successful", "The new service has been installed successfully. Please restart ScreenDroid to activate the changes.")
    elif proc.returncode == 1602:
        messagebox.showinfo("Installtion Failure",f"User cancelled installation")
        bonjour_install_btn.configure(state='normal')
        wireless_back_btn.configure(state='normal')
        PIN_pair_option_btn.configure(state='normal')
    elif proc.returncode == 1619:
        messagebox.showinfo("Installtion Failure",f"The installation package could not be opened")
        bonjour_install_btn.configure(state='normal')
        wireless_back_btn.configure(state='normal')
        PIN_pair_option_btn.configure(state='normal')
    else:
        messagebox.showinfo("Installtion Failure",f"Failed to install\nMSI installation error code : {proc.returncode}")
        bonjour_install_btn.configure(state='normal')
        wireless_back_btn.configure(state='normal')
        PIN_pair_option_btn.configure(state='normal')

def bonjour_service_check():
    global WIRELESS_QR_PAIRING_STATE
    result = subprocess.run(["reg","query",r"HKLM\SOFTWARE\WOW6432Node\Apple Inc.\Bonjour"],shell=True,capture_output=True)
    if "ERROR: The system was unable to find the specified registry key or value." in result.stderr.decode():
        image_assign(QR_code_label,disabled_qr_code_svg,window_size[0]/1.6)
        bonjour_install_btn.place(x=100,y=500)
    else:
        threading.Thread(target=create_bonjour_kill_service,args=(True,),daemon=True).start()
        threading.Thread(target=create_bonjour_start_service,daemon=True).start()
        threading.Thread(target=qr_code_generator,daemon=True).start()
        WIRELESS_QR_PAIRING_STATE = True

def kill_bonjour_service():
    if subprocess.run(['schtasks','/run','/tn','ScreenDroid_BONJOUR_SERVICE_KILLER'],shell=True,capture_output=True).returncode ==1:
        create_bonjour_kill_service(restart=True)

def start_bonjour_service():
    if subprocess.run(['schtasks','/run','/tn','ScreenDroid_BONJOUR_SERVICE_STARTER'],shell=True,capture_output=True).returncode ==1:
        create_bonjour_start_service()
    
def qr_code_generator():
    data = f"WIFI:T:ADB;S:{WIFI_PAIRING_SSID};P:{WIFI_PAIRING_PASSWORD};;"
    qr = qrcode.QRCode(version=1,error_correction=qrcode.constants.ERROR_CORRECT_H,box_size=100,border=2)
    qr.add_data(data)
    qr.make(fit=True)
    qr_image = qr.make_image(fill_color="black", back_color="white")
    icon_image = Image.open("qrcode_icon.png").convert("RGBA")
    icon_size = min(qr_image.size) // 5
    icon_image = icon_image.resize((icon_size, icon_size), Image.Resampling.LANCZOS)
    icon_position = ((qr_image.size[0] - icon_image.size[0]) // 2, (qr_image.size[1] - icon_image.size[1]) // 2)
    qr_image.paste(icon_image, icon_position, icon_image)
    qr_image.save("qrcode.png")
    qrcode_image = ImageTk.PhotoImage(Image.open(r"qrcode.png").resize((250,250),Image.Resampling.LANCZOS))
    QR_code_label.configure(image=qrcode_image)
    QR_code_label.image = qrcode_image 
    
def exiting():
    for index,value in enumerate(Active_Routes):
        for device_id in value.keys():
            try:
                subprocess.run(value[device_id].split(" "),shell=True,capture_output=True)
            except KeyError:
                pass
    main_window.destroy()
    subprocess.run(["adb", "kill-server"], shell=True, capture_output=True)
    os.kill(os.getpid(),9)


def startup_check():
    global STARTUP_CHECK, vid_playback_startup
    main_window.update()
    threading.Thread(target=vid_playback_4_startup,daemon=True).start()
    bonjour_thread = threading.Thread(target=bonjour_service_check,daemon=True)
    network_thread = threading.Thread(target=recheck_network_adapters,daemon=True)
    adb_thread = threading.Thread(target=re_checkup,daemon=True)
    bonjour_thread.start()
    network_thread.start()
    adb_thread.start()
    for function_button,function_svg in primary_button_svg:
        threading.Thread(target=image_assign,args=(function_button,function_svg,48),daemon=True).start()
    for function_button,function_svg in secondary_button_svg:
        threading.Thread(target=image_assign,args=(function_button,function_svg,36),daemon=True).start()
    threading.Thread(target=PIN_IP_label_image_assign,args=(400,600),daemon=True).start()
    network_thread.join()
    adb_thread.join()
    bonjour_thread.join()
    STARTUP_CHECK = True
    vid_playback_startup = False

def auto_refresh_checkup():
    global RESTART_TIMER, STARTUP_CHECK, adapters_list_option
    if STARTUP_CHECK == None:
        startup_check()
    while True:
        for i in time_list:
            if not RESTART_TIMER:
                auto_refresh.configure(text=str(i))
                time.sleep(1)
                if i == 0:
                    re_checkup()
            else:
                RESTART_TIMER = False
                break


def add_task_with_pid_scrcpy(window_name, device_id,scrcpy: subprocess.Popen, current_selection):
    time.sleep(0.5)
    filter_id = f"WINDOWTITLE eq {window_name}*"
    global count_task_pid
    count_task_pid = 0
    def rerun():
        time.sleep(0.5)
        global count_task_pid
        add_task_pid = subprocess.run(["tasklist", "/fi", filter_id, "/fo", "list"],shell=True,capture_output=True,).stdout.decode()
        if "No tasks are running" not in add_task_pid: 
            add_task_pid = add_task_pid.splitlines()
            for i in add_task_pid:
                if "PID:" in i:
                    i = i.removeprefix("PID:").strip(" ")
                    Running_tasks_pid[device_id] = i
        else:
            if scrcpy.returncode == 0 or scrcpy.returncode == None:
                if count_task_pid == 20:
                    if (
                        messagebox.askyesno("Timeout Error",message="10 seconds has passed and the task still doesn't exist. Do you wish to terminate all running and queued tasks? ",)
                        == True
                    ):
                        kill_process()
                        for index,value in enumerate(Active_Routes):
                            try:
                                subprocess.run(value[device_id].split(" "),shell=True,capture_output=True)
                                Active_Routes.pop(index)
                                break
                            except KeyError:
                                pass
                    else:
                        messagebox.showwarning("Warning",message="Unexpected Errors May Occur")
                        running_with_errors_btn.place(x=166,y=40)
                else:
                    count_task_pid += 1
                    rerun()
            elif scrcpy.returncode == 1:
                messagebox.showerror("Unsupported Device",message=f"{current_selection} may not support screen sharing\nError: {scrcpy.stderr.decode()}")
    rerun()
    re_checkup()


def wait_until_disconnect(device_id,addr,window_name,port,adb_tcpip_out,adb_connect_out,vid_label_wireless : Frame,current_selection):
    global vid_playback_wireless
    if "invalid" not in adb_tcpip_out.stdout.decode():
        if "connected" in adb_connect_out.stdout.decode():
            def rereun():
                global vid_playback_wireless
                check_4_device_battery = subprocess.run(["adb", "-s", addr, "shell", "dumpsys", "battery"],shell=True,capture_output=True,).stdout.decode()
                if (
                    "USB powered: true" in check_4_device_battery
                    or "AC powered: true" in check_4_device_battery
                ):
                    time.sleep(0.5)
                    rereun()
                else:
                    vid_playback_wireless = False
                    #main_page.pack()
                    vid_label_wireless.pack_forget()
            rereun()
        else:
            vid_playback_wireless = False
            #main_page.pack()
            vid_label_wireless.pack_forget()
            messagebox.showerror("Connection Error", message=f"Couldn't connect to {addr}")
    else:
        vid_playback_wireless = False
        vid_label_wireless.pack_forget()
        messagebox.showerror("Port Error", message=f"An error occured\nPort: {port}")


def all_btn_activity(state,list_selection=False):
    if state == "normal":
        if WIRELESS_BUTTON_NETWORK_STATE:
            wireless_tcpip_btn.configure(state=state)
            wireless_pairing_btn.configure(state=state)
        if not list_selection:
            settings_btn.configure(state=state)
            background_color_btn.configure(state=state)
            devices_refresh_btn.configure(state=state)
            kill_btn.configure(state=state)
        screen_share_scrcpy_btn.configure(state=state)
        file_downloading_btn.configure(state=state)
        file_download_btn.configure(state=state)
        file_upload_btn.configure(state=state)
        shell_btn.configure(state=state)
        file_upload_btn.update()
    elif state == "disabled":
        if WIRELESS_BUTTON_NETWORK_STATE:
            wireless_tcpip_btn.configure(state=state)
            wireless_pairing_btn.configure(state=state)
        if not list_selection:
            settings_btn.configure(state=state)
            background_color_btn.configure(state=state)
            devices_refresh_btn.configure(state=state)
            kill_btn.configure(state=state)
        screen_share_scrcpy_btn.configure(state=state)
        file_downloading_btn.configure(state=state)
        file_download_btn.configure(state=state)
        file_upload_btn.configure(state=state)
        shell_btn.configure(state=state)
        file_upload_btn.update()

def all_btn_command(state):
    if state:
        unauthorized_noti_btn.config(command=unauthorized_message)
        offline_noti_btn.config(command=offline_message)
        permission_error_btn.config(command=unauthorized_message)
        running_with_errors_btn.config(command=running_errors_message)
        wireless_tcpip_btn.config(command=wireless_connection_setup)
        settings_back_btn.config(command=lambda:threading.Thread(target=back_btn_settings,daemon=True).start())
        network_refresh_btn.config(command=network_refresh)
        preferred_interface_info_btn.config(command=show_info)
        pairing_info_btn.config(command=show_disclaimer)
        wireless_back_btn.config(command=back_btn_wireless_pairing)
        QR_pair_option_btn.config(command=QR_pair_menu)
        PIN_pair_option_btn.config(command=PIN_pair_menu)
        bonjour_install_btn.config(command=lambda: threading.Thread(target=install_bonjour).start())
        settings_btn.config(command=lambda:threading.Thread(target=open_settings,daemon=True).start())
        background_color_btn.config(command=change_bg)
        devices_refresh_btn.config(command=lambda : threading.Thread(target=re_checkup,daemon=True).start())
        kill_btn.config(command=lambda:threading.Thread(target=kill_process,daemon=True).start())
        wireless_pairing_btn.config(command=wireless_pairing)
        screen_share_scrcpy_btn.config(command=screen_share_scrcpy)
        file_downloading_btn.config(command=not_implemented_message)
        file_download_btn.config(command=not_implemented_message)
        file_upload_btn.config(command=not_implemented_message)
        shell_btn.config(command=not_implemented_message)
        shell_btn.update()
    else:
        unauthorized_noti_btn.config(command=lambda: ...)
        offline_noti_btn.config(command=lambda: ...)
        permission_error_btn.config(command=lambda: ...)
        running_with_errors_btn.config(command=lambda: ...)
        wireless_tcpip_btn.config(command=lambda: ...)
        settings_back_btn.config(command=lambda: ...)
        network_refresh_btn.config(command=lambda: ...)
        preferred_interface_info_btn.config(command=lambda: ...)
        pairing_info_btn.config(command=lambda: ...)
        wireless_back_btn.config(command=lambda: ...)
        QR_pair_option_btn.config(command=lambda: ...)
        PIN_pair_option_btn.config(command=lambda: ...)
        bonjour_install_btn.config(command=lambda: ...)
        settings_btn.config(command=lambda: ...)
        background_color_btn.config(command=lambda: ...)
        devices_refresh_btn.config(command=lambda: ...)
        kill_btn.config(command=lambda: ...)
        wireless_pairing_btn.config(command=lambda: ...)
        screen_share_scrcpy_btn.config(command=lambda: ...)
        file_downloading_btn.config(command=lambda: ...)
        file_download_btn.config(command=lambda: ...)
        file_upload_btn.config(command=lambda: ...)
        shell_btn.config(command=lambda: ...)
        shell_btn.update()


def kill_process():
    global Running_tasks_pid, kill_process_running
    if not kill_process_running:
        kill_process_running = True
        all_btn_activity("disabled")
        all_btn_command(False)
        running_with_errors_btn.place_forget()
        subprocess.run(["adb", "kill-server"], shell=True, capture_output=True)
        subprocess.run(["adb", "start-server"], shell=True, capture_output=True)
        Running_tasks_pid = {}
        re_checkup()
        kill_process_running = False


def wireless_connection_setup_handle(IPv4_gate,Interface_subnet,current_selection,device_id,path_vid,window_name,phone_ip,ping_check):
    global vid_playback_wireless

    if (phone_ip_validation_result := ip_validation(IPv4_gate,Interface_subnet, phone_ip)) and ping_check.returncode == 0:
        port = str(random.randint(5555, 10000))
        addr = f"{phone_ip}:{port}"
        adb_tcpip_out = subprocess.run(["adb", "-s", device_id, "tcpip", port],shell=True,capture_output=True,)
        adb_connect_out = subprocess.run(["adb", "connect", addr],shell=True,capture_output=True,)
        vid_label_wireless.pack()
        vid_label_wireless.wait_visibility()
        vid_playback_wireless = True
        threading.Thread(target=vid_playback_4_wireless,daemon=True,args=(path_vid,),).start()
        threading.Thread(target=wait_until_disconnect,args=(device_id,addr,window_name,port,adb_tcpip_out,adb_connect_out,vid_label_wireless,current_selection),daemon=True).start()
    else:
        if not phone_ip_validation_result:
            messagebox.showerror("Network Error",message=f"{phone_ip} is connected to a different network")
        elif ping_check.returncode != 0:
            messagebox.showerror("Network Error",message=f"{phone_ip} didn't respond to a ping")
        else:
            messagebox.showerror("Network Error",message=f"{phone_ip} Unknow error occured\n{ping_check}")

def route_n_ping(Route_Traffic,phone_ip,IPv4_gate,Interface_Index,device_id):
    if Route_Traffic:
        routing_traffic = subprocess.run(["route","add", phone_ip, "MASK", "255.255.255.255", IPv4_gate, "IF", Interface_Index],shell=True,capture_output=True)
        if routing_traffic.returncode == 0 :
            if device_id is not None:
                Active_Routes.append({device_id:f"route delete {phone_ip}"})
        else:
            return (routing_traffic.stderr,"ROUTE_FAILED")

    if network_ping_check_state_int.get() == 1:
        class Ping_Check:
            pass
        ping_check = Ping_Check()
        ping_check.returncode = 0
        return (ping_check,"ROUTE_SUCCESS")
    else:
        ping_check = subprocess.run(["ping", phone_ip, "-n", "1"],shell=True,stderr=subprocess.PIPE,stdout=subprocess.PIPE,)
        return (ping_check,"ROUTE_SUCCESS")

def ip_validation(default_gateway,subnet_mask, phone_ip : str):
    if ip_validation_check_state_int.get() == 1:
        return True
    network = ipaddress.IPv4Network(f"{default_gateway}/{subnet_mask}", strict=False)
    network_address = str(network.network_address)
    broadcast_address = str(network.broadcast_address)
    splitting_count = subnet_mask.split(".").count("255")
    network_address = network_address.split(".")
    network_address.reverse()
    broadcast_address = broadcast_address.split(".")
    broadcast_address.reverse()
    phone_ip = phone_ip.split(".")
    phone_ip.reverse()
    for i in range(splitting_count):
        network_address.pop(-1)
        phone_ip.pop(-1)
        broadcast_address.pop(-1)
    broadcast_address.reverse()
    phone_ip.reverse()
    network_address.reverse()
    for i in range(4-splitting_count):
        execute = int(network_address[i]) <= int(phone_ip[i]) <= int(broadcast_address[i])
        if not execute:
            return False
    else:
        return True

def wireless_connection_setup():
    all_btn_activity("disabled")
    all_btn_command(False)
    try:
        preferred_interface = preferred_adapter.get()
        for key,value in network_devices_info.items():
            if value[1] == preferred_interface:
                Interface_MAC,IPv4_gate,Interface_subnet,Interface_Index = value[0],value[2],value[3],value[4]
                break
        if len(attached_adapters) > 1:
            Route_Traffic = True
        else:
            Route_Traffic = False
        current_selection = devices_list.get(devices_list.curselection())
        for index, i in enumerate(devices.values()):
            if i[0] == current_selection:
                device_id = list(devices.keys())[index]
        window_name = f"{current_selection} {device_id}"
        phone_ip = subprocess.run(["adb", "-s", device_id, "shell", "ifconfig", "wlan0"],shell=True,capture_output=True,).stdout.decode()
        global bg_color_main, vid_playback_wireless
        if bg_color_main == "#1f1f1f":
            path_vid = r"vids\\White_phone_disconnect_v1.0.mp4"
        elif bg_color_main == "#e0e0e0":
            path_vid = r"vids\\Black_phone_disconnect_V3.1.mp4"
        if len(phone_ip) == 0:
            messagebox.showerror("USB Connection Error",message=f"{current_selection} isn't connected via a USB cable",)
            threading.Thread(target=re_checkup,daemon=True).start()
        elif "inet addr:" not in phone_ip:
            messagebox.showerror("Network Error",message=f"{current_selection} isn't connected to a network",)
        else:
            raw_full_addr = phone_ip.splitlines()[1]
            raw_full_addr = raw_full_addr.removeprefix("          inet addr:")
            raw_full_addr = raw_full_addr.split(" ")
            phone_ip = raw_full_addr[0]
            if len(Active_Routes) != 0:
                for index,value in enumerate(Active_Routes):
                    try:
                        subprocess.run(value[device_id].split(" "),shell=True,capture_output=True)
                        Active_Routes.pop(index)
                        break
                    except KeyError:
                        pass
            if bool(Running_tasks_pid) != False:
                try:
                    pid = Running_tasks_pid[device_id]
                    filter_id = f"PID eq {pid}"
                    check_task_pid = subprocess.run(["tasklist", "/fi", filter_id, "/fo", "list"],shell=True,capture_output=True,).stdout.decode()
                    if "No tasks are running" in check_task_pid:
                        ping_check, route_status = route_n_ping(Route_Traffic,phone_ip,IPv4_gate,Interface_Index,device_id)
                        if ping_check and route_status == "ROUTE_SUCCESS":
                            wireless_connection_setup_handle(IPv4_gate,Interface_subnet,current_selection,device_id,path_vid,window_name,phone_ip,ping_check)
                        else:
                            messagebox.showerror("Insuffeicient Permissions",message=f"Admin privilege is required to route traffic to the preferred network adapter",)
                    else:
                        messagebox.showerror("Screen Share Error", message="Task already exists")
                except KeyError:
                    ping_check, route_status = route_n_ping(Route_Traffic,phone_ip,IPv4_gate,Interface_Index,device_id)
                    if ping_check and route_status == "ROUTE_SUCCESS":
                        wireless_connection_setup_handle(IPv4_gate,Interface_subnet,current_selection,device_id,path_vid,window_name,phone_ip,ping_check)
                    else:
                        messagebox.showerror("Insuffeicient Permissions",message=f"Admin privilege is required to route traffic to the preferred network adapter",)
            else:
                ping_check, route_status = route_n_ping(Route_Traffic,phone_ip,IPv4_gate,Interface_Index,device_id)
                if ping_check and route_status == "ROUTE_SUCCESS":
                    wireless_connection_setup_handle(IPv4_gate,Interface_subnet,current_selection,device_id,path_vid,window_name,phone_ip,ping_check)
                else:
                    messagebox.showerror("Insuffeicient Permissions",message=f"Admin privilege is required to route traffic to the preferred network adapter",)
    except TclError:
        pass
    threading.Thread(target=re_checkup,daemon=True).start()


def screen_share_scrcpy_handle(window_name, device_id, current_selection):
    if device_screen_state_int.get() == 1:
        scrcpy = subprocess.Popen(["scrcpy", "--window-title", window_name, "--serial", device_id,"--turn-screen-off"],shell=True,stderr=subprocess.PIPE,stdout=subprocess.PIPE,)
    else:
        scrcpy = subprocess.Popen(["scrcpy", "--window-title", window_name, "--serial", device_id,],shell=True,stderr=subprocess.PIPE,stdout=subprocess.PIPE,)    
    threading.Thread(target=add_task_with_pid_scrcpy,args=(window_name, device_id, scrcpy,current_selection),daemon=True,).start()


def screen_share_scrcpy():
    all_btn_activity("disabled")
    all_btn_command(False)
    try:
        current_selection = devices_list.get(devices_list.curselection())
        for index, i in enumerate(devices.values()):
            if i[0] == current_selection:
                device_id = list(devices.keys())[index]
        window_name = f"{current_selection} {device_id}"
        if bool(Running_tasks_pid) != False:
            try:
                pid = Running_tasks_pid[device_id]
                filter_id = f"PID eq {pid}"
                check_task_pid = subprocess.run(["tasklist", "/fi", filter_id, "/fo", "list"],shell=True,capture_output=True,).stdout.decode()
                if "No tasks are running" in check_task_pid:
                    screen_share_scrcpy_handle(window_name, device_id, current_selection)
                else:
                    messagebox.showerror("Screen Share Error", message="Task already exists")
                    threading.Thread(target=re_checkup,daemon=True).start()
            except KeyError:
                screen_share_scrcpy_handle(window_name, device_id , current_selection)
        else:
            screen_share_scrcpy_handle(window_name, device_id, current_selection)
    except TclError:
        threading.Thread(target=re_checkup,daemon=True).start()


def file_download():
    raise NotImplementedError
    all_btn_activity("disabled")
    try:
        current_selection = devices_list.get(devices_list.curselection())
        for index, i in enumerate(devices.values()):
            if i[0] == current_selection:
                device_id = list(devices.keys())[index]
        window_name = f"{current_selection} {device_id}"
        if bool(Running_tasks_pid) != False:
            try:
                pid = Running_tasks_pid[device_id]
                filter_id = f"PID eq {pid}"
                check_task_pid = subprocess.run(
                    ["tasklist", "/fi", filter_id, "/fo", "list"],
                    shell=True,
                    capture_output=True,
                ).stdout.decode()
                if "No tasks are running" in check_task_pid:
                    # code without checking for task
                    pass
                else:
                    messagebox.showerror(
                        "Multiple Tasks Requested",
                        message="Another Task Already Exist",
                    )
                    all_btn_activity("normal")
            except:
                # code without checking for task
                pass
        else:
            # code without checking for task
            pass
    except:
        all_btn_activity("normal")


def file_upload():
    raise NotImplementedError


def open_shell_handle(device_id, current_selection):
    raise NotImplementedError
    shell_proc = subprocess.Popen(["start","cmd","/c",f"adb -s {device_id} shell"],shell=True,stderr=subprocess.PIPE,stdout=subprocess.PIPE)   
    print(shell_proc.pid)
    #add task to PID


def open_shell():
    raise NotImplementedError
    all_btn_activity("disabled")
    try:
        current_selection = devices_list.get(devices_list.curselection())
        for index, i in enumerate(devices.values()):
            if i[0] == current_selection:
                device_id = list(devices.keys())[index]
        if bool(Running_tasks_pid) != False:
            try:
                pid = Running_tasks_pid[device_id]
                filter_id = f"PID eq {pid}"
                check_task_pid = subprocess.run(["tasklist", "/fi", filter_id, "/fo", "list"],shell=True,capture_output=True,).stdout.decode()
                if "No tasks are running" in check_task_pid:
                    open_shell_handle(device_id, current_selection)
                else:
                    messagebox.showerror("Error", message="Another task is running.")
                    threading.Thread(target=re_checkup,daemon=True).start()
            except KeyError:
                open_shell_handle(device_id , current_selection)
        else:
            open_shell_handle(device_id, current_selection)
    except TclError:
        threading.Thread(target=re_checkup,daemon=True).start()




def repeat_until_success(index, i, connected_devices_vals, n):
    i = f"{i} {n}"
    if i in connected_devices_vals:
        i = i.removesuffix(f" {n}")
        n += 1
        repeat_until_success(index, i, connected_devices_vals, n)
    else:
        connected_devices_vals[index] = i

def find_duplicates(serial_number_duplicate_devices):
    counter = Counter(serial_number_duplicate_devices)
    duplicates = [value for value, count in counter.items() if count > 1]
    return duplicates


def checkup():
    global UNAUTHORIZED_BUTTON_PLACEMENT,OFFLINE_BUTTON_PLACEMENT, PERMISSION_ERROR_PLACEMENT
    connected_devices = dict()
    serial_number_running_tasks = list()
    serial_number_duplicate_devices = list()
    try:
        connection_type = preferred_interface_opt.get()
    except TclError:
        preferred_interface_opt.set("Any")
        connection_type = "Any"
    attached = subprocess.run(["adb", "devices"], shell=True, capture_output=True).stdout.decode().splitlines()[1:]
    for i in attached:
        if len(i) != 0:
            try:
                i = i.split("\t")
                device_id = i[0]
                device_state = i[1]
            except IndexError:
                continue
            if "._adb-tls-connect._tcp." in device_id:
                subprocess.run(["adb","disconnect",device_id],shell=True,capture_output=True)
                continue
            if device_state == "device":
                device_name = subprocess.run(["adb","-s",device_id,"shell","getprop","ro.product.model",],shell=True,capture_output=True)
                serial_number = subprocess.run(["adb","-s",device_id,"shell","getprop","ro.serialno",],shell=True,capture_output=True)
                if "Permission denied" in device_name.stderr.decode():
                    device_name = f"Permission Error {device_id}"
                else:
                    device_name = device_name.stdout.decode().removesuffix("\r\n")
                    if ":" in device_id:
                        device_name += ' Wireless'
                if "Permission denied" in serial_number.stderr.decode():
                    serial_number = f"Permission Error {device_id}"
                else:
                    serial_number = serial_number.stdout.decode().removesuffix('\r\n')
                    serial_number_duplicate_devices.append(serial_number)
                if bool(Running_tasks_pid):
                    try:
                        pid = Running_tasks_pid[device_id]
                        filter_id = f"PID eq {pid}"
                        check_task_pid = subprocess.run(["tasklist", "/fi", filter_id, "/fo", "list"],shell=True,capture_output=True,).stdout.decode()
                    except KeyError:
                        check_task_pid = "No tasks are running"
                    if "No tasks are running" not in check_task_pid:
                        device_name += ' (Task Running)'
                        serial_number_running_tasks.append(serial_number)
                connected_devices[device_id] = (device_name,serial_number)
            elif device_state == "unauthorized":
                connected_devices[device_id] = (f"Unauthorized","Unauthorized")
            elif device_state == "offline":
                connected_devices[device_id] = (f"Offline","Offline")
    for i in serial_number_running_tasks:
        for dev_id,dev_name_serial in connected_devices.items():
            dev_name,dev_serial = dev_name_serial
            if i == dev_serial and " (Task Running)" not in dev_name and not any(error in dev_name for error in ["Permission Error","Unauthorized","Offline"]):
                dev_name += ' (Task Running)'
                connected_devices[dev_id] = (dev_name,dev_serial)
    if connection_type != "Any":
        serial_number_duplicate_devices = find_duplicates(serial_number_duplicate_devices)
        devices_id_duplicates = list()
        for i in serial_number_duplicate_devices:
            for dev_id, dev_name_serial in connected_devices.items():
                if dev_name_serial[1] == i:
                    devices_id_duplicates.append((dev_id,dev_name_serial[0],dev_name_serial[1]))
        for dev_id,dev_name,dev_serial in devices_id_duplicates:
            if connection_type == "Wireless":
                if "Wireless" not in dev_name:
                    connected_devices.pop(dev_id)
            elif connection_type == "Wired":
                if "Wireless" in dev_name:
                    subprocess.run(["adb","disconnect",dev_id],shell=True,capture_output=True)
                    connected_devices.pop(dev_id)
    connected_devices_vals = list(connected_devices.values())
    for index, i in enumerate(connected_devices_vals):
        if connected_devices_vals.count(i[0]) > 1:
            n = 1
            repeat_until_success(index, i[0], connected_devices_vals, n)
    connected_devices = dict(zip(connected_devices.keys(), connected_devices_vals))
    for i, serial in sorted(connected_devices.values()):
        if "Unauthorized" in i:
            unauthorized_noti_btn.place(x=window_size[0]*0.825, y=window_size[1]*0.4)
            UNAUTHORIZED_BUTTON_PLACEMENT = True
        elif "Offline" in i:
            offline_noti_btn.place(x=window_size[0]*0.825, y=window_size[1]*(29/60))
            OFFLINE_BUTTON_PLACEMENT = True
        elif "Permission Error" in i:
            permission_error_btn.place(x=window_size[0]*0.825, y=window_size[1]*(17/30))
            PERMISSION_ERROR_PLACEMENT = True
        else:
            devices_list.insert(END, i)
    for i in range(devices_list.size()):
        if i % 2 == 0:
            devices_list.itemconfigure(i, bg="#1a8cff")
        else:
            devices_list.itemconfigure(i, bg="#ffff00")
    return connected_devices

def re_checkup():
    global devices, RESTART_TIMER, OFFLINE_BUTTON_PLACEMENT, UNAUTHORIZED_BUTTON_PLACEMENT, PERMISSION_ERROR_PLACEMENT, re_checkup_running
    if not re_checkup_running:
        re_checkup_running = True
        all_btn_command(False)
        all_btn_activity("disabled")
        UNAUTHORIZED_BUTTON_PLACEMENT = OFFLINE_BUTTON_PLACEMENT = PERMISSION_ERROR_PLACEMENT =  False
        unauthorized_noti_btn.place_forget()
        offline_noti_btn.place_forget()
        devices_list.delete(0, END)
        RESTART_TIMER = True
        devices = checkup()
        all_btn_activity("normal")
        all_btn_command(True)
        re_checkup_running = False

def change_bg():
    return
    global bg_color_main
    if bg_color_main == "#1f1f1f":
        bg_color_main = "#e0e0e0"
        current_mode_svg = light_mode_svg
    elif bg_color_main == "#e0e0e0":
        bg_color_main = "#1f1f1f"
        current_mode_svg = dark_mode_svg
    png_bytes = cairosvg.svg2png(bytestring=current_mode_svg, output_width=secondary_icon_size, output_height=secondary_icon_size)
    new_btn_image = ImageTk.PhotoImage(Image.open(BytesIO(png_bytes)))
    background_color_btn.image = new_btn_image
    background_color_btn.configure(width=secondary_icon_size,height=secondary_icon_size,image=new_btn_image)
    for i in [main_page,wireless_pairing_frame,settings_frame]:
        i.configure(background=bg_color_main)

def unauthorized_message():
    Unauthorized_list = []
    for key,value in devices.items():
        if "Unauthorized" in value:
            Unauthorized_list.append(key)
    if len(Unauthorized_list) > 1:
        Unauthorized_devices = "\n".join(Unauthorized_devices)
        messagebox.showinfo(f"Unauthorized Devices Detected",message=f"1.) Enable USB Debugging\n2.) Authorize this computer\nThe following devices are unauthorized:\n{Unauthorized_devices}")
    else:
        Unauthorized_devices = Unauthorized_devices[0]
        messagebox.showinfo(f"Unauthorized Device Detected",message=f"1.) Enable USB Debugging\n2.) Authorize this computer\nThe following fevice is unauthorized:\n{Unauthorized_devices}")

def permission_message():
    permission_list = []
    for key,value in devices.items():
        if "Permission Error" in value:
            permission_list.append(key)
    if len(permission_list) > 1:
        permission_devices = "\n".join(permission_list)
        messagebox.showinfo("Permission Issue Detected",f"Your devices lacks the necessary permissions for this operation.\n\nPlease follow these steps to resolve the issue:\n\n1.) Go to 'Rooted Debugging' or 'Root Access Options'.\n2.) Change the setting to 'ADB only' or grant ADB root access through your root manager.\n3.) It may be necessary to reboot your devices.\n\nDevices with Insufficient Permissions:\n{permission_devices}")
    else:
        permission_devices = permission_list[0]
        messagebox.showinfo("Permission Issue Detected",f"Your device lacks the necessary permissions for this operation.\n\nPlease follow these steps to resolve the issue:\n\n1.) Go to 'Rooted Debugging' or 'Root Access Options'.\n2.) Change the setting to 'ADB only' or grant ADB root access through your root manager.\n3.) It may be necessary to reboot your device.\n\nDevice with Insufficient Permissions:\n{permission_devices}")

def offline_message():
    offline_list = list()
    for key,value in devices.items():
        if "Offline" in value:
            offline_list.append(key)
    if len(offline_list) > 1:
        offline_devices = "\n".join(offline_list)
        message = (
            "Offline Devices Detected\n\n"
            "Please follow these steps to resolve the issue:\n\n"
            "1. Disconnect the offline devices.\n"
            "2. Kill any associated processes (press F4).\n"
            "3. Reconnect the devices and refresh (press F5).\n\n"
            "Note: Certain devices might need to be unlocked before reconnecting.\n\n"
            f"The following devices are currently offline:\n\n{offline_devices}"
        )
    else:
        offline_devices = offline_list[0]
        message = (
            "Offline Device Detected\n\n"
            "Please follow these steps to resolve the issue:\n\n"
            "1. Disconnect the offline device.\n"
            "2. Kill any associated processes (press F4).\n"
            "3. Reconnect the device and refresh (press F5).\n\n"
            "Note: Certain devices might need to be unlocked before reconnecting.\n\n"
            f"The following device is currently offline:\n\n{offline_devices}"
        )
    messagebox.showinfo("Offline Device", message)

def running_errors_message():
    messagebox.showinfo("Running With Errors",message="Some errors were encountered while running the program. To resolve the issue and ensure smooth operation, it is recommended to terminate all active processes. Press F4 to do so.")

def check_keyword(event):
    try:
        current_selection = devices_list.get(devices_list.curselection())
        if "Task Running" in current_selection:
            all_btn_activity("disabled",list_selection=True)
            return
        else:
            all_btn_activity("normal",list_selection=True)
        if "Wireless" in current_selection:
            wireless_tcpip_btn.configure(state="disabled")
            return
        else:
            wireless_tcpip_btn.configure(state='normal')
    except TclError:
        pass



def connect_pairing():
    PIN_devices_label.place_forget()
    connect_pairing_btn.configure(state="disabled")
    address_box_pairing_address.configure(state="disabled")
    address_box_pairing_port.configure(state="disabled")
    pin_box_pairing.configure(state="disabled")
    phone_ip = address_box_pairing_address.get()
    port = address_box_pairing_port.get()
    pin_code = pin_box_pairing.get()
    preferred_interface = preferred_adapter.get()
    for key,value in network_devices_info.items():
        if value[1] == preferred_interface:
            Interface_MAC,IPv4_gate,Interface_subnet,Interface_Index = value[0],value[2],value[3],value[4]
            break
    if len(attached_adapters) > 1:
        Route_Traffic = True
    else:
        Route_Traffic = False
    if len(Active_Routes) != 0:
        for index, active_routes_dict in enumerate(Active_Routes):
            active_routes_dict : dict
            if active_routes_dict.values()[0] == f"route delete {phone_ip}":
                subprocess.run(f"route delete {phone_ip}".split(" "),shell=True,capture_output=True)
                Active_Routes.pop(index)
                break
    ping_check, route_status = route_n_ping(Route_Traffic,phone_ip,IPv4_gate,Interface_Index,None)
    if not ip_validation(IPv4_gate,Interface_subnet, phone_ip):
        threading.Thread(target=messagebox.showerror,args=("Network Error",f"{phone_ip} is connected to a different network")).start()
    elif route_status == "ROUTE_FAILED":
        threading.Thread(target=messagebox.showerror,args=("Network Error",f"Routing Error:\n{ping_check}")).start()
    elif ping_check.returncode != 0:
        subprocess.run(f"route delete {phone_ip}".split(" "),shell=True,capture_output=True)
        threading.Thread(target=messagebox.showerror,args=("Network Error",f"{phone_ip} didn't respond to a ping")).start()
    else:
        process = subprocess.run(["adb","pair" ,f"{phone_ip}:{port}" ,pin_code], shell=True,capture_output=True)
        if "Successfully paired" in process.stdout.decode():
            wireless_back_btn.configure(state='disabled')
            device_name = re.findall(r"guid=adb-(.*)-",process.stdout.decode())[0]
            threading.Thread(target=messagebox.showinfo, args=("Pairing Successful",f"Successfully paired to {device_name}\n{phone_ip}")).start() # replace with Entry/Label
            threading.Thread(target=connecting_service,args=(device_name,phone_ip,True),daemon=True).start()
        else:
            threading.Thread(target=messagebox.showerror, args=("Pairing Error",process.stdout.decode("utf-8"))).start()
            back_btn_wireless_pairing()
    # connect_pairing_btn.configure(state="active")
    # address_box_pairing_address.configure(state="normal")
    # address_box_pairing_port.configure(state="normal")
    # pin_box_pairing.configure(state="normal")





def open_settings():
    adapters_list_option.configure(state="disabled")
    all_btn_command(False)
    placements = list(range(0,window_size[0]+1))
    placements.reverse()
    for i in placements:
        settings_frame.place(x=i,y=0)
        time.sleep(0.00_00_08)
        if i % 50 ==0:
            settings_frame.update()
    main_page.pack_forget()
    all_btn_command(True)
    adapters_list_option.configure(state="normal")

def back_btn_settings():
    adapters_list_option.configure(state="disabled")
    all_btn_command(False)
    main_page.pack()
    placements = list(range(0,window_size[0]+1))
    for i in placements:
        settings_frame.place(x=i,y=0)
        time.sleep(0.00_00_08)
        if i % 50 ==0:
            settings_frame.update()
    settings_frame.place_forget()
    adapters_list_option.configure(state="disabled")
    all_btn_command(True)

def network_refresh():
    settings_back_btn.configure(state='disabled')
    adapters_list_option.configure(state='disabled')
    network_refresh_btn.configure(state='disabled')
    preferred_adapter.set("Scanning For Network Adapters")
    threading.Thread(target=recheck_network_adapters,daemon=True).start()

def show_disclaimer():
    if WIRELESS_QR_PAIRING_STATE:
        title = "Trouble with Pairing?"
        message=("If your phone and PC aren't pairing successfully for wireless debugging using QR code:\n\n"
                "1. Disable WiFi Throttling if enabled.\n\n"
                "2. Refresh Wireless Debugging: Turn off, then on, the wireless debugging on your phone.\n\n"
                "These steps can improve the pairing experience.")
        messagebox.showinfo(title, message)
    else:
        title = "Enable QR Code Pairing"
        message = ("To enable QR code pairing for wireless debugging, please install the Bonjour Print Service on your system. "
                   "Click the button below to initiate the installation process. After installation, restart ScreenDroid "
                   "to apply the changes.")
        messagebox.showwarning(title, message)

def show_info():
    connection_type = preferred_interface_opt.get()
    if connection_type == "Wired":
        title = "Wired Interface"
        message = ("Wired Interface:\n\n"
                        "If a device is connected both through a wire and wirelessly, selecting the 'Wired' option will "
                        "disconnect any devices that have a dual connection. This won't affect devices solely connected "
                        "wirelessly.")
    elif connection_type == "Wireless":
        title = "Wireless Interface"
        message = ("Wireless Interface:\n\n"
                            "Opting for the 'Wireless' interface means ScreenDroid will only control devices connected "
                            "wirelessly. Devices connected through both methods won't be managed via a wired connection.")
    elif connection_type == "Any":
        title = "Any Interface"
        message = ("Any Interface:\n\n"
                    "Choosing the 'Any' option allows you to interact with both wireless and wired devices without any "
                    "specific restrictions. You'll have the freedom to manage your devices according to your preference.")
    messagebox.showinfo(title, message)


def validate_pin_pairing_entry_status():
    if PIN_BOX_PAIR_STATUS and IP_ADDRESS_BOX_PAIR_STATUS and PORT_BOX_PAIR_STATUS:
        connect_pairing_btn.configure(state="active")
    else:
        connect_pairing_btn.configure(state="disabled")

def validate_port_pin_pairing(port:str):
    global PORT_BOX_PAIR_HINT, PORT_BOX_PAIR_STATUS
    if PORT_BOX_PAIR_HINT:
        return True
    if port.isdigit() and len(port)<6 or len(port) == 0:
        if len(port) == 5 and int(port) in range(30000,49999):
            PORT_BOX_PAIR_STATUS = True
            validate_pin_pairing_entry_status()
            return True
        else:
            PORT_BOX_PAIR_STATUS = False
            validate_pin_pairing_entry_status()
            if len(port) == 1 and int(port) not in (3,4):
                return False
            else:
                return True
    else:
        return False

def validate_address_pin_pairing(addr:str):
    global auto_complete_gateway, IP_ADDRESS_BOX_PAIR_STATUS
    if AUTO_COMPLETE_ADDRESS_BOX_PIN_PAIR:
        return True
    ip_addr = addr
    if ip_validation_check_state_int.get() == 0 and addr != auto_complete_gateway:
        if auto_complete_gateway not in addr:
            return False
        if addr.count(".") > 3:
            return False
        addr = addr[len(auto_complete_gateway):].split(".")
        for index, octet in enumerate(addr):
            valid_numbers = list(range(int(network_address_lower_limit[index]),int(broadcast_address_upper_limit[index])+1))
            if len(octet) == 0:
                continue
            if not (octet.isdigit() and int(octet) > 0 and int(octet) < 256):
                return False
            elif len(str(octet)) >= len(network_address_lower_limit[index]):
                if not(int(octet) in valid_numbers):
                    return False
            else:
                for digit in octet:
                    if not any(digit==str(num)[:len(octet)] for num in valid_numbers ):
                        return False
        else:
            try:
                ipaddress.ip_address(ip_addr)
                IP_ADDRESS_BOX_PAIR_STATUS = True
                validate_pin_pairing_entry_status()
            except ValueError:
                IP_ADDRESS_BOX_PAIR_STATUS = False
                validate_pin_pairing_entry_status()
            return True
    else:
        if addr.count(".") > 3:
            return False
        addr = addr.split(".")
        for octet in addr:
            if len(octet) == 0:
                continue
            if not (octet.isdigit() and int(octet) > 0 and int(octet) < 256):
                return False
        else:
            try:
                ipaddress.ip_address(ip_addr)
                IP_ADDRESS_BOX_PAIR_STATUS = True
                validate_pin_pairing_entry_status()
            except ValueError:
                IP_ADDRESS_BOX_PAIR_STATUS = False
                validate_pin_pairing_entry_status()
            return True

def validate_pin_code_pairing(pin : str):
    global PIN_BOX_PAIR_HINT, PIN_BOX_PAIR_STATUS
    if PIN_BOX_PAIR_HINT:
        return True
    if pin.isdigit() and len(pin) <7:
        if len(pin) == 6:
            PIN_BOX_PAIR_STATUS = True
            validate_pin_pairing_entry_status()
        else:
            PIN_BOX_PAIR_STATUS = False
            validate_pin_pairing_entry_status()
        return True
    else:
        return False



def image_assign(function_button :Button,function_svg,new_icon_size):
    try:
        if function_button.image.get(new_icon_size) is None:
            png_bytes = cairosvg.svg2png(bytestring=function_svg, output_width=new_icon_size, output_height=new_icon_size)
            new_btn_image = ImageTk.PhotoImage(Image.open(BytesIO(png_bytes)))
            function_button.image[new_icon_size] = new_btn_image
            function_button.configure(width=new_icon_size,height=new_icon_size,image=new_btn_image)
        else:
            function_button.configure(width=new_icon_size,height=new_icon_size,image=function_button.image[new_icon_size])
    except AttributeError:
        png_bytes = cairosvg.svg2png(bytestring=function_svg, output_width=new_icon_size, output_height=new_icon_size)
        new_btn_image = ImageTk.PhotoImage(Image.open(BytesIO(png_bytes)))
        function_button.image = dict()
        function_button.image[new_icon_size] = new_btn_image
        function_button.configure(width=new_icon_size,height=new_icon_size,image=new_btn_image)
    function_button.update()

def PIN_IP_label_image_assign(width,height):
    width_svg = round(width*0.8325)
    height_svg = round(height*0.13)
    png_bytes = cairosvg.svg2png(bytestring=PIN_deices_IP_label_svg, output_width=width_svg, output_height=height_svg)
    new_btn_image = ImageTk.PhotoImage(Image.open(BytesIO(png_bytes)))
    PIN_devices_label.image = new_btn_image
    PIN_devices_label.configure(width=width_svg,height=height_svg,image=new_btn_image)

def replace_elements(new_width,new_height):
    qr_code_size = int(new_width/1.6)
    secondary_row_height = new_height/15
    primary_upper_row_height = new_height/1.5
    primary_lower_row_height = new_height*(47/60)
    wireless_pairing_row_height = new_height*(7/60)
    screen_share_scrcpy_btn.place(x=new_width/8,y=primary_upper_row_height)
    wireless_tcpip_btn.place(x=new_width*0.3,y=primary_upper_row_height)
    file_download_btn.place(x=new_width*0.475,y=primary_upper_row_height)
    file_upload_btn.place(x=new_width*0.65,y=primary_upper_row_height)
    file_downloading_btn.place(x=new_width/4,y=new_height/6)
    wireless_pairing_btn.place(x=new_width*0.3,y=primary_lower_row_height)
    shell_btn.place(x=new_width*0.475,y=primary_lower_row_height)
    devices_list.place(x=new_width/8,y=new_height/3)
    auto_refresh.place(x=new_width*0.75,y=new_height/4)
    background_color_btn.place(x=new_width/10,y=secondary_row_height)
    devices_refresh_btn.place(x=new_width*0.205,y=secondary_row_height)
    kill_btn.place(x=new_width*0.31,y=secondary_row_height)
    settings_btn.place(x=new_width*0.85,y=secondary_row_height)
    QR_pair_option_btn.place(x=new_width/10,y=wireless_pairing_row_height)
    PIN_pair_option_btn.place(x=new_width/2,y=wireless_pairing_row_height)
    if RESIZE_AND_PLACE_QR_CODE_LABEL:
        QR_code_label.place(x=new_width*0.1875,y=new_height/3)
    if UNAUTHORIZED_BUTTON_PLACEMENT:
        unauthorized_noti_btn.place(x=window_size[0]*0.825, y=window_size[1]*0.4)
    if OFFLINE_BUTTON_PLACEMENT:
        offline_noti_btn.place(x=window_size[0]*0.825, y=window_size[1]*(29/60))
    if PERMISSION_ERROR_PLACEMENT:
        permission_error_btn.place(x=window_size[0]*0.825, y=window_size[1]*(17/30))
    main_window.update()
    devices_list.config(width=int(new_width*0.065),height=int(new_height*(7/600)))
    auto_refresh.config(width=int(new_width/100))
    QR_pair_option_btn.config(width=int(new_width*0.0375),height=int(new_height/300))
    PIN_pair_option_btn.config(width=int(new_width*0.0375),height=int(new_height/300))
    QR_code_label.config(width=qr_code_size,height=qr_code_size)
    if WIRELESS_QR_PAIRING_STATE:
        qrcode_image = ImageTk.PhotoImage(Image.open(r"qrcode.png").resize((qr_code_size,qr_code_size),Image.Resampling.LANCZOS))
        QR_code_label.image = qrcode_image
        try:
            if QR_code_label.image.get(qr_code_size) is None:
                QR_code_label.image[qr_code_size] = qrcode_image
                QR_code_label.configure(image=qrcode_image)
            else:
                QR_code_label.configure(image=QR_code_label.image[qr_code_size])
        except AttributeError:
            QR_code_label.image = dict()
            QR_code_label.image[qr_code_size] = qrcode_image
            QR_code_label.configure(image=qrcode_image)
    else:
        if RESIZE_AND_PLACE_QR_CODE_LABEL:
            bonjour_install_btn.configure(width=int(new_width/20))
            bonjour_install_btn.place(x=new_width/4,y=new_height/1.2)
    main_window.update()

def resize_maintain(event : Event):
    global window_size,secondary_icon_size, RESIZING
    if RESIZING:
        return
    RESIZING = True
    new_width = main_window.winfo_width()
    new_height = main_window.winfo_height()
    new_window_size = (new_width,new_height)
    new_aspect_ratio = new_width/new_height
    if new_window_size != window_size:
        if new_height == window_size[1]:
            new_height = int(new_width/ aspect_ratio)
        elif new_width == window_size[0]:
            new_width = int(new_height*aspect_ratio)
        else:
            if new_aspect_ratio > aspect_ratio:
                new_height = int(new_width/ aspect_ratio)
            elif new_aspect_ratio < aspect_ratio:
                new_width = int(new_height*aspect_ratio)
        window_size = (new_width,new_height)
        main_window.geometry(f"{new_width}x{new_height}")
        main_window.update()
        for i in [main_page,wireless_pairing_frame,settings_frame,startup_label]:
            i.configure(width=new_width,height=new_height)
            i.update()
        primary_icon_size = round(0.12*window_size[0])
        secondary_icon_size = round(0.09*window_size[0])
        for function_button,function_svg in primary_button_svg:
            threading.Thread(target=image_assign,args=(function_button,function_svg,primary_icon_size),daemon=True).start()
        for function_button,function_svg in secondary_button_svg:
            threading.Thread(target=image_assign,args=(function_button,function_svg,secondary_icon_size),daemon=True).start()
        if not WIRELESS_QR_PAIRING_STATE:
            threading.Thread(target=image_assign,args=(QR_code_label,disabled_qr_code_svg,window_size[0]/1.6),daemon=True).start()
        threading.Thread(target=replace_elements,args=(new_width,new_height),daemon=True).start()
        threading.Thread(target=PIN_IP_label_image_assign,args=(new_width,new_height),daemon=True).start()
        adapters_list_option.configure(width=int(new_width/10))
        adapters_list_option.place(x=new_width/20,y=new_height/4)
        menu = adapters_list_option['menu']
        menu.delete(0, "end")
        
        for string in attached_adapters:
            string = f"•  {string:<{int(new_width/10)+4}}"
            menu.add_command(label=string, command=lambda value=string: preferred_adapter.set(value))
        main_window.update()
    RESIZING = False




main_window = Tk()
main_window.title("ScreenDroid")
main_window.geometry("400x600+200+10")
main_window.configure(background=bg_color_main)
secondary_icon_size = 36
window_width, window_height = 400, 600
window_size = (window_width, window_height)
max_screen_width, max_screen_height = main_window.winfo_screenwidth(), main_window.winfo_screenheight()
if max_screen_width/2 > max_screen_height/3:
    max_screen_width = int(max_screen_height*aspect_ratio)
elif max_screen_width/2 < max_screen_height/3:
    max_screen_height = int(max_screen_width/aspect_ratio )
elif max_screen_width == max_screen_height:
    max_screen_width = int(max_screen_height * aspect_ratio)
main_window.maxsize(width=max_screen_width, height=max_screen_height)
main_window.minsize(width=400, height=600)
main_window_icon = PhotoImage(file=r'android_FILL0_wght400_GRAD0_opsz48.png')
main_window.iconphoto(False,main_window_icon)
main_window.protocol("WM_DELETE_WINDOW", exiting)



startup_label = Label(main_window,width=window_size[0],height=window_size[1],bg="#000000")
startup_label.pack()


main_page = Frame(main_window, width=window_width, height=window_height, background=bg_color_main)

devices_list = Listbox(main_page, bd=3, width=26,height=7, activestyle="none", selectbackground="#00c300",background="#1f1f1f",highlightcolor="#4389c4",highlightbackground="#4389c4",highlightthickness=3)
devices_list.place(x=50, y=200)

background_color_btn = Button(main_page, text="BGCOLOR", command=change_bg,width=30, height=30, bd=0,bg="#1f1f1f",fg="#1f1f1f",disabledforeground="#1f1f1f",activebackground=active_color,activeforeground=active_color, highlightthickness=0, highlightbackground="#1f1f1f",relief="flat",)
background_color_btn.place(x=40, y=40)

devices_refresh_btn = Button(main_page,text="Refresh",command=lambda : threading.Thread(target=re_checkup,daemon=True).start(),width=30, height=30, state="normal",bd=0,bg="#1f1f1f",fg="#1f1f1f",disabledforeground="#1f1f1f",activebackground=active_color,activeforeground=active_color, highlightthickness=0, highlightbackground="#1f1f1f",relief="flat",)
devices_refresh_btn.place(x=82, y=40)

unauthorized_noti_btn = Button(main_page, text="Error Unauthorized", state="normal",width=30, height=30,command=unauthorized_message, bd=0,bg="#1f1f1f",fg="#1f1f1f",disabledforeground="#1f1f1f",activebackground=active_color,activeforeground=active_color, highlightthickness=0, highlightbackground="#1f1f1f",relief="flat",)
offline_noti_btn = Button(main_page, text="Error Offline", state="normal",width=30, height=30,command=offline_message,bd=0,bg="#1f1f1f",fg="#1f1f1f",disabledforeground="#1f1f1f",activebackground=active_color,activeforeground=active_color, highlightthickness=0, highlightbackground="#1f1f1f",relief="flat",)
permission_error_btn = Button(main_page, text="Error Permission", state="normal",width=30, height=30,command=permission_message,bd=0,bg="#1f1f1f",fg="#1f1f1f",disabledforeground="#1f1f1f",activebackground=active_color,activeforeground=active_color, highlightthickness=0, highlightbackground="#1f1f1f",relief="flat",)
running_with_errors_btn = Button(main_page, text="Error Running", state="normal",width=30, height=30,command=running_errors_message,bd=0,bg="#1f1f1f",fg="#1f1f1f",disabledforeground="#1f1f1f",activebackground=active_color,activeforeground=active_color, highlightthickness=0, highlightbackground="#1f1f1f",relief="flat",)

screen_share_scrcpy_btn = Button(main_page, text="scrcpy cable", command=screen_share_scrcpy, width=48, height=48,bd=0,bg="#1f1f1f",fg="#1f1f1f",disabledforeground="#1f1f1f",activebackground=active_color,activeforeground=active_color, highlightthickness=0, highlightbackground="#1f1f1f",relief="flat",)
screen_share_scrcpy_btn.place(x=50, y=400)

wireless_tcpip_btn = Button(main_page, text="scrcpy wireless", command=wireless_connection_setup,width=48, height=48, bd=0,bg="#1f1f1f",fg="#1f1f1f",disabledforeground="#1f1f1f",activebackground=active_color,activeforeground=active_color, highlightthickness=0, highlightbackground="#1f1f1f",relief="flat",)
wireless_tcpip_btn.place(x=120, y=400)

kill_btn = Button(main_page, text="end_all", command=lambda:threading.Thread(target=kill_process,daemon=True).start(),width=30, height=30,bd=0,bg="#1f1f1f",fg="#1f1f1f",disabledforeground="#1f1f1f",activebackground=active_color,activeforeground=active_color, highlightthickness=0, highlightbackground="#1f1f1f",relief="flat",)
kill_btn.place(x=124, y=40)

auto_refresh = Label(main_page, width=4, font="Terminal",height=2,bg="#1f1f1f",fg="#ffffff",bd=0)
auto_refresh.place(x=300, y=150) 

file_download_btn = Button(main_page, text="adb pull", command=not_implemented_message,width=48, height=48, bd=0,bg="#1f1f1f",fg="#1f1f1f",disabledforeground="#1f1f1f",activebackground=active_color,activeforeground=active_color, highlightthickness=0, highlightbackground="#1f1f1f",relief="flat",)
file_download_btn.place(x=190, y=400)

file_upload_btn = Button(main_page, text="adb push", command=not_implemented_message,width=48, height=48,bd=0,bg="#1f1f1f",fg="#1f1f1f",disabledforeground="#1f1f1f",activebackground=active_color,activeforeground=active_color, highlightthickness=0, highlightbackground="#1f1f1f",relief="flat",)
file_upload_btn.place(x=260, y=400)

#whatsapp_btn = Button(main_page, text="adb pull whats", command=not_implemented_message,width=48, height=48, bd=3, activebackground="green")
#whatsapp_btn.place(x=50, y=470)

file_downloading_btn = Button(main_page, width=48, height=48,command=not_implemented_message, bd=0,bg="#1f1f1f",fg="#1f1f1f",disabledforeground="#1f1f1f",activebackground=active_color,activeforeground=active_color, highlightthickness=0, highlightbackground="#1f1f1f",relief="flat",)
file_downloading_btn.place(x=100, y=100)

wireless_pairing_btn = Button(main_page, width=48, height=48, command=wireless_pairing, bd=0,bg="#1f1f1f",fg="#1f1f1f",disabledforeground="#1f1f1f",activebackground=active_color,activeforeground=active_color, highlightthickness=0, highlightbackground="#1f1f1f",relief="flat",)
wireless_pairing_btn.place(x=120, y=470)


shell_btn = Button(main_page, width=48, height=48, bd=0,bg="#1f1f1f",fg="#1f1f1f",disabledforeground="#1f1f1f",activebackground=active_color,activeforeground=active_color, highlightthickness=0, highlightbackground="#1f1f1f",relief="flat",command=lambda:print("no"))
shell_btn.place(x=190, y=470)

settings_btn = Button(main_page, text="settings", command=lambda:threading.Thread(target=open_settings,daemon=True).start(),width=30, height=30,bd=0,bg="#1f1f1f",fg="#1f1f1f",disabledforeground="#1f1f1f",activebackground=active_color,activeforeground=active_color, highlightthickness=0, highlightbackground="#1f1f1f",relief="flat",)
settings_btn.place(x=340, y=40)

settings_frame = Frame(main_window, width=window_width, height=window_height, background=bg_color_main)

settings_back_btn = Button(settings_frame,width=30,height=30,name='back_btn',command=lambda:threading.Thread(target=back_btn_settings,daemon=True).start(),bd=0,bg="#1f1f1f",fg="#1f1f1f",disabledforeground="#1f1f1f",activebackground=active_color,activeforeground=active_color, highlightthickness=0, highlightbackground="#1f1f1f",relief="flat",)
settings_back_btn.place(x=20,y=30)

device_screen_state_int = IntVar()
device_screen_state_box = Checkbutton(settings_frame,text="Turn screen off while sharing screen",textvariable=StringVar(value="Turn screen off while sharing screen"),variable=device_screen_state_int,background=bg_color_main,fg="#ffffff",selectcolor="#000000",activebackground="#1f1f1f",activeforeground="#ffffff")
device_screen_state_box.place(x=20,y=240)

network_ping_check_state_int = IntVar()
network_ping_check_state_box = Checkbutton(settings_frame,text="Disable ping tests for wireless connections",textvariable=StringVar(value="Disable ping tests for wireless connections"),variable=network_ping_check_state_int,background=bg_color_main,fg="#ffffff",selectcolor="#000000",activebackground="#1f1f1f",activeforeground="#ffffff")
network_ping_check_state_box.place(x=20,y=270)

ip_validation_check_state_int = IntVar()
ip_validation_check_state_box = Checkbutton(settings_frame,text="Disable device IP verification within network range",textvariable=StringVar(value="Disable device IP verification within network range"),variable=ip_validation_check_state_int,background=bg_color_main,fg="#ffffff",selectcolor="#000000",activebackground="#1f1f1f",activeforeground="#ffffff")
ip_validation_check_state_box.place(x=20,y=300)

network_refresh_btn = Button(settings_frame, text="network_refresh",width=30, height=30, command=network_refresh,bd=0,bg="#1f1f1f",fg="#1f1f1f",disabledforeground="#1f1f1f",activebackground=active_color,activeforeground=active_color, highlightthickness=0, highlightbackground="#1f1f1f",relief="flat")
network_refresh_btn.place(x=340,y=150)

preferred_adapter = StringVar(value="Preferred Network Interface Adapter")
adapters_list_option = OptionMenu(settings_frame,preferred_adapter,"Preferred Network Interface Adapter")
adapters_list_option.configure(bg="#1f1f1f",fg="#ffffff",activebackground="#333333",highlightbackground="#6c757d",highlightcolor="#6c757d",activeforeground="#ffffff",width=40)
adapters_list_option["menu"].config(bg="#1f1f1f", fg="#ffffff",activebackground="#333333")
adapters_list_option.place(x=20,y=150)


prefrred_connection_label = Label(settings_frame,width=20,height=4,text="Preferred Interface",font="Terminal 12",justify="left",anchor='w',background=bg_color_main,fg="#ffffff")
prefrred_connection_label.place(x=20,y=350)

preferred_interface_opt = StringVar(value="Any")

preferred_interface_wired_checkbox = Radiobutton(settings_frame,text='Wired',variable=preferred_interface_opt,value="Wired",width=8,height=1,font='Terminal',justify="left",anchor='w',background=bg_color_main,fg="#ffffff",selectcolor="#000000",activebackground="#1f1f1f",activeforeground="#ffffff")
preferred_interface_wired_checkbox.place(x=20,y=430)

preferred_interface_wireless_checkbox = Radiobutton(settings_frame,text='Wireless',variable=preferred_interface_opt,value="Wireless",width=8,height=1,font='Terminal',justify="left",anchor='w',background=bg_color_main,fg="#ffffff",selectcolor="#000000",activebackground="#1f1f1f",activeforeground="#ffffff")
preferred_interface_wireless_checkbox.place(x=20,y=460)

preferred_interface_any_checkbox = Radiobutton(settings_frame,text="Any",variable=preferred_interface_opt,value="Any",width=8,height=1,font='Terminal',justify="left",anchor='w',background=bg_color_main,fg="#ffffff",selectcolor="#000000",activebackground="#1f1f1f",activeforeground="#ffffff")
preferred_interface_any_checkbox.place(x=20,y=490)

preferred_interface_info_btn = Button(settings_frame, command=show_info,width=30, height=30,bd=0,bg="#1f1f1f",fg="#1f1f1f",disabledforeground="#1f1f1f",activebackground=active_color,activeforeground=active_color, highlightthickness=0, highlightbackground="#1f1f1f",relief="flat",)
preferred_interface_info_btn.place(x=340, y=385)

vid_label_wireless = Label(main_page,width=window_width, height=window_height,background=bg_color_main)

wireless_pairing_frame = Frame(main_window,width=window_width,height=window_height)
wireless_pairing_frame.configure(background=bg_color_main)

pairing_info_btn = Button(wireless_pairing_frame, command=show_disclaimer,width=30, height=30,bd=0,bg="#1f1f1f",fg="#1f1f1f",disabledforeground="#1f1f1f",activebackground=active_color,activeforeground=active_color, highlightthickness=0, highlightbackground="#1f1f1f",relief="flat",)
pairing_info_btn.place(x=340, y=20)

wireless_back_btn = Button(wireless_pairing_frame,width=30,height=30,name='back_btn',command=back_btn_wireless_pairing, bd=0,bg="#1f1f1f",fg="#1f1f1f",disabledforeground="#1f1f1f",activebackground=active_color,activeforeground=active_color, highlightthickness=0, highlightbackground="#1f1f1f",relief="flat",)
wireless_back_btn.place(x=20,y=20)

QR_code_label = Label(wireless_pairing_frame,width=250,height=250,background=bg_color_main)
QR_code_label.place(x=75,y=200)

QR_pair_option_btn = Button(wireless_pairing_frame,width=15,height=2,text="QR Pairing",command=QR_pair_menu,bg="#1f1f1f", fg="#d3d3d3",activebackground="#1f1f1f",activeforeground="#d3d3d3",state="disabled")
QR_pair_option_btn.place(x=40,y=70)

PIN_pair_option_btn = Button(wireless_pairing_frame,width=15,height=2,text="PIN Pairing",command=PIN_pair_menu,bg="#1f1f1f", fg="#ffffff",activebackground="#1f1f1f",activeforeground="#ffffff")
PIN_pair_option_btn.place(x=200,y=70)


PIN_devices_label = Label(wireless_pairing_frame,width=35,height=3,background=bg_color_main,bd=0,bg="#1f1f1f",fg="#1f1f1f",disabledforeground="#1f1f1f",activebackground=active_color,activeforeground=active_color, highlightthickness=0, highlightbackground="#1f1f1f",relief="flat",)

PIN_devies_IP_label_string_var = StringVar(value="192.168.100.255:39999")
ip_label = Label(PIN_devices_label,textvariable=PIN_devies_IP_label_string_var,width=21,font="Terminal",bg="#1f1f1f", fg="#ffffff",activebackground="#1f1f1f",activeforeground="#ffffff")
ip_label.place(x=60,y=30)




bonjour_install_btn = Button(wireless_pairing_frame, text="Install Bonjour Service", width=20, command=lambda: threading.Thread(target=install_bonjour).start(), bd=4,bg="#1f1f1f", fg="#ffffff", activeforeground="#ffffff", activebackground="#1f1f1f")


connect_pairing_btn = Button(wireless_pairing_frame,width=10,height=2,text="Connect",command=lambda:threading.Thread(target=connect_pairing,daemon=True).start(),font="Terminal",state="disabled", bd=3,bg="#1f1f1f",fg="#ffffff",activebackground="#1f1f1f",activeforeground="#ffffff")


file_downloading_svg = b'<svg xmlns="http://www.w3.org/2000/svg" height="48" viewBox="0 -960 960 960" width="48"><path d="M437.154-102.001q-71.769-7.616-133.307-40.077-61.538-32.462-106.538-83.577-45-51.115-70.461-116.653-25.462-65.538-25.462-138.307 0-146.923 95.923-255.153 95.922-108.231 240.845-123.461v45.383q-125.692 18.231-208.538 112.5-82.846 94.269-82.846 220.731 0 126.076 82.346 220.538 82.346 94.461 208.038 112.692v45.384ZM480-293.847 294.232-479.615l32.23-32.615 130.846 130.846v-284.769h45.384v284.769l131.231-131.231L666.153-480 480-293.847Zm43.231 191.846v-45.384q44.846-6 86.576-22.731 41.731-16.73 77.347-45.346l33.999 33.23q-43.692 32.308-93.731 53.384-50.038 21.077-104.191 26.847Zm165.307-642.383Q651.307-771 609.884-789.115q-41.423-18.115-86.653-24.731v-45.383q54.153 7 103.691 27.769 49.539 20.769 94.231 53.461l-32.615 33.615Zm89.23 500.921-32.614-31.614q28.23-36.231 44.846-77.962 16.615-41.73 22.615-86.961h45.999q-6.615 54.154-27.077 104.192-20.461 50.038-53.769 92.345Zm34.847-277.768q-6-45.23-22.615-87.269-16.616-42.038-44.846-77.654l36.23-31.768q31.538 43.692 50.999 93.423 19.462 49.73 26.231 103.268h-45.999Z" fill="#ffffff"/></svg>'
file_downloading_btn_complete_svg = b'<svg xmlns="http://www.w3.org/2000/svg" height="48" viewBox="0 -960 960 960" width="48"><path d="M380.385-348.539 180.771-548.538l32.23-31.999 167.384 167.768 367.23-367.23 31.999 32.615-399.229 398.845ZM220.001-180.001v-45.384h519.998v45.384H220.001Z" fill="#ffffff"/></svg>'
light_mode_svg = b'<svg xmlns="http://www.w3.org/2000/svg" height="48" viewBox="0 -960 960 960" width="48"><path d="M479.765-340Q538-340 579-380.765q41-40.764 41-99Q620-538 579.235-579q-40.764-41-99-41Q422-620 381-579.235q-41 40.764-41 99Q340-422 380.765-381q40.764 41 99 41Zm.235 60q-83 0-141.5-58.5T280-480q0-83 58.5-141.5T480-680q83 0 141.5 58.5T680-480q0 83-58.5 141.5T480-280ZM70-450q-12.75 0-21.375-8.675Q40-467.351 40-480.175 40-493 48.625-501.5T70-510h100q12.75 0 21.375 8.675 8.625 8.676 8.625 21.5 0 12.825-8.625 21.325T170-450H70Zm720 0q-12.75 0-21.375-8.675-8.625-8.676-8.625-21.5 0-12.825 8.625-21.325T790-510h100q12.75 0 21.375 8.675 8.625 8.676 8.625 21.5 0 12.825-8.625 21.325T890-450H790ZM479.825-760Q467-760 458.5-768.625T450-790v-100q0-12.75 8.675-21.375 8.676-8.625 21.5-8.625 12.825 0 21.325 8.625T510-890v100q0 12.75-8.675 21.375-8.676 8.625-21.5 8.625Zm0 720Q467-40 458.5-48.625T450-70v-100q0-12.75 8.675-21.375 8.676-8.625 21.5-8.625 12.825 0 21.325 8.625T510-170v100q0 12.75-8.675 21.375Q492.649-40 479.825-40ZM240-678l-57-56q-9-9-8.629-21.603.37-12.604 8.526-21.5 8.896-8.897 21.5-8.897Q217-786 226-777l56 57q8 9 8 21t-8 20.5q-8 8.5-20.5 8.5t-21.5-8Zm494 495-56-57q-8-9-8-21.375T678.5-282q8.5-9 20.5-9t21 9l57 56q9 9 8.629 21.603-.37 12.604-8.526 21.5-8.896 8.897-21.5 8.897Q743-174 734-183Zm-56-495q-9-9-9-21t9-21l56-57q9-9 21.603-8.629 12.604.37 21.5 8.526 8.897 8.896 8.897 21.5Q786-743 777-734l-57 56q-8 8-20.364 8-12.363 0-21.636-8ZM182.897-182.897q-8.897-8.896-8.897-21.5Q174-217 183-226l57-56q8.8-9 20.9-9 12.1 0 20.709 9Q291-273 291-261t-9 21l-56 57q-9 9-21.603 8.629-12.604-.37-21.5-8.526ZM480-480Z" fill="#ffffff"/></svg>'
unauthorized_noti_svg = b'<svg xmlns="http://www.w3.org/2000/svg" height="48" viewBox="0 -960 960 960" width="48"><path d="M480.018-286Q466-286 456.5-295.482q-9.5-9.483-9.5-23.5 0-14.018 9.482-23.518 9.483-9.5 23.5-9.5 14.018 0 23.518 9.482 9.5 9.483 9.5 23.5 0 14.018-9.482 23.518-9.483 9.5-23.5 9.5ZM451-396v-268h60v268h-60ZM260-40q-24 0-42-18t-18-42v-760q0-24 18-42t42-18h440q24 0 42 18t18 42v760q0 24-18 42t-42 18H260Zm0-90v30h440v-30H260Zm0-60h440v-580H260v580Zm0-640h440v-30H260v30Zm0 0v-30 30Zm0 700v30-30Z" fill="#ffffff"/></svg>'
offline_noti_svg = b'<svg xmlns="http://www.w3.org/2000/svg" height="48" viewBox="0 -960 960 960" width="48"><path d="M634-320q-14 0-24-10t-10-24v-132q0-14 10-24t24-10h6v-40q0-33 23.5-56.5T720-640q33 0 56.5 23.5T800-560v40h6q14 0 24 10t10 24v132q0 14-10 24t-24 10H634Zm46-200h80v-40q0-17-11.5-28.5T720-600q-17 0-28.5 10.925T680-562v42ZM260-40q-24.75 0-42.375-17.625T200-100v-760q0-24.75 17.625-42.375T260-920h440q24.75 0 42.375 17.625T760-860v146h-60v-56H260v580h440v-56h60v146q0 24.75-17.625 42.375T700-40H260Zm0-90v30h440v-30H260Zm0-700h440v-30H260v30Zm0 0v-30 30Zm0 700v30-30Z" fill="#ffffff"/></svg>'
running_with_errors_svg = b'<svg xmlns="http://www.w3.org/2000/svg" height="48" viewBox="0 -960 960 960" width="48"><path d="M478-80q-83 0-156-31.5T195-197q-54-54-85.5-127T78-480q0-83 31.5-156T195-763q54-54 127-85.5T478-880q88 0 166.5 36T780-742L478-440v-380q-142 0-241 98.812Q138-622.375 138-480t98.812 241.188Q335.625-140 478-140q81 0 153.5-36.5T757-276v83q-57 54-129 83.5T478-80Zm339-147v-327h60v327h-60Zm33.018 140Q836-87 826.5-96.483q-9.5-9.482-9.5-23.499 0-14.018 9.482-23.518 9.483-9.5 23.5-9.5 14.018 0 23.518 9.482 9.5 9.483 9.5 23.5Q883-106 873.518-96.5q-9.483 9.5-23.5 9.5Z" fill="#ffffff"/></svg>'
permission_error_svg = b'<svg xmlns="http://www.w3.org/2000/svg" height="48" viewBox="0 -960 960 960" width="48"><path d="m800-247-60-60v-267H473l-60-60h197v-95q0-54.583-39.5-92.792Q531-860 475.5-860t-94 38.5Q343-783 343-729v25l-55-55q9-70 62.5-115.5T476-920q80.915 0 137.457 55.5Q670-809 670-729v95h70q24.75 0 42.375 17.625T800-574v327Zm67 265L764-85q-8 3-13 4t-11 1H220q-24.75 0-42.375-17.625T160-140v-434q0-23 16-40.5t39-19.5L-14-863l43-42L910-24l-43 42ZM710-140 535-314q-11 11-24.239 16T482-293q-32 0-53.5-21T407-366.68q0-16.32 5.5-29.82T429-421L275-574h-55v434h490ZM493-357Zm113-84Z" fill="#ffffff"/></svg>'
disabled_qr_code_svg = b'<svg xmlns="http://www.w3.org/2000/svg" height="48" viewBox="0 -960 960 960" width="48"><path d="M480-490Zm-30-385q14.328-8 30.164-8Q496-883 510-875l300 173q14.25 8.426 22.125 22.213T840-650v157q-13.655-10.156-28.828-17.578Q796-518 780-524v-96l-149 87q-59 14-106.5 51T450-392v-71L180-619v309l265 153q10 21 23.5 40.5T499-80q-12 5-25 3.5T450-85L150-258q-14.25-8.426-22.125-22.213T120-310v-340q0-16 7.875-29.787Q135.75-693.574 150-702l300-173Zm30 52L213-669l267 155 266-155-266-154ZM690-80q-78 0-134-55.399-56-55.4-56-134Q500-348 556-404t134-56q78 0 134 55.867Q880-348.265 880-269q0 78.435-56 133.717Q768-80 690-80Zm-.5-76q9.5 0 16-6t6.5-16q0-10-6.6-16t-15.4-6q-10 0-16 6t-6 16q0 10 6 16t15.5 6ZM672-241h35v-143h-35v143Z" fill="#ffffff"/></svg>'

PIN_deices_IP_label_svg = b'<?xml version="1.0" encoding="UTF-8" standalone="no"?> <svg width="222" height="52" viewBox="0 0 58.737452 13.758332" version="1.1" id="svg1" xml:space="preserve" inkscape:version="1.3 (0e150ed6c4, 2023-07-21)" sodipodi:docname="paring_detecting_svg.svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" xmlns:svg="http://www.w3.org/2000/svg"><sodipodi:namedview id="namedview1" pagecolor="#ffffff" bordercolor="#000000" borderopacity="0.25" inkscape:showpageshadow="2" inkscape:pageopacity="0.0" inkscape:pagecheckerboard="0" inkscape:deskcolor="#d1d1d1" inkscape:document-units="px" inkscape:zoom="4" inkscape:cx="115.5" inkscape:cy="-16.125" inkscape:window-width="1920" inkscape:window-height="1009" inkscape:window-x="-8" inkscape:window-y="-8" inkscape:window-maximized="1" inkscape:current-layer="layer1" /><defs id="defs1"><linearGradient inkscape:collect="always" xlink:href="#swatch2" id="linearGradient2" x1="0.15625" y1="-479.92862" x2="959.99872" y2="-479.92862" gradientUnits="userSpaceOnUse" gradientTransform="matrix(0.06313237,0,0,0.01423846,-0.93634947,13.713343)" /><linearGradient id="swatch2" inkscape:swatch="solid"><stop style="stop-color:#000000;stop-opacity:0;" offset="0" id="stop2" /></linearGradient></defs><g inkscape:label="Layer 1" inkscape:groupmode="layer" id="layer1"><rect style="opacity:1;fill:#000000;fill-opacity:0;stroke:#1f1f1f;stroke-width:0.646153;stroke-linecap:square;stroke-linejoin:miter;stroke-miterlimit:4;stroke-dasharray:none;stroke-dashoffset:0;stroke-opacity:1;paint-order:normal" id="rect1" width="58.09132" height="13.112174" x="0.32307673" y="0.32307652" ry="0" rx="0" /><rect style="fill:#1f1f1f;fill-opacity:0;stroke:#1f1f1f;stroke-width:0.526104;stroke-linecap:square;stroke-linejoin:miter;stroke-miterlimit:4;stroke-dasharray:none;stroke-dashoffset:0;paint-order:normal" id="rect2" width="0.51170897" height="0.3421599" x="0.55388832" y="0.63573956" /><rect style="fill:#1f1f1f;fill-opacity:0;stroke:#1f1f1f;stroke-width:0.529166;stroke-linecap:square;stroke-linejoin:miter;stroke-miterlimit:4;stroke-dasharray:none;stroke-dashoffset:0;paint-order:normal" id="rect2-8" width="0.54957277" height="0.52034009" x="0.53501272" y="12.799498" ry="0" /><rect style="fill:#1f1f1f;fill-opacity:0;stroke:#1f1f1f;stroke-width:0.529166;stroke-linecap:square;stroke-linejoin:miter;stroke-miterlimit:4;stroke-dasharray:none;stroke-dashoffset:0;paint-order:normal" id="rect2-0" width="0.32156032" height="0.46187535" x="57.792061" y="12.712662" /><rect style="fill:#1f1f1f;fill-opacity:0;stroke:#1f1f1f;stroke-width:0.551875;stroke-linecap:square;stroke-linejoin:miter;stroke-miterlimit:4;stroke-dasharray:none;stroke-dashoffset:0;paint-order:normal" id="rect2-4" width="0.39824054" height="0.63210022" x="57.770313" y="0.42049804" /><rect style="display:inline;fill:url(#linearGradient2);fill-opacity:1;stroke:#4389c4;stroke-width:0.660136;stroke-dasharray:none;stroke-opacity:1" id="blue_border" width="58.077339" height="13.098192" x="0.33006763" y="0.33006743" ry="2.4354458" rx="2.6655314" inkscape:label="blue_border" sodipodi:insensitive="true" /><path d="m 3.4395815,12.699994 q -0.3174998,0 -0.5556246,-0.238125 Q 2.6458321,12.223744 2.6458321,11.906244 V 1.8520824 q 0,-0.3174998 0.2381248,-0.5556247 0.2381248,-0.2381249 0.5556246,-0.2381249 h 5.8208322 q 0.3175013,0 0.5556257,0.2381249 0.2381266,0.2381249 0.2381266,0.5556247 V 11.906244 q 0,0.3175 -0.2381266,0.555625 -0.2381244,0.238125 -0.5556257,0.238125 z m 0,-1.190624 v 0.396874 H 9.2604137 V 11.50937 Z m 0,-0.79375 H 9.2604137 V 3.0427069 H 3.4395815 Z m 0,-8.4666627 H 9.2604137 V 1.8520824 H 3.4395815 Z m 0,0 V 1.8520824 Z m 0,9.2604127 v 0.396874 z" id="path1" style="stroke-width:0.0132292" sodipodi:insensitive="true" /></g></svg>'
info_svg = b'<?xml version="1.0" encoding="UTF-8" standalone="no"?> <svg height="48" viewBox="0 -960 960 960" width="48" version="1.1" id="svg1" sodipodi:docname="info_edited1.svg" inkscape:version="1.3 (0e150ed6c4, 2023-07-21)" xml:space="preserve" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" xmlns:svg="http://www.w3.org/2000/svg"><defs id="defs1"><linearGradient id="swatch2" inkscape:swatch="solid"><stop style="stop-color:#000000;stop-opacity:0;" offset="0" id="stop2" /></linearGradient><linearGradient inkscape:collect="always" xlink:href="#swatch2" id="linearGradient2" x1="0.15625" y1="-479.92862" x2="959.99872" y2="-479.92862" gradientUnits="userSpaceOnUse" /></defs><sodipodi:namedview id="namedview1" pagecolor="#ffffff" bordercolor="#000000" borderopacity="0.25" inkscape:showpageshadow="2" inkscape:pageopacity="0.0" inkscape:pagecheckerboard="0" inkscape:deskcolor="#d1d1d1" inkscape:zoom="8" inkscape:cx="19.6875" inkscape:cy="17.0625" inkscape:window-width="1920" inkscape:window-height="986" inkscape:window-x="-11" inkscape:window-y="-11" inkscape:window-maximized="1" inkscape:current-layer="svg1" /><rect style="fill:none;fill-opacity:0;stroke:#1f1f1f;stroke-width:40;stroke-dasharray:none" id="rect1" width="58.75" height="39.375" x="870" y="-937.5" ry="14.6875" /><rect style="fill:none;fill-opacity:0;stroke:#1f1f1f;stroke-width:40;stroke-dasharray:none" id="rect1-8" width="58.75" height="39.375" x="876.875" y="-60.625" ry="14.6875" /><rect style="fill:none;fill-opacity:0;stroke:#1f1f1f;stroke-width:40;stroke-dasharray:none" id="rect1-2" width="58.75" height="39.375" x="21.25" y="-61.875" ry="14.6875" /><rect style="fill:none;fill-opacity:0;stroke:#1f1f1f;stroke-width:40;stroke-dasharray:none" id="rect1-6" width="58.75" height="39.375" x="21.875" y="-935" ry="14.6875" /><rect style="display:inline;fill:#1f1f1f;fill-opacity:0;stroke:#1f1f1f;stroke-width:40.0797;stroke-dasharray:none;stroke-opacity:1" id="corner_fill" width="919.92035" height="919.92035" x="20.039835" y="-939.96021" ry="0" rx="0" /><rect style="display:inline;fill:url(#linearGradient2);fill-opacity:1;stroke:#4389c4;stroke-width:35;stroke-dasharray:none;stroke-opacity:1" id="blue_border" width="919.93054" height="919.91833" x="20.059727" y="-939.94025" ry="179.25378" rx="179.25378" inkscape:label="blue_border" sodipodi:insensitive="true" /><path d="m 453,-280 h 60 v -240 h -60 z m 26.982,-314 q 14.018,0 23.518,-9.2 9.5,-9.2 9.5,-22.8 0,-14.45 -9.482,-24.225 -9.483,-9.775 -23.5,-9.775 -14.018,0 -23.518,9.775 -9.5,9.775 -9.5,24.225 0,13.6 9.482,22.8 9.483,9.2 23.5,9.2 z m 0.284,514 q -82.734,0 -155.5,-31.5 Q 252,-143 197.5,-197.5 143,-252 111.5,-324.841 80,-397.681 80,-480.5 80,-563.319 111.5,-636.159 143,-709 197.5,-763 252,-817 324.841,-848.5 397.681,-880 480.5,-880 q 82.819,0 155.659,31.5 Q 709,-817 763,-763 q 54,54 85.5,127 31.5,73 31.5,155.734 0,82.734 -31.5,155.5 Q 817,-252 763,-197.684 q -54,54.316 -127,86 Q 563,-80 480.266,-80 Z m 0.234,-60 q 141.5,0 240.5,-99.5 99,-99.5 99,-241 Q 820,-622 721.188,-721 622.375,-820 480,-820 339,-820 239.5,-721.188 140,-622.375 140,-480 q 0,141 99.5,240.5 99.5,99.5 241,99.5 z M 480,-480 Z" id="path1" fill="#ffffff"/></svg>'
kill_svg = b'<?xml version="1.0" encoding="UTF-8" standalone="no"?> <svg height="48" viewBox="0 -960 960 960" width="48" version="1.1" id="svg1" sodipodi:docname="cancel_edited1.svg" inkscape:version="1.3 (0e150ed6c4, 2023-07-21)" xml:space="preserve" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" xmlns:svg="http://www.w3.org/2000/svg"><defs id="defs1"><linearGradient id="swatch2" inkscape:swatch="solid"><stop style="stop-color:#000000;stop-opacity:0;" offset="0" id="stop2" /></linearGradient><linearGradient inkscape:collect="always" xlink:href="#swatch2" id="linearGradient2" x1="0.15625" y1="-479.92862" x2="959.99872" y2="-479.92862" gradientUnits="userSpaceOnUse" /></defs><sodipodi:namedview id="namedview1" pagecolor="#ffffff" bordercolor="#000000" borderopacity="0.25" inkscape:showpageshadow="2" inkscape:pageopacity="0.0" inkscape:pagecheckerboard="0" inkscape:deskcolor="#d1d1d1" inkscape:zoom="8" inkscape:cx="19.6875" inkscape:cy="17.0625" inkscape:window-width="1920" inkscape:window-height="986" inkscape:window-x="-11" inkscape:window-y="-11" inkscape:window-maximized="1" inkscape:current-layer="svg1" /><rect style="fill:none;fill-opacity:0;stroke:#1f1f1f;stroke-width:40;stroke-dasharray:none" id="rect1" width="58.75" height="39.375" x="870" y="-937.5" ry="14.6875" /><rect style="fill:none;fill-opacity:0;stroke:#1f1f1f;stroke-width:40;stroke-dasharray:none" id="rect1-8" width="58.75" height="39.375" x="876.875" y="-60.625" ry="14.6875" /><rect style="fill:none;fill-opacity:0;stroke:#1f1f1f;stroke-width:40;stroke-dasharray:none" id="rect1-2" width="58.75" height="39.375" x="21.25" y="-61.875" ry="14.6875" /><rect style="fill:none;fill-opacity:0;stroke:#1f1f1f;stroke-width:40;stroke-dasharray:none" id="rect1-6" width="58.75" height="39.375" x="21.875" y="-935" ry="14.6875" /><rect style="display:inline;fill:#1f1f1f;fill-opacity:0;stroke:#1f1f1f;stroke-width:40.0797;stroke-dasharray:none;stroke-opacity:1" id="corner_fill" width="919.92035" height="919.92035" x="20.039835" y="-939.96021" ry="0" rx="0" /><rect style="display:inline;fill:url(#linearGradient2);fill-opacity:1;stroke:#4389c4;stroke-width:35;stroke-dasharray:none;stroke-opacity:1" id="blue_border" width="919.93054" height="919.91833" x="20.059727" y="-939.94025" ry="179.25378" rx="179.25378" inkscape:label="blue_border" sodipodi:insensitive="true" /><path d="m 330,-288 150,-150 150,150 42,-42 -150,-150 150,-150 -42,-42 -150,150 -150,-150 -42,42 150,150 -150,150 z m 150,208 q -82,0 -155,-31.5 -73,-31.5 -127.5,-86 Q 143,-252 111.5,-325 80,-398 80,-480 q 0,-83 31.5,-156 31.5,-73 86,-127 54.5,-54 127.5,-85.5 73,-31.5 155,-31.5 83,0 156,31.5 73,31.5 127,85.5 54,54 85.5,127 31.5,73 31.5,156 0,82 -31.5,155 -31.5,73 -85.5,127.5 -54,54.5 -127,86 Q 563,-80 480,-80 Z m 0,-60 q 142,0 241,-99.5 99,-99.5 99,-240.5 0,-142 -99,-241 -99,-99 -241,-99 -141,0 -240.5,99 -99.5,99 -99.5,241 0,141 99.5,240.5 Q 339,-140 480,-140 Z m 0,-340 z" id="path1" fill="#ffffff"/></svg>'
dark_mode_svg = b'<?xml version="1.0" encoding="UTF-8" standalone="no"?> <svg height="48" viewBox="0 -960 960 960" width="48" version="1.1" id="svg1" sodipodi:docname="dark_mode_edited1.svg" inkscape:version="1.3 (0e150ed6c4, 2023-07-21)" xml:space="preserve" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" xmlns:svg="http://www.w3.org/2000/svg"><defs id="defs1"><linearGradient id="swatch2" inkscape:swatch="solid"><stop style="stop-color:#000000;stop-opacity:0;" offset="0" id="stop2" /></linearGradient><linearGradient inkscape:collect="always" xlink:href="#swatch2" id="linearGradient2" x1="0.15625" y1="-479.92862" x2="959.99872" y2="-479.92862" gradientUnits="userSpaceOnUse" /></defs><sodipodi:namedview id="namedview1" pagecolor="#ffffff" bordercolor="#000000" borderopacity="0.25" inkscape:showpageshadow="2" inkscape:pageopacity="0.0" inkscape:pagecheckerboard="0" inkscape:deskcolor="#d1d1d1" inkscape:zoom="8" inkscape:cx="19.6875" inkscape:cy="17.0625" inkscape:window-width="1920" inkscape:window-height="986" inkscape:window-x="-11" inkscape:window-y="-11" inkscape:window-maximized="1" inkscape:current-layer="svg1" /><rect style="fill:none;fill-opacity:0;stroke:#1f1f1f;stroke-width:40;stroke-dasharray:none" id="rect1" width="58.75" height="39.375" x="870" y="-937.5" ry="14.6875" /><rect style="fill:none;fill-opacity:0;stroke:#1f1f1f;stroke-width:40;stroke-dasharray:none" id="rect1-8" width="58.75" height="39.375" x="876.875" y="-60.625" ry="14.6875" /><rect style="fill:none;fill-opacity:0;stroke:#1f1f1f;stroke-width:40;stroke-dasharray:none" id="rect1-2" width="58.75" height="39.375" x="21.25" y="-61.875" ry="14.6875" /><rect style="fill:none;fill-opacity:0;stroke:#1f1f1f;stroke-width:40;stroke-dasharray:none" id="rect1-6" width="58.75" height="39.375" x="21.875" y="-935" ry="14.6875" /><rect style="display:inline;fill:#1f1f1f;fill-opacity:0;stroke:#1f1f1f;stroke-width:40.0797;stroke-dasharray:none;stroke-opacity:1" id="corner_fill" width="919.92035" height="919.92035" x="20.039835" y="-939.96021" ry="0" rx="0" /><rect style="display:inline;fill:url(#linearGradient2);fill-opacity:1;stroke:#4389c4;stroke-width:35;stroke-dasharray:none;stroke-opacity:1" id="blue_border" width="919.93054" height="919.91833" x="20.059727" y="-939.94025" ry="179.25378" rx="179.25378" inkscape:label="blue_border" sodipodi:insensitive="true" /><path d="m 480,-120 q -150,0 -255,-105 -105,-105 -105,-255 0,-150 105,-255 105,-105 255,-105 8,0 17,0.5 9,0.5 23,1.5 -36,32 -56,79 -20,47 -20,99 0,90 63,153 63,63 153,63 52,0 99,-18.5 47,-18.5 79,-51.5 1,12 1.5,19.5 0.5,7.5 0.5,14.5 0,150 -105,255 -105,105 -255,105 z m 0,-60 q 109,0 190,-67.5 81,-67.5 101,-158.5 -25,11 -53.667,16.5 Q 688.667,-384 660,-384 545.311,-384 464.655,-464.655 384,-545.311 384,-660 q 0,-24 5,-51.5 5,-27.5 18,-62.5 -98,27 -162.5,109.5 Q 180,-582 180,-480 q 0,125 87.5,212.5 Q 355,-180 480,-180 Z m -4,-297 z" id="path1" fill="#ffffff"/></svg>'
refresh_svg = b'<?xml version="1.0" encoding="UTF-8" standalone="no"?> <svg height="48" viewBox="0 -960 960 960" width="48" version="1.1" id="svg1" sodipodi:docname="refresh_edited1.svg" inkscape:version="1.3 (0e150ed6c4, 2023-07-21)" xml:space="preserve" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" xmlns:svg="http://www.w3.org/2000/svg"><defs   id="defs1"><linearGradient     id="swatch2"     inkscape:swatch="solid"><stop       style="stop-color:#000000;stop-opacity:0;"       offset="0"       id="stop2" /></linearGradient><linearGradient     inkscape:collect="always"     xlink:href="#swatch2"     id="linearGradient2"     x1="0.15625"     y1="-479.92862"     x2="959.99872"     y2="-479.92862"     gradientUnits="userSpaceOnUse" /></defs><sodipodi:namedview   id="namedview1"   pagecolor="#ffffff"   bordercolor="#000000"   borderopacity="0.25"   inkscape:showpageshadow="2"   inkscape:pageopacity="0.0"   inkscape:pagecheckerboard="0"   inkscape:deskcolor="#d1d1d1"   inkscape:zoom="8"   inkscape:cx="19.6875"   inkscape:cy="17.0625"   inkscape:window-width="1920"   inkscape:window-height="986"   inkscape:window-x="-11"   inkscape:window-y="-11"   inkscape:window-maximized="1"   inkscape:current-layer="svg1" /><rect   style="fill:none;fill-opacity:0;stroke:#1f1f1f;stroke-width:40;stroke-dasharray:none"   id="rect1"   width="58.75"   height="39.375"   x="870"   y="-937.5"   ry="14.6875" /><rect   style="fill:none;fill-opacity:0;stroke:#1f1f1f;stroke-width:40;stroke-dasharray:none"   id="rect1-8"   width="58.75"   height="39.375"   x="876.875"   y="-60.625"   ry="14.6875" /><rect   style="fill:none;fill-opacity:0;stroke:#1f1f1f;stroke-width:40;stroke-dasharray:none"   id="rect1-2"   width="58.75"   height="39.375"   x="21.25"   y="-61.875"   ry="14.6875" /><rect   style="fill:none;fill-opacity:0;stroke:#1f1f1f;stroke-width:40;stroke-dasharray:none"   id="rect1-6"   width="58.75"   height="39.375"   x="21.875"   y="-935"   ry="14.6875" /><rect   style="display:inline;fill:#1f1f1f;fill-opacity:0;stroke:#1f1f1f;stroke-width:40.0797;stroke-dasharray:none;stroke-opacity:1"   id="corner_fill"   width="919.92035"   height="919.92035"   x="20.039835"   y="-939.96021"   ry="0"   rx="0" /><rect   style="display:inline;fill:url(#linearGradient2);fill-opacity:1;stroke:#4389c4;stroke-width:35;stroke-dasharray:none;stroke-opacity:1"   id="blue_border"   width="919.93054"   height="919.91833"   x="20.059727"   y="-939.94025"   ry="179.25378"   rx="179.25378"   inkscape:label="blue_border"   sodipodi:insensitive="true" /><path   d="M 480,-160 Q 347,-160 253.5,-253.5 160,-347 160,-480 160,-613 253.5,-706.5 347,-800 480,-800 q 85,0 149,34.5 64,34.5 111,94.5 v -129 h 60 v 254 H 546 v -60 h 168 q -38,-60 -97,-97 -59,-37 -137,-37 -109,0 -184.5,75.5 Q 220,-589 220,-480 q 0,109 75.5,184.5 75.5,75.5 184.5,75.5 83,0 152,-47.5 69,-47.5 96,-125.5 h 62 q -29,105 -115,169 -86,64 -195,64 z"   id="path1" fill="#ffffff"/></svg>'
settings_svg = b'<?xml version="1.0" encoding="UTF-8" standalone="no"?> <svg height="48" viewBox="0 -960 960 960" width="48" version="1.1" id="svg1" sodipodi:docname="settings_edited1.svg" inkscape:version="1.3 (0e150ed6c4, 2023-07-21)" xml:space="preserve" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" xmlns:svg="http://www.w3.org/2000/svg"><defs   id="defs1"><linearGradient     id="swatch2"     inkscape:swatch="solid"><stop       style="stop-color:#000000;stop-opacity:0;"       offset="0"       id="stop2" /></linearGradient><linearGradient     inkscape:collect="always"     xlink:href="#swatch2"     id="linearGradient2"     x1="0.15625"     y1="-479.92862"     x2="959.99872"     y2="-479.92862"     gradientUnits="userSpaceOnUse" /></defs><sodipodi:namedview   id="namedview1"   pagecolor="#ffffff"   bordercolor="#000000"   borderopacity="0.25"   inkscape:showpageshadow="2"   inkscape:pageopacity="0.0"   inkscape:pagecheckerboard="0"   inkscape:deskcolor="#d1d1d1"   inkscape:zoom="8"   inkscape:cx="19.6875"   inkscape:cy="17.0625"   inkscape:window-width="1920"   inkscape:window-height="986"   inkscape:window-x="-11"   inkscape:window-y="-11"   inkscape:window-maximized="1"   inkscape:current-layer="svg1" /><rect   style="fill:none;fill-opacity:0;stroke:#1f1f1f;stroke-width:40;stroke-dasharray:none"   id="rect1"   width="58.75"   height="39.375"   x="870"   y="-937.5"   ry="14.6875" /><rect   style="fill:none;fill-opacity:0;stroke:#1f1f1f;stroke-width:40;stroke-dasharray:none"   id="rect1-8"   width="58.75"   height="39.375"   x="876.875"   y="-60.625"   ry="14.6875" /><rect   style="fill:none;fill-opacity:0;stroke:#1f1f1f;stroke-width:40;stroke-dasharray:none"   id="rect1-2"   width="58.75"   height="39.375"   x="21.25"   y="-61.875"   ry="14.6875" /><rect   style="fill:none;fill-opacity:0;stroke:#1f1f1f;stroke-width:40;stroke-dasharray:none"   id="rect1-6"   width="58.75"   height="39.375"   x="21.875"   y="-935"   ry="14.6875" /><rect   style="display:inline;fill:#1f1f1f;fill-opacity:0;stroke:#1f1f1f;stroke-width:40.0797;stroke-dasharray:none;stroke-opacity:1"   id="corner_fill"   width="919.92035"   height="919.92035"   x="20.039835"   y="-939.96021"   ry="0"   rx="0" /><rect   style="display:inline;fill:url(#linearGradient2);fill-opacity:1;stroke:#4389c4;stroke-width:35;stroke-dasharray:none;stroke-opacity:1"   id="blue_border"   width="919.93054"   height="919.91833"   x="20.059727"   y="-939.94025"   ry="179.25378"   rx="179.25378"   inkscape:label="blue_border"   sodipodi:insensitive="true" /><path   d="m 388,-80 -20,-126 q -19,-7 -40,-19 -21,-12 -37,-25 l -118,54 -93,-164 108,-79 q -2,-9 -2.5,-20.5 -0.5,-11.5 -0.5,-20.5 0,-9 0.5,-20.5 0.5,-11.5 2.5,-20.5 l -108,-79 93,-164 118,54 q 16,-13 37,-25 21,-12 40,-18 l 20,-127 h 184 l 20,126 q 19,7 40.5,18.5 21.5,11.5 36.5,25.5 l 118,-54 93,164 -108,77 q 2,10 2.5,21.5 0.5,11.5 0.5,21.5 0,10 -0.5,21 -0.5,11 -2.5,21 l 108,78 -93,164 -118,-54 q -16,13 -36.5,25.5 Q 612,-212 592,-206 l -20,126 z m 92,-270 q 54,0 92,-38 38,-38 38,-92 0,-54 -38,-92 -38,-38 -92,-38 -54,0 -92,38 -38,38 -38,92 0,54 38,92 38,38 92,38 z m 0,-60 q -29,0 -49.5,-20.5 Q 410,-451 410,-480 q 0,-29 20.5,-49.5 20.5,-20.5 49.5,-20.5 29,0 49.5,20.5 20.5,20.5 20.5,49.5 0,29 -20.5,49.5 Q 509,-410 480,-410 Z m 0,-70 z m -44,340 h 88 l 14,-112 q 33,-8 62.5,-25 29.5,-17 53.5,-41 l 106,46 40,-72 -94,-69 q 4,-17 6.5,-33.5 2.5,-16.5 2.5,-33.5 0,-17 -2,-33.5 -2,-16.5 -7,-33.5 l 94,-69 -40,-72 -106,46 q -23,-26 -52,-43.5 -29,-17.5 -64,-22.5 l -14,-112 h -88 l -14,112 q -34,7 -63.5,24 -29.5,17 -52.5,42 l -106,-46 -40,72 94,69 q -4,17 -6.5,33.5 -2.5,16.5 -2.5,33.5 0,17 2.5,33.5 2.5,16.5 6.5,33.5 l -94,69 40,72 106,-46 q 24,24 53.5,41 29.5,17 62.5,25 z"   id="settings" fill="#ffffff"/></svg>'
back_svg = b'<?xml version="1.0" encoding="UTF-8" standalone="no"?> <svg height="48" viewBox="0 -960 960 960" width="48" version="1.1" id="svg1" sodipodi:docname="arrow_back_edited1.svg" inkscape:version="1.3 (0e150ed6c4, 2023-07-21)" xml:space="preserve" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" xmlns:svg="http://www.w3.org/2000/svg"><defs   id="defs1"><linearGradient     id="swatch2"     inkscape:swatch="solid"><stop       style="stop-color:#000000;stop-opacity:0;"       offset="0"       id="stop2" /></linearGradient><linearGradient     inkscape:collect="always"     xlink:href="#swatch2"     id="linearGradient2"     x1="0.15625"     y1="-479.92862"     x2="959.99872"     y2="-479.92862"     gradientUnits="userSpaceOnUse" /></defs><sodipodi:namedview   id="namedview1"   pagecolor="#ffffff"   bordercolor="#000000"   borderopacity="0.25"   inkscape:showpageshadow="2"   inkscape:pageopacity="0.0"   inkscape:pagecheckerboard="0"   inkscape:deskcolor="#d1d1d1"   inkscape:zoom="16"   inkscape:cx="9.84375"   inkscape:cy="21.09375"   inkscape:window-width="1920"   inkscape:window-height="986"   inkscape:window-x="-11"   inkscape:window-y="-11"   inkscape:window-maximized="1"   inkscape:current-layer="svg1" /><rect   style="fill:none;fill-opacity:0;stroke:#1f1f1f;stroke-width:40;stroke-dasharray:none"   id="rect1"   width="58.75"   height="39.375"   x="870"   y="-937.5"   ry="14.6875" /><rect   style="fill:none;fill-opacity:0;stroke:#1f1f1f;stroke-width:40;stroke-dasharray:none"   id="rect1-8"   width="58.75"   height="39.375"   x="876.875"   y="-60.625"   ry="14.6875" /><rect   style="fill:none;fill-opacity:0;stroke:#1f1f1f;stroke-width:40;stroke-dasharray:none"   id="rect1-2"   width="58.75"   height="39.375"   x="21.25"   y="-61.875"   ry="14.6875" /><rect   style="fill:none;fill-opacity:0;stroke:#1f1f1f;stroke-width:40;stroke-dasharray:none"   id="rect1-6"   width="58.75"   height="39.375"   x="21.875"   y="-935"   ry="14.6875" /><rect   style="display:inline;fill:#1f1f1f;fill-opacity:0;stroke:#1f1f1f;stroke-width:40.0797;stroke-dasharray:none;stroke-opacity:1"   id="corner_fill"   width="919.92035"   height="919.92035"   x="20.039835"   y="-939.96021"   ry="0"   rx="0" /><rect   style="display:inline;fill:url(#linearGradient2);fill-opacity:1;stroke:#4389c4;stroke-width:35;stroke-dasharray:none;stroke-opacity:1"   id="blue_border"   width="919.93054"   height="919.91833"   x="20.059727"   y="-939.94025"   ry="179.25378"   rx="179.25378"   inkscape:label="blue_border"   sodipodi:insensitive="true" /><path   d="m 274,-450 248,248 -42,42 -320,-320 320,-320 42,42 -248,248 h 526 v 60 z"   id="path1" fill="#ffffff"/></svg>'
shell_svg = b'<?xml version="1.0" encoding="UTF-8" standalone="no"?> <svg height="48" viewBox="0 -960 960 960" width="48" version="1.1" id="svg1" sodipodi:docname="terminal_edited4.svg" inkscape:version="1.3 (0e150ed6c4, 2023-07-21)" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" xmlns:svg="http://www.w3.org/2000/svg"> <defs   id="defs1">  <linearGradient     id="swatch2"     inkscape:swatch="solid">    <stop       style="stop-color:#000000;stop-opacity:0;"       offset="0"       id="stop2" />  </linearGradient>  <linearGradient     inkscape:collect="always"     xlink:href="#swatch2"     id="linearGradient2"     x1="0.15625"     y1="-479.92862"     x2="959.99872"     y2="-479.92862"     gradientUnits="userSpaceOnUse" /> </defs> <sodipodi:namedview   id="namedview1"   pagecolor="#ffffff"   bordercolor="#000000"   borderopacity="0.25"   inkscape:showpageshadow="2"   inkscape:pageopacity="0.0"   inkscape:pagecheckerboard="0"   inkscape:deskcolor="#d1d1d1"   inkscape:zoom="16"   inkscape:cx="9.84375"   inkscape:cy="31.09375"   inkscape:window-width="1920"   inkscape:window-height="986"   inkscape:window-x="-11"   inkscape:window-y="-11"   inkscape:window-maximized="1"   inkscape:current-layer="svg1" /> <rect   style="fill:none;fill-opacity:0;stroke:#1f1f1f;stroke-width:40;stroke-dasharray:none"   id="rect1"   width="58.75"   height="39.375"   x="870"   y="-937.5"   ry="14.6875" /> <rect   style="fill:none;fill-opacity:0;stroke:#1f1f1f;stroke-width:40;stroke-dasharray:none"   id="rect1-8"   width="58.75"   height="39.375"   x="876.875"   y="-60.625"   ry="14.6875" /> <rect   style="fill:none;fill-opacity:0;stroke:#1f1f1f;stroke-width:40;stroke-dasharray:none"   id="rect1-2"   width="58.75"   height="39.375"   x="21.25"   y="-61.875"   ry="14.6875" /> <rect   style="fill:none;fill-opacity:0;stroke:#1f1f1f;stroke-width:40;stroke-dasharray:none"   id="rect1-6"   width="58.75"   height="39.375"   x="21.875"   y="-935"   ry="14.6875" /> <rect   style="display:inline;fill:#1f1f1f;fill-opacity:0;stroke:#1f1f1f;stroke-width:40.0797;stroke-dasharray:none;stroke-opacity:1"   id="corner_fill"   width="919.92035"   height="919.92035"   x="20.039835"   y="-939.96021"   ry="0"   rx="0" /> <rect   style="display:inline;fill:url(#linearGradient2);fill-opacity:1;stroke:#4389c4;stroke-width:35;stroke-dasharray:none;stroke-opacity:1"   id="blue_border"   width="919.93054"   height="919.91833"   x="20.059727"   y="-939.94025"   ry="179.25378"   rx="179.25378"   inkscape:label="blue_border"   sodipodi:insensitive="true" /> <path   d="m 140,-160 q -24,0 -42,-18 -18,-18 -18,-42 v -520 q 0,-24 18,-42 18,-18 42,-18 h 680 q 24,0 42,18 18,18 18,42 v 520 q 0,24 -18,42 -18,18 -42,18 z m 0,-60 H 820 V -656 H 140 Z m 160,-72 -42,-42 103,-104 -104,-104 43,-42 146,146 z m 190,4 v -60 h 220 v 60 z"   id="terminal_file"   sodipodi:insensitive="true" fill="#ffffff"/> </svg>'
screen_share_scrcpy_svg = b'<?xml version="1.0" encoding="UTF-8" standalone="no"?> <svg height="48" viewBox="0 -960 960 960" width="48" version="1.1" id="svg1" sodipodi:docname="mobile_screen_share edited2.svg" inkscape:version="1.3 (0e150ed6c4, 2023-07-21)" xml:space="preserve" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" xmlns:svg="http://www.w3.org/2000/svg"><defs   id="defs1"><linearGradient     id="swatch2"     inkscape:swatch="solid"><stop       style="stop-color:#000000;stop-opacity:0;"       offset="0"       id="stop2" /></linearGradient><linearGradient     inkscape:collect="always"     xlink:href="#swatch2"     id="linearGradient2"     x1="0.15625"     y1="-479.92862"     x2="959.99872"     y2="-479.92862"     gradientUnits="userSpaceOnUse" /></defs><sodipodi:namedview   id="namedview1"   pagecolor="#ffffff"   bordercolor="#000000"   borderopacity="0.25"   inkscape:showpageshadow="2"   inkscape:pageopacity="0.0"   inkscape:pagecheckerboard="0"   inkscape:deskcolor="#d1d1d1"   inkscape:zoom="16"   inkscape:cx="9.84375"   inkscape:cy="21.09375"   inkscape:window-width="1920"   inkscape:window-height="986"   inkscape:window-x="-11"   inkscape:window-y="-11"   inkscape:window-maximized="1"   inkscape:current-layer="svg1" /><rect   style="fill:none;fill-opacity:0;stroke:#1f1f1f;stroke-width:40;stroke-dasharray:none"   id="rect1"   width="58.75"   height="39.375"   x="870"   y="-937.5"   ry="14.6875" /><rect   style="fill:none;fill-opacity:0;stroke:#1f1f1f;stroke-width:40;stroke-dasharray:none"   id="rect1-8"   width="58.75"   height="39.375"   x="876.875"   y="-60.625"   ry="14.6875" /><rect   style="fill:none;fill-opacity:0;stroke:#1f1f1f;stroke-width:40;stroke-dasharray:none"   id="rect1-2"   width="58.75"   height="39.375"   x="21.25"   y="-61.875"   ry="14.6875" /><rect   style="fill:none;fill-opacity:0;stroke:#1f1f1f;stroke-width:40;stroke-dasharray:none"   id="rect1-6"   width="58.75"   height="39.375"   x="21.875"   y="-935"   ry="14.6875" /><rect   style="display:inline;fill:#1f1f1f;fill-opacity:0;stroke:#1f1f1f;stroke-width:40.0797;stroke-dasharray:none;stroke-opacity:1"   id="corner_fill"   width="919.92035"   height="919.92035"   x="20.039835"   y="-939.96021"   ry="0"   rx="0" /><rect   style="display:inline;fill:url(#linearGradient2);fill-opacity:1;stroke:#4389c4;stroke-width:35;stroke-dasharray:none;stroke-opacity:1"   id="blue_border"   width="919.93054"   height="919.91833"   x="20.059727"   y="-939.94025"   ry="179.25378"   rx="179.25378"   inkscape:label="blue_border"   sodipodi:insensitive="true" /><path   d="m 377.923,-364.463 v -53.307 q 0,-44.731 31.285,-74.519 31.285,-29.788 75.868,-29.788 h 46.077 v -56 l 78.691,78.691 -78.691,78.691 v -55.999 h -46.077 q -25.308,0 -43.539,17.143 -18.231,17.142 -18.231,41.781 v 53.307 z m -100.23,304.46 q -23.529,0 -40.611,-17.081 Q 220,-94.166 220,-117.695 v -724.612 q 0,-23.529 17.082,-40.611 Q 254.164,-900 277.693,-900 h 404.612 q 23.529,0 40.611,17.082 17.082,17.082 17.082,40.611 v 724.612 q 0,23.53 -17.082,40.61 -17.082,17.084 -40.611,17.084 H 277.693 Z m -12.309,-88.076 v 30.384 q 0,4.616 3.846,8.463 3.847,3.846 8.463,3.846 h 404.612 q 4.616,0 8.463,-3.846 3.846,-3.847 3.846,-8.463 v -30.384 z m 0,-45.384 h 429.23 v -573.076 h -429.23 z m 0,-618.46 h 429.23 v -30.384 q 0,-4.616 -3.846,-8.463 -3.847,-3.846 -8.463,-3.846 H 277.693 q -4.616,0 -8.463,3.846 -3.846,3.847 -3.846,8.463 z m 0,0 v -42.693 z m 0,663.844 v 42.693 z"   id="mobile_screen_share" fill="#ffffff"/></svg>'
wireless_pairing_svg = b'<?xml version="1.0" encoding="UTF-8" standalone="no"?> <svg height="48" viewBox="0 -960 960 960" width="48" version="1.1" id="svg1" sodipodi:docname="tap_and_play edited2.svg" inkscape:version="1.3 (0e150ed6c4, 2023-07-21)" xml:space="preserve" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" xmlns:svg="http://www.w3.org/2000/svg"><defs   id="defs1"><linearGradient     id="swatch2"     inkscape:swatch="solid"><stop       style="stop-color:#000000;stop-opacity:0;"       offset="0"       id="stop2" /></linearGradient><linearGradient     inkscape:collect="always"     xlink:href="#swatch2"     id="linearGradient2"     x1="0.15625"     y1="-479.92862"     x2="959.99872"     y2="-479.92862"     gradientUnits="userSpaceOnUse" /></defs><sodipodi:namedview   id="namedview1"   pagecolor="#ffffff"   bordercolor="#000000"   borderopacity="0.25"   inkscape:showpageshadow="2"   inkscape:pageopacity="0.0"   inkscape:pagecheckerboard="0"   inkscape:deskcolor="#d1d1d1"   inkscape:zoom="16"   inkscape:cx="9.84375"   inkscape:cy="26.09375"   inkscape:window-width="1920"   inkscape:window-height="986"   inkscape:window-x="-11"   inkscape:window-y="-11"   inkscape:window-maximized="1"   inkscape:current-layer="svg1" /><rect   style="fill:none;fill-opacity:0;stroke:#1f1f1f;stroke-width:40;stroke-dasharray:none"   id="rect1"   width="58.75"   height="39.375"   x="870"   y="-937.5"   ry="14.6875" /><rect   style="fill:none;fill-opacity:0;stroke:#1f1f1f;stroke-width:40;stroke-dasharray:none"   id="rect1-8"   width="58.75"   height="39.375"   x="876.875"   y="-60.625"   ry="14.6875" /><rect   style="fill:none;fill-opacity:0;stroke:#1f1f1f;stroke-width:40;stroke-dasharray:none"   id="rect1-2"   width="58.75"   height="39.375"   x="21.25"   y="-61.875"   ry="14.6875" /><rect   style="fill:none;fill-opacity:0;stroke:#1f1f1f;stroke-width:40;stroke-dasharray:none"   id="rect1-6"   width="58.75"   height="39.375"   x="21.875"   y="-935"   ry="14.6875" /><rect   style="display:inline;fill:#1f1f1f;fill-opacity:0;stroke:#1f1f1f;stroke-width:40.0797;stroke-dasharray:none;stroke-opacity:1"   id="corner_fill"   width="919.92035"   height="919.92035"   x="20.039835"   y="-939.96021"   ry="0"   rx="0" /><rect   style="display:inline;fill:url(#linearGradient2);fill-opacity:1;stroke:#4389c4;stroke-width:35;stroke-dasharray:none;stroke-opacity:1"   id="blue_border"   width="919.93054"   height="919.91833"   x="20.059727"   y="-939.94025"   ry="179.25378"   rx="179.25378"   inkscape:label="blue_border"   sodipodi:insensitive="true" /><path   d="m 649.614,-60.003 v -45.383 h 32.691 q 4.616,0 8.463,-3.846 3.846,-3.847 3.846,-8.463 v -648.844 h -429.23 v 276.923 H 220 v -352.691 q 0,-23.529 17.082,-40.611 Q 254.164,-900 277.693,-900 h 404.612 q 23.529,0 40.611,17.082 17.082,17.082 17.082,40.611 v 724.612 q 0,23.53 -17.082,40.61 -17.082,17.084 -40.611,17.084 h -32.691 z m -429.614,0 v -122.688 q 51.538,0 87.114,35.576 35.576,35.576 35.576,87.114 H 220 Z m 195.768,0 q 0,-81.922 -56.922,-138.845 Q 301.923,-255.77 220,-255.77 v -45.384 q 99.967,0 170.56,70.592 70.592,70.593 70.592,170.56 h -45.384 z m 118.462,0 q 0,-131.153 -91.434,-222.691 Q 351.363,-374.232 220,-374.232 v -45.383 q 74.627,0 140.255,28.342 65.629,28.343 114.155,76.875 48.526,48.533 76.864,114.17 28.339,65.637 28.339,140.226 H 534.23 Z m -268.846,-751.92 h 429.23 v -30.384 q 0,-4.616 -3.846,-8.463 -3.847,-3.846 -8.463,-3.846 H 277.693 q -4.616,0 -8.463,3.846 -3.846,3.847 -3.846,8.463 z m 0,0 v -42.693 z"   id="tap_and_play" fill="#ffffff"/></svg>'
wireless_tcpip_svg = b'<?xml version="1.0" encoding="UTF-8" standalone="no"?> <svg height="48" viewBox="0 -960 960 960" width="48" version="1.1" id="svg1" sodipodi:docname="tap_and_play edited2.svg" inkscape:version="1.3 (0e150ed6c4, 2023-07-21)" xml:space="preserve" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" xmlns:svg="http://www.w3.org/2000/svg"><defs   id="defs1"><linearGradient     id="swatch2"     inkscape:swatch="solid"><stop       style="stop-color:#000000;stop-opacity:0;"       offset="0"       id="stop2" /></linearGradient><linearGradient     inkscape:collect="always"     xlink:href="#swatch2"     id="linearGradient2"     x1="0.15625"     y1="-479.92862"     x2="959.99872"     y2="-479.92862"     gradientUnits="userSpaceOnUse" /></defs><sodipodi:namedview   id="namedview1"   pagecolor="#ffffff"   bordercolor="#000000"   borderopacity="0.25"   inkscape:showpageshadow="2"   inkscape:pageopacity="0.0"   inkscape:pagecheckerboard="0"   inkscape:deskcolor="#d1d1d1"   inkscape:zoom="16"   inkscape:cx="9.84375"   inkscape:cy="26.09375"   inkscape:window-width="1920"   inkscape:window-height="986"   inkscape:window-x="-11"   inkscape:window-y="-11"   inkscape:window-maximized="1"   inkscape:current-layer="svg1" /><rect   style="fill:none;fill-opacity:0;stroke:#1f1f1f;stroke-width:40;stroke-dasharray:none"   id="rect1"   width="58.75"   height="39.375"   x="870"   y="-937.5"   ry="14.6875" /><rect   style="fill:none;fill-opacity:0;stroke:#1f1f1f;stroke-width:40;stroke-dasharray:none"   id="rect1-8"   width="58.75"   height="39.375"   x="876.875"   y="-60.625"   ry="14.6875" /><rect   style="fill:none;fill-opacity:0;stroke:#1f1f1f;stroke-width:40;stroke-dasharray:none"   id="rect1-2"   width="58.75"   height="39.375"   x="21.25"   y="-61.875"   ry="14.6875" /><rect   style="fill:none;fill-opacity:0;stroke:#1f1f1f;stroke-width:40;stroke-dasharray:none"   id="rect1-6"   width="58.75"   height="39.375"   x="21.875"   y="-935"   ry="14.6875" /><rect   style="display:inline;fill:#1f1f1f;fill-opacity:0;stroke:#1f1f1f;stroke-width:40.0797;stroke-dasharray:none;stroke-opacity:1"   id="corner_fill"   width="919.92035"   height="919.92035"   x="20.039835"   y="-939.96021"   ry="0"   rx="0" /><rect   style="display:inline;fill:url(#linearGradient2);fill-opacity:1;stroke:#4389c4;stroke-width:35;stroke-dasharray:none;stroke-opacity:1"   id="blue_border"   width="919.93054"   height="919.91833"   x="20.059727"   y="-939.94025"   ry="179.25378"   rx="179.25378"   inkscape:label="blue_border"   sodipodi:insensitive="true" /><path   d="m 730.459,-367.002 -31.614,-31.999 q 17.769,-16.231 27.731,-37.305 9.961,-21.074 9.961,-45.118 0,-23.577 -9.631,-45.216 -9.631,-21.64 -27.446,-38.207 l 30.999,-31.615 q 23.846,22.308 37.654,51.832 13.808,29.525 13.808,62.308 0,32.782 -13.808,62.705 -13.808,29.923 -37.654,52.615 z m 81.692,81.308 -31.383,-31.615 q 33,-32.849 50.73,-75.201 17.731,-42.351 17.731,-88.652 0,-46.3 -18.731,-88.723 -18.73,-42.423 -54.807,-71.808 l 34.845,-34.845 q 40.889,38.863 62.483,89.248 21.594,50.384 21.594,106.674 0,55.769 -21.27,106.085 -21.269,50.316 -61.192,88.837 z M 277.693,-60.003 q -23.596,0 -40.645,-17.047 Q 220,-94.098 220,-117.695 v -724.612 q 0,-23.596 17.048,-40.645 Q 254.097,-900 277.693,-900 h 404.612 q 23.596,0 40.645,17.048 17.048,17.049 17.048,40.645 v 135.999 h -45.384 v -60.231 h -429.23 v 573.076 h 429.23 v -60.231 h 45.384 v 135.999 q 0,23.597 -17.048,40.645 -17.049,17.048 -40.645,17.048 H 277.693 Z m -12.309,-88.076 v 30.384 q 0,4.616 3.846,8.463 3.847,3.846 8.463,3.846 h 404.612 q 4.616,0 8.463,-3.846 3.846,-3.847 3.846,-8.463 v -30.384 z m 0,-663.844 h 429.23 v -30.384 q 0,-4.616 -3.846,-8.463 -3.847,-3.846 -8.463,-3.846 H 277.693 q -4.616,0 -8.463,3.846 -3.846,3.847 -3.846,8.463 z m 0,0 v -42.693 z m 0,663.844 v 42.693 z"   id="phonelink_ring" fill="#ffffff"/></svg>'
file_upload_svg = b'<?xml version="1.0" encoding="UTF-8" standalone="no"?> <svg height="48" viewBox="0 -960 960 960" width="48" version="1.1" id="svg1" sodipodi:docname="upload_file_edited2.svg" inkscape:version="1.3 (0e150ed6c4, 2023-07-21)" xml:space="preserve" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" xmlns:svg="http://www.w3.org/2000/svg"><defs   id="defs1"><linearGradient     id="swatch2"     inkscape:swatch="solid"><stop       style="stop-color:#000000;stop-opacity:0;"       offset="0"       id="stop2" /></linearGradient><linearGradient     inkscape:collect="always"     xlink:href="#swatch2"     id="linearGradient2"     x1="0.15625"     y1="-479.92862"     x2="959.99872"     y2="-479.92862"     gradientUnits="userSpaceOnUse" /></defs><sodipodi:namedview   id="namedview1"   pagecolor="#ffffff"   bordercolor="#000000"   borderopacity="0.25"   inkscape:showpageshadow="2"   inkscape:pageopacity="0.0"   inkscape:pagecheckerboard="0"   inkscape:deskcolor="#d1d1d1"   inkscape:zoom="16"   inkscape:cx="21.84375"   inkscape:cy="21.09375"   inkscape:window-width="1920"   inkscape:window-height="986"   inkscape:window-x="-11"   inkscape:window-y="-11"   inkscape:window-maximized="1"   inkscape:current-layer="svg1" /><rect   style="fill:none;fill-opacity:0;stroke:#1f1f1f;stroke-width:40;stroke-dasharray:none"   id="rect1"   width="58.75"   height="39.375"   x="870"   y="-937.5"   ry="14.6875" /><rect   style="fill:none;fill-opacity:0;stroke:#1f1f1f;stroke-width:40;stroke-dasharray:none"   id="rect1-8"   width="58.75"   height="39.375"   x="876.875"   y="-60.625"   ry="14.6875" /><rect   style="fill:none;fill-opacity:0;stroke:#1f1f1f;stroke-width:40;stroke-dasharray:none"   id="rect1-2"   width="58.75"   height="39.375"   x="21.25"   y="-61.875"   ry="14.6875" /><rect   style="fill:none;fill-opacity:0;stroke:#1f1f1f;stroke-width:40;stroke-dasharray:none"   id="rect1-6"   width="58.75"   height="39.375"   x="21.875"   y="-935"   ry="14.6875" /><rect   style="display:inline;fill:#1f1f1f;fill-opacity:0;stroke:#1f1f1f;stroke-width:40.0797;stroke-dasharray:none;stroke-opacity:1"   id="corner_fill"   width="919.92035"   height="919.92035"   x="20.039835"   y="-939.96021"   ry="0"   rx="0" /><rect   style="display:inline;fill:url(#linearGradient2);fill-opacity:1;stroke:#4389c4;stroke-width:35;stroke-dasharray:none;stroke-opacity:1"   id="blue_border"   width="919.93054"   height="919.91833"   x="20.059727"   y="-939.94025"   ry="179.25378"   rx="179.25378"   inkscape:label="blue_border"   sodipodi:insensitive="true" /><path   d="m 457.307,-323.386 v -368.693 l -110.384,110 -32.614,-32.23 165.69,-165.691 165.69,165.691 -32.614,32.23 -110.384,-110 v 368.693 z m -219.614,143.384 q -23.529,0 -40.611,-17.082 Q 180,-214.166 180,-237.695 v -125.306 h 45.384 v 125.306 q 0,4.616 3.846,8.463 3.847,3.846 8.463,3.846 h 484.612 q 4.616,0 8.463,-3.846 3.846,-3.847 3.846,-8.463 v -125.306 h 45.384 v 125.306 q 0,23.529 -17.082,40.611 -17.082,17.082 -40.611,17.082 z"   id="file_upload" fill="#ffffff"/></svg>'
file_download_svg = b'<?xml version="1.0" encoding="UTF-8" standalone="no"?> <svg height="48" viewBox="0 -960 960 960" width="48" version="1.1" id="svg1" sodipodi:docname="download_file_edited2.svg" inkscape:version="1.3 (0e150ed6c4, 2023-07-21)" xml:space="preserve" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" xmlns:svg="http://www.w3.org/2000/svg"><defs   id="defs1"><linearGradient     id="swatch2"     inkscape:swatch="solid"><stop       style="stop-color:#000000;stop-opacity:0;"       offset="0"       id="stop2" /></linearGradient><linearGradient     inkscape:collect="always"     xlink:href="#swatch2"     id="linearGradient2"     x1="0.15625"     y1="-479.92862"     x2="959.99872"     y2="-479.92862"     gradientUnits="userSpaceOnUse" /></defs><sodipodi:namedview   id="namedview1"   pagecolor="#ffffff"   bordercolor="#000000"   borderopacity="0.25"   inkscape:showpageshadow="2"   inkscape:pageopacity="0.0"   inkscape:pagecheckerboard="0"   inkscape:deskcolor="#d1d1d1"   inkscape:zoom="16"   inkscape:cx="9.84375"   inkscape:cy="31.09375"   inkscape:window-width="1920"   inkscape:window-height="986"   inkscape:window-x="-11"   inkscape:window-y="-11"   inkscape:window-maximized="1"   inkscape:current-layer="svg1" /><rect   style="fill:none;fill-opacity:0;stroke:#1f1f1f;stroke-width:40;stroke-dasharray:none"   id="rect1"   width="58.75"   height="39.375"   x="870"   y="-937.5"   ry="14.6875" /><rect   style="fill:none;fill-opacity:0;stroke:#1f1f1f;stroke-width:40;stroke-dasharray:none"   id="rect1-8"   width="58.75"   height="39.375"   x="876.875"   y="-60.625"   ry="14.6875" /><rect   style="fill:none;fill-opacity:0;stroke:#1f1f1f;stroke-width:40;stroke-dasharray:none"   id="rect1-2"   width="58.75"   height="39.375"   x="21.25"   y="-61.875"   ry="14.6875" /><rect   style="fill:none;fill-opacity:0;stroke:#1f1f1f;stroke-width:40;stroke-dasharray:none"   id="rect1-6"   width="58.75"   height="39.375"   x="21.875"   y="-935"   ry="14.6875" /><rect   style="display:inline;fill:#1f1f1f;fill-opacity:0;stroke:#1f1f1f;stroke-width:40.0797;stroke-dasharray:none;stroke-opacity:1"   id="corner_fill"   width="919.92035"   height="919.92035"   x="20.039835"   y="-939.96021"   ry="0"   rx="0" /><rect   style="display:inline;fill:url(#linearGradient2);fill-opacity:1;stroke:#4389c4;stroke-width:35;stroke-dasharray:none;stroke-opacity:1"   id="blue_border"   width="919.93054"   height="919.91833"   x="20.059727"   y="-939.94025"   ry="179.25378"   rx="179.25378"   inkscape:label="blue_border"   sodipodi:insensitive="true" /><path   d="m 479.999,-323.386 -165.69,-165.691 32.614,-32.23 110.384,110 V -780 h 45.384 v 368.693 l 110.384,-110 32.614,32.23 z m -242.306,143.384 q -23.529,0 -40.611,-17.082 Q 180,-214.166 180,-237.695 v -125.306 h 45.384 v 125.306 q 0,4.616 3.846,8.463 3.847,3.846 8.463,3.846 h 484.612 q 4.616,0 8.463,-3.846 3.846,-3.847 3.846,-8.463 v -125.306 h 45.384 v 125.306 q 0,23.529 -17.082,40.611 -17.082,17.082 -40.611,17.082 z"   id="path1" fill="#ffffff"/></svg>'
current_mode_svg = dark_mode_svg

def debounce(func, wait):
    def debounced(event):
        global after_id
        try:
            main_window.after_cancel(after_id)
        except ValueError:
            pass
        after_id = main_window.after(wait, func, event)
    return debounced

after_id = None
resize_debounced = debounce(resize_maintain, 100) 


devices_list.bind("<<ListboxSelect>>",check_keyword)
main_window.bind("<Escape>", ask_4_exit)
main_window.bind("<F5>", lambda event : threading.Thread(target=re_checkup,daemon=True).start())
main_window.bind("<F4>", lambda event: threading.Thread(target=kill_process,daemon=True).start())
main_window.bind("<Configure>",resize_debounced)
main_window.bind("<Button-1>",keep_flat)


widgets_interactive_highlight = (preferred_interface_any_checkbox, preferred_interface_wireless_checkbox, preferred_interface_wired_checkbox, device_screen_state_box, network_ping_check_state_box, ip_validation_check_state_box, screen_share_scrcpy_btn, wireless_tcpip_btn, shell_btn, wireless_pairing_btn, file_download_btn, file_upload_btn, file_downloading_btn, kill_btn, background_color_btn, devices_refresh_btn, unauthorized_noti_btn, offline_noti_btn, permission_error_btn, running_with_errors_btn, settings_btn, preferred_interface_info_btn, pairing_info_btn, settings_back_btn, wireless_back_btn, network_refresh_btn, PIN_pair_option_btn, QR_pair_option_btn)

for widget in widgets_interactive_highlight:
    widget.bind("<Enter>", hover_highlight)
    widget.bind("<Leave>",hover_unhighlight)

def hover_highlight_pin(event :Event):
    PIN_devices_label.configure(background="#333333")
    ip_label.configure(background="#333333")


def hover_unhighlight_pin(event :Event):
    PIN_devices_label.configure(background="#1f1f1f")
    ip_label.configure(background="#1f1f1f")

def hover_highlight_connect_pair(event : Event):
    connect_pairing_btn.configure(bg="#333333",activebackground="#333333")

def hover_unhighlight_connect_pair(event : Event):
    connect_pairing_btn.configure(bg="#1f1f1f",activebackground="#1f1f1f")


PIN_devices_label.bind("<Enter>", hover_highlight_pin)
PIN_devices_label.bind("<Leave>",hover_unhighlight_pin)

PIN_devices_label.bind("<Button-1>",pin_pair_address_completion)
ip_label.bind("<Button-1>",pin_pair_address_completion)

connect_pairing_btn.bind("<Enter>", hover_highlight_connect_pair)
connect_pairing_btn.bind("<Leave>",hover_unhighlight_connect_pair)

validation_port = wireless_pairing_frame.register(validate_port_pin_pairing)
validation_addr = wireless_pairing_frame.register(validate_address_pin_pairing)
validation_pin = wireless_pairing_frame.register(validate_pin_code_pairing)

address_box_pairing_address = Entry(wireless_pairing_frame,width=16,font='Terminal',validate='key',validatecommand=(validation_addr,"%P"),bd=3,bg="#3a3a3a",fg="#ffffff", highlightthickness=0, highlightbackground="#1f1f1f",disabledbackground="#3a3a3a",disabledforeground="#ffffff")
address_box_pairing_port = Entry(wireless_pairing_frame,width=6,font='Terminal',validate='key',validatecommand=(validation_port,"%P"),bd=3,bg="#3a3a3a",fg="#ffffff", highlightthickness=0, highlightbackground="#1f1f1f",disabledbackground="#3a3a3a",disabledforeground="#ffffff")
pin_box_pairing = Entry(wireless_pairing_frame, width=7, font='Terminal',validate='key',validatecommand=(validation_pin,"%P"), bd=3,bg="#3a3a3a",fg="#ffffff", highlightthickness=0, highlightbackground="#1f1f1f",disabledbackground="#3a3a3a",disabledforeground="#ffffff")

def on_entry_click_pin(event):
    global PIN_BOX_PAIR_HINT
    if pin_box_pairing.get() == "PIN":
        PIN_BOX_PAIR_HINT = True
        pin_box_pairing.delete(0, END)
        pin_box_pairing.config(fg="#ffffff")  
        PIN_BOX_PAIR_HINT = False

def on_entry_leave_pin(event):
    global PIN_BOX_PAIR_HINT
    if not pin_box_pairing.get():
        PIN_BOX_PAIR_HINT = True
        pin_box_pairing.insert(0, "PIN")
        pin_box_pairing.config(fg="#969696")  
        PIN_BOX_PAIR_HINT = False

def on_entry_click_port(event):
    global PORT_BOX_PAIR_HINT
    if address_box_pairing_port.get() == "PORT":
        PORT_BOX_PAIR_HINT = True
        address_box_pairing_port.delete(0, END)
        address_box_pairing_port.config(fg="#ffffff")  
        PORT_BOX_PAIR_HINT = False

def on_entry_leave_port(event):
    global PORT_BOX_PAIR_HINT
    if not address_box_pairing_port.get():
        PORT_BOX_PAIR_HINT = True
        address_box_pairing_port.insert(0, "PORT")
        address_box_pairing_port.config(fg="#969696")  
        PORT_BOX_PAIR_HINT = False

on_entry_leave_pin(None)
on_entry_leave_port(None)
pin_box_pairing.bind('<FocusIn>', on_entry_click_pin)
pin_box_pairing.bind('<FocusOut>', on_entry_leave_pin)
address_box_pairing_port.bind('<FocusIn>', on_entry_click_port)
address_box_pairing_port.bind('<FocusOut>', on_entry_leave_port)



primary_button_svg =((screen_share_scrcpy_btn, screen_share_scrcpy_svg),(wireless_tcpip_btn, wireless_tcpip_svg),(shell_btn, shell_svg),(wireless_pairing_btn, wireless_pairing_svg),(file_download_btn, file_download_svg),(file_upload_btn, file_upload_svg),(file_downloading_btn, file_downloading_svg))
secondary_button_svg = ((kill_btn,kill_svg),(pairing_info_btn,info_svg),(preferred_interface_info_btn,info_svg),(devices_refresh_btn,refresh_svg),(unauthorized_noti_btn,unauthorized_noti_svg),(settings_btn,settings_svg),(settings_back_btn,back_svg),(offline_noti_btn,offline_noti_svg),(running_with_errors_btn,running_with_errors_svg),(network_refresh_btn,refresh_svg),(background_color_btn,current_mode_svg),(wireless_back_btn,back_svg),(permission_error_btn,permission_error_svg))
threading.Thread(target=auto_refresh_checkup, daemon=True).start()
main_window.mainloop()
subprocess.Popen(["adb","kill-server"],shell=True,stderr=subprocess.PIPE,stdout=subprocess.PIPE)