from digi.xbee.devices import XBeeDevice,RemoteXBeeDevice,XBee64BitAddress
import serial, time

BUFFER_LIMIT = 4095
MAX_XBEE_BYTE = 70

PORT = '/dev/ttyUSB0'
BAUD_RATE = 230400
GCS_ID = "0013A200419B5208"
drone = serial.Serial('/dev/ttyACM0',115200)


def initialize_GCS(my_device):
    print("\n...Discovering GCS...\n")
    network = my_device.get_network()

    network.start_discovery_process()

    while network.is_discovery_running():
        time.sleep(0.1)

    gcs_address = XBee64BitAddress.from_hex_string(GCS_ID)
    GCS = network.get_device_by_64(gcs_address)
    if GCS is None:
        print("GCS not found, Restarting search of GCS")
        initialize_GCS(my_device)
    else:
        print("...Discovering Complete...")
        print("GCS found with name:",GCS.get_node_id()," and address:",gcs_address)
        return GCS

def main():
    my_device = XBeeDevice(PORT, BAUD_RATE)
    my_device.open()

    
    #GCS = initialize_GCS(my_device)
    GCS = RemoteXBeeDevice(my_device, XBee64BitAddress.from_hex_string(GCS_ID))
    my_device.add_data_received_callback(receive_data_callback)
    print("Sending MAVLink messages")   
    
    while True:
        # Read from drone, Write to XBee
        try:
            if 100 <= drone.in_waiting < BUFFER_LIMIT:
                data = drone.read(drone.in_waiting)
                while data:
                    my_device.send_data(GCS,data[:MAX_XBEE_BYTE])
                    data = data[MAX_XBEE_BYTE:]
            elif drone.in_waiting == BUFFER_LIMIT:
                drone.reset_input_buffer()
            else:
                pass
        except Exception as e:
            print("Conn lost")
            GCS = RemoteXBeeDevice(my_device, XBee64BitAddress.from_hex_string(GCS_ID))
        #time.sleep(0.001)

def receive_data_callback(xbee_message):
    rx_data = bytes(xbee_message.data)
    drone.write(rx_data)

if __name__ == '__main__':
	main()