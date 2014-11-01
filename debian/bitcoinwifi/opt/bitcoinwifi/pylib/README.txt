Simple C extension to help with finding NICs and MAC addresses

Python 2.7.5+ (default, Feb 27 2014, 19:39:55) 
[GCC 4.8.1] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import bcnet
>>> bcnet.getnics()
{'lo': ['00:00:00:00:00:00', '127.0.0.1'], 'wlan0': ['00:1b:b1:a2:48:8e', '192.168.1.66']}
