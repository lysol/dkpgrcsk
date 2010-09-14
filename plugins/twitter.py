import os
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

    def on_pubmsg(self, c, e):
        pass

    def load_hook(self):
        while not os.path.exists('.twitter_auth'):
            self.initialize_twitter_auth()
        self.initialize_twitter()

        
        

