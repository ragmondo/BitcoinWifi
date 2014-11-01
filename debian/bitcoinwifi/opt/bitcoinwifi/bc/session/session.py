__author__ = 'CMS'

import logging
import os
import time
from threading import Timer

log = logging.getLogger(__file__)

class TimedSession(object):

    def __init__(self, mac, length, price):
        self.mac = mac
        self.now = int(time.time())
        self.length = length
        self.end = self.now + length
        self.price = price
        self.create_session()

    def create_session(self):
        log.info("Enabling for MAC %s" % (self.mac))
        sys_cmd = "iptables -I internet 1 -t mangle -m mac --mac-source %s -j RETURN" % self.mac
        log.info(sys_cmd)
        log.info(os.popen(sys_cmd).read())
        callback = Timer(self.length, self.destroy_session)
        callback.start()

    def destroy_session(self):
        log.info("Disabling MAC %s" % (self.mac))
        # Check this!
        sys_cmd = "iptables -D -I internet 1 -t mangle -m mac --mac-source %s -j RETURN" % self.mac
        log.info(sys_cmd)
        log.info(os.popen(sys_cmd).read())

    def remaining(self):
        return max(0, int(time.time())-self.end)

    def refund(self):
        # How much is eligable for refund
        return self.remaining / self.price
