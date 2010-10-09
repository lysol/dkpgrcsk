import os
import traceback
from time import localtime, mktime, strptime
import oauth2 as oauth
from oauthtwitter import OAuthApi
import cPickle
from douglbutt import ButtPlugin

class TwitterPlugin(ButtPlugin):
    
    __provides__ = 'twitter'

    required_settings = (
        'consumer_key',
        'consumer_secret'
        )

    def timed(self, ticker):
        if ticker % 120 == 0 or ticker == 0:
            tweets = self.twitter.GetMentions()
            times = [strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y') \
                for tweet in tweets]
            if len(times) > 0:
                max_time = times[0]
            else:
                return
            for tweet in tweets:
                time_posted = strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
                new_text = '<%s> %s' % (tweet['user']['screen_name'], tweet['text'])

                if time_posted > localtime(self.last_reply_time):
                    for chname, chobj in self.bot.channels.items():
                        self.bot.connection.privmsg(chname, new_text)
            self.last_reply_time = mktime(max_time)

    def do_quote(self, message, reply_to):
        args = message.strip().split(' ')
        tags = filter(lambda x: x[0] == '#', args)
        user = args[0]
        if self.bot.log.has_key(reply_to) and self.bot.log[reply_to].has_key(user):
            last_said = self.bot.log[reply_to][user][-1].strip()
            last_said += " " + " ".join(tags)
            if len(last_said) > 140:
                self.bot.connection.privmsg(reply_to, "Too long :(")
                return
            self.twitter.UpdateStatus(last_said)
            self.bot.connection.privmsg(reply_to, 
                "%s has been quoted to twitter." % user)

    def do_untwit(self, message, reply_to):
        now = mktime(localtime(None))
        if self.last_untwit + 60 >= now:
            self.bot.connection.privmsg(reply_to, "Chill.")
            return
        timeline = \
            self.twitter.GetUserTimeline(options={
                'screen_name': self.screen_name
                })
        id = timeline[0]['id']
        result = self.twitter.ApiCall("statuses/destroy/%s" % id, "POST", {})
        self.bot.connection.privmsg(reply_to, "Deleted tweet %s" % id)
        self.last_untwit = mktime(localtime(None))

    def do_sup(self, message, reply_to):
        username = message.split(' ')[0]
        timeline = \
            self.twitter.GetUserTimeline(options={'screen_name': username})
        new_text = '<%s> %s' % (timeline[0]['user']['screen_name'], 
            timeline[0]['text'])
        self.bot.connection.privmsg(reply_to, new_text)

    def do_twit(self, message, reply_to):
        if len(message) > 140:
            self.bot.connection.privmsg(reply_to,
                "Trim off %d characters, dickface" % (len(message) - 140))
            return
        self.twitter.UpdateStatus(message)

    def initialize_twitter_auth(self):
        """Follow Twitter's idiotic authentication procedures"""
        self.twitter = OAuthApi(self.consumer_key, self.consumer_secret)
        temp_credentials = self.twitter.getRequestToken()
        print(self.twitter.getAuthorizationURL(temp_credentials))
        oauth_verifier = raw_input('Enter the PIN Twitter returns: ')
        access_token = self.twitter.getAccessToken(temp_credentials, oauth_verifier)
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
        self.last_reply_time = mktime(localtime(None))
        self.last_untwit = mktime(localtime(None))
