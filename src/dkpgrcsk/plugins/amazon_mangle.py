from .._dkpgrcsk import *
import os
import traceback
from time import localtime, mktime, strptime
from urlparse import urlparse
import urllib2
import re

class AmazonManglePlugin(DPlugin):

    __provides__ = 'amazon_mangle'

    required_settings = [
        'code'
        ]

    def middleware(self, c, e):
        urls = self._get_urls(e)
        ama = re.compile(r"amazon\.com")
        asinm = re.compile(r"/([A-Z0-9]{10})")
        for url in filter(lambda u: ama.search(u), urls):
            print "Matched %s as an amazon url" % url
            result = asinm.search(url)
            if result:
                # amazon url
                asin = result.groups(1)
                if (type(asin) in [tuple, list]):
                    asin = asin[0]
                e._arguments[0] = e._arguments[0].replace(url, 
                    "http://amazon.com/dp/%s/%s" % (asin, self.code))
        return [c, e]
