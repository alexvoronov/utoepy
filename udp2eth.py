#!/usr/bin/env python

import argparse
import socket
import dpkt
import pcappy
import netifaces
import binascii

# Simple test:
# echo "TEST" | socat - UDP4-DATAGRAM:127.0.0.1:4001

# Simple test for raw:
# echo ffffffffffff542696d082018947414141 | xxd -r -p | socat - UDP4-DATAGRAM:127.0.0.1:4001

UDP_BUFFER_SIZE = 65535

broadcast_mac = '\xff\xff\xff\xff\xff\xff'

# Geonetworking: 0x8947, or 35143 in decimal.
# See http://standards.ieee.org/develop/regauth/ethertype/eth.txt
gn_ether_type = 0x8947


def mac(device_name):
    mac_str = netifaces.ifaddresses(device_name)[netifaces.AF_LINK][0]['addr']
    return binascii.unhexlify(mac_str.replace(':', ''))


def main_loop(port, interface, ether_type, mode):
    ip = ''
    sock = socket.socket(socket.AF_INET,     # Internet
                         socket.SOCK_DGRAM)  # UDP
    sock.bind((ip, port))

    device_mac = mac(interface.device)

    if mode == 'cooked':
        while True:
            data = sock.recv(UDP_BUFFER_SIZE)
            print repr(data)
            frame = dpkt.ethernet.Ethernet(dst=broadcast_mac, src=device_mac,
                                           type=ether_type, data=data)
            interface.inject(frame.pack())
    elif mode == 'raw':
        while True:
            data = sock.recv(UDP_BUFFER_SIZE)
            frame = dpkt.ethernet.Ethernet(data)
            print repr(frame)
            interface.inject(frame.pack())
    else:
        raise Exception('Unknown mode ' + str(mode))


def all_interfaces():
    return [dev.name for dev in pcappy.findalldevs()]


def interface_from_name(name):
    try:
        return pcappy.open_live(name, snaplen=65535)
    except pcappy.PcapPyException:
        msg = "Can't open interface %s (available interfaces: %s)." % (
            name, ", ".join(all_interfaces()))
        raise argparse.ArgumentTypeError(msg)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='udp2eth')
    parser.add_argument('--mode',      required=True, nargs=1,   help='Cooked packet mode appends ethernet header consisting of broadcast destination, sender source, and ethertype. Raw packet mode assumes that UDP payload already has an Ethernet header.', choices=['raw', 'cooked'])
    parser.add_argument('--port',      type=int,                 help='Local UDP port to listen for incoming payload')
    parser.add_argument('--interface', type=interface_from_name, help='Interface name, e.g. eth0')
    parser.add_argument('--ethertype', type=int,                 help='Ethertype of the upper protocol (35143 for GeoNetworking)', default=gn_ether_type)
    args = parser.parse_args()


    main_loop(args.port, args.interface, args.ethertype, args.mode[0])
