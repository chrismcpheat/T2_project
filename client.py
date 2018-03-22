# https://www.youtube.com/watch?v=gjU3Lx8XMS8
# https://stackoverflow.com/questions/3352918/how-to-center-a-window-on-the-screen-in-tkinter

import socket
import json
from tcp_settings import IP, PORT
import tkinter
from tkinter import *
from functools import partial
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time
import numpy as np



class ClientGUI(tkinter.Frame):

    # test function for dropdown menu
    def doNothing(self):
        print("TESTING")

    def __init__(self, master=None):
        tkinter.Frame.__init__(self, master)
        self.starttime = (time.time())
        self.CreateWidgets()


    def CreateWidgets(self):

        # set title and icon of application
        self.winfo_toplevel().title("ScanWare")
        self.winfo_toplevel().iconbitmap(r'c:\t2\icon.ico')

        # dropdown menu bar
        menuBar = Menu(master=root)
        master=root.config(menu=menuBar)

        # creates left frame for labels and buttons
        leftFrame = Frame(master=root, width=50, height=50)
        leftFrame.grid(row=0, column=0, padx=10, pady=2)

        # creates right frame for graph
        rightFrame = Frame(master=root, width=50, height=50)
        rightFrame.grid(row=0, column=1, padx=10, pady=2)

        # 'File' menu
        fileMenu = Menu(menuBar, tearoff=0)
        menuBar.add_cascade(label="File", menu=fileMenu)
        fileMenu.add_command(label="New 2", command=partial(self.doNothing))
        fileMenu.add_command(label="New", command=partial(self.doNothing))
        fileMenu.add_separator()
        fileMenu.add_command(label="Exit", command=root.destroy)

        # 'Edit' menu
        editMenu = Menu(menuBar, tearoff=0)
        menuBar.add_cascade(label="Edit", menu=editMenu)
        editMenu.add_command(label="Redo", command=partial(self.doNothing))

        # --- labels
        # cpu
        label_cpu = Label(leftFrame, text="CPU")
        label_cpu.grid(row=0, column=0, padx=10, pady=10, sticky=W)
        # clocks
        label_clock = Label(leftFrame, text="Clocks")
        label_clock.grid(row=3, column=0, padx=10, pady=10, sticky=W)

        # --- buttons and commands
        # temperature
        self.temp_button = tkinter.Button(leftFrame, text="Temperature", width=15, command=lambda: self.plot(canvas,ax))
        self.temp_button.grid(row=1, column=0, padx=10, pady=5, sticky=W)
        # load time
        # self.load_button = tkinter.Button(leftFrame, text="Load Time", width=15, command=lambda: self.plot(canvas, ax))
        # self.load_button.grid(row=2, column=0, padx=10, pady=5, sticky=W)
        self.load_button = tkinter.Button(leftFrame, text="Load Time", width=15, command=self.GetLoad)
        self.load_button.grid(row=2, column=0, padx=10, pady=5, sticky=W)
        # clock speed
        self.clock_button = tkinter.Button(leftFrame, text="Clock Speed", width=15, command=lambda: self.plot(canvas, ax))
        self.clock_button.grid(row=4, column=0, padx=10, pady=5, sticky=W)
        # reset
        self.reset_button = tkinter.Button(master=root, text="Reset", width=15, command=lambda: self.reset(canvas, ax))
        self.reset_button.grid(row=2, column=1, pady=20)

        # create canvas and graph in right frame
        mpl.rc('axes', edgecolor='b')
        fig=plt.figure(figsize=(8,6))
        ax=fig.add_axes([0.1,0.1,0.8,0.8],polar=False)
        canvas = FigureCanvasTkAgg(fig, rightFrame)
        canvas.get_tk_widget().grid(row=0,column=1)
        canvas.draw()

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
            #print("connecting again...")
            sock.connect((IP, PORT))

            # request cpu load data from the server
            request = {"type": "request",
                       "param": "cpu_core_load"}
            #print(f"client sent: {request}")
            sock.sendall(bytes(json.dumps(request), "utf-8"))
            #print("load request sent...")

            # Receive load data from the server
            load_response = str(sock.recv(2048), "utf-8")
            print(f"server load received: {load_response}")
            load_time = json.loads(load_response)
            core1 = load_time['CPU Core #1']
            core2 = load_time['CPU Core #2']
            print(core1)
            print(core2)

            """
            self.windowLog.insert(0.0, load_response)
            self.windowLog.insert(0.0, "\n")
            """


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

    def plot(self, canvas, ax):
        x = epoch_time = (time.time())
        x = x - self.starttime
        y = np.random.random()
        ax.plot(x,y, color='red', marker='o', linestyle='dashed', linewidth=2, markersize=6)
        canvas.draw()

    def reset(self, canvas, ax):
        ax.clear()
        self.starttime = (time.time())
        canvas.draw()


if __name__ == '__main__':
    # tkinter gui
    # create root
    root = Tk()
    client = ClientGUI(master=root)
    client.mainloop()
    print("exiting...")
