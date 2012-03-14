import datetime
from .._dkpgrcsk import *


class RepostPlugin(DPlugin):

    __provides__ = 'repost'

    required_settings = (
        'max_days',
        )

    def prune_old(self):
        tups = [t for t in self.urls.iteritems()]
        cutoff = datetime.datetime.now() - \
            datetime.timedelta(days=int(self.max_days))
        pruned = filter(lambda t: t[1] > cutoff, tups)
        self.urls = dict(pruned)

    def host_ignored(self, host):
        for mask in self.ignore:
            if host_matches(host, mask):
                return True
        return False

    def handle_url(self, message, reply_to, url, sender, times=0):
        # Check the ignore list
        if self.host_ignored(sender):
            return
        if url in self.urls.keys():
            last_time = self.urls[url]
            datediff = datetime.datetime.now() - last_time
            if datediff > datetime.timedelta(0,15):
                self.bot.connection.privmsg(reply_to,
                    'Thanks for posting this again. (%s since last time)' % \
                        str(datetime.datetime.now() - last_time).split('.')[0])
        self.urls[url] = datetime.datetime.now()
        self.prune_old()

    def __init__(self, bot, settings):
        self.urls = {}
        DPlugin.__init__(self, bot, settings)
        if not hasattr(self, 'ignore'):
            self.ignore = []
        if hasattr(self, 'ignore') and not (type(self.ignore) == list):
            self.ignore = [self.ignore]
