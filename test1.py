__author__ = 'richard'

import re

x = '  192.168.1.72          64-27-37-fe-dd-c1     dynamic   '

#x = ' 192.168.1.72'#          64-27-37-fe-dd-c1     dynamic   \n'#
#x = ' 64-27-37-fe-dd-c1 '
ip_mac_re = re.compile("(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}).*(?P<mac>[0-9a-f]{2}-[0-9a-f]{2}-[0-9a-f]{2}-[0-9a-f]{2}-[0-9a-f]{2}-[0-9a-f]{2})")
ip_re = re.compile("\s(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}).*")
mac_re = re.compile("([0-9a-f]{2}-[0-9a-f]{2}-[0-9a-f]{2}-[0-9a-f]{2}-[0-9a-f]{2}-[0-9a-f]{2})")


#print ip_re.match(x).group("ip")
print ip_mac_re.findall(x)