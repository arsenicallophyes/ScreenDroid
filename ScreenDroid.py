from tkinter import *
import subprocess, os, sys, time, threading, random, imageio, re
from tkinter import messagebox
from PIL import Image, ImageTk
from getpass import getuser as username

# import ctypes
# ctypes.windll.shcore.SetProcessDpiAwareness(True) # increases DPI for better image, Not optimized yet

lock_file = rf"C:\\Users\\{username()}\\AppData\\Local\\Temp\\ADBV2.lock"
if os.path.exists(lock_file):
    sys.exit(0)
open(lock_file, "w").close()
vid_playback_startup = True
bg_color_main = "#000000"
Running_tasks_pid = {}
time_list = list(range(0, 31))
time_list.reverse()
RESTART_TIMER = False
EXIT_END = False
STARTUP_CHECK = None
vid_playback_wireless = None
vid_playback_downloading = None
attached_adapters = []
network_devices_info = {}
WIRELESS_BUTTON_NETWORK_STATE = True
Active_Routes = []
vid_playback_startup = True


try:
    os.chdir(f"{sys._MEIPASS}\\addons")  # if compiled using pyinstaller (autopy2exe)
except:
    try:
        path_dir = input(
            "Script Directory: "
        )  # Where you saved the .py, should have icons and vids directory
        os.chdir(path_dir)
    except:
        raise Exception(f"Directory Doesn't Exist.\nCurrent Directory: {os.getcwd()}")
adb_check = subprocess.run(["adb", "kill-server"], shell=True, capture_output=True)
if adb_check.returncode == 1:
    raise Exception(
        f"Invalid Directory, Couldn't Find adb.exe\nCurrent Directroy[ {os.getcwd()} ]"
    )


def network_check():
    global attached_adapters, network_devices_info
    attached_adapters = []
    network_devices_info = {}
    network_info_addr = (
        subprocess.run(
            ["powershell", "Get-NetIPConfiguration"], shell=True, capture_output=True
        )
        .stdout.decode()
        .split("\r\n\r\n")
    )
    network_info_subnet = (
        subprocess.run(
            ["wmic", "NICCONFIG"],
            shell=True,
            capture_output=True,
        )
        .stdout.decode()
        .split("""\r\r\n                                       """)
    )
    for i in (
        subprocess.run(
            [
                "powershell",
                "" "Get-NetAdapter -physical | where status -eq 'up' | Format-List" "",
            ],
            shell=True,
            capture_output=True,
        )
        .stdout.decode()
        .split("\r\n\r\n")
    ):
        if len(i) != 0:
            Interface_description = re.findall("InterfaceDescription       : (.*)", i)[
                0
            ].replace("\r", "")
            Interface_MAC = re.findall("MacAddress                 : (.*)", i)[
                0
            ].replace("\r", "")
            Interface_Name = re.findall("Name                       : (.*)", i)[
                0
            ].replace("\r", "")
            Interface_Index = re.findall("InterfaceIndex             : (.*)", i)[
                0
            ].replace("\r", "")
            for x in network_info_addr:
                if len(x) != 0:
                    if (
                        Interface_Name
                        in re.findall("InterfaceAlias       : (.*)", x)[0]
                    ):
                        if len(re.findall("IPv4DefaultGateway   : (.*)", x)) != 0:
                            IPv4_gate = re.findall("IPv4DefaultGateway   : (.*)", x)[
                                0
                            ].replace("\r", "")
                            try:
                                for p in network_info_subnet:
                                    if Interface_description in p:
                                        Interface_subnet = re.findall(
                                            '}                   {"(.*?")', p
                                        )[0].strip('"')
                                        changing_sub = Interface_subnet.split(".")
                                        splittings_count = changing_sub.count("0")
                                        splitted_gate = IPv4_gate.split(".")
                                        for i in range(1, splittings_count + 1):
                                            splitted_gate.pop(-1)
                                        auto_complete_gateway = (
                                            ".".join(splitted_gate) + "."
                                        )
                                        network_devices_info[Interface_Name] = (
                                            Interface_MAC,
                                            Interface_description[:34],
                                            IPv4_gate,
                                            auto_complete_gateway,
                                            Interface_Index,
                                        )
                            except IndexError:
                                pass
    if len(network_devices_info) != 0:
        for i in network_devices_info.values():
            attached_adapters.append(i[1])
    else:
        attached_adapters = ["Couldn't Detect Any Adapter"]
        wireless_btn.configure(state="disabled")
        global WIRELESS_BUTTON_NETWORK_STATE
        WIRELESS_BUTTON_NETWORK_STATE = False


