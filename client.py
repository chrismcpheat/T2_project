# https://www.youtube.com/watch?v=gjU3Lx8XMS8
# https://stackoverflow.com/questions/3352918/how-to-center-a-window-on-the-screen-in-tkinter

import socket
import json
from tcp_settings import IP, PORT
import tkinter
from tkinter import *
import tkinter.ttk as ttk
from functools import partial
import time
import numpy as np
import matplotlib as mpl
from matplotlib import style
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.patches as mpatches
import warnings
import matplotlib.cbook
warnings.filterwarnings("ignore",category=matplotlib.cbook.mplDeprecation)


# style of graph
style.use("ggplot")
# bg colours
BG_COLOUR = "#f7f7f7"
# fonts
LARGE_FONT = ("Arial", 10, "bold") # for headings
SMALL_FONT = ("Arial", 8) # for 'About' window


# last pushed button
# changes state to value of button, to prevent data being reset/cleared if the button pushed is the same as the last
def enum(**named_values):
    return type('Enum', (), named_values)
LastPush = enum(TEMP='temp', LOAD='load', CLOCK='clock', POWER='power')

# GUI class
class ClientApp(tkinter.Frame):

    # init method - creates window, sets bg colour, starts timer to plot on X axis
    def __init__(self, master=None):
        tkinter.Frame.__init__(self, master)
        master.configure(background=BG_COLOUR)
        self.starttime = (time.time())
        self.CreateWidgets()

    # function creates all widgets
    def CreateWidgets(self):

        # ------ set title and icon of application
        self.winfo_toplevel().title("ScanWare")
        self.winfo_toplevel().iconbitmap(r'c:\t2\icon.ico')

        # ------ frames
        # creates left frame for labels and buttons
        leftFrame = Frame(master=root, width=150, height=300, bg=BG_COLOUR)
        leftFrame.grid(row=0, column=0, padx=10, pady=0)
        leftFrame.grid_propagate(0)
        # creates right frame for graph
        graphFrame = Frame(master=root, width=0, height=50)
        graphFrame.grid(row=0, column=1, pady=2)

        # ------ menus
        # dropdown menu bar
        menuBar = Menu(master=root)
        master=root.config(menu=menuBar)
        # 'File' menu
        fileMenu = Menu(menuBar, tearoff=0)
        menuBar.add_cascade(label="File", menu=fileMenu)
        fileMenu.add_command(label="Exit", command=root.destroy)
        # 'Edit' menu
        editMenu = Menu(menuBar, tearoff=0)
        menuBar.add_cascade(label="Edit", menu=editMenu)
        editMenu.add_command(label="Reset", command=lambda: self.ResetData())
        # 'Help' menu
        helpMenu = Menu(menuBar, tearoff=0)
        menuBar.add_cascade(label="Help", menu=helpMenu)
        helpMenu.add_command(label="About", command=lambda: self.AboutWindow())

        # ------ labels
        # cpu
        label_cpu = Label(leftFrame, text="CPU", font=LARGE_FONT)
        label_cpu.grid(row=0, column=0, padx=10, pady=10, sticky=W)
        # clocks
        label_clock = Label(leftFrame, text="Clocks", font=LARGE_FONT)
        label_clock.grid(row=4, column=0, padx=10, pady=10, sticky=W)

        # ------ buttons and commands
        # cpu temperatures
        self.temp_button = ttk.Button(leftFrame, text="Temperature", width=20, command=self.GetTemp)
        self.temp_button.grid(row=1, column=0, padx=10, pady=5, sticky=W)
        # cpu loads
        self.load_button = ttk.Button(leftFrame, text="Load", width=20, command=self.GetLoad)
        self.load_button.grid(row=2, column=0, padx=10, pady=5, sticky=W)
        # cpu powers
        self.power_button = ttk.Button(leftFrame, text="Power", width=20, command=self.GetPower)
        self.power_button.grid(row=3, column=0, padx=10, pady=5, sticky=W)
        # clock speeds
        self.clock_button = ttk.Button(leftFrame, text="Clock Speed", width=20, command=self.GetClock)
        self.clock_button.grid(row=5, column=0, padx=10, pady=5, sticky=W)
        # reset
        self.reset_button = ttk.Button(master=root, text="Reset", width=15, command=lambda: self.ResetData())
        self.reset_button.grid(row=2, column=1, pady=20)

        # ------ graph / figure
        # create figure and set size
        self.fig=plt.figure(figsize=(8,5), facecolor=BG_COLOUR)
        # multiple axes for multiple plots
        self.ax0 = self.fig.add_axes([0.1, 0.1, 0.8, 0.8], polar=False)
        self.ax1 = self.fig.add_axes([0.1, 0.1, 0.8, 0.8], polar=False)
        self.ax2 = self.fig.add_axes([0.1, 0.1, 0.8, 0.8], polar=False)
        self.ax3 = self.fig.add_axes([0.1, 0.1, 0.8, 0.8], polar=False)
        # creates graphs
        self.canvas = FigureCanvasTkAgg(self.fig, graphFrame)
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

    # function creates 'About' window
    def AboutWindow(msg):
        # creates 'About ScanWare' window
        about_window = Tk()
        about_window.config(bg=BG_COLOUR)
        about_window.winfo_toplevel().title("About ScanWare")
        about_window.winfo_toplevel().iconbitmap(r'c:\t2\icon.ico')
        # text box + information
        about_txt = Text(about_window, width=30, height=5, font=SMALL_FONT, bg=BG_COLOUR, relief=FLAT)
        about_txt.config(state=NORMAL)
        about_txt.insert(END, "© ScanWare\nVersion 1.0\nChris McPheat\nIntro to Software Development\nGRLA07002\nUWS")
        about_txt.config(state=DISABLED)
        about_txt.pack(side=TOP, fill="x", padx=50, pady=20)
        # 'OK' button, which kills window
        ok_btn = ttk.Button(about_window, text="OK", command=about_window.destroy)
        ok_btn.pack(pady=20)
        # loops the window
        about_window.mainloop()

    # function pulls out data from response from server
    def ExtractResponse(self, message, key):
        # extract value by key from the string message
        data_json = json.loads(message)
        val = int(data_json[key])
        return val

    # function is called when 'Temperature' button is pressed
    def GetTemp(self):

        if self.prev_button_state != LastPush.TEMP:
            self.ResetData()
            self.prev_button_state = LastPush.TEMP

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # Connect to server and send data
            sock.connect((IP, PORT))

            # request cpu temperature data from the server
            request = {"type": "request",
                       "param": "cpu_core_temp"}
            sock.sendall(bytes(json.dumps(request), "utf-8"))

            response = str(sock.recv(1024), "utf-8")
            val1 = self.ExtractResponse(response, "CPU Core #1")
            val2 = self.ExtractResponse(response, "CPU Core #2")

            x = time.time()
            x = x - self.starttime
            y1 = val1
            y2 = val2

            self.temp_c1_x.append(x)
            self.temp_c1_y.append(y1)
            self.temp_c2_y.append(y2)

            label_x = 'Time (s)'
            label_y = 'Temperature (°C)'
            legend_0 = mpatches.Patch(color='#5B76AC', label='CPU Core #1')
            legend_1 = mpatches.Patch(color='#F96B6F', label='CPU Core #2')

            plt.legend(handles=[legend_0, legend_1])
            plt.xlabel(label_x, fontsize=8, labelpad=10)
            plt.ylabel(label_y, fontsize=7, labelpad=10)

            """
            # ------ attempting to place legend outside - not working
            legend_0 = mpatches.Patch(color='red', label='CPU Core #1')
            legend_1 = mpatches.Patch(color='blue', label='CPU Core #2')
            plt.legend(handles=[legend_0, legend_1], bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
            """

            self.PlotData(self.temp_c1_x, self.temp_c1_y, 0)
            self.PlotData(self.temp_c1_x, self.temp_c2_y, 1)

    # function is called when 'Load' button is pressed
    def GetLoad(self):
        if self.prev_button_state != LastPush.LOAD:
            self.ResetData()
            self.prev_button_state = LastPush.LOAD

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # Connect to server and send data
            sock.connect((IP, PORT))

            # request cpu load data from the server
            request = {"type": "request",
                       "param": "cpu_core_load"}
            sock.sendall(bytes(json.dumps(request), "utf-8"))

            # Receive load data from the server
            response = str(sock.recv(2048), "utf-8")
            val1 = self.ExtractResponse(response, "CPU Core #1")
            val2 = self.ExtractResponse(response, "CPU Core #2")

            x = time.time()
            x = x - self.starttime
            y1 = val1
            y2 = val2

            self.load_c1_x.append(x)
            self.load_c1_y.append(y1)
            self.load_c2_y.append(y2)

            label_x = 'Time (s)'
            label_y = 'Load (%)'
            legend_0 = mpatches.Patch(color='#5B76AC', label='CPU Core #1')
            legend_1 = mpatches.Patch(color='#F96B6F', label='CPU Core #2')

            plt.legend(handles=[legend_0, legend_1])
            plt.xlabel(label_x, fontsize=8, labelpad=10)
            plt.ylabel(label_y, fontsize=8, labelpad=10)

            self.PlotData(self.load_c1_x, self.load_c1_y, 0)
            self.PlotData(self.load_c1_x, self.load_c2_y, 1)

    # function is called when 'Power' button is pressed
    def GetPower(self):
        if self.prev_button_state != LastPush.POWER:
            self.ResetData()
            self.prev_button_state = LastPush.POWER

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # Connect to server and send data
            sock.connect((IP, PORT))

            # request cpu load data from the server
            request = {"type": "request",
                       "param": "cpu_core_power"}
            sock.sendall(bytes(json.dumps(request), "utf-8"))

            # Receive load data from the server
            response = str(sock.recv(2048), "utf-8")

            val1 = self.ExtractResponse(response, "CPU DRAM")
            val2 = self.ExtractResponse(response, "CPU Package")
            val3 = self.ExtractResponse(response, "CPU Cores")
            val4 = self.ExtractResponse(response, "CPU Graphics")

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
            legend_0 = mpatches.Patch(color='#5B76AC', label='DRAM')
            legend_1 = mpatches.Patch(color='#F96B6F', label='Package')
            legend_2 = mpatches.Patch(color='#16A28F', label='Cores')
            legend_3 = mpatches.Patch(color='#EAA846', label='Graphics')

            plt.legend(handles=[legend_0, legend_1, legend_2, legend_3])
            plt.xlabel(label_x, fontsize=8, labelpad=10)
            plt.ylabel(label_y, fontsize=8, labelpad=10)


            self.PlotData(self.power_cd_x, self.power_cd_y, 0)
            self.PlotData(self.power_cd_x, self.power_cp_y, 1)
            self.PlotData(self.power_cd_x, self.power_cc_y, 2)
            self.PlotData(self.power_cd_x, self.power_cg_y, 3)

    # function is called when 'Clock Speed' button is pressed
    def GetClock(self):
        if self.prev_button_state != LastPush.CLOCK:
            self.ResetData()
            self.prev_button_state = LastPush.CLOCK

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # Connect to server and send data
            sock.connect((IP, PORT))

            # request cpu load data from the server
            request = {"type": "request",
                       "param": "clock_speeds"}
            sock.sendall(bytes(json.dumps(request), "utf-8"))

            # Receive load data from the server
            response = str(sock.recv(2048), "utf-8")

            val1 = self.ExtractResponse(response, "CPU Core #1")
            val2 = self.ExtractResponse(response, "CPU Core #2")
            val3 = self.ExtractResponse(response, "Bus Speed")

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
            legend_0 = mpatches.Patch(color='#5B76AC', label='CPU Core #1')
            legend_1 = mpatches.Patch(color='#F96B6F', label='CPU Core #2')
            legend_2 = mpatches.Patch(color='#16A28F', label='Bus Speed')

            plt.legend(handles=[legend_0, legend_1, legend_2])
            plt.xlabel(label_x, fontsize=8, labelpad=10)
            plt.ylabel(label_y, fontsize=8, labelpad=10)

            self.PlotData(self.clock_c1_x, self.clock_c1_y, 0)
            self.PlotData(self.clock_c1_x, self.clock_c2_y, 1)
            self.PlotData(self.clock_c1_x, self.clock_bs_y, 2)

    # function polts data to the graph
    def PlotData(self, x, y, id):

        if id == 0:
            self.ax0.plot(x, y, color='#5B76AC', marker='.', linestyle='solid', linewidth=2, markersize=0) # blue
        elif id == 1:
            self.ax1.plot(x, y, color='#F96B6F', marker='.', linestyle='solid', linewidth=2, markersize=0) # red
        elif id == 2:
            self.ax2.plot(x, y, color='#16A28F', marker='.', linestyle='solid', linewidth=2, markersize=0) # green
        elif id == 3:
            self.ax3.plot(x, y, color='#EAA846', marker='.', linestyle='solid', linewidth=2, markersize=0) # yellow
        self.canvas.draw()

    # function clears the graph
    def ResetData(self):
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
    client = ClientApp(master=root)
    client.mainloop()
    print("exiting...")
