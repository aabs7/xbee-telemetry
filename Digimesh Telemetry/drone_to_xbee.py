from digi.xbee.devices import XBeeDevice,RemoteXBeeDevice,XBee64BitAddress
import serial, time

PORT = '/dev/ttyUSB0'
BAUD_RATE = 230400
GCS_ID = "0013A200419B5208"
drone = serial.Serial('/dev/ttyACM0',115200)

def main():
    my_device = XBeeDevice(PORT, BAUD_RATE)
    my_device.open()
    GCS = RemoteXBeeDevice(my_device, XBee64BitAddress.from_hex_string(GCS_ID))
    my_device.add_data_received_callback(receive_data_callback)
    
    while True:
        # Read from drone, Write to XBee
        if 100 <= drone.in_waiting < 4905:
            data = drone.read(drone.in_waiting)
            while data:
                my_device.send_data(GCS,data[:70])
                data = data[70:]
        elif drone.in_waiting == 4095:
            drone.reset_input_buffer()
        else:
            pass

        #time.sleep(0.001)

def receive_data_callback(xbee_message):
    rx_data = bytes(xbee_message.data)
    drone.write(rx_data)

if __name__ == '__main__':
	main()