import socket
import json
from network_config import HOST, PORT
import tkinter
from tkinter import *
from functools import partial


### TESTING BRANCH ###

class ClientGUI():
    def __init__(self, master):
        # upper frame and its contents
        upperFrame = Frame(master, width=50, height=30)
        upperFrame.grid(row=0, column=0, padx=10, pady=2)

        # Right Frame and its contents
        lowerFrame = Frame(master, width=50, height=60)
        lowerFrame.grid(row=1, column=0, padx=10, pady=2)

        # button frame
        btnFrame = Frame(upperFrame, width=50, height=30)
        btnFrame.grid(row=1, column=0, padx=10, pady=2)

        # text box
        self.windowLog = Text(lowerFrame, width=50, height=30, takefocus=0)
        self.windowLog.grid(row=2, column=0, padx=10, pady=2)

        # pressing a button can trigger a function call (and we can pass input arguments / parameters)
        #  https://pythonprogramming.net/passing-functions-parameters-tkinter-using-lambda/
        tempBtn = Button(btnFrame, text="Temp", command=partial(self.GetTemp))
        tempBtn.grid(row=0, column=0, padx=10, pady=2)

        loadBtn = Button(btnFrame, text="Load", command=partial(self.GetLoad))
        loadBtn.grid(row=0, column=1, padx=10, pady=2)

    def GetTemp(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # Connect to server and send data
            print("connecting...")
            sock.connect((HOST, PORT))

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
            sock.connect((HOST, PORT))

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


if __name__ == '__main__':
    # tkinter gui
    # create root
    root = tkinter.Tk()
    client = ClientGUI(root)
    root.mainloop()
    print("exiting...")
