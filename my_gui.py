# https://www.youtube.com/watch?v=gjU3Lx8XMS8
# https://stackoverflow.com/questions/3352918/how-to-center-a-window-on-the-screen-in-tkinter

import socket
import json
from tcp_settings import IP, PORT
import tkinter
from tkinter import *
from functools import partial

root = Tk()


class ClientGUI:

    def __init__(self, master):  # constructor - creates frame and positions in centre of window

        main_frame = Frame(master, width=1200, height=1200, bg="#f9f9f9")  # creates frame and sets colour to light grey
        main_frame.pack()  # places frame in window

        root.title("ScanWare")  # sets window title to 'ScanWare'
        root.iconbitmap(r'c:\t2\icon.ico')  # sets window icon to custom-made icon

        self.windowLog = Text(main_frame, takefocus=0)
        self.windowLog.grid(column=1, padx=10, pady=10)

        leftFrame = Frame(main_frame, width=50, height=50, bg="#f9f9f9")
        leftFrame.grid(row=0, column=0, padx=10, pady=2)

        # CPU label and buttons
        label_cpu = Label(leftFrame, text="CPU")
        label_cpu.grid(row=0, column=0, padx=40, pady=10, sticky=W)

        btn_cpu_temp = Button(leftFrame, text="Temperature", width=10, command=partial(self.GetTemp))
        btn_cpu_temp.grid(row=1, column=0, padx=40, pady=10)

        btn_cpu_load = Button(leftFrame, text="Load Times", width=10, command=partial(self.GetLoad))
        btn_cpu_load.grid(row=2, column=0, padx=40, pady=10)

        # clock label and buttons
        label_clock = Label(leftFrame, text="Clocks")
        label_clock.grid(row=3, column=0, padx=40, pady=10, sticky=W)

        btn_clock = Button(leftFrame, text="Speed", width=10, command=partial(self.GetClock))
        btn_clock.grid(row=4, column=0, padx=40, pady=10)

    def GetTemp(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # Connect to server and send data
            print("connecting...")
            sock.connect((IP, PORT))

            # request cpu temperature data from the server
            request = {"type": "request",
                       "param": "cpu_core_temp"}
            print(f"client sent: {request}")
            sock.sendall(bytes(json.dumps(request), "utf-8"))
            print("temp request sent...")

            # Receive temperature data from the server
            temp_response = str(sock.recv(1024), "utf-8")
            print(f"server temp received: {temp_response}")

            self.windowLog.insert(0.0, temp_response)
            self.windowLog.insert(0.0, "\n")

    def GetLoad(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # Connect to server and send data
            print("connecting again...")
            sock.connect((IP, PORT))

            # request cpu load data from the server
            request = {"type": "request",
                       "param": "cpu_core_load"}
            print(f"client sent: {request}")
            sock.sendall(bytes(json.dumps(request), "utf-8"))
            print("load request sent...")

            # Receive load data from the server
            load_response = str(sock.recv(2048), "utf-8")
            print(f"server load received: {load_response}")

            self.windowLog.insert(0.0, load_response)
            self.windowLog.insert(0.0, "\n")

    def GetClock(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # Connect to server and send data
            print("connecting again...")
            sock.connect((IP, PORT))

            # request cpu load data from the server
            request = {"type": "request",
                       "param": "clock_speeds"}
            print(f"client sent: {request}")
            sock.sendall(bytes(json.dumps(request), "utf-8"))
            print("load request sent...")

            # Receive load data from the server
            load_response = str(sock.recv(2048), "utf-8")
            print(f"server load received: {load_response}")

            self.windowLog.insert(0.0, load_response)
            self.windowLog.insert(0.0, "\n")

    """
    def win_center(self):
        master.update_idletasks()  # calls all pending idle tasks to ensure that measurements of window are accurate,
        x_win = self.winfo_screenwidth()  # measures size of window along X axis
        y_win = self.winfo_screenheight()  # measures size of window along Y axis
        size = tuple(int(_) for _ in self.geometry().split('+')[0].split('x'))
        x_pos = x_win / 2 - size[0] / 2  # calculates position of window along X axis
        y_pos = y_win / 2 - size[1] / 2  # calculates position of window along Y axis
        self.geometry("%dx%d+%d+%d" % (size + (x_pos, y_pos)))  # combines size plus positions to centre the frame
        """


if __name__ == '__main__':
    ClientGUI(root)
    root.mainloop()
