import re
from cryptography.fernet import Fernet
import subprocess
import time
from colorama import Fore
import os
from tkinter import Tk, filedialog as fd
from win32com.client import Dispatch
import winshell
import random
import getpass
import shutil
path_dir = fr"{input('Script Directory: ')}\addons"
os.chdir(path_dir)
def random_logo():
    drawing_logo = random.randint(1,2)
    os.system('cls')
    os.system('color')
    if drawing_logo == 1:    
        print(Fore.RED+'           |      |')
        print(Fore.GREEN+'          ||||||||||\n'
        '         ||'+Fore.RED+'-'+Fore.GREEN+'||||||'+Fore.RED+'-'+Fore.GREEN+'||\n'
        '     __  ||||||||||||  __\n'
        '     \ \              / /\n'
        '      \ \||||||||||||/ /\n'
        '       \_||||||||||||_/\n'
        '         ||||||||||||\n'
        '         ||||||||||||\n'
        '          |||    |||\n'
        '          |||    |||')
    else:
        pass
    if drawing_logo == 2:
        print(Fore.WHITE+'            |||       |||\n'
        '            |||       |||\n'
        '        ||||||||||||||||||||\n'
        '       ||||||||||||||||||||||     \n'
        '      ||||  ||||||||||||  ||||    \n'
        '      ||||  ||||||||||||  ||||    \n'
        '__    ||||||||||||||||||||||||    __')
        print(Fore.RED+'\ \   ||||||||||||||||||||||||   / /\n'
        ' \ \                            / /\n'
        '  \ \ |||||||||||||||||||||||| / /\n'
        '   \ \||||||||||||||||||||||||/ /\n'
        '    \ |||||||||||||||||||||||| /\n'
        '     \||||||||||||||||||||||||/\n'
        '      ||||||||||||||||||||||||\n'
        '      ||||||||||||||||||||||||')
        print(Fore.GREEN+'      ||||||||||||||||||||||||\n'
        '      ||||||||||||||||||||||||\n'
        '        ||||            ||||\n'
        '        ||||            ||||\n'
        '        ||||            ||||\n'
        '        ||||            ||||\n'
        '        ||||            ||||')
    else:
        pass
def startup():
    os.system('color')
    random_logo()
    print(Fore.RED+'Developed By:'+Fore.BLUE+' @arsenicallophyes')
    print(Fore.GREEN +"Starting Service...")
    subprocess.run(["adb","kill-server"],capture_output=True)
    subprocess.run(["adb","devices"],shell=True,capture_output=True)
