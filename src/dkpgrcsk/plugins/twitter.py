from .._dkpgrcsk import *
import os
import traceback
from time import localtime, mktime, strptime
import oauth2 as oauth
from oauthtwitter import OAuthApi
import cPickle
from urlparse import urlparse
import urllib2


class TwitterPlugin(DPlugin):

    __provides__ = 'twitter'

    required_settings = (
        'consumer_key',
        'consumer_secret'
        )

    def timed(self, ticker):
        """
        Check for replies using the API. Supply a since_id per the API,
        but also filter on date and time in case the bot is just starting up.
        """
        if ticker % 45 == 0 or ticker == 0:
            def handle_tweets(tweets):
                if isinstance(tweets, Exception):
                    print str(tweets)
                    return
                if len(tweets) == 0:
                    return
                if self.last_id is not None:
                    for tweet in tweets:
                        new_text = u'<%s> %s' % (tweet['user']['screen_name'],
                            tweet['text'])
                        new_text = new_text.encode('utf-8').replace("\n", "")

                        for chname, chobj in self.bot.channels.items():
                            self.bot.connection.privmsg(chname,
                                new_text)
                self.last_id = tweets[0]['id']

            if self.last_id is not None:
                kwargs = {
                    'options': {
                        'since_id': self.last_id
                     }
                }
            else:
                kwargs = {}
            self.bot.set_callback(self.twitter.GetMentions, handle_tweets,
                kwargs=kwargs)

    def do_trends(self, message, reply_to):
        def run_trends(trends):
            data = trends['trends']
            keywords = [t['name'] for t in data]
            new_text = ", ".join(keywords)
            new_text = new_text.encode('utf-8')
            self.bot.connection.privmsg(reply_to, new_text)
        self.bot.set_callback(self.twitter.ApiCall, run_trends,
            args=("trends", "GET", {}))

    def do_quote(self, message, reply_to):
        args = message.strip().split(' ')
        tags = filter(lambda x: x[0] == '#', args)
        user = args[0]
        if reply_to in self.bot.log and \
            user in self.bot.log[reply_to]:
            last_said = self.bot.log[reply_to][user][-1].strip()
            last_said += " " + " ".join(tags)
            if len(last_said) > 140:
                self.bot.connection.privmsg(reply_to, "Too long :(")
                return

            def reply(result):
                self.bot.connection.privmsg(reply_to,
                    "%s has been quoted to twitter." % user)
            self.bot.set_callback(self.twitter.UpdateStatus, reply,
                args=[last_said])

    def do_untwit(self, message, reply_to):
        now = mktime(localtime(None))
        if self.last_untwit + 60 >= now:
            self.bot.connection.privmsg(reply_to, "Chill.")
            return

        def run_timeline(timeline):

            try:
                id = timeline[0]['id']
            except IndexError:
                self.bot.connection.privmsg(reply_To, "Fail whale (Try again)")
                return
            result = self.twitter.ApiCall("statuses/destroy/%s" % id, "POST",
                {})
            if type(result) == urllib2.HTTPError or \
                type(result) == urllib2.URLError:
                self.bot.connection.privmsg(reply_to, "Fail whale")
                return
            try:
                self.bot.connection.privmsg(reply_to, "Deleted tweet %s" % id)
                self.last_untwit = mktime(localtime(None))
            except Exception, e:
                print 'untwit error: %s because of %s' % (e, result)
        self.bot.set_callback(self.twitter.GetUserTimeline, run_timeline,
            kwargs={'options': {'screen_name': self.screen_name}})

    def do_sup(self, message, reply_to):
        username = message.split(' ')[0]

        def run_timeline(timeline):
            try:
                new_text = u'<%s> %s' % (timeline[0]['user']['screen_name'],
                    timeline[0]['text'])
                new_text = new_text.encode('utf-8').replace("\n", " ")
                self.bot.connection.privmsg(reply_to, new_text)
            except IndexError:
                self.bot.connection.privmsg(reply_to,
                    "Could not retrieve timeline.")

        self.bot.set_callback(self.twitter.GetUserTimeline, run_timeline,
            kwargs={'options': {'screen_name': username}})

    def do_twit(self, message, reply_to):
        if len(message) > 140:
            self.bot.connection.privmsg(reply_to,
                "Tweet too long. Trim off %d characters." % (len(message) - 140))
            return
        self.bot.set_callback(self.twitter.UpdateStatus, lambda x: None,
            args=[message])

    def handle_url(self, message, reply_to, url, sender, times=0):
        """Autodetect twitter urls and paste links."""
        parsed = urlparse(url)
        if parsed.netloc[-11:] == 'twitter.com':
            path = (parsed.path + '#' + parsed.fragment).split('/')
            if path[-2][:6] == 'status':
                tweet_id = path[-1]
                # lazy. old urls have no fragment.
                if tweet_id[-1] == '#':
                    tweet_id = tweet_id[:-1]
                apipath = "statuses/show/%s" % tweet_id

                def process_tweet(result):
                    if type(result) == urllib2.HTTPError or \
                        type(result) == urllib2.URLError:
                        self.bot.connection.privmsg(reply_to, "Fail whale")
                        return
                    try:
                        new_text = u'<%s> %s' % (result['user']['screen_name'],
                            result['text'])
                    except Exception, e:
                        print 'Error received: %s because of %s' % (e, result)
                    new_text = new_text.encode('utf-8').replace("\n", "")
                    self.bot.connection.privmsg(reply_to, new_text)

                self.bot.set_callback(self.twitter.ApiCall, process_tweet,
                    args=(apipath, "GET", {}))

    def initialize_twitter_auth(self):
        """Follow Twitter's idiotic authentication procedures"""
        self.twitter = OAuthApi(self.consumer_key, self.consumer_secret)
        temp_credentials = self.twitter.getRequestToken()
        print(self.twitter.getAuthorizationURL(temp_credentials))
        oauth_verifier = raw_input('Enter the PIN Twitter returns: ')
        access_token = self.twitter.getAccessToken(temp_credentials,
            oauth_verifier)
        auth_file = open('.twitter_auth', 'wb')
        cPickle.dump(access_token, auth_file)
        auth_file.close()

    def initialize_twitter(self):
        """Use saved access credentials to set up the API."""
        auth_file = open('.twitter_auth', 'rb')
        access_token = cPickle.load(auth_file)
        self.twitter = OAuthApi(self.consumer_key, self.consumer_secret,
            access_token['oauth_token'], access_token['oauth_token_secret'])
        self.screen_name = access_token['screen_name']

    def load_hook(self):
        while not os.path.exists('.twitter_auth'):
            self.initialize_twitter_auth()
        self.initialize_twitter()
        self.last_id = None
        self.last_untwit = mktime(localtime(None))
