#!/usr/bin/env python

import argparse
import socket
import dnet

# Simple test:
# echo "TEST" | socat - UDP4-DATAGRAM:127.0.0.1:4001

UDP_BUFFER_SIZE = 65535

broadcast_mac = dnet.eth_aton('ff:ff:ff:ff:ff:ff')

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

        dst = broadcast_mac
        src = interface.get()  # MAC address
        interface.send(dnet.eth_pack_hdr(dst, src, ether_type) + data)


def all_interfaces():
    def callback(properties, arg):
        arg.append(properties['name'])
    names = []
    dnet.intf().loop(callback, names)
    return names


def interface_from_name(name):
    try:
        return dnet.eth(name)
    except OSError:
        msg = "Can't open interface %s (available interfaces: %s)." % (
            name, ", ".join(all_interfaces()))
        raise argparse.ArgumentTypeError(msg)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='udp2eth')
    parser.add_argument('port',      type=int,                 help='Local UDP port to listen for incoming payload')
    parser.add_argument('interface', type=interface_from_name, help='Interface name, e.g. eth0')
    parser.add_argument('ethertype', type=int,                 help='Ethertype of the upper protocol. Default: %d (GeoNetworking)' % (gn_ether_type), nargs='?', default=gn_ether_type)
    args = parser.parse_args()

    main_loop(args.port, args.interface, args.ethertype)
