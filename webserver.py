__author__ = 'richard'

from flask import Flask
from flask import request, redirect, render_template
from flask import Response
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///file.db'
db = SQLAlchemy(app)

#from sqlalchemy.ext.declarative import declarative_base
from bc.session.session import TimedSession
import bc.database.access
from bc.bitcoin.transactions import flush_funds, get_balance, get_last_transaction
from bc.network.nics import read_arp_table, my_eth0_ip, my_wlan0_ip

import datetime
import addrgen
import qrcode
import StringIO
import logging

payment_options = [ ("a",0.0001,"1 hour",datetime.timedelta(1.0/24.0)),
                    ("b",0.01,"6 hours",datetime.timedelta(0.25)),
                   ("c",0.10, "24 hours", datetime.timedelta(1))]

bitcoin_format = "bitcoin:%(address)s?amount=%(amount)s&label=BitcoinWifiHotspot"

log = logging.getLogger(__file__)
sessiondb = None
sessions = []

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
    else:
        logging.debug("Found an entry", q)
        bitcoin_address = q.pub_key

    return render_template('index.html', ip=ip_address, arp=arp_address, bitcoinaddress=bitcoin_address, paymentoptions=payment_options)

@app.route("/qrcode/<choice>")
def qr_code(choice):
    amount = None
    for p in payment_options:
        if p[0] == choice:
            amount = p[1]
    if not amount:
        amount = payment_options['a'][1]
    ip_address = request.remote_addr
    arp_address = read_arp_table()[ip_address]
    q = sessiondb.get_key(ip_address, arp_address)
    bitcoin_address = q.pub_key
    output = StringIO.StringIO()
    qr = qrcode.make(bitcoin_format % ({"address":bitcoin_address,"amount":amount }))
    qr._img.save(output, "GIF")
    return Response(output.getvalue(), mimetype='image/gif')

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

if __name__ == "__main__":
    # TODO restore sessions
    #sessions = [ x for x in sessiondb.restore_sessions() ]
    sessiondb = bc.database.access.SessionDB()
    app.run(host='0.0.0.0', port=8080, debug=True)
