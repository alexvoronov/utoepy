#!/usr/bin/env python

import argparse
import socket
import dpkt
import pcappy
import threading


# Geonetworking: 0x8947, or 35143 in decimal.
# See http://standards.ieee.org/develop/regauth/ethertype/eth.txt
gn_ether_type = 0x8947


def address_from_name(name):
    try:
        ip, port_str = name.split(':')
        port = int(port_str)
        return (ip, port)
    except:
        msg = "Expected hostname:port, got %s" % (name)
        raise argparse.ArgumentTypeError(msg)


def all_interfaces():
    return [dev.name for dev in pcappy.findalldevs()]


def interface_from_name(name):
    try:
        return pcappy.open_live(name)
    except pcappy.PcapPyException:
        msg = "Can't open interface %s (available interfaces: %s)." % (
            name, ", ".join(all_interfaces()))
        raise argparse.ArgumentTypeError(msg)


def gotpacket(user_arg, hdr, data):
    """loop()'s callback"""
    eth_frame = dpkt.ethernet.Ethernet(data)
    print eth_frame.data
    sock = user_arg['sock']
    sock.sendto(eth_frame.data, user_arg['address'])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='eth2udp')
    parser.add_argument('address',   type=address_from_name,   help='Remote IP:Port to send incoming payload (e.g. 127.0.0.1:4000)')
    parser.add_argument('interface', type=interface_from_name, help='Interface name, e.g. eth0')
    parser.add_argument('ethertype', type=int,                 help='Ethertype of the upper protocol. Default: %d (GeoNetworking)' % (gn_ether_type), nargs='?', default=gn_ether_type)
    args = parser.parse_args()

    p = args.interface
    p.filter = "ether proto %s" % (hex(args.ethertype))
    sock = socket.socket(socket.AF_INET,     # Internet
                         socket.SOCK_DGRAM)  # UDP

    # Parameters to loop()'s callback. Can be any python object.
    user_arg = {'sock': sock, 'address': args.address}

    # Parameters are count, callback_function, user_params_to_callback_function
    # p.loop(-1, gotpacket, user_arg)  # Can't handle KeyboardInterrupt

    # To handle KeyboardInterrupt (from http://stackoverflow.com/questions/14271697/ctrlc-doesnt-interrupt-call-to-shared-library-using-ctypes-in-python)
    t = threading.Thread(target=p.loop, args=[-1, gotpacket, user_arg])
    t.daemon = True
    t.start()
    while t.is_alive():  # wait for the thread to exit
        t.join(.1)
