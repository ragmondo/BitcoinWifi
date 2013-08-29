__author__ = 'richard'

from flask import Flask
app = Flask(__name__)
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from flask import Response

from collections import defaultdict


import re
import datetime
import addrgen
import qrcode
import StringIO
import os
import logging
import httplib
import socket

payment_options = [ ("a",0.0001,"1 hour",datetime.timedelta(1.0/24.0)),
                    ("b",0.01,"6 hours",datetime.timedelta(0.25)),
                   ("c",0.10, "24 hours", datetime.timedelta(1))]

bitcoin_format = "bitcoin:%(address)s?amount=%(amount)s&label=BitcoinWifiHotspot"

@app.route("/")
def home():
    ip_address = request.remote_addr
    arp_address = read_arp_table()[ip_address]
    bitcoin_address = "1JkmD3vBBKpL9SuugetrNvK6FqjM4iMiNT"
    return render_template('home.html',ip=ip_address,arp=arp_address,bitcoinaddress=bitcoin_address, paymentoptions=payment_options)

@app.route("/qrcode/<choice>")
def qr_code(choice):
    for p in payment_options:
        if p[0] == choice:
            amount = p[1]

    bitcoin_address = "1JkmD3vBBKpL9SuugetrNvK6FqjM4iMiNT"
    output = StringIO.StringIO()
    qr = qrcode.make(bitcoin_format % ({"address":bitcoin_address,"amount":amount }))
    qr._img.save(output,"GIF")
    return Response(output.getvalue(), mimetype='image/gif')


def my_gateway():
    r = os.popen("route print").read()

def my_eth0_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("gmail.com",80))
    ret = s.getsockname()[0]
    s.close()
    return ret

def my_wlan0_ip():
    return "192.168.42.1"

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
    if True:
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
    ip_list = defaultdict(str)
    int_f = re.compile("Interface: ")
    header = re.compile("Internet Address")
    ip_mac_re = re.compile("(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}).*(?P<mac>[0-9a-f]{2}[:-][0-9a-f]{2}[:-][0-9a-f]{2}[:-][0-9a-f]{2}[:-][0-9a-f]{2}[:-][0-9a-f]{2})")
    l = os.popen("arp -a")
    for r in l:
        g = ip_mac_re.findall(r)
        if g:
            for g2 in g:
                ip_list[g2[0]] = g2[1]

    return ip_list

if __name__ == "__main__":
    global session
    app.run(host='0.0.0.0',port=80,debug=True)
