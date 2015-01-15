__author__ = 'CMS'

import httplib

def get_balance(pub_key):
    try:
        # RG - this returns the balance in bitcoins of that address
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

def flush_funds(private_key, wallet):
    # RG: move all funds from privatekey to wallet so that we don't double authorize.
    pass
