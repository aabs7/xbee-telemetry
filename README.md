# Digimesh and UDP
This repository contains code that can be utilized in a digimesh protocol of XBee (mainly used for controlling drones) with XBee sending mavlink message in API mode and relaying data from digimesh.  

### Transparent mode:
When XBee digimesh is used in transparent mode with unicast addressing mode, Mavlink message from Drone and GCS can be relayed through network. For this we have to set DL and DH of GCS XBee to as SL and SH of drone, and also we have to set DL and DH of Drone XBee to SL and SH of GCS. This way we can obtain Unicast mode of addressing in Digimesh network. This way we can control only one drone in a digimesh network. But often we want to control multiple drone at a time from QGC,Mission Planner or any other GCS.

### API mode:
For this we use API mode of communication of XBee. In API mode we can:
- Find out from which XBee(Drone) the data is coming from.
- Set the destination XBee(Drone) to send data from GCS. 

The problem here with using API mode is that API mode wraps the mavlink message in seperate frame and hence we cannot connect GCS directly to USB port.  

The solution is that we can extract mavlink data from API frame and open a UDP socket in which we are transferring mavlink data into. And after that we connect GCS to that UDP port. 

### Development upto now:
Mavlink message is extracted from API frame and is broadcast in UDP port 14555.

### How to run?:
- Run ```drone_to_xbee.py``` on your companion computer in your drone. Make sure you change XBee address, XBee port.
- Run ```xbee_to_udp.py``` on your GCS Computer. Make sure you change XBee address, XBee port.
- Open QGC, Mission Planner and connect to udp port 14555.