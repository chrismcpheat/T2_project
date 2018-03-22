import socketserver
import time
from tcp_settings import IP, PORT

from OHM import OHM
import json


class TCPRequestHandler(socketserver.BaseRequestHandler):
    """
    The request handler receives the response data from the client
    """

    def __init__(self, request, client_address, server):

        print("initialising. . . ")
        # Init the base class
        super(TCPRequestHandler, self).__init__(request, client_address, server)

    def handle(self):
        # time.sleep(1)
        """
        The request handler class.
        """
        print("client data incoming...")
        #  self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip().decode("utf-8")  # NB bytes to string
        # print(f"data received: {self.data}")

        # request OHM data
        requested_data = {}
        my_ohm = OHM()
        request = json.loads(self.data)
        if request['type'] == 'request':
            if request['param'] == 'cpu_core_temp':
                requested_data = my_ohm.get_core_temps()
            elif request['param'] == "clock_speeds":
                requested_data = my_ohm.get_clock_speeds()
            elif request['param'] == "cpu_core_load":
                requested_data = my_ohm.get_core_loads()

        # print(requested_data)
        # return the data to the client
        response = json.dumps(requested_data)
        self.request.sendall(response.encode('utf-8'))


def main():
    with socketserver.TCPServer((IP, PORT), TCPRequestHandler) as server:
        print("starting server")
        server.serve_forever()


if __name__ == '__main__':
    main()
    print("exiting...")