def vid_playback_4_startup():
    global vid_playback_startup
    frame_data = imageio.get_reader(r"vids\\startup_vid.mp4")
    size = (400, 600)
    while vid_playback_startup:
        for image in frame_data.iter_data():
            frame_image = ImageTk.PhotoImage(Image.fromarray(image).resize(size))
            startup_label.config(image=frame_image)
            startup_label.image = frame_image
            if vid_playback_startup != True:
                main_page.pack()
                startup_label.pack_forget()
            time.sleep(0.018)


def vid_playback_4_wireless(path):
    global vid_playback_wireless
    frame_data = imageio.get_reader(path)
    size = (400, 600)
    while vid_playback_wireless:
        for image in frame_data.iter_data():
            frame_image = ImageTk.PhotoImage(Image.fromarray(image).resize(size))
            vid_label_wireless.config(image=frame_image)
            vid_label_wireless.image = frame_image
            if vid_playback_wireless != True:
                break
            time.sleep(0.001)


def vid_playback_4_downloading(path):
    global vid_playback_downloading
    frame_data = imageio.get_reader(path)
    size = (48, 48)
    while vid_playback_downloading:
        for image in frame_data.iter_data():
            frame_image = ImageTk.PhotoImage(Image.fromarray(image).resize(size))
            file_downloading_btn.config(image=frame_image)
            file_downloading_btn.image = frame_image
            if vid_playback_downloading == False:
                break
            time.sleep(0.03)
    else:
        file_downloading_btn.config(image=file_downloading_btn_complete_png)


def exiting():
    os.unlink(lock_file)
    global EXIT_END
    EXIT_END = True
    main_window.destroy()
    for index, value in enumerate(Active_Routes):
        for device_id in value.keys():
            try:
                subprocess.run(
                    value[device_id].split(" "), shell=True, capture_output=True
                )
            except KeyError:
                pass
    subprocess.run(["adb", "kill-server"], shell=True, capture_output=True)


def ask_4_exit(event):
    if messagebox.askyesno("Exiting", message="Do You Wish To Exit?"):
        exiting()


def recheck_network_adapters():
    network_check()
    prefered_adapter.set(attached_adapters[-1])
    menu = adapters_list_option["menu"]
    menu.delete(0, "end")
    for string in attached_adapters:
        menu.add_command(
            label=string, command=lambda value=string: prefered_adapter.set(value)
        )
    loading_entry.place_forget()
    back_settings_btn.configure(state="normal")
    adapters_list_option.configure(state="normal")
    network_refresh_btn.configure(state="normal")
    device_screen_state_box.configure(state="normal")


def auto_refresh_checkup():
    global RESTART_TIMER, STARTUP_CHECK, vid_playback_startup, adapters_list_option
    while EXIT_END != True:
        if STARTUP_CHECK == True:
            for i in time_list:
                if RESTART_TIMER == False:
                    auto_refresh.configure(state="normal")
                    auto_refresh.delete(0, END)
                    auto_refresh.insert(END, str(i))
                    auto_refresh.configure(state="disabled")
                    time.sleep(1)
                    if i == 0:
                        re_checkup()
                elif RESTART_TIMER:
                    RESTART_TIMER = False
                    auto_refresh_checkup()
            auto_refresh_checkup()
            break
        elif STARTUP_CHECK == None:
            threading.Thread(target=vid_playback_4_startup, daemon=True).start()
            re_checkup()
            recheck_network_adapters()
            STARTUP_CHECK = True
            vid_playback_startup = False
    else:
        exit()