startup()
def start():
    os.system('color')
    print(Fore.WHITE+"==========================================================")
    print(Fore.CYAN+"Screen Mirror             [/C]\nScreen Mirror Wirelessly  [/W]\nFile Transfer             [/F]\nCreate Shortcut           [/S]\nTerminate Server And Exit [/X]\nUninstall                 [/U]")
    def shortcut_create():
        desktop = winshell.desktop()
        current= os.getcwd()
        path = os.path.join(desktop, "Android Debugger.lnk")
        file_target = current+"\\Android Debugger.exe"
        icon_loci = current+"\\Android.ico"
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = file_target
        shortcut.WorkingDirectory = current
        shortcut.IconLocation = icon_loci
        shortcut.save()
        print(Fore.GREEN+"Shortcut Created Successfully")
        time.sleep(2)
        start()
    def wireless():
        print(Fore.WHITE+"=========================================================="+Fore.RED)
        current = os.getcwd()
        device_dir = current+"\\Devices"
        device_dir_store = device_dir+"\\IDs.inf"
        print(Fore.RED+"Scanning For Devices")
        subprocess.run(["adb","kill-server"],shell=True,capture_output=True)
        subprocess.run(["adb","devices"],shell=True,capture_output=True)
        devices_connected = subprocess.run(["adb","devices"],shell=True,capture_output=True).stdout.decode()
        devices_connected = devices_connected.splitlines()
        if len(devices_connected) == 3:
            print(Fore.GREEN+"Device Detected")
            print(Fore.WHITE+"==========================================================")
            pass
        else:
            pass
        if len(devices_connected) >3:
            print(Fore.RED+"Multiple Devices Connected, Please Connect One Device Only")
            start()
        else:
            pass
        if len(devices_connected) <3:
            print(Fore.RED+"No Devices Connected, Please Connect One Device Only")
            start()
        else:
            pass
        def new_wireless_input():
            device_id =subprocess.run(["adb","devices"],shell=True,capture_output=True).stdout.decode()
            device_id = device_id.splitlines()
            device_id = device_id[1]
            device_id = str(device_id)
            device_id = device_id.replace("device","")
            device_id = device_id.strip()
            start_port = 7
            stop_port = 65531
            port_list = list(range(start_port, stop_port))
            print(Fore.WHITE+"==========================================================")
            def port_input():
                try:
                    port = int((input(Fore.GREEN+"Port Number:")))
                    if port not in port_list:
                        print(Fore.RED+"Allowed TCP Ports: (7-65530)")
                        new_wireless_input()
                    else:
                        return port
                except ValueError:
                    print(Fore.RED+"Value Must Be An Integer")
                    new_wireless_input()
            port = port_input()
            def connect_new_step():
                subprocess.run(["adb","kill-server"],shell=True,capture_output=True)
                print(Fore.GREEN+"Port Successfully Validated")
                My_port = str(port)
                print(Fore.YELLOW+"Establishing Connection")
                subprocess.run(["adb","tcpip",My_port],shell=True,capture_output=True)
                time.sleep(1)
                ip_address_input = input(Fore.GREEN+"Enter Your Phone IP Address:")
                print(Fore.RED+"Dissconnect Your Device")
                time.sleep(3)
                list_yes = ["y","yes","ye"]
                def disconnect_input():
                    diconnect_inp = str(input(Fore.GREEN+"Type 'Y' To Connect: "))
                    disconnect_inp_low = diconnect_inp.lower()
                    if disconnect_inp_low not in list_yes:
                        disconnect_input()
                    else:
                        pass
                disconnect_input()
                ip_str = str(ip_address_input)
                portdots = ":" + My_port
                ip_port = ip_str+portdots
                print(Fore.YELLOW+"Connecting Please Wait...")
                port_wifi_errors =subprocess.run(["adb","connect",ip_port],capture_output=True).stdout.decode()
                check_bad_port_number =re.search("No connection could be made because the target machine actively refused it",port_wifi_errors)
                check_wifi = re.search("A connection attempt failed because the connected party did not properly respond after a period of time, or established connection failed because connected host has failed to respond",port_wifi_errors)
                no_errors_wifi = re.search("connected to",port_wifi_errors)
                if check_bad_port_number is not None:
                    print(Fore.RED+"Bad Port Number Try A Bigger Port")
                    time.sleep(1)
                    start()
                else:
                    pass
                if check_wifi is not None:
                    print(Fore.RED+"Device Not Connected On The Same Network")
                    time.sleep(1)
                    start()
                else:
                    pass
                if no_errors_wifi is not None:
                    pass
                else:
                    print(Fore.RED+"An Error Occured")
                    subprocess.run(["adb","kill-server"],shell=True,capture_output=True)
                    time.sleep(1)
                    start()
                screen_share = subprocess.run(["scrcpy"],capture_output=True).stdout.decode()
                device_name = re.findall("Device: (.*)\r",screen_share)
                verify_no_errors = re.search("scrcpy-server... file pushed, 0 skipped",screen_share)
                verify_no_errors_2 = re.search("no devices/emulators found",screen_share)
                verify_no_errors_3 = re.search("more than one device/emulator",screen_share)
                if verify_no_errors_2 is True:
                    print(Fore.RED+"Could Not Connect To Device\nAttempting To Troubleshoot...")
                    print(Fore.GREEN+"Possible Solutions: Device Is Not Connected On The Same Network\nUSB Debugging And Wireless Debugging (ADB Over Network) Should Both Be Enabled")
                    subprocess.run(["adb","kill-server"],shell=True,capture_output=True)
                    time.sleep(1)
                    start()
                else:
                    pass
                if verify_no_errors_3 is True:
                    print(Fore.RED+"Error Multiple Connections\nAttempting To Troubleshoot...")
                    print(Fore.GREEN+"Possible Solution: Connect One Device Only")
                    subprocess.run(["adb","kill-server"],shell=True,capture_output=True)
                    time.sleep(1)
                    start()
                else:
                    pass
                if verify_no_errors is None:
                    print(Fore.RED+"Error Occured\nAttempting To Troubleshoot...")
                    subprocess.run(["adb","kill-server"],shell=True,capture_output=True)
                    time.sleep(1)
                    start()
                else:
                    pass
                subprocess.run(["adb","kill-server"],shell=True,capture_output=True)
                def ask_to_save_device_id():
                    print(Fore.BLUE+"Save Device ID To Connect On The Same Network Again Quickly (Y/N)?")
                    save_id_inp = str(input())
                    save_id_inp_low = save_id_inp.lower()
                    if save_id_inp_low in list_yes:
                        device_name_str = str(device_name[0])
                        device_name_str =device_name_str.replace("samsung ","")
                        device_id_save_file = device_name_str+";"+ip_port
                        fernet = Fernet(b'fhmRikpCQrOe7f0dN-RLAosBzDxhHdeSBidr0hby9NE=')
                        try:
                            os.mkdir(device_dir)
                        except FileExistsError:
                            pass
                        encrypt_message = fernet.encrypt(device_id_save_file.encode())
                        if os.path.exists(device_dir_store) is False:
                            text_file = open(device_dir_store,"w+")
                            text_file.close()
                        else:
                            pass
                        text_file = open(device_dir_store,"r")
                        check_text_file = str(text_file.read())
                        check_text_file = list(check_text_file.splitlines())
                        text_file.close()
                        if not check_text_file:
                            text_file = open(device_dir_store,"w+")
                            text_file.write(encrypt_message.decode("cp1252"))
                            text_file.close()
                        else:
                            text_file = open(device_dir_store,"a")
                            text_file.write("\n")
                            text_file.write(encrypt_message.decode("cp1252"))
                            text_file.close()
                        print(Fore.GREEN+"Device ID Saved Successfully")
                        time.sleep(1)
                        start()
                    else:
                        start()
                ask_to_save_device_id()
            connect_new_step()
        def old_wirless_input():
            print(Fore.WHITE+"=========================================================="+Fore.BLUE)
            read_id = open(device_dir_store,'r')
            Ip_port_file = str(read_id.read())
            Ip_port_file =list(Ip_port_file.splitlines())
            Ip_port_file_len = len(Ip_port_file)
            if Ip_port_file_len == 0:
                print(Fore.RED+"No Devices ID Saved")
                time.sleep(1.5)
                start()
            else:
                fernet = Fernet(b'fhmRikpCQrOe7f0dN-RLAosBzDxhHdeSBidr0hby9NE=')
                device_list = []
                for Ip_port_file_dec in Ip_port_file:
                    encrypt_message =bytes(str.encode(Ip_port_file_dec))
                    dec_message = fernet.decrypt(encrypt_message).decode()
                    device_list.append(dec_message)
                print(Fore.YELLOW+"Type '/L' To Abort Process")
                print(Fore.YELLOW+"If You Wish To Modifiy The List Type 'DEL'"+Fore.BLUE)
                for device_id in device_list:
                    n = device_list.index(device_id)
                    device_id =str(device_id)
                    device_id_name =device_id.split(";")
                    device_name = device_id_name[0] 
                    device_id = device_id_name[1]
                    n = n + 1
                    n = str(n)
                    device_name = "{:<35}".format(device_name)
                    print(device_name+"   ["+n+"]")
                def ask_device_id_file():
                    try:
                        phone_id_inp = str(input(Fore.GREEN+"Connect To Phone ID: "+Fore.BLUE))
                        phone_id = int(phone_id_inp)
                        if phone_id > Ip_port_file_len:
                            print(Fore.RED+"Value Out Of Range")
                            time.sleep(1)
                            ask_device_id_file()
                        else:
                            if phone_id !=0:
                                phone_id=phone_id -1
                                Ip_port_file_dec = Ip_port_file[phone_id]
                                encrypt_message =bytes(str.encode(Ip_port_file_dec))
                                dec_message = fernet.decrypt(encrypt_message).decode()
                                dec_message =dec_message.split(";")
                                device_name = dec_message[0] 
                                device_id = dec_message[1]
                                open_id =device_id.split(":")
                                ip_address_file = str(open_id[0])
                                port_file = str(open_id[1])
                                subprocess.run(["adb","kill-server"],shell=True,capture_output=True)
                                subprocess.run(["adb","devices"],shell=True,capture_output=True)
                                print(Fore.YELLOW+"Establishing Connection")
                                subprocess.run(["adb","tcpip",port_file],shell=True,capture_output=True)
                                print(Fore.RED+"Dissconnect Your Device")
                                list_yes = ["y","yes","ye"]
                                def disconnect_input():
                                    diconnect_inp = str(input(Fore.GREEN+"Type "+Fore.RED+"'Y'"+Fore.GREEN+ " To Connect To "+Fore.YELLOW+device_name+" : "+Fore.BLUE))
                                    disconnect_inp_low = diconnect_inp.lower()
                                    if disconnect_inp_low not in list_yes:
                                        disconnect_input()
                                    else:
                                        pass
                                disconnect_input()
                                print(Fore.YELLOW+"Connecting Please Wait...")
                                subprocess.run(["adb","connect",ip_address_file])
                                subprocess.run(["scrcpy"],capture_output=True)
                            else:
                                print(Fore.RED+"Value Out Of Range")
                                time.sleep(1)
                                ask_device_id_file()  
                    except ValueError:
                        phone_id_inp = phone_id_inp.lower()
                        phone_id_inp_del_list = "del"
                        phone_id_inp_abort_list = "/l"
                        if phone_id_inp in phone_id_inp_abort_list:
                            print(Fore.RED+"Proccess Was Aborted By User")
                            start()
                        else:
                            pass
                        if phone_id_inp in phone_id_inp_del_list:
                            print(Fore.WHITE+"==========================================================")
                            print(Fore.YELLOW+"Type '/L' To Abort Process"+Fore.BLUE)
                            for device_id in device_list:
                                n = device_list.index(device_id)
                                device_id =str(device_id)
                                device_id_name =device_id.split(";")
                                device_name = device_id_name[0] 
                                device_id = device_id_name[1]
                                n = n + 1
                                n = str(n)
                                device_name = "{:<35}".format(device_name)
                                print(device_name+"   ["+n+"]")
                            def modify_phone_id_list():
                                try:
                                    phone_id_del_inp = (input(Fore.GREEN+"Delete Phone ID: "+Fore.RED))
                                    phone_id_del = int(phone_id_del_inp)
                                    return phone_id_del
                                except ValueError:
                                    phone_id_del_inp_abort = phone_id_del_inp.lower()
                                    phone_id_del_inp_abort_list = "/l"
                                    if phone_id_del_inp_abort in phone_id_del_inp_abort_list:
                                        print(Fore.RED+"Proccess Was Aborted By User")
                                        start()
                                    else:
                                        print(Fore.RED+"Value Must Be An Integer")
                                        time.sleep(1)
                                        modify_phone_id_list()
                            phone_id_del =modify_phone_id_list()
                            if phone_id_del > Ip_port_file_len:
                                print(Fore.RED+"Value Out Of Range")
                                time.sleep(1)
                                modify_phone_id_list()
                            else:
                                phone_id_del = phone_id_del -1
                                Ip_port_file.pop(phone_id_del)
                                text_file = open(device_dir_store,"w+")
                                for Ip_port_file_after_del in Ip_port_file:
                                    encrypt_message =bytes(str.encode(Ip_port_file_after_del))
                                    text_file.write(encrypt_message.decode("cp1252")+"\n")
                                text_file.close()
                                read_id_2 = open(device_dir_store,'r+')
                                Ip_port_file_del_blank = str(read_id_2.read())
                                Ip_port_file_del_blank = list(Ip_port_file_del_blank.splitlines())
                                if not Ip_port_file_del_blank:
                                    print(Fore.GREEN+"Successfully Deleted")
                                    time.sleep(1.5)
                                    start()
                                else:
                                    pass
                                Ip_port_file_del_blank =Ip_port_file_del_blank.pop(0)
                                for Ip_port_file_after_del_blank in Ip_port_file_del_blank:
                                    encrypt_message =bytes(str.encode(Ip_port_file_after_del_blank))
                                    read_id_2.write(encrypt_message.decode("cp1252")+"\n")
                                print(Fore.GREEN+"Successfully Deleted")
                                time.sleep(1.5)
                                start()
                        else:
                            print(Fore.RED+"Value Must Be An Integer")
                            time.sleep(1)
                            ask_device_id_file()
                ask_device_id_file()
            start()
        print(Fore.BLUE+"Connect To New Phone      [/N]\nConnect To Saved Phone    [/O]\nAbort Process             [/L]")
        connect_method = str(input())
        connect_method_low = connect_method.lower()
        connect_method_new = "/n"
        connect_method_old = "/o"
        connect_method_abort_list = "/l"
        connect_method_list = ["/o","/n","/l"]
        if connect_method_low in connect_method_abort_list:
            start()
        else:
            pass
        if connect_method_low not in connect_method_list:
            print(Fore.RED+"Invalid Input")
            time.sleep(1)
            wireless()
        else:
            pass
        if connect_method_low in connect_method_new:
            new_wireless_input()
        else:
            pass
        if connect_method_low in connect_method_old:
            old_wirless_input()
        else:
            pass
        if connect_method_low in connect_method_abort_list:
            start()
        else:
            pass
        if connect_method_low not in connect_method_list:
            print(Fore.RED+"Invalid Input")
            time.sleep(1)
            wireless()
        else:
            pass
        if connect_method_low in connect_method_new:
            new_wireless_input()
        else:
            pass
        if connect_method_low in connect_method_old:
            old_wirless_input()
        else:
            pass
    def wired():
        print(Fore.YELLOW+"Connecting Please Wait...")
        subprocess.run(["adb","kill-server"],shell=True,capture_output=True)
        subprocess.run(["adb","devices"],shell=True,capture_output=True).stdout.decode()
        devices_connected = subprocess.run(["adb","devices"],shell=True,capture_output=True).stdout.decode()
        devices_connected = devices_connected.splitlines()
        if len(devices_connected) >3:
            print(Fore.RED+"Multiple Devices Connected, Please Connect One Device Only")
            start()
        else:
            pass
        if len(devices_connected) <3:
            print(Fore.RED+"No Devices Connected, Please Connect One Device Only")
            start()
        else:
            pass
        connecting_wired = subprocess.run(["scrcpy"],capture_output=True).stdout.decode()
        search_connecting_wired = re.search("no devices/emulators found",connecting_wired)
        if search_connecting_wired is True:
            print(Fore.RED+"No Devices Detected")
            time.sleep(1)
            start()
        else:
            pass
        start()
    def kill_process():
        print(Fore.RED+"Killing Server...")
        subprocess.run(["adb","devices"],shell=True,capture_output=True)
        subprocess.run(["adb","kill-server"],capture_output=True)
        exit()
    def filetransferfiles():
        print(Fore.WHITE+"==========================================================")
        print(Fore.BLUE+"PC To Phone               [/H]\nPhone To PC               [/B]\nAbort Process             [/L]")
        file_tranfer_pull_push = str(input())
        file_tranfer_pull_push_low = file_tranfer_pull_push.lower()
        file_tranfer_pull_list = "/b"
        file_tranfer_push_list = "/h"
        file_tranfer_pull_push_exit_list = "/l"
        file_tranfer_pull_push_list = ["/h","/b","/l"]
        def filetransferpush():
            print(Fore.WHITE+"==========================================================")
            print(Fore.RED+"Scanning For Devices")
            subprocess.run(["adb","kill-server"],shell=True,capture_output=True)
            subprocess.run(["adb","devices"],shell=True,capture_output=True)
            devices_connected = subprocess.run(["adb","devices"],shell=True,capture_output=True).stdout.decode()
            devices_connected = devices_connected.splitlines()
            if len(devices_connected) == 3:
                print(Fore.GREEN+"Device Detected")
                print(Fore.WHITE+"==========================================================")
                pass
            else:
                pass
            if len(devices_connected) >3:
                print(Fore.RED+"Multiple Devices Connected, Please Connect One Device Only")
                filetransferfiles()
            else:
                pass
            if len(devices_connected) <3:
                print(Fore.RED+"No Devices Connected, Please Connect One Device Only")
                filetransferfiles()
            else:
                pass
            print(Fore.WHITE+"==========================================================")
            print(Fore.RED+"Select Files For Transfer")
            root_tk = Tk()
            root_tk.iconify()
            file_path = fd.askopenfilenames()
            list_files = list(file_path)
            length_files = len(list_files)
            if length_files == 0:
                print(Fore.RED+"No Files Added Operation Aborted")
            else:
                print(Fore.GREEN+"Transferring Selected Files Please Wait")
                subprocess.run(["adb","shell","mkdir","sdcard/DCIM/Debugger"],shell=True,capture_output=True).stdout.decode()
                pass
            for file_path_str in list_files:
                transfered_file = subprocess.run(["adb","push",file_path_str,"sdcard/DCIM/Debugger"], shell=True,capture_output=True).stdout.decode()
                check_transfered_file = re.search('0 skipped',transfered_file)
                if check_transfered_file is None:
                    print(Fore.RED+"An Error Occured While Transfering "+Fore.YELLOW+file_path_str+Fore.GREEN+" Try Again")
                else:
                    pass
            print(Fore.GREEN+"Successfully Transferred ")
        def whatsapptransfer():
            print(Fore.WHITE+"==========================================================")
            print(Fore.GREEN+"Copy Images From Whatsapp  [/P]\nCopy Videos From Whatsapp  [/V]\nBackup Whatsapp Messages   [/U]\nAbort Process              [/L]")
            whatsapptransfer_input = str(input())
            whatsapptransfer_input_low = whatsapptransfer_input.lower()
            file_transfer_img_whats_list = "/p"
            file_transfer_vid_whats_list = "/v"
            file_transfer_backup_whats_list = "/u"
            file_transfer_whats_all_list = ["/v","/p","/l","/u"]
            file_transfer_whats_abort_list = "/l"
            if whatsapptransfer_input_low not in file_transfer_whats_all_list:
                print(Fore.RED+"Invalid Input")
                whatsapptransfer()
            else:
                pass
            if whatsapptransfer_input_low in file_transfer_whats_abort_list:
                filetransferfiles()
            else:
                pass
            if whatsapptransfer_input_low in file_transfer_img_whats_list:
                print(Fore.GREEN+"Select Which Folder You Want To Save Copied Files Into")
                time.sleep(1)
                root_tk = Tk()
                root_tk.iconify()
                ask_save_dir = fd.askdirectory()
                dir_len = len(ask_save_dir)
                if dir_len != 0:
                    print(Fore.BLUE+"Copying Files...")
                    one_dir_whats_img = subprocess.run(["adb","pull","sdcard/Android/media/com.whatsapp/WhatsApp/Media/WhatsApp Images",ask_save_dir],shell=True, capture_output=True).stdout.decode()
                    search_one_dir_whats_img_search = re.search("No such file or directory", one_dir_whats_img)
                    if search_one_dir_whats_img_search is None:
                        print(Fore.GREEN+"Transfer Completed "+Fore.YELLOW+"Saved in "+ask_save_dir)
                    else:
                        print(Fore.RED+"Directory Not Located"+Fore.GREEN+" Searching In A Diffrent Location")
                        time.sleep(1)
                        two_dir_whats_img =subprocess.run(["adb","pull","sdcard/WhatsApp/Media/WhatsApp Images",ask_save_dir],shell=True, capture_output=True).stdout.decode()
                        search_two_dir_whats_img = re.search("No such file or directory", two_dir_whats_img)
                        if search_two_dir_whats_img is None:
                            print(Fore.GREEN +"Transfer Completed Saved in "+Fore.YELLOW+ask_save_dir)
                        else:
                            print(Fore.RED+"Error: Could Not Find Specified Directory")
                            time.sleep(1.5)
                            filetransferfiles()
                else:
                    print(Fore.RED+"Process Was Cancelled By The User")
                    time.sleep(1.5)
                    whatsapptransfer()
                time.sleep(1.5)
                whatsapptransfer()
            else:
                pass
            if whatsapptransfer_input_low in file_transfer_vid_whats_list:
                print(Fore.GREEN+"Select Which Folder You Want To Save Copied Files Into")
                time.sleep(1)
                root_tk = Tk()
                root_tk.iconify()
                ask_save_dir = fd.askdirectory()
                dir_len = len(ask_save_dir)
                if dir_len != 0:
                    print(Fore.BLUE+"Copying Files...")
                    one_dir_whats_vid = subprocess.run(["adb","pull","sdcard/Android/media/com.whatsapp/WhatsApp/Media/WhatsApp Video",ask_save_dir],shell=True, capture_output=True).stdout.decode()
                    search_one_dir_whats_vid_search = re.search("No such file or directory", one_dir_whats_vid)
                    if search_one_dir_whats_vid_search is None:
                        print(Fore.GREEN+"Transfer Completed "+Fore.RED+"Saved in "+ask_save_dir)
                    else:
                        print(Fore.RED+"Directory Not Located"+Fore.GREEN+" Searching In A Diffrent Location")
                        time.sleep(1)
                        two_dir_whats_vid =subprocess.run(["adb","pull","sdcard/WhatsApp/Media/WhatsApp Video",ask_save_dir],shell=True, capture_output=True).stdout.decode()
                        search_two_dir_whats_vid = re.search("No such file or directory", two_dir_whats_vid)
                        if search_two_dir_whats_vid is None:
                            print(Fore.GREEN+"Transfer Completed "+Fore.YELLOW+"Saved in "+ask_save_dir)
                        else:
                            print(Fore.RED+"Error: Could Not Find Specified Directory")
                            time.sleep(1.5)
                            filetransferfiles()
                else:
                    print(Fore.RED+"Process Was Cancelled By The User")
                    time.sleep(1.5)
                    whatsapptransfer()
                time.sleep(1.5)
                whatsapptransfer()
            else:
                pass
            if whatsapptransfer_input_low in file_transfer_backup_whats_list:
                print(Fore.YELLOW+"Under Development, Coming Soon!")
                time.sleep(2)
                whatsapptransfer()
            else:
                pass
        def filetransferpull():
            print(Fore.WHITE+"==========================================================")
            print(Fore.RED+"Scanning For Devices")
            subprocess.run(["adb","kill-server"],shell=True,capture_output=True)
            subprocess.run(["adb","devices"],shell=True,capture_output=True)
            devices_connected = subprocess.run(["adb","devices"],shell=True,capture_output=True).stdout.decode()
            devices_connected = devices_connected.splitlines()
            if len(devices_connected) == 3:
                print(Fore.GREEN+"Device Detected")
                print(Fore.WHITE+"==========================================================")
                pass
            else:
                pass
            if len(devices_connected) >3:
                print(Fore.RED+"Multiple Devices Connected, Please Connect One Device Only")
                filetransferfiles()
            else:
                pass
            if len(devices_connected) <3:
                print(Fore.RED+"No Devices Connected, Please Connect One Device Only")
                filetransferfiles()
            else:
                pass
            print(Fore.WHITE+"==========================================================")
            print(Fore.LIGHTBLUE_EX+"Copy Screenshots           [/S]\nCopy Files From WhatsApp   [/W]\nCopy Custom Files          [/C]\nAbort Process              [/L]")
            file_transfer_input = str(input())
            file_transfer_input_low = file_transfer_input.lower()
            file_transfer_whatsapp = "/w"
            file_transfer_screenshot_list = "/s"
            file_transfer_specific_list = "/c"
            file_transfer_leave_list = "/l"
            file_transfer_list_all = ["/w","/s","/c","/l"]
            if file_transfer_input_low not in file_transfer_list_all:
                print(Fore.RED+"Invalid Input")
                time.sleep(1.5)
                filetransferpull()
            else:
                pass
            if file_transfer_input_low in file_transfer_leave_list:
                filetransferfiles()
            else:
                pass
            if file_transfer_input_low in file_transfer_screenshot_list:
                print(Fore.GREEN+"Select Which Folder You Want To Save Copied Files Into")
                time.sleep(1)
                root_tk = Tk()
                root_tk.iconify()
                ask_save_dir = fd.askdirectory()
                dir_len = len(ask_save_dir)
                if dir_len != 0:
                    print(Fore.BLUE+"Copying Files...")
                    screenshot_one_dir_pull = subprocess.run(["adb","pull","sdcard/DCIM/Screenshots",ask_save_dir],shell=True, capture_output=True).stdout.decode()
                    screenshot_one_dir_pull_search = re.search("No such file or directory",screenshot_one_dir_pull)
                    if screenshot_one_dir_pull_search is None:
                        print(Fore.GREEN+"Transfer Completed "+Fore.YELLOW+"Saved in "+ask_save_dir)
                        time.sleep(1.5)
                        filetransferfiles()
                    else:
                        print(Fore.RED+"Directory Not Located"+Fore.GREEN+" Searching In A Diffrent Location")
                        time.sleep(1)
                        screenshot_two_dir_pull = subprocess.run(["adb","pull","sdcard/Screenshots",ask_save_dir],shell=True, capture_output=True).stdout.decode()
                        screenshot_two_dir_pull_search = re.search("No such file or directory",screenshot_two_dir_pull)
                        if screenshot_two_dir_pull_search is None:
                            print(Fore.GREEN+"Transfer Completed "+Fore.YELLOW+"Saved in "+ask_save_dir)
                            time.sleep(1.5)
                            filetransferfiles()
                        else:
                            print(Fore.RED+"Directory Not Located"+Fore.GREEN+" Searching In A Diffrent Location")
                            time.sleep(1)
                            screenshot_three_dir_pull = subprocess.run(["adb","pull","sdcard/Pictures/Screenshots",ask_save_dir],shell=True, capture_output=True).stdout.decode()
                            screenshot_three_dir_pull_search = re.search("No such file or directory",screenshot_three_dir_pull)
                            if screenshot_three_dir_pull_search is None:
                                print(Fore.GREEN+"Transfer Completed "+Fore.YELLOW+"Saved in "+ask_save_dir)
                                time.sleep(1.5)
                                filetransferfiles()
                            else:
                                print(Fore.RED+"Error: Could Not Find Specified Directory")
                                time.sleep(1.5)
                                filetransferfiles()
                else:
                    print(Fore.RED+"Process Was Cancelled By The User")
                    time.sleep(1.5)
                    filetransferfiles()
                filetransferfiles()
            else:
                pass
            if file_transfer_input_low in file_transfer_whatsapp:
                whatsapptransfer()
            else:
                pass
            if file_transfer_input_low in file_transfer_specific_list:
                print(Fore.GREEN+"Select Which Folder You Want To Save Copied Files Into")
                time.sleep(1)
                root_tk = Tk()
                root_tk.iconify()
                ask_save_dir = fd.askdirectory()
                dir_len = len(ask_save_dir)
                if dir_len != 0:
                    print(Fore.RED+"Type In The Folder Location You Wish To Copy")
                    print(Fore.GREEN+"Example: sdcard/DCIM/Screenshots")
                    print(Fore.GREEN+"DCIM = Gallery\nsdcard = Internal Storage")
                    custom_file_input = str(input())
                    print(Fore.BLUE+"Copying Files...")
                    custom_command = subprocess.run(["adb","pull",custom_file_input,ask_save_dir],shell=True,capture_output=True).stdout.decode()
                    custom_command_search = re.search("No such file or directory",custom_command)
                    if custom_command_search is None:
                        print(Fore.GREEN+"Transfer Completed "+Fore.RED+"Saved in "+ask_save_dir)
                        time.sleep(1.5)
                        filetransferfiles()
                    else:
                        print(Fore.RED+"No such file or directory")
                        time.sleep(1.5)
                        filetransferfiles()
                else:
                    print(Fore.RED+"Process Was Cancelled By The User")
                    time.sleep(1.5)
                    filetransferfiles()
        if file_tranfer_pull_push_low not in file_tranfer_pull_push_list:
            print(Fore.RED+"Invalid Input")
            time.sleep(1)
            filetransferfiles()
        else:
            pass
        if file_tranfer_pull_push_low in file_tranfer_pull_list:
            filetransferpull()
        else:
            pass
        if file_tranfer_pull_push_low in file_tranfer_push_list:
            filetransferpush()
        else:
            pass
        if file_tranfer_pull_push_low in file_tranfer_pull_push_exit_list:
            start()
        else:
            pass
    debug_mode = str(input())
    debug_mode_low = debug_mode.lower()
    debug_mode_wired_list = "/c"
    debug_mode_wirelessy_list = "/w"
    debug_mode_exit_list = "/x"
    debug_mode_uninstall_list = "/u"
    debug_mode_filetransfer_list = "/f"
    debug_mode_shortcut_list = "/s"
    debug_mode_all_list = ["/f","/u","/x","/w","/c","/s"]
    if debug_mode_low not in debug_mode_all_list:
        print(Fore.RED+"Invalid Input")
        time.sleep(1)
        start()
    else:
        pass
    if debug_mode_low in debug_mode_wired_list:
        wired()
    else:
        pass
    if debug_mode_low in debug_mode_wirelessy_list:
        wireless()
    else:
        pass
    if debug_mode_low in debug_mode_exit_list:
        kill_process()
    else:
        pass
    if debug_mode_low in debug_mode_filetransfer_list:
        filetransferfiles()
    else:
        pass
    if debug_mode_low in debug_mode_shortcut_list:
        shortcut_create()
    else:
        pass
    if debug_mode_low in debug_mode_uninstall_list:
        print(Fore.RED+"Uninstalling...")
        subprocess.run(["adb","kill-server"],capture_output=True)
        subprocess.run(["adb","kill-server"],capture_output=True)
        dir_devices_del = os.path.isdir((os.getcwd()+'\\Devices'))
        if dir_devices_del is True:
            shutil.rmtree(dir_devices_del)
        else:
            pass
        batch_path = r'C:\\Users\\' + getpass.getuser() + r'\\AppData\\LocalLow\\Temp\\android-del.bat'
        current_dir_unins = '"'+ os.getcwd() + r"\unins000.exe"+'"'
        batch_file = open(batch_path,"w+")
        batch_file.write('TASKKILL /F /IM "Android Debugger.exe"'+'\n'+current_dir_unins+' /VERYSILENT /ALLUSERS'+'\n'+'del %0')
        batch_file.close()
        os.startfile(batch_path)
    else:
        start()
start()