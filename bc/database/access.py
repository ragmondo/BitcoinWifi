__author__ = 'CMS'

from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
import time

from webserver import db

Base = declarative_base()

def create_db(app):
    pass

class Key(db.Model):
    __tablename__ = "key"
    id = Column(Integer, primary_key=True)
    priv_key = Column(String)
    pub_key = Column(String)
    ip_address = Column(String)
    mac_address = Column(String)

class Session(db.Model):
    __tablename__ =  "session"
    id = Column(Integer, primary_key=True)
    pub_key = Column(String)
    endtime = Column(Integer)
    transaction = Column(String)

class Price(db.Model):
    __tablename__ = "price"
    id = Column(Integer, primary_key=True)
    rate = Column(Float)
    length = Column(Integer)
    shortname = Column(String)
    longname = Column(String)

class SessionDB(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SessionDB, cls).__new__(cls, *args)
        return cls._instance

    def __init__(self):
        self.db = db
        self.db.create_all()

    # def _initConnection(self):
    #     DBSession = sessionmaker()
    #     self.engine = create_engine('sqlite+pysqlite:///file.db', module=sqlite)
    #     DBSession.configure(bind=self.engine)
    #     Base.metadata.create_all(self.engine)
    #     self.session = DBSession()

    def create_key(self, pub_key, priv_key, ip_address, mac_address):
#        self._initConnection()
        k = Key(pub_key=pub_key, priv_key=priv_key, ip_address=ip_address, mac_address=mac_address)
        self.db.session.add(k)
        self.db.session.commit()

    def get_key(self, ip, mac):
        return self.db.session.query(Key).filter(Key.ip_address == ip).filter(Key.mac_address == mac).first()

    def add_session(self, mac, length, tx):
        s = Session(mac=mac, endtime=int(time.time()+length), transaction=tx)
        self.db.session.add(s)
        self.db.session.commit()

    def get_session(self, mac):
        rightnow = time.time()
        q = self.db.session.query(Session).filter(mac == mac).filter(Session.endtime > rightnow).first()
        return q

    def restore_sessions(self):
        rightnow = time.time()
        return self.db.session.query(Session).filter(Session.endtime > rightnow)

    def update_price(self, price):
        # TODO Update price from front end
        pass

    def new_price(self, shortname, longname, amount, length):
        r = Price(rate=amount, length=length, shortname=shortname, longname=longname)
        self.db.session.add(r)
        self.db.session.commit()