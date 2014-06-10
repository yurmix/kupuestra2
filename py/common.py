import calendar
import dateutil.parser
import datetime
import socket
import arrow
import time

OPENTSDB_HOST = 'node2.cloudera1.enremmeta.com'
OPENTSDB_PORT = 4242

OPENTSDB_FILENAME = 'otsdb_%s.txt' % datetime.date.today().strftime('%m%d%Y_%M%h%s')
OPENTSDB_FILE = None
global OPENTSDB_FILE

from pricing import *

def if_send(key, value, ts=None):
    pass

def otsdb_send(key, value, tags, ts=None, file_only=False):
    if ts is None:
        ts = arrow.utcnow().timestamp
    tags_str = ' '.join(["%s=%s"  % (normalize_key(k),normalize_key(v)) for k,v in tags.items()])
    msg = "put %s %s %s %s" % (key, ts, value, tags_str)
    
    print "Sending to OpenTSDB:\n\t%s" % msg
    msg += "\n"
    # This is just for historical data
    if file_only:
        if not OPENTSDB_FILE:
            global OPENTSDB_FILE
            print "Creating %s" % OPENTSDB_FILENAME
            OPENTSDB_FILE = open(OPENTSDB_FILENAME, 'w')
        OPENTSDB_FILE.write(msg)
    else:
        i = 1
        while True:
            try:
                sock = socket.socket()
                sock.connect((OPENTSDB_HOST, OPENTSDB_PORT))
                sock.sendall(msg)
                sock.close()
                break
            except Exception, e:
                if i > 10:
                    raise
                print  e
                time.sleep(i*3)
                print "Trying again %s" % i
                i += 1
                continue

def g_send(key, value, ts=None):
    if ts is None:
        ts = arrow.utcnow().timestamp
    msg = "%s %s %s" % (key,value,ts)
    #print ts
#    print msg 
    msg += "\n"
    sock = socket.socket()
    sock.connect((CARBON_SERVER, CARBON_PORT))
    sock.sendall(msg)
    sock.close()

def normalize_key(key):
    key = key.replace('/','_')
    key = key.replace('-','_')
    key = key.replace(' ','_')
    key = key.replace(':','_')
    key = key.replace('(','')
    key = key.replace(')','')
    return key

def ts_from_aws(arg):
    arg0 = arg
    if isinstance(arg, dict):
        arg = arg['Timestamp']
    if not isinstance(arg, datetime.datetime):
      #  print "Parsing %s"  %arg
        arg = dateutil.parser.parse(arg)
    ts = calendar.timegm(arg.utctimetuple())
    #print "Parsed %s to %s" % (arg0, ts)
    return ts

DEFAULT_LOOKBACK_MINUTES=-8
