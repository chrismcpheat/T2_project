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


def enum(**named_values):
    return type('Enum', (), named_values)
Buttons = enum(TEMP='temp', LOAD='load', CLOCK='clock')

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
        # self.winfo_toplevel().iconbitmap(r'c:\t2\icon.ico')

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
        self.temp_button = tkinter.Button(leftFrame, text="Temperature", width=15, command=self.GetTemp)
        self.temp_button.grid(row=1, column=0, padx=10, pady=5, sticky=W)
        # load time
        self.load_button = tkinter.Button(leftFrame, text="Load Time", width=15, command=self.GetLoad)
        self.load_button.grid(row=2, column=0, padx=10, pady=5, sticky=W)
        # clock speed
        self.clock_button = tkinter.Button(leftFrame, text="Clock Speed", width=15, command=self.GetClock)
        self.clock_button.grid(row=4, column=0, padx=10, pady=5, sticky=W)
        # reset
        self.reset_button = tkinter.Button(master=root, text="Reset", width=15, command=lambda: self.reset())
        self.reset_button.grid(row=2, column=1, pady=20)

        # create canvas and graph in right frame
        mpl.rc('axes', edgecolor='b')
        fig=plt.figure(figsize=(8,6))
        self.ax0 = fig.add_axes([0.1, 0.1, 0.8, 0.8], polar=False)
        self.ax1 = fig.add_axes([0.1, 0.1, 0.8, 0.8], polar=False)
        self.ax2 = fig.add_axes([0.1, 0.1, 0.8, 0.8], polar=False)
        self.canvas = FigureCanvasTkAgg(fig, rightFrame)
        self.canvas.get_tk_widget().grid(row=0,column=1)
        self.canvas.draw()

        # --- empty lists for temperature, loads and clock speeds for X and Y axes of graphs
        # temperature
        self.temp_c1_x = []
        self.temp_c1_y = []
        self.temp_c2_y = []
        # load times
        self.load_c1_x = []
        self.load_c1_y = []
        self.load_c2_y = []
        # clock speeds
        self.clock_c1_x = []
        self.clock_c1_y = []
        self.clock_c2_y = []
        self.clock_bs_y = []

        # sets default button state to 'temp' - this will enumarate each time a different button is pressed
        self.prev_button_state = Buttons
        self.prev_button_state = Buttons.TEMP


    def extract_value_message(self, message, key):
        # extract value by key from the string message
        print(message)
        data_json = json.loads(message)
        print(data_json[key])
        val = int(data_json[key])
        return val

    def GetTemp(self):
        if self.prev_button_state != Buttons.TEMP:
            self.reset()
            self.prev_button_state = Buttons.TEMP

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

            response = str(sock.recv(1024), "utf-8")
            val1 = self.extract_value_message(response, "CPU Core #1")
            val2 = self.extract_value_message(response, "CPU Core #2")


            x = time.time()
            x = x - self.starttime
            y1 = val1
            y2 = val2

            self.temp_c1_x.append(x)
            self.temp_c1_y.append(y1)
            self.temp_c2_y.append(y2)

            self.plot(self.temp_c1_x, self.temp_c1_y, 0)
            self.plot(self.temp_c1_x, self.temp_c2_y, 1)


    def GetLoad(self):
        if self.prev_button_state != Buttons.LOAD:
            self.reset()
            self.prev_button_state = Buttons.LOAD

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
            response = str(sock.recv(2048), "utf-8")
            val1 = self.extract_value_message(response, "CPU Core #1")
            val2 = self.extract_value_message(response, "CPU Core #2")

            x = time.time()
            x = x - self.starttime
            y1 = val1
            y2 = val2

            self.load_c1_x.append(x)
            self.load_c1_y.append(y1)
            self.load_c2_y.append(y2)

            self.plot(self.load_c1_x, self.load_c1_y, 0)
            self.plot(self.load_c1_x, self.load_c2_y, 1)


    def GetClock(self):
        if self.prev_button_state != Buttons.CLOCK:
            self.reset()
            self.prev_button_state = Buttons.CLOCK

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # Connect to server and send data
            # print("connecting again...")
            sock.connect((IP, PORT))

            # request cpu load data from the server
            request = {"type": "request",
                       "param": "clock_speeds"}
            # print(f"client sent: {request}")
            sock.sendall(bytes(json.dumps(request), "utf-8"))
            # print("load request sent...")

            # Receive load data from the server
            response = str(sock.recv(2048), "utf-8")

            val1 = self.extract_value_message(response, "CPU Core #1")
            val2 = self.extract_value_message(response, "CPU Core #2")
            val3 = self.extract_value_message(response, "Bus Speed")

            x = time.time()
            x = x - self.starttime
            y1 = val1
            y2 = val2
            y3 = val3

            self.clock_c1_x.append(x)
            self.clock_c1_y.append(y1)
            self.clock_c2_y.append(y2)
            self.clock_bs_y.append(y3)

            self.plot(self.clock_c1_x, self.clock_c1_y, 0)
            self.plot(self.clock_c1_x, self.clock_c2_y, 1)
            self.plot(self.clock_c1_x, self.clock_bs_y, 2)


    def plot(self, x, y, id):
        if id == 0:
            self.ax0.plot(x, y, color='blue', marker='o', linestyle='dashed', linewidth=1, markersize=3)
        elif id == 1:
            self.ax1.plot(x, y, color='red', marker='o', linestyle='dashed', linewidth=1, markersize=3)
        elif id == 2:
            self.ax2.plot(x, y, color='green', marker='o', linestyle='dashed', linewidth=1, markersize=3)
        self.canvas.draw()

    def reset(self):
        # --- clears all data from graph
        self.ax0.clear()
        self.ax1.clear()
        self.ax2.clear()
        self.starttime = (time.time())
        self.canvas.draw()
        # clears temp data
        self.temp_c1_x.clear()
        self.temp_c1_y.clear()
        self.temp_c2_y.clear()
        # clears load data
        self.load_c1_x.clear()
        self.load_c1_y.clear()
        self.load_c2_y.clear()
        # clears clock data
        self.clock_c1_x.clear()
        self.clock_c1_y.clear()
        self.clock_c2_y.clear()
        self.clock_bs_y.clear()


if __name__ == '__main__':
    # tkinter gui
    # create root
    root = Tk()
    client = ClientGUI(master=root)
    client.mainloop()
    print("exiting...")
