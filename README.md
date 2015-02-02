# utoepy - UDP to Ethernet and back, in Python.

Python scripts to forward data from a UDP port to an Ethernet interface and back. Scripts allow setting [Ethertype](http://standards.ieee.org/develop/regauth/ethertype/eth.txt) parameter.

The purpose of these scripts is to be a "Link Layer entity" for a [GeoNetwroking implementation](https://github.com/alexvoronov/geonetworking).

# Dependencies

The scripts require [PcapPy](https://github.com/allfro/pcappy), [dpkt](https://code.google.com/p/dpkt/) and [netifaces](https://pypi.python.org/pypi/netifaces). Install them with:

```
pip install  --allow-external pcappy  --allow-unverified pcappy   pcappy  dpkt  netifaces
```