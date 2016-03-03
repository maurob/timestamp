"""
Web API consumer for www.timeapi.org
"""
import urllib2
from urllib2 import URLError
from dateutil.parser import parse
from dateutil import tz
from datetime import datetime

url = "http://www.timeapi.org/utc/now"


def remote_now():
    """ Return the a local time zone datetime or raise an URLError """
    socket = urllib2.urlopen(url)
    text = socket.read()
    socket.close()
    return parse(text).replace(tzinfo=tz.tzutc(), microsecond=0).astimezone(tz.tzlocal())


def localhost_now():
    """ Return the a local time zone datetime from the localhost """
    return datetime.utcnow().replace(tzinfo=tz.tzutc(), microsecond=0).astimezone(tz.tzlocal())


def now(return_type=datetime):
    """ Try with remote_now first, otherwise use localhost_now """
    try:
        d = remote_now()
    except URLError:
        print("Warning: Internet isn't available then using localhost time.")
        d = localhost_now()
    if return_type is str:
        return tostr(d)
    else:
        return d


def tostr(datetime_obj):
    return datetime_obj.strftime('%Y-%m-%d %H:%M:%S %z')
