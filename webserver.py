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
from bc.session.session import TimedSession
from bc.database.access import SessionDB
from bc.bitcoin.transactions import flush_funds, get_balance, get_last_transaction

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

# List of sessions
sessions = []
sessiondb = SessionDB()
log = logging.getLogger(__file__)

@app.route("/")
def home():
    if my_wlan0_ip() not in request.url_root and my_eth0_ip() not in request.url_root:
        return redirect("http://" + my_wlan0_ip())
        
    ip_address = request.remote_addr
    arp_address = read_arp_table()[ip_address]
    q = sessiondb.get_key(ip_address, arp_address)
    if not q:
        k = addrgen.gen_eckey()
        log.debug(k)
        adds = addrgen.get_addr(k)
        sessiondb.create_key(pub_key=adds[0], priv_key=adds[1], ip_address=ip_address, mac_address=arp_address)
        bitcoin_address = adds[0]
    if q:
        logging.debug("Found an entry", q)
        bitcoin_address = q.pub_key

    return render_template('home.html', ip=ip_address, arp=arp_address, bitcoinaddress=bitcoin_address, paymentoptions=payment_options)

@app.route("/qrcode/<choice>")
def qr_code(choice):
    for p in payment_options:
        if p[0] == choice:
            amount = p[1]

    ip_address = request.remote_addr
    arp_address = read_arp_table()[ip_address]
    q = sessiondb.get_key(ip_address, arp_address)
    bitcoin_address = q.pub_key
    output = StringIO.StringIO()
    qr = qrcode.make(bitcoin_format % ({"address":bitcoin_address,"amount":amount }))
    qr._img.save(output, "GIF")
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

def enable_access(length, tx):
    ip = request.remote_addr
    mac = read_arp_table()[ip]
    sessions.append(TimedSession(mac, length))
    sessiondb.add_session(mac, length, tx)

def get_payment_length(amount):
    # TODO turn payment into length
    length = 0
    for p in payment_options:
        length = p[1] * amount % p[3]
    return length

@app.route("/checkaccess")
def check_access():
    ip = request.remote_addr
    mac = read_arp_table()[ip]
    q = sessiondb.get_key(ip, mac)
    if get_balance(q.pub_key):
        tx = get_last_transaction(q.pub_key)
        length = get_payment_length(tx.amount)
        enable_access(length, tx.id)
        flush_funds(q.pub_key)
        return render_template("access_enabled.html")
    else:
        return render_template("no_access_yet.html")

@app.route('/<path:path>')
def catch_all(path):
    return redirect("http://" + my_wlan0_ip() )

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

if __name__ == "__main__":
    # TODO restore sessions
    sessions = [ x for x in sessiondb.restore_sessions() ]
    app.run(host='0.0.0.0', port=80, debug=True)
