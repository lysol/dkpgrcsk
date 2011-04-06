from .._douglbutt import *
from twitter import *
from tumblr import *
from echo import *
from friend import *
from markov import *
from repost import *


class LogPlugin(ButtPlugin):

    __provides__ = 'log'

    def do_printlog(self, message, reply_to):
        log = self.bot.log
        for channel in log.keys():
            if type(log[channel]) == list:
                for item in log[channel]:
                    print channel, item
            else:
                for key in log[channel].keys():
                    for item in log[channel][key]:
                        print channel, key, item
