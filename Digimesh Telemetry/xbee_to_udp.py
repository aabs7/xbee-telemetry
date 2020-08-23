import socket, serial, time, datetime, threading, os
from digi.xbee.devices import XBeeDevice,RemoteXBeeDevice,XBee64BitAddress
import logging

#Buffer values based off QGroundControl git in src/comm/UDPLink.cc 1.298-299
KiB = 1024

# Localhost IP and arbitarily defined based port
UDP_PORT = 14555
UDP_IP = '127.0.0.1'

#Drone IDS
BAUD_RATE = 230400
PORT = '/dev/ttyUSB1'

#define for logging
#Create and configure logger 
logging.basicConfig(filename="GCS.log", 
                    format='%(asctime)s : %(levelname)s :: %(message)s', 
                    filemode='w') 

#Creating an object 
logger=logging.getLogger() 
  
#Setting the threshold of logger to WARNING. i.e only warning, error, and critical message is shown in log. 
'''
 Thresholds:
 DEBUG
 INFO
 WARNING
 ERROR
 CRITICAL 
'''
logger.setLevel(logging.INFO)

SCRIPT_START = time.time()


class HandleUDP():
    def __init__(self, address, gcs, udp_ip, udp_port):
        # initialize
        print("Initializing new UDP port at 127.0.0.1:",udp_port," for drone ID:",address)
        self.gcs = gcs
        self.drone_id = address
        # To check if error occured during initialization
        self.__initialise_error = False

        #create object for remote xbee device
        try:
            self.drone = RemoteXBeeDevice(self.gcs,XBee64BitAddress.from_hex_string(self.drone_id))
        except:
            error = {'context':'UDP_INIT','msg':'Drone could not initialize'}
            logger.error(error)
            self.__initialise_error = True
            
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.connect((udp_ip,udp_port))
        except:
            error = {'context':'UDP_INIT','msg':'Socket initializing error'}
            logger.error(error)
            self.__initialise_error = True

        udp_rx = threading.Thread(target= self.udp_rx_thread, daemon = True)
        udp_rx.start()
    
    def udp_rx_thread(self):
        while True:
            try:
                outdata,_ = self.socket.recvfrom(KiB)
                self.gcs.send_data(self.drone,outdata)
            except:
                pass
    
    @property
    def initialise_error(self):
        return self.__initialise_error

    def send_to_udp(self,indata):
        try:
            sent = self.socket.send(indata)
        except:
            pass



class GCS():
    def __init__(self,serial_port = PORT,baud_rate = BAUD_RATE, udp=('127.0.0.1',14555), **kwargs):

        #Initialize XBee device connection which is connected in GCS
        print("GCS Start")
        self.gcs = XBeeDevice(port = serial_port,baud_rate = baud_rate, **kwargs)

        #UDP variables
        self.udp_ip, self.udp_port = udp
        self.udp_connections = {}
    
    def __del__(self):
        self.gcs.close()

    def start(self): 
        #open GCS XBee connection
        self.gcs.open()
        # handle_data deals with the incoming of XBee data
        self.gcs.add_data_received_callback(self.handle_data)
        time.sleep(0.1)
        
    def handle_data(self,xbee_message):
        indata = bytes(xbee_message.data)
        address = xbee_message.remote_device.get_64bit_addr()

        if address not in self.udp_connections:
            self.udp_connections[address] = HandleUDP(str(address),self.gcs,self.udp_ip,self.udp_port)
            if self.udp_connections[address].initialise_error is False:
                info = {'context':'UDP_CONN','msg':'Initialized UDP port at 127.0.0.1:'+str(self.udp_port)+' for drone ID:'+str(address)}
                logger.info(info)
                self.udp_port += 2
            else:
                # delete object and try again
                del self.udp_connections[address]
                info = {'context':'UDP_CONN','msg':'Failed to initialize UDP port for drone ID:'+str(address)+',Restarting UDP Connection'}
                logger.info(info)

        self.udp_connections[address].send_to_udp(indata)


if __name__ == '__main__':
    gcs = GCS(PORT,BAUD_RATE,udp=(UDP_IP,UDP_PORT))
    gcs.start()
    
    try:
        while True:
            time.sleep(0.5)
    except (KeyboardInterrupt, SystemExit):
        print('Terminating all threads and closing all ports.\nExiting...')