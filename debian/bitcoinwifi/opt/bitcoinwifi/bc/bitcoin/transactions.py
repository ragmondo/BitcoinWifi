__author__ = 'CMS'

import httplib

def get_balance(pub_key):
    try:
        h1 = httplib.HTTPConnection("blockchain.info")
        h1.request("GET","/q/getreceivedbyaddress/%s" % (pub_key))
        r = h1.getresponse()
    except:
        return 0
    return int(r.read())

def get_last_transaction(pub_key):
    #TODO
    # return the amount of the last transaction
    pass

def flush_funds(wallet):
    #TODO
    # move funds to central wallet
    pass
