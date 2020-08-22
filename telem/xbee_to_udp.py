import socket, serial, time, datetime, threading, os
from digi.xbee.devices import XBeeDevice

#Buffer values based off QGroundControl git in src/comm/UDPLink.cc 1.298-299
KiB = 1024
BUFFER_LIMIT = 4095

# Localhost IP and arbitarily defined based port
UDP_PORT = 14555
UDP_IP = '127.0.0.1'

KNOWN_64BIT_ADDRS = {
    0x0013A20040D68C2E: ('GCS', None),
    0x0013A20040D68C32: ('Worker #1', 14556),
}

SCRIPT_START = time.time()

# MAVLink constants
HEADER_LEN = 6
LEN_BYTE = 1
CRC_LEN = 2
START_BYTE = 0xfe

class XBeeToUDP(XBeeDevice):
    def __init__(self,serial_port = '/dev/ttyUSB1',baud_rate = 230400, udp=('127.0.0.1',14555),**kwargs):

        #Initialize XBee device connection
        super().__init__(port = serial_port,baud_rate = baud_rate, **kwargs)

        #UDP variables
        self.udp_ip, self.udp_port = udp
        self.udp_connections = {} # Port: (b'\xfe\x42... queue_in, queue_out)
        self.sockets = {}
        self.queued_data = None
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.connect((self.udp_ip, self.udp_port))
        

    def start(self): 
        self.open()
        # handle_data deals with the incoming of XBee data
        self.add_data_received_callback(self.handle_data)
        time.sleep(0.1)
        
    def handle_data(self,xbee_message):
        indata = bytes(xbee_message.data)
        #key = xbee_message.remote_device.get_64bit_addr()
        
        self.queued_data = b'' + indata
        try:
            sent = self.sock.send(self.queued_data)
            self.queued_data = self.queued_data[sent:]
        except Exception as e:
            print("pass")   
        print(self.queued_data)   
        

if __name__ == '__main__':
    xbee = XBeeToUDP('/dev/ttyUSB1',230400)
    xbee.start()
    
    try:
        while True:
            time.sleep(0.5)
    except (KeyboardInterrupt, SystemExit):
        xbee.close()
        print('Terminating all threads and closing all ports.\nExiting...')