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

payment_options = [ ("a",0.001,"1 hour",datetime.timedelta(1.0/24.0)),
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

    return render_template('t1.html',ip=ip_address,arp=arp_address,bitcoinaddress=bitcoin_address, paymentoptions=payment_options)

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


def has_balance(pub_key):
    h1 = httplib.HTTPConnection("blockchain.info")
    h1.request("GET","/q/getreceivedbyaddress/%s" % (pub_key))
    r = h1.getresponse()
    ret = int(r.read())
    logging.debug("Amount found is %s" % ret)
    return ret

def enable_access():
    return

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
    return redirect(url_for('home', region=None, ip=None))

def read_arp_table():
    ip_list = defaultdict(str)
    int_f = re.compile("Interface: ")
    header = re.compile("Internet Address")
    ip_mac_re = re.compile("(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}).*(?P<mac>[0-9a-f]{2}-[0-9a-f]{2}-[0-9a-f]{2}-[0-9a-f]{2}-[0-9a-f]{2}-[0-9a-f]{2})")
    l = os.popen("arp -a")
    for r in l:
        g = ip_mac_re.findall(r)
        if g:
            for g2 in g:
                ip_list[g2[0]] = g2[1]

    return ip_list

if __name__ == "__main__":
    global session
    Session = sessionmaker()
    engine = create_engine('sqlite+pysqlite:///file.db', module=sqlite)
    Session.configure(bind=engine)
    Base.metadata.create_all(engine)
    session = Session()
    app.run(host='0.0.0.0',debug=True)
