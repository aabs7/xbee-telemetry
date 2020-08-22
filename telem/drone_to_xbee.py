from digi.xbee.devices import XBeeDevice,RemoteXBeeDevice,XBee64BitAddress
import serial, time

PORT = '/dev/ttyUSB0'
BAUD_RATE = 230400
GCS_ID = "0013A200419B5208"

def main():
    drone = serial.Serial('/dev/ttyACM0',115200)
    my_device = XBeeDevice(PORT, BAUD_RATE)
    my_device.open()
    GCS = RemoteXBeeDevice(my_device, XBee64BitAddress.from_hex_string(GCS_ID))
    
    while True:
        # Read from drone, Write to XBee
        if 100 <= drone.in_waiting < 4905:
            data = drone.read(drone.in_waiting)
            while data:
                print('[Drone -> XBee] {}'.format(data[:70]))
                pkt_sent = my_device.send_data(GCS,data[:70])
                data = data[70:]
        elif drone.in_waiting == 4095:
            drone.reset_input_buffer()
        else:
            pass

        message = my_device.read_data_from(GCS)
        if message:
            data = bytes(message.data)
            print('[XBee -> Drone] {}'.format(data))
            drone.write(data)

        time.sleep(0.001)



if __name__ == '__main__':
	main()