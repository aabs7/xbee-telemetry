from digi.xbee.devices import XBeeDevice
from digi.xbee.devices import RemoteXBeeDevice
from digi.xbee.models.address import XBee64BitAddress
from apscheduler.schedulers.background import BackgroundScheduler
import time
from pymavlink import mavutil
import json

PORT = '/dev/ttyUSB0'
BAUD_RATE = 230400
DRONE_ID = "0013A200419B5208"

master = mavutil.mavlink_connection('/dev/ttyACM0',baud=230400)
my_device = XBeeDevice(PORT, BAUD_RATE)
DATA_TO_SEND = "Hello world"


my_device.open()
remote_device = RemoteXBeeDevice(my_device, XBee64BitAddress.from_hex_string(DRONE_ID))
count = 0
	
def send_data(data):
    _data = str(data)
    n = 70
    for i in range(0,len(_data),n):
        DATA_TO_SEND = _data[i:i+n]
        my_device.send_data(remote_device,DATA_TO_SEND)

while True:
    msg = master.recv_match()
    
    if not msg:
        continue
    else:
        print(msg)
        send_data(msg)
        if(msg.get_type() == 'ATTITUDE'):
            print("\r\n")
