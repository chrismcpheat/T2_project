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
import matplotlib.patches as mpatches
import time
import numpy as np
import warnings
import matplotlib.cbook
warnings.filterwarnings("ignore",category=matplotlib.cbook.mplDeprecation)


# last pushed button
# changes state to value of button, to prevent data being reset/cleared if the button pushed is the same as the last
def enum(**named_values):
    return type('Enum', (), named_values)
LastPush = enum(TEMP='temp', LOAD='load', CLOCK='clock', POWER='power')

class ClientGUI(tkinter.Frame):


    # test function for dropdown menu
    def doNothing(self):
        print("TESTING")


    def __init__(self, master=None):
        tkinter.Frame.__init__(self, master)
        master.configure(background='grey')
        self.starttime = (time.time())
        self.CreateWidgets()


    def CreateWidgets(self):

        # ------ set title and icon of application
        self.winfo_toplevel().title("ScanWare")
        self.winfo_toplevel().iconbitmap(r'c:\t2\icon.ico')

        # ------ frames
        # creates left frame for labels and buttons
        leftFrame = Frame(master=root, width=150, height=300, bg="#EEF1F6")
        leftFrame.grid(row=0, column=0, padx=10, pady=0)
        leftFrame.grid_propagate(0)

        # creates right frame for graph
        middleFrame = Frame(master=root, width=0, height=50)
        middleFrame.grid(row=0, column=1, pady=2)

        # ------ menus
        # dropdown menu bar
        menuBar = Menu(master=root)
        master=root.config(menu=menuBar)

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
        editMenu.add_command(label="Reset", command=lambda: self.reset())

        # ------ labels
        # cpu
        label_cpu = Label(leftFrame, text="CPU", font="Helvetica 10 bold")
        label_cpu.grid(row=0, column=0, padx=10, pady=10, sticky=W)
        # clocks
        label_clock = Label(leftFrame, text="Clocks", font="Helvetica 10 bold")
        label_clock.grid(row=4, column=0, padx=10, pady=10, sticky=W)


        # ------ buttons and commands
        # cpu temperatures
        self.temp_button = tkinter.Button(leftFrame, text="Temperatures", width=15, command=self.GetTemp)
        self.temp_button.grid(row=1, column=0, padx=10, pady=5, sticky=W)
        # cpu loads
        self.load_button = tkinter.Button(leftFrame, text="Loads", width=15, command=self.GetLoad)
        self.load_button.grid(row=2, column=0, padx=10, pady=5, sticky=W)
        # cpu powers`
        self.power_button = tkinter.Button(leftFrame, text="Powers", width=15, command=self.GetPower)
        self.power_button.grid(row=3, column=0, padx=10, pady=5, sticky=W)
        # clock speeds
        self.clock_button = tkinter.Button(leftFrame, text="Clock Speed", width=15, command=self.GetClock)
        self.clock_button.grid(row=5, column=0, padx=10, pady=5, sticky=W)
        # reset
        self.reset_button = tkinter.Button(master=root, text="Reset", width=15, command=lambda: self.reset())
        self.reset_button.grid(row=2, column=1, pady=20)

        # create canvas and graph in right frame
        self.fig=plt.figure(figsize=(8,5), facecolor="#EEF1F6")



        self.ax0 = self.fig.add_axes([0.1, 0.1, 0.8, 0.8], polar=False)
        self.ax1 = self.fig.add_axes([0.1, 0.1, 0.8, 0.8], polar=False)
        self.ax2 = self.fig.add_axes([0.1, 0.1, 0.8, 0.8], polar=False)
        self.ax3 = self.fig.add_axes([0.1, 0.1, 0.8, 0.8], polar=False)

        self.canvas = FigureCanvasTkAgg(self.fig, middleFrame)
        self.canvas.get_tk_widget().grid(row=0, column=1, padx=0)
        self.canvas.draw()

        # ------ empty lists for cpu temperature, cpu loads, clock speeds and cpu powers for X and Y axes
        # cpu temperatures
        self.temp_c1_x = [] # x axis - time
        self.temp_c1_y = [] # y axis core 1
        self.temp_c2_y = [] # y axis core 2
        # cpu load times
        self.load_c1_x = [] # x axis - time
        self.load_c1_y = [] # y axis core 1
        self.load_c2_y = [] # y axis core 2
        # clock speeds
        self.clock_c1_x = [] # x axis - time
        self.clock_c1_y = [] # y axis core 1
        self.clock_c2_y = [] # y axis core 2
        self.clock_bs_y = [] # y axis bus speed
        # cpu powers
        self.power_cd_x = [] # x asis - time
        self.power_cd_y = [] # y axis cpu dram
        self.power_cp_y = [] # y axis cpu package
        self.power_cc_y = [] # y axis cpu cores
        self.power_cg_y = [] # y axis cpu graphics

        # sets default button state to 'temp' - this will enumarate each time a different button is pressed
        self.prev_button_state = LastPush
        self.prev_button_state = LastPush.TEMP


    def extract_value_message(self, message, key):
        # extract value by key from the string message
        print(message)
        data_json = json.loads(message)
        print(data_json[key])
        val = int(data_json[key])
        return val


    def GetTemp(self):

        if self.prev_button_state != LastPush.TEMP:
            self.reset()
            self.prev_button_state = LastPush.TEMP

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # Connect to server and send data
            # print("connecting...")
            sock.connect((IP, PORT))

            # request cpu temperature data from the server
            request = {"type": "request",
                       "param": "cpu_core_temp"}
            # print(f"client sent: {request}")
            sock.sendall(bytes(json.dumps(request), "utf-8"))
            # print("temp request sent...")

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

            label_x = 'Time (s)'
            label_y = 'Temperature (°C)'
            legend_0 = mpatches.Patch(color='blue', label='CPU Core #1')
            legend_1 = mpatches.Patch(color='red', label='CPU Core #2')

            plt.legend(handles=[legend_0, legend_1])
            plt.xlabel(label_x, fontsize=8, labelpad=10)
            plt.ylabel(label_y, fontsize=7, labelpad=10)

            """
            # ------ attempting to place legend outside - not working
            legend_0 = mpatches.Patch(color='red', label='CPU Core #1')
            legend_1 = mpatches.Patch(color='blue', label='CPU Core #2')
            plt.legend(handles=[legend_0, legend_1], bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
            """

            self.plot(self.temp_c1_x, self.temp_c1_y, 0)
            self.plot(self.temp_c1_x, self.temp_c2_y, 1)


    def GetLoad(self):
        if self.prev_button_state != LastPush.LOAD:
            self.reset()
            self.prev_button_state = LastPush.LOAD

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

            label_x = 'Time (s)'
            label_y = 'Load (%)'
            legend_0 = mpatches.Patch(color='blue', label='CPU Core #1')
            legend_1 = mpatches.Patch(color='red', label='CPU Core #2')

            plt.legend(handles=[legend_0, legend_1])
            plt.xlabel(label_x, fontsize=8, labelpad=10)
            plt.ylabel(label_y, fontsize=8, labelpad=10)

            self.plot(self.load_c1_x, self.load_c1_y, 0)
            self.plot(self.load_c1_x, self.load_c2_y, 1)


    def GetPower(self):
        if self.prev_button_state != LastPush.POWER:
            self.reset()
            self.prev_button_state = LastPush.POWER

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # Connect to server and send data
            # print("connecting again...")
            sock.connect((IP, PORT))

            # request cpu load data from the server
            request = {"type": "request",
                       "param": "cpu_core_power"}
            # print(f"client sent: {request}")
            sock.sendall(bytes(json.dumps(request), "utf-8"))
            # print("load request sent...")

            # Receive load data from the server
            response = str(sock.recv(2048), "utf-8")

            val1 = self.extract_value_message(response, "CPU DRAM")
            val2 = self.extract_value_message(response, "CPU Package")
            val3 = self.extract_value_message(response, "CPU Cores")
            val4 = self.extract_value_message(response, "CPU Graphics")

            x = time.time()
            x = x - self.starttime
            y1 = val1
            y2 = val2
            y3 = val3
            y4 = val4

            self.power_cd_x.append(x)
            self.power_cd_y.append(y1)
            self.power_cp_y.append(y2)
            self.power_cc_y.append(y3)
            self.power_cg_y.append(y4)

            label_x = 'Time (s)'
            label_y = 'Power (W)'
            legend_0 = mpatches.Patch(color='blue', label='DRAM')
            legend_1 = mpatches.Patch(color='red', label='Package')
            legend_2 = mpatches.Patch(color='green', label='Cores')
            legend_3 = mpatches.Patch(color='yellow', label='Graphics')

            plt.legend(handles=[legend_0, legend_1, legend_2, legend_3])
            plt.xlabel(label_x, fontsize=8, labelpad=10)
            plt.ylabel(label_y, fontsize=8, labelpad=10)


            self.plot(self.power_cd_x, self.power_cd_y, 0)
            self.plot(self.power_cd_x, self.power_cp_y, 1)
            self.plot(self.power_cd_x, self.power_cc_y, 2)
            self.plot(self.power_cd_x, self.power_cg_y, 3)


    def GetClock(self):
        if self.prev_button_state != LastPush.CLOCK:
            self.reset()
            self.prev_button_state = LastPush.CLOCK

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

            label_x = 'Time (s)'
            label_y = 'Rate (MHz)'
            legend_0 = mpatches.Patch(color='blue', label='CPU Core #1')
            legend_1 = mpatches.Patch(color='red', label='CPU Core #2')
            legend_2 = mpatches.Patch(color='green', label='Bus Speed')

            plt.legend(handles=[legend_0, legend_1, legend_2])
            plt.xlabel(label_x, fontsize=8, labelpad=10)
            plt.ylabel(label_y, fontsize=8, labelpad=10)

            self.plot(self.clock_c1_x, self.clock_c1_y, 0)
            self.plot(self.clock_c1_x, self.clock_c2_y, 1)
            self.plot(self.clock_c1_x, self.clock_bs_y, 2)


    def plot(self, x, y, id):

        if id == 0:
            self.ax0.plot(x, y, color='#2124ff', marker='o', linestyle='solid', linewidth=1, markersize=2)
        elif id == 1:
            self.ax1.plot(x, y, color='#ff2121', marker='o', linestyle='solid', linewidth=1, markersize=2)
        elif id == 2:
            self.ax2.plot(x, y, color='#21ff21', marker='o', linestyle='solid', linewidth=1, markersize=2)
        elif id == 3:
            self.ax3.plot(x, y, color='#fff721', marker='o', linestyle='solid', linewidth=1, markersize=2)
        self.canvas.draw()


    def reset(self):
        # ------ resets graph
        # clears axes
        self.ax0.clear()
        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()
        # clears start time
        self.starttime = (time.time())
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
        # clears power data
        self.power_cd_x.clear()
        self.power_cd_y.clear()
        self.power_cp_y.clear()
        self.power_cc_y.clear()
        self.power_cg_y.clear()
        # re-draws blank canvas
        self.canvas.draw()


if __name__ == '__main__':
    # tkinter gui
    # create root
    root = Tk()
    # root.configure(background='#EEF1F6')
    client = ClientGUI(master=root)
    client.mainloop()
    print("exiting...")
