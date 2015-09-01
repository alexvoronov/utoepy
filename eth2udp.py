#!/usr/bin/env python

import argparse
import socket
import dpkt
import pcappy
import threading
import netifaces
import binascii


# Simple test:
# socat -u udp-recv:4002 -

# Geonetworking: 0x8947, or 35143 in decimal.
# See http://standards.ieee.org/develop/regauth/ethertype/eth.txt
gn_ether_type = 0x8947


def mac(device_name):
    mac_str = netifaces.ifaddresses(device_name)[netifaces.AF_LINK][0]['addr']
    return binascii.unhexlify(mac_str.replace(':', ''))


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
        return pcappy.open_live(name, snaplen=65535)
    except pcappy.PcapPyException:
        msg = "Can't open interface %s (available interfaces: %s)." % (
            name, ", ".join(all_interfaces()))
        raise argparse.ArgumentTypeError(msg)


def gotpacket_raw(user_arg, hdr, data):
    """loop()'s callback"""
    eth_frame = dpkt.ethernet.Ethernet(data)
    if user_arg['keep_own_frames'] or eth_frame.src != user_arg['my_mac']:
        print repr(eth_frame)
        sock = user_arg['sock']
        sock.sendto(data, user_arg['address'])  # Send full frame.

def gotpacket_cooked(user_arg, hdr, data):
    """loop()'s callback"""
    eth_frame = dpkt.ethernet.Ethernet(data)
    if user_arg['keep_own_frames'] or eth_frame.src != user_arg['my_mac']:
        print repr(eth_frame.data)
        sock = user_arg['sock']
        sock.sendto(eth_frame.data, user_arg['address'])  # Send only data.


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='eth2udp')
    parser.add_argument('--address',   required=True, type=address_from_name,   help='Remote IP:Port to send incoming payload (e.g. 127.0.0.1:4000)')
    parser.add_argument('--mode',      required=True, nargs=1,                  help='Cooked packet mode appends ethernet header consisting of broadcast destination, sender source, and ethertype. Raw packet mode assumes that UDP payload already has an Ethernet header.', choices=['raw', 'cooked'])
    parser.add_argument('--interface', required=True, type=interface_from_name, help='Interface name, e.g. eth0')
    parser.add_argument('--ethertype', type=int,                                help='Ethertype of the upper protocol. Default: 35143 (GeoNetworking)', default=gn_ether_type)
    parser.add_argument('--keep-own-frames', action='store_true',               help='Keep frames originating from the interface. Default: skip them')
    parser.set_defaults(keep_own_frames=False)
    args = parser.parse_args()

    p = args.interface
    p.filter = "ether proto %s" % (hex(args.ethertype))
    sock = socket.socket(socket.AF_INET,     # Internet
                         socket.SOCK_DGRAM)  # UDP

    # Parameters to loop()'s callback. Can be any python object.
    user_arg = {'sock': sock,
                'address': args.address,
                'keep_own_frames': args.keep_own_frames,
                'my_mac': mac(p.device)}

    # Parameters are count, callback_function, user_params_to_callback_function
    # p.loop(-1, gotpacket, user_arg)  # Can't handle KeyboardInterrupt

    # To handle KeyboardInterrupt (from http://stackoverflow.com/questions/14271697/ctrlc-doesnt-interrupt-call-to-shared-library-using-ctypes-in-python)
    t = threading.Thread(target=p.loop, args=[-1, gotpacket_cooked if args.mode[0] == 'cooked' else gotpacket_raw, user_arg])
    t.daemon = True
    t.start()
    while t.is_alive():  # wait for the thread to exit
        t.join(.1)
