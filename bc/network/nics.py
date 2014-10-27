__author__ = 'mets'
import os
from collections import defaultdict
try:
    from _bcnet import getnics
except ImportError:
    from dummy import getnics

def get_ip(nic):
    try:
        nics = getnics()
        return nics[nic][1]
    except KeyError:
        return '0.0.0.0'

def my_eth0_ip():
    return get_ip('eth0')

def my_wlan0_ip():
    return get_ip('wlan0')

def my_gateway():
    r = os.popen("route print").read()

def read_arp_table():
    # The linux ARP command parses the special file /proc/net/arp.
    # Ignore what man arp says, ioctls do not work!
    ip_list = defaultdict(str)
    with open('/proc/net/arp') as f:
        f.readline()  # Skip header
        for l in f.readlines():
            d = l.split()
            ip_list[d[0]] = d[3]
    return ip_list
