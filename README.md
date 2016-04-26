# utoepy - UDP to Ethernet and back, in Python.

Python scripts to forward data from a UDP port to an Ethernet interface and back. Scripts allow setting [Ethertype](http://standards.ieee.org/develop/regauth/ethertype/eth.txt) parameter.

The purpose of these scripts is to be a "Link Layer entity" for a [GeoNetwroking implementation](https://github.com/alexvoronov/geonetworking).

For a Python-free AF_PACKET-based Linux-only alternative, see [udp2eth](https://github.com/jandejongh/udp2eth).

# Dependencies

The scripts require [PcapPy](https://github.com/allfro/pcappy), [dpkt](https://code.google.com/p/dpkt/) and [netifaces](https://pypi.python.org/pypi/netifaces) (requires `python-dev`). Install them with:

```
easy_install pcappy
pip install  dpkt  netifaces
```
