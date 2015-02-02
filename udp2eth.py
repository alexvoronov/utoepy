#!/usr/bin/env python

import argparse
import socket
import dpkt
import pcappy
import netifaces
import binascii

# Simple test:
# echo "TEST" | socat - UDP4-DATAGRAM:127.0.0.1:4001

UDP_BUFFER_SIZE = 65535

broadcast_mac = '\xff\xff\xff\xff\xff\xff'

# Geonetworking: 0x8947, or 35143 in decimal.
# See http://standards.ieee.org/develop/regauth/ethertype/eth.txt
gn_ether_type = 0x8947


def main_loop(port, interface, ether_type):
    ip = ''
    sock = socket.socket(socket.AF_INET,     # Internet
                         socket.SOCK_DGRAM)  # UDP
    sock.bind((ip, port))

    while True:
        data = sock.recv(UDP_BUFFER_SIZE)
        print data

        mac_str = netifaces.ifaddresses(interface.device)[netifaces.AF_LINK][0]['addr']
        src_mac = binascii.unhexlify(mac_str.replace(':', ''))

        frame = dpkt.ethernet.Ethernet(dst=broadcast_mac, src=src_mac,
                                       type=ether_type, data=data)
        interface.inject(frame.pack())


def all_interfaces():
    return [dev.name for dev in pcappy.findalldevs()]


def interface_from_name(name):
    try:
        return pcappy.open_live(name)
    except pcappy.PcapPyException:
        msg = "Can't open interface %s (available interfaces: %s)." % (
            name, ", ".join(all_interfaces()))
        raise argparse.ArgumentTypeError(msg)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='udp2eth')
    parser.add_argument('port',      type=int,                 help='Local UDP port to listen for incoming payload')
    parser.add_argument('interface', type=interface_from_name, help='Interface name, e.g. eth0')
    parser.add_argument('ethertype', type=int,                 help='Ethertype of the upper protocol (35143 for GeoNetworking)', nargs='?', default=gn_ether_type)
    args = parser.parse_args()

    main_loop(args.port, args.interface, args.ethertype)
