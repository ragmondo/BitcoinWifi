__author__ = 'richard'

from flask import Flask
app = Flask(__name__)
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from flask import Response

from sqlalchemy import create_engine
from sqlite3 import dbapi2 as sqlite
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from collections import defaultdict

Base = declarative_base()

import re
import datetime
import addrgen
import qrcode
import StringIO
import os
import logging
import httplib
import socket
import bcnet

payment_options = [ ("a",0.0001,"1 hour",datetime.timedelta(1.0/24.0)),
                    ("b",0.01,"6 hours",datetime.timedelta(0.25)),
                   ("c",0.10, "24 hours", datetime.timedelta(1))]

bitcoin_format = "bitcoin:%(address)s?amount=%(amount)s&label=BitcoinWifiHotspot"

class Key(Base):
    __tablename__  = "key"
    id = Column(Integer,primary_key=True)
    priv_key = Column(String)
    pub_key = Column(String)
    ip_address = Column(String)
    mac_address = Column(String)

@app.route("/")
def home():
    if my_wlan0_ip() not in request.url_root and my_eth0_ip() not in request.url_root:
        return redirect("http://" + my_wlan0_ip())
        
    ip_address = request.remote_addr
    arp_address = read_arp_table()[ip_address]
    q = session.query(Key).filter(Key.ip_address == ip_address).filter(Key.mac_address == arp_address).first()
    if not q:
        k = addrgen.gen_eckey()
        print k
        adds = addrgen.get_addr(k)
        key = Key(pub_key = adds[0], priv_key=adds[1], ip_address = ip_address, mac_address = arp_address)
        bitcoin_address = adds[0]
        print key
        session.add(key)
        session.commit()
        print key
    if q:
        logging.debug("Found an entry", q)
        bitcoin_address = q.pub_key

    ## lookup ip / arp

    return render_template('home.html',ip=ip_address,arp=arp_address,bitcoinaddress=bitcoin_address, paymentoptions=payment_options)

@app.route("/qrcode/<choice>")

def qr_code(choice):
    for p in payment_options:
        if p[0] == choice:
            amount = p[1]

    ip_address = request.remote_addr
    arp_address = read_arp_table()[ip_address]
    q = session.query(Key).filter(Key.ip_address == ip_address).filter(Key.mac_address == arp_address).first()
    bitcoin_address = q.pub_key
    t = ""
    output = StringIO.StringIO()
    qr = qrcode.make(bitcoin_format % ({"address":bitcoin_address,"amount":amount }))
    qr._img.save(output,"GIF")
    return Response(output.getvalue(), mimetype='image/gif')


def my_gateway():
    r = os.popen("route print").read()
    
def _my_ip(nic):
    try:
        nics = bcnet.getnics()
        return nics[nic][1]
    except KeyError:
        return '0.0.0.0'

def my_eth0_ip():
    return _my_ip('eth0')

def my_wlan0_ip():
    return _my_ip('wlan0')


def has_balance(pub_key):
    h1 = httplib.HTTPConnection("blockchain.info")
    h1.request("GET","/q/getreceivedbyaddress/%s" % (pub_key))
    r = h1.getresponse()
    ret = int(r.read())

    # pretend it's working 

    ret = 1

    logging.debug("Amount found is %s" % ret)
    return ret

def enable_access():
    ip = request.remote_addr
    print "ip is " ,ip
    mac = read_arp_table()[ip]
    print "arp table is ", read_arp_table()
    q = session.query(Key).filter(Key.ip_address == ip).filter(Key.mac_address == mac).first()
    logging.info("Enabling for MAC %s" % (mac))
    print "Mac is ",mac
    sys_cmd = "iptables -I internet 1 -t mangle -m mac --mac-source %s -j RETURN" % mac
    print "****", sys_cmd, "****"
    logging.info(sys_cmd)
    logging.info(os.popen(sys_cmd).read())


def flush_funds():
    return

@app.route("/checkaccess")
def check_access():
    ip = request.remote_addr
    mac = read_arp_table()[ip]
    q = session.query(Key).filter(Key.ip_address == ip).filter(Key.mac_address == mac).first()
    if has_balance(q.pub_key):
        enable_access()
        flush_funds()
        return render_template("access_enabled.html")
    else:
        return render_template("no_access_yet.html")


@app.route('/<path:path>')
def catch_all(path):
    return redirect("http://" + my_wlan0_ip() )
    #return redirect(url_for('home', region=None, ip=None))



def read_arp_table():
    # The linux ARP command parses the special file /proc/net/arp.
    # Ignore what man arp says, ioctls do not work!
    ip_list = defaultdict(str)
    with open('/proc/net/arp') as f:
        f.readline() # Skip header
        for l in f.readlines():
            d = l.split()
            ip_list[d[0]] = d[3]
    # int_f = re.compile("Interface: ")
    # header = re.compile("Internet Address")
    # ip_mac_re = re.compile("(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}).*(?P<mac>[0-9a-f]{2}[:-][0-9a-f]{2}[:-][0-9a-f]{2}[:-][0-9a-f]{2}[:-][0-9a-f]{2}[:-][0-9a-f]{2})")
    # l = os.popen("arp -a")
    # for r in l:
    #     g = ip_mac_re.findall(r)
    #     if g:
    #         for g2 in g:
    #             ip_list[g2[0]] = g2[1]
    #
    return ip_list

if __name__ == "__main__":
    global session
    Session = sessionmaker()
    engine = create_engine('sqlite+pysqlite:///file.db', module=sqlite)
    Session.configure(bind=engine)
    Base.metadata.create_all(engine)
    session = Session()
    app.run(host='0.0.0.0',port=80,debug=True)
