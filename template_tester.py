__author__ = 'richard'

from flask import Flask
app = Flask(__name__)
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, send_file, flash
from flask import Response

from collections import defaultdict

import json
import time

import re
import datetime
#import addrgen
import qrcode
import StringIO
import os
import logging
import httplib
import socket

payment_options = {
    'a':{'price': 0.001,'time': '1 hour' },
    'b':{'price': 0.01, 'time': '1 day'  },
    'c':{'price': 0.2,  'time': '1 month'}
}

bitcoin_format = 'bitcoin:%(address)s?amount=%(amount)s&label=BitcoinWifiHotspot'

@app.route('/')
def home():
    return send_file('templates/index.html')

@app.route('/admin')
def admin():
    return send_file('templates/admin.html')

@app.route('/status')
def status():
    r = {
        'info':{
            0:{
            'type':'success',
            'text':'Status loaded'
            }
        },
        'data':{
            'helptext':True,
            'sys': {
                'timezone':'UTC',
                'name':'Hoebaaa Wifi',
                'signal':True,
                'paywall':True,
                'allownew':True
                },
            'ports': {'free':'4028','paid':'21,22,80,8080'},
            'prices': payment_options,
            'btcaddr': '1JkmD3vBBKpL9SuugetrNvK6FqjM4iMiNT',
            'arp': read_arp_table(),
            'ip': request.remote_addr,
            'time': time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime()),
            'sessions': {
                0:{
                    'ip':'192.168.0.119',
                    'mac':'qs-df-fd-fs',
                    'btc':0,
                    'gen': 5,
                    'addr': '1HnRrbVZdLbSKDYyhqdiWmkywkTWPL2nKA'
                },
                1:{
                    'ip':'192.168.0.118',
                    'mac':'qs-df-fd-fs',
                    'btc':.001,
                    'gen': 43,
                    'status':20,
                    'addr': '18apStsmkM7PYfmdVi4g2QLvhvynKGYq2w'
                },
                2:{
                    'ip':'192.168.0.117',
                    'mac':'qs-df-fd-fs',
                    'btc':.005,
                    'gen': 245,
                    'status':90,
                    'addr': '1Fi57hAqyYYwaQVdA7a9qSKfiukBbt31G3'
                },
                3:{
                    'ip':'192.168.0.112',
                    'mac':'qs-df-fd-fs',
                    'btc':0.01,
                    'gen': 6398,
                    'status':100,
                    'addr': '1JkmD3vBBKpL9SuugetrNvK6FqjM4iMiNT'
                },
                4:{
                    'ip':'192.168.0.107',
                    'mac':'qs-df-fd-fs',
                    'btc':0,
                    'gen': 7334,
                    'addr': '13fa3X8qm9f6dYr3iK74aVzsHCLsTzBtmq'
                },
                5:{
                    'ip':'192.168.0.103',
                    'mac':'qs-df-fd-fs',
                    'btc':0,
                    'allow':True,
                    'gen': 78685,
                    'addr': '12qC685rf8dqNLgm6hVabtVvz3vSSF2uby'
                }
            }
        }
    }
    return Response(json.dumps(r), mimetype='application/json')

@app.route('/qrcode/<choice>')
def qr_code(choice):
    for p in payment_options:
        if p[0] == choice:
            amount = p[1]

    bitcoin_address = '1JkmD3vBBKpL9SuugetrNvK6FqjM4iMiNT'
    output = StringIO.StringIO()
    qr = qrcode.make(bitcoin_format % ({'address':bitcoin_address,'amount':amount }))
    qr._img.save(output,'GIF')
    return Response(output.getvalue(), mimetype='image/gif')

def my_gateway():
    r = os.popen('route print').read()

def my_eth0_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('gmail.com',80))
    ret = s.getsockname()[0]
    s.close()
    return ret

def my_wlan0_ip():
    return '192.168.42.1'

def has_balance(pub_key):
    h1 = httplib.HTTPConnection('blockchain.info')
    h1.request('GET','/q/getreceivedbyaddress/%s' % (pub_key))
    r = h1.getresponse()
    ret = int(r.read())
    logging.debug('Amount found is %s' % ret)
    return ret

def enable_access():
    return

def flush_funds():
    return

@app.route('/checkaccess')
def check_access():
    ip = request.remote_addr
    mac = read_arp_table()[ip]
    if True:
        enable_access()
        flush_funds()
        return render_template('access_enabled.html')
    else:
        return render_template('no_access_yet.html')


@app.route('/<path:path>')
def catch_all(path):
    return redirect('http://' + my_wlan0_ip() )
    #return redirect(url_for('home', region=None, ip=None))

def read_arp_table():
    ip_list = dict()
    test = []
    ip_mac_re = re.compile('(?P<ip>[0-9\.]+)\s+(?P<mac>[0-9a-f-]+)\s+(?P<type>[sd])')
    l = os.popen('arp -a')
    for r in l:
        g = ip_mac_re.findall(r)
        if g:
            h = g[0]
            ip_list[h[0]] = {'ip':h[0],'mac':h[1],'dyn':h[2]=='d'}

    return ip_list

if __name__ == '__main__':
    global session
    app.run(host='0.0.0.0',port=80,debug=True)