def add_task_with_pid(
    window_name, device_id, scrcpy: subprocess.Popen, current_selection
):
    while EXIT_END != True:
        time.sleep(0.5)
        filter_id = f"WINDOWTITLE eq {window_name}*"
        global count_task_pid
        count_task_pid = 0

        def rerun():
            time.sleep(0.5)
            global count_task_pid
            add_task_pid = subprocess.run(
                ["tasklist", "/fi", filter_id, "/fo", "list"],
                shell=True,
                capture_output=True,
            ).stdout.decode()
            if "No tasks are running" not in add_task_pid:
                add_task_pid = add_task_pid.splitlines()
                for i in add_task_pid:
                    if "PID:" in i:
                        i = i.removeprefix("PID:").strip(" ")
                        Running_tasks_pid[device_id] = i
            else:
                if scrcpy.returncode == 0:
                    if count_task_pid == 20:
                        if (
                            messagebox.askyesno(
                                "Timeout Error",
                                message="10 Seconds Has Passed and The Task Still Doesn't Exist. Do You Wish To Terminate All and Queued Tasks? ",
                            )
                            == True
                        ):
                            kill_process()
                            for index, value in enumerate(Active_Routes):
                                try:
                                    subprocess.run(
                                        value[device_id].split(" "),
                                        shell=True,
                                        capture_output=True,
                                    )
                                    Active_Routes.pop(index)
                                except KeyError:
                                    pass
                        else:
                            messagebox.showwarning(
                                "Warning", message="Unexpected Errors May Occur"
                            )
                            running_with_errors_btn.place(x=166, y=40)
                    else:
                        count_task_pid += 1
                        rerun()
                elif scrcpy.returncode == 1:
                    messagebox.showerror(
                        "Unsupported Device",
                        message=f"{current_selection} May Not Support Screen Sharing",
                    )

        rerun()
        re_checkup()
        break
    else:
        subprocess.Popen(
            ["adb", "kill-server"],
            shell=True,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
        exit()


def wait_until_disconnect(
    device_id,
    addr,
    window_name,
    port,
    adb_tcpip_out,
    adb_connect_out,
    wireless_frame_disconnect,
    current_selection,
):
    while EXIT_END != True:
        global vid_playback_wireless
        if "invalid" not in adb_tcpip_out.stdout.decode():
            if "connected" in adb_connect_out.stdout.decode():

                def rereun():
                    global vid_playback_wireless
                    check_4_device_battery = subprocess.run(
                        ["adb", "-s", addr, "shell", "dumpsys", "battery"],
                        shell=True,
                        capture_output=True,
                    ).stdout.decode()
                    if (
                        "USB powered: true" in check_4_device_battery
                        or "AC powered: true" in check_4_device_battery
                    ):
                        time.sleep(0.5)
                        rereun()
                    else:
                        vid_playback_wireless = False
                        main_page.pack()
                        wireless_frame_disconnect.pack_forget()
                        if device_screen_state_int.get() == 1:
                            scrcpy = subprocess.Popen(
                                [
                                    "scrcpy",
                                    "-s",
                                    addr,
                                    "--window-title",
                                    window_name,
                                    "-p",
                                    port,
                                    "--turn-screen-off",
                                ],
                                shell=True,
                                stderr=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                            )
                        else:
                            scrcpy = subprocess.Popen(
                                [
                                    "scrcpy",
                                    "-s",
                                    addr,
                                    "--window-title",
                                    window_name,
                                    "-p",
                                    port,
                                ],
                                shell=True,
                                stderr=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                            )
                        add_task_with_pid_thread = threading.Thread(
                            target=add_task_with_pid,
                            args=(window_name, device_id, scrcpy, current_selection),
                            daemon=True,
                        )
                        add_task_with_pid_thread.start()
                        re_checkup()

                rereun()
            else:
                vid_playback_wireless = False
                main_page.pack()
                wireless_frame_disconnect.pack_forget()
                messagebox.showerror(
                    "Connection Error", message=f"Couldn't Connect To {addr}"
                )
                re_checkup()
        else:
            vid_playback_wireless = False
            wireless_frame_disconnect.pack_forget()
            messagebox.showerror(
                "Port Error", message=f"An Error Occured, Port Used {port}"
            )
            re_checkup()
        break
    else:
        subprocess.Popen(
            ["adb", "kill-server"],
            shell=True,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
        exit()


def all_btn_activity(state):
    if state == "normal":
        if WIRELESS_BUTTON_NETWORK_STATE:
            wireless_btn.configure(state=state)
        settings_btn.configure(state=state)
        clr_btn.configure(state=state)
        rfrsh_btn.configure(state=state)
        wired_btn.configure(state=state)
        kill_btn.configure(state=state)
        whatsapp_btn.configure(state=state)
        file_download_btn.configure(state=state)
        file_upload_btn.configure(state=state)
        file_upload_btn.update()
    elif state == "disabled":
        if WIRELESS_BUTTON_NETWORK_STATE:
            wireless_btn.configure(state=state)
        settings_btn.configure(state=state)
        clr_btn.configure(state=state)
        rfrsh_btn.configure(state=state)
        wired_btn.configure(state=state)
        kill_btn.configure(state=state)
        whatsapp_btn.configure(state=state)
        file_download_btn.configure(state=state)
        file_upload_btn.configure(state=state)
        file_upload_btn.update()


def kill_process():
    all_btn_activity("disabled")
    running_with_errors_btn.place_forget()
    subprocess.run(["adb", "kill-server"], shell=True, capture_output=True)
    global Running_tasks_pid
    Running_tasks_pid = {}
    re_checkup()


def kill_process_bind(event):
    kill_process()


def wireless_handle(
    auto_complete_gateway,
    current_selection,
    device_id,
    path_vid,
    window_name,
    phone_ip,
    ping_check,
):
    global vid_playback_wireless
    if auto_complete_gateway in phone_ip and ping_check.returncode == 0:
        port = str(random.randint(5555, 10000))
        addr = f"{phone_ip}:{port}"
        adb_tcpip_out = subprocess.run(
            ["adb", "-s", device_id, "tcpip", port],
            shell=True,
            capture_output=True,
        )
        adb_connect_out = subprocess.run(
            ["adb", "connect", addr],
            shell=True,
            capture_output=True,
        )
        wireless_frame_disconnect.pack()
        main_page.pack_forget()
        wireless_frame_disconnect.wait_visibility()
        vid_playback_wireless = True
        vid_playback_4_wireless_thread = threading.Thread(
            target=vid_playback_4_wireless,
            daemon=True,
            args=(path_vid,),
        )
        vid_playback_4_wireless_thread.start()
        wait_until_disconnect_thread = threading.Thread(
            target=wait_until_disconnect,
            args=(
                device_id,
                addr,
                window_name,
                port,
                adb_tcpip_out,
                adb_connect_out,
                wireless_frame_disconnect,
                current_selection,
            ),
            daemon=True,
        )
        wait_until_disconnect_thread.start()
    else:
        messagebox.showerror(
            "Network Error",
            message=f"{current_selection} Is Connected To A Different Network\n{phone_ip} Didn't Respond To A Ping",
        )
        re_checkup()


def route_n_ping(Route_Traffic, phone_ip, IPv4_gate, Interface_Index, device_id):
    if Route_Traffic:
        routing_traffic = subprocess.run(
            [
                "route",
                "add",
                phone_ip,
                "MASK",
                "255.255.255.255",
                IPv4_gate,
                "IF",
                Interface_Index,
            ],
            shell=True,
            capture_output=True,
        )
        route_status = routing_traffic.returncode
    else:
        route_status = 0
    if route_status == 0:
        Active_Routes.append({device_id: f"route delete {phone_ip}"})
        ping_check = subprocess.run(
            ["ping", phone_ip, "-n", "1"],
            shell=True,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
        return ping_check
    else:
        return False


def wireless():
    while EXIT_END != True:
        all_btn_activity("disabled")
        try:
            prefered_interface = prefered_adapter.get()
            for key, value in network_devices_info.items():
                if value[1] == prefered_adapter.get():
                    Interface_MAC, IPv4_gate, auto_complete_gateway, Interface_Index = (
                        value[0],
                        value[2],
                        value[3],
                        value[4],
                    )
                    break
            if len(attached_adapters) > 1:
                Route_Traffic = True
            else:
                Route_Traffic = False
            if auto_complete_gateway:
                current_selection = list_box.get(list_box.curselection())
                for index, i in enumerate(devices.values()):
                    if i == current_selection:
                        device_id = list(devices.keys())[index]
                window_name = f"{current_selection} {device_id}"
                phone_ip = subprocess.run(
                    ["adb", "-s", device_id, "shell", "ifconfig", "wlan0"],
                    shell=True,
                    capture_output=True,
                ).stdout.decode()
                global bg_color_main, vid_playback_wireless
                if bg_color_main == "#000000":
                    path_vid = r"vids\\White_phone_disconnect_v1.0.mp4"
                elif bg_color_main == "#ffffff":
                    path_vid = r"vids\\Black_phone_disconnect_V3.1.mp4"
                if len(phone_ip) == 0:
                    messagebox.showerror(
                        "USB Connection Error",
                        message=f"{current_selection} Isn't Connected Via A USB",
                    )
                    re_checkup()
                elif "inet addr:" not in phone_ip:
                    messagebox.showerror(
                        "Network Error",
                        message=f"{current_selection} Isn't Connected To A Network",
                    )
                else:
                    raw_full_addr = phone_ip.splitlines()[1]
                    raw_full_addr = raw_full_addr.removeprefix("          inet addr:")
                    raw_full_addr = raw_full_addr.split(" ")
                    phone_ip = raw_full_addr[0]
                    if len(Active_Routes) != 0:
                        for index, value in enumerate(Active_Routes):
                            try:
                                subprocess.run(
                                    value[device_id].split(" "),
                                    shell=True,
                                    capture_output=True,
                                )
                                Active_Routes.pop(index)
                            except KeyError:
                                pass
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
                                ping_check = route_n_ping(
                                    Route_Traffic,
                                    phone_ip,
                                    IPv4_gate,
                                    Interface_Index,
                                    device_id,
                                )
                                if ping_check:
                                    wireless_handle(
                                        auto_complete_gateway,
                                        current_selection,
                                        device_id,
                                        path_vid,
                                        window_name,
                                        phone_ip,
                                        ping_check,
                                    )
                                else:
                                    messagebox.showerror(
                                        "Insuffeicient Permissions",
                                        message=f"Admin Privilege Is Required To Route Traffic To The Prefered Netowork Adapter",
                                    )
                            else:
                                messagebox.showerror(
                                    "Screen Share Error", message="Task Already Exists"
                                )
                                re_checkup()
                        except KeyError:
                            ping_check = route_n_ping(
                                Route_Traffic,
                                phone_ip,
                                IPv4_gate,
                                Interface_Index,
                                device_id,
                            )
                            if ping_check:
                                wireless_handle(
                                    auto_complete_gateway,
                                    current_selection,
                                    device_id,
                                    path_vid,
                                    window_name,
                                    phone_ip,
                                    ping_check,
                                )
                            else:
                                messagebox.showerror(
                                    "Insuffeicient Permissions",
                                    message=f"Admin Privilege Is Required To Route Traffic To The Prefered Netowork Adapter",
                                )
                    else:
                        ping_check = route_n_ping(
                            Route_Traffic,
                            phone_ip,
                            IPv4_gate,
                            Interface_Index,
                            device_id,
                        )
                        if ping_check:
                            wireless_handle(
                                auto_complete_gateway,
                                current_selection,
                                device_id,
                                path_vid,
                                window_name,
                                phone_ip,
                                ping_check,
                            )
                        else:
                            messagebox.showerror(
                                "Insuffeicient Permissions",
                                message=f"Admin Privilege Is Required To Route Traffic To The Prefered Netowork Adapter",
                            )
            else:
                messagebox.showerror(
                    "Network Error",
                    message=f"Your PC Isn't Connected Any Network\nInterface: {prefered_interface}\nMAC: {Interface_MAC}\nWindows Name: {key}",
                )
                re_checkup()
        except TclError:
            re_checkup()
        break
    else:
        subprocess.Popen(
            ["adb", "kill-server"],
            shell=True,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
        exit()


def wired_handle(window_name, device_id, current_selection):
    if device_screen_state_int.get() == 1:
        scrcpy = subprocess.Popen(
            [
                "scrcpy",
                "--window-title",
                window_name,
                "--serial",
                device_id,
                "--turn-screen-off",
            ],
            shell=True,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
    else:
        scrcpy = subprocess.Popen(
            [
                "scrcpy",
                "--window-title",
                window_name,
                "--serial",
                device_id,
            ],
            shell=True,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
    add_task_with_pid_thread = threading.Thread(
        target=add_task_with_pid,
        args=(window_name, device_id, scrcpy, current_selection),
        daemon=True,
    )
    add_task_with_pid_thread.start()


def wired():
    while EXIT_END != True:
        all_btn_activity("disabled")
        try:
            current_selection = list_box.get(list_box.curselection())
            for index, i in enumerate(devices.values()):
                if i == current_selection:
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
                        wired_handle(window_name, device_id, current_selection)
                    else:
                        messagebox.showerror(
                            "Screen Share Error", message="Task Already Exists"
                        )
                        re_checkup()
                except KeyError:
                    wired_handle(window_name, device_id, current_selection)
            else:
                wired_handle(window_name, device_id, current_selection)
        except TclError:
            re_checkup()
        break
    else:
        subprocess.Popen(
            ["adb", "kill-server"],
            shell=True,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
        exit()


def file_download():
    messagebox.showinfo("Under Development",message="Under Development")


def file_upload():
    messagebox.showinfo("Under Development",message="Under Development")


def repeat_until_success(index, i, connected_devices_vals, n):
    i = f"{i} {n}"
    if i in connected_devices_vals:
        i = i.removesuffix(f" {n}")
        n += 1
        repeat_until_success(index, i, connected_devices_vals, n)
    else:
        connected_devices_vals[index] = i


def checkup():
    connected_devices = {}
    attached = (
        subprocess.run(["adb", "devices"], shell=True, capture_output=True)
        .stdout.decode()
        .splitlines()[1:]
    )
    for i in attached:
        if ":" not in i and len(i) != 0:
            try:
                i = i.split("\t")
                device_id = i[0]
                device_state = i[1]
                Proceed = True
            except IndexError:
                Proceed = False
            if device_state == "device" and Proceed:
                device_name = subprocess.run(
                    [
                        "adb",
                        "-s",
                        device_id,
                        "shell",
                        "getprop",
                        "ro.product.model",
                    ],
                    shell=True,
                    capture_output=True,
                )
                if bool(Running_tasks_pid):
                    try:
                        pid = Running_tasks_pid[device_id]
                        filter_id = f"PID eq {pid}"
                        check_task_pid = subprocess.run(
                            ["tasklist", "/fi", filter_id, "/fo", "list"],
                            shell=True,
                            capture_output=True,
                        ).stdout.decode()
                    except KeyError:
                        check_task_pid = "No tasks are running"
                    if "No tasks are running" in check_task_pid:
                        if "Permission denied" in device_name.stderr.decode():
                            device_name = f"Permission Error {device_id}"
                            connected_devices[device_id] = device_name
                        else:
                            device_name = device_name.stdout.decode().removesuffix(
                                "\r\n"
                            )
                            connected_devices[device_id] = device_name
                else:
                    if "Permission denied" in device_name.stderr.decode():
                        device_name = f"Permission Error {device_id}"
                        connected_devices[device_id] = device_name
                    else:
                        device_name = device_name.stdout.decode().removesuffix("\r\n")
                        connected_devices[device_id] = device_name
            elif device_state == "unauthorized":
                connected_devices[device_id] = f"Unauthorized"
            elif device_state == "offline":
                connected_devices[device_id] = f"Offline"
    connected_devices_vals = list(connected_devices.values())
    for index, i in enumerate(connected_devices_vals):
        if connected_devices_vals.count(i) > 1:
            n = 1
            repeat_until_success(index, i, connected_devices_vals, n)
    connected_devices = dict(zip(connected_devices.keys(), connected_devices_vals))
    for i in sorted(connected_devices.values()):
        if "Unauthorized" in i:
            unauthorized_noti_btn.place(x=300, y=250)
        elif "Offline" in i:
            offline_noti_btn.place(x=300, y=292)
        else:
            list_box.insert(END, i)
    for i in range(list_box.size()):
        if i % 2 == 0:
            list_box.itemconfigure(i, bg="#1a8cff")
        else:
            list_box.itemconfigure(i, bg="#ffff00")
    return connected_devices


def re_checkup():
    while EXIT_END != True:
        global devices, RESTART_TIMER
        all_btn_activity("disabled")
        unauthorized_noti_btn.place_forget()
        offline_noti_btn.place_forget()
        list_box.delete(0, END)
        RESTART_TIMER = True
        devices = checkup()
        all_btn_activity("normal")
        break
    else:
        exit()


def change_bg():
    global bg_color_main, current_mode_png
    if bg_color_main == "#000000":
        bg_color_main = "#ffffff"
        current_mode_png = light_mode_png
    elif bg_color_main == "#ffffff":
        bg_color_main = "#000000"
        current_mode_png = dark_mode_png
    clr_btn.configure(image=current_mode_png)
    main_page.configure(background=bg_color_main)


def re_checkup_bind(event):
    re_checkup()


def unauthorized_message():
    Unauthorized_list = []
    for key, value in devices.items():
        if "Unauthorized" in value:
            Unauthorized_list.append(key)
    if len(Unauthorized_list) > 1:
        Unauthorized_devices = ""
        for i in Unauthorized_list:
            Unauthorized_devices += f"{i}\n"
        messagebox.showinfo(
            f"Unauthorized Devices Detected",
            message=f"1.) Enable USB Debugging\n2.) Authorize This Computer\nThe Following Devices Are Unauthorized:\n{Unauthorized_devices}",
        )
    else:
        messagebox.showinfo(
            f"Unauthorized Device Detected",
            message=f"1.) Enable USB Debugging\n2.) Authorize This Computer\nThe Following Devices Are Unauthorized:\n{Unauthorized_list[0]}",
        )


def offline_message():
    Offline_list = []
    for key, value in devices.items():
        if "Offline" in value:
            Offline_list.append(key)
    if len(Offline_list) > 1:
        Offline_devices = ""
        for i in Offline_list:
            Offline_devices += f"{i}\n"
        messagebox.showinfo(
            "Offline Devices Detected",
            message=f"1.) Disconnect The Device\n2.) Kill The Process (F4)\n3.) Reconnect The Device And Refresh (F5)\nCertain Devices Might Need To Be Unlocked\nThe Following Devices Are Offline:\n{Offline_devices}",
        )
    else:
        messagebox.showinfo(
            "Offline Device Detected",
            message=f"1.) Disconnect The Device\n2.) Kill The Process (F4)\n3.) Reconnect The Device And Refresh (F5)\nCertain Devices Might Need To Be Unlocked\nThe Following Devices Are Offline:\n{Offline_list[0]}",
        )


def running_errors_message():
    messagebox.showinfo(
        "Running With Errors", message="Killing All Active Processes Is Recommend (F4)"
    )


main_window = Tk()
main_window.title("ScreenDroid")
main_window.geometry("400x600+200+10")
main_window.configure(background=bg_color_main)
main_window.maxsize(width=400, height=600)
main_window.minsize(width=400, height=600)
main_window_icon = PhotoImage(file=r"icons\\android_FILL0_wght400_GRAD0_opsz48.png")
main_window.iconphoto(False, main_window_icon)
main_window.protocol("WM_DELETE_WINDOW", exiting)
main_window.bind("<Escape>", ask_4_exit)
main_window.bind("<F5>", re_checkup_bind)
main_window.bind("<F4>", kill_process_bind)


startup_label = Label(main_window)
startup_label.pack()

main_page = Frame(main_window, width=400, height=600, background=bg_color_main)


list_box = Listbox(
    main_page, bd=3, width=30, activestyle="none", selectbackground="#00c300"
)
list_box.place(x=100, y=200)


clr_btn = Button(
    main_page,
    text="BGCOLOR",
    command=change_bg,
    bd=3,
    activebackground="#989898",
    width=30,
    height=30,
)
clr_btn.place(x=40, y=40)


rfrsh_btn = Button(
    main_page,
    text="Refresh",
    command=re_checkup,
    bd=3,
    activebackground="#33d333",
    width=30,
    height=30,
    state="normal",
)
rfrsh_btn.place(x=82, y=40)

unauthorized_noti_btn = Button(
    main_page,
    text="Error_Unauthor",
    state="normal",
    bd=3,
    width=30,
    height=30,
    command=unauthorized_message,
)
offline_noti_btn = Button(
    main_page,
    text="Error_Unauthor",
    state="normal",
    bd=3,
    width=30,
    height=30,
    command=offline_message,
)
running_with_errors_btn = Button(
    main_page,
    text="Error_Unauthor",
    state="normal",
    bd=3,
    width=30,
    height=30,
    command=running_errors_message,
)

wired_btn = Button(
    main_page,
    text="scrcpy cable",
    command=wired,
    width=48,
    height=48,
    bd=3,
    activebackground="#377bb9",
)
wired_btn.place(x=50, y=400)

wireless_btn = Button(
    main_page,
    text="scrcpy wireless",
    command=wireless,
    width=48,
    height=48,
    bd=3,
    activebackground="#b0416e",
)
wireless_btn.place(x=120, y=400)

kill_btn = Button(
    main_page,
    text="end_all",
    command=kill_process,
    bd=3,
    width=30,
    height=30,
    activebackground="#ce1000",
)
kill_btn.place(x=124, y=40)


auto_refresh = Entry(main_page, width=4, font="Terminal", bd=3)
auto_refresh.place(x=320, y=200)


file_download_btn = Button(
    main_page,
    text="adb pull",
    command=file_download,
    width=48,
    height=48,
    bd=3,
    activebackground="#66ffcc",
)
file_download_btn.place(x=190, y=400)


file_upload_btn = Button(
    main_page,
    text="adb push",
    command=file_upload,
    width=48,
    height=48,
    bd=3,
    activebackground="#ff9602",
)
file_upload_btn.place(x=260, y=400)

whatsapp_btn = Button(
    main_page,
    text="adb pull whats",
    command=file_upload,
    width=48,
    height=48,
    bd=3,
    activebackground="green",
)
whatsapp_btn.place(x=50, y=470)


file_downloading_btn = Button(main_page, width=48, height=48)
file_downloading_btn.place(x=100, y=100)


def open_settings():
    main_page.pack_forget()
    settings_frame.pack()


def back_btn_settings_func():
    settings_frame.pack_forget()
    main_page.pack()


settings_btn = Button(
    main_page,
    text="settings",
    command=open_settings,
    bd=3,
    width=30,
    height=30,
    activebackground="#ce1000",
)
settings_btn.place(x=340, y=40)

settings_frame = Frame(main_window, width=400, height=600, background=bg_color_main)

back_settings_btn = Button(
    settings_frame, width=30, height=30, name="back_btn", command=back_btn_settings_func
)
back_settings_btn.place(x=20, y=30)

device_screen_state_text = StringVar(value="Turn Screen Off While Sharing Screen")
device_screen_state_int = IntVar()
device_screen_state_box = Checkbutton(
    settings_frame,
    text="Turn Screen Off While Sharing Screen",
    textvariable=device_screen_state_text,
    variable=device_screen_state_int,
)
device_screen_state_box.place(x=80, y=240)

loading_text = StringVar(value="Refreshing Please Wait")
loading_entry = Entry(
    settings_frame,
    width=24,
    background="#ffffff",
    font="Terminal",
    state="disabled",
    bd=5,
    textvariable=loading_text,
)


def network_refresh():
    device_screen_state_box.configure(state="disabled")
    back_settings_btn.configure(state="disabled")
    adapters_list_option.configure(state="disabled")
    network_refresh_btn.configure(state="disabled")
    loading_entry.place(x=50, y=200)
    threading.Thread(target=recheck_network_adapters, daemon=True).start()


network_refresh_btn = Button(
    settings_frame,
    text="network_refresh",
    command=network_refresh,
    bd=3,
    activebackground="#33d333",
)
network_refresh_btn.configure(width=30, height=30)
network_refresh_btn.place(x=40, y=150)

prefered_adapter = StringVar(value="Prefered Network Interface Adapter")
adapters_list_option = OptionMenu(
    settings_frame, prefered_adapter, "Prefered Network Interface Adapter"
)
adapters_list_option.place(x=100, y=150)

wireless_frame_disconnect = Frame(
    main_window, width=400, height=600, background=bg_color_main
)
vid_label_wireless = Label(wireless_frame_disconnect)
vid_label_wireless.pack()


light_mode_png = PhotoImage(file=r"icons\\light_mode_FILL0_wght400_GRAD0_opsz36.png")
dark_mode_png = PhotoImage(file=r"icons\\dark_mode_FILL0_wght400_GRAD0_opsz36.png")
refresh_png = PhotoImage(file=r"icons\\refresh_FILL0_wght400_GRAD0_opsz36.png")
unauthorized_noti_png = PhotoImage(
    file=r"icons\\security_update_warning_FILL0_wght400_GRAD0_opsz36.png"
)
wired_btn_png = PhotoImage(
    file=r"icons\\mobile_screen_share_FILL0_wght300_GRAD0_opsz48.png"
)
wireless_btn_png = PhotoImage(
    file=r"icons\\mobile_screen_wireless_share_FILL0_wght300_GRAD0_opsz48.png"
)
kill_btn_png = PhotoImage(file=r"icons\\cancel_FILL0_wght400_GRAD0_opsz36.png")
file_download_btn_png = PhotoImage(
    file=r"icons\\file_download_FILL0_wght400_GRAD0_opsz48.png"
)
file_upload_btn_png = PhotoImage(
    file=r"icons\\file_upload_FILL0_wght400_GRAD0_opsz48.png"
)
whatsapp_btn_png = PhotoImage(file=r"icons\\whats_trans_black_v3.png")
whatsapp_btn_pressed_png = PhotoImage(file=r"icons\\whats_trans_green_button.png")
file_downloading_btn_png = PhotoImage(
    file=r"icons\\downloading_FILL0_wght400_GRAD0_opsz48.png"
)
file_downloading_btn_complete_png = PhotoImage(
    file=r"icons\\file_download_done_FILL0_wght400_GRAD0_opsz48.png"
)
settings_btn_png = PhotoImage(file=r"icons\\settings_FILL0_wght400_GRAD0_opsz36.png")
back_settings_btn_png = PhotoImage(
    file=r"icons\\arrow_back_FILL0_wght400_GRAD0_opsz36.png"
)
offline_noti_png = PhotoImage(
    file=r"icons\\phonelink_lock_FILL0_wght400_GRAD0_opsz36.png"
)
running_with_errors_btn_png = PhotoImage(
    file=r"icons\\running_with_errors_FILL0_wght400_GRAD0_opsz36.png"
)


def change_pic_whats(event):
    whatsapp_btn.configure(image=whatsapp_btn_pressed_png)


def change_pic_whats_og(event):
    whatsapp_btn.configure(image=whatsapp_btn_png)


current_mode_png = dark_mode_png
whatsapp_btn.bind("<ButtonPress>", change_pic_whats)
whatsapp_btn.bind("<ButtonRelease>", change_pic_whats_og)

clr_btn.configure(image=current_mode_png)
rfrsh_btn.configure(image=refresh_png)
unauthorized_noti_btn.configure(image=unauthorized_noti_png)
offline_noti_btn.configure(image=offline_noti_png)
running_with_errors_btn.configure(image=running_with_errors_btn_png)
wired_btn.configure(image=wired_btn_png)
wireless_btn.configure(image=wireless_btn_png)
kill_btn.configure(image=kill_btn_png)
file_download_btn.configure(image=file_download_btn_png)
file_upload_btn.configure(image=file_upload_btn_png)
file_downloading_btn.configure(image=file_downloading_btn_png)
settings_btn.configure(image=settings_btn_png)
whatsapp_btn.configure(image=whatsapp_btn_png)
back_settings_btn.configure(image=back_settings_btn_png)
network_refresh_btn.configure(image=refresh_png)

try:
    auto_refresh_checkup_thread = threading.Thread(
        target=auto_refresh_checkup, daemon=True
    )
    auto_refresh_checkup_thread.start()
    main_window.mainloop()
except:
    os.unlink(lock_file)
subprocess.run(
    ["adb", "kill-server"], shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE
)
