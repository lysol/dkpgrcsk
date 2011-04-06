from .._douglbutt import *
import marko


class Markov(ButtPlugin):

    __provides__ = 'markov'

    def initialize_marko(self):
        self.m = marko.Markov('sqlite', self.database)

    def do_markov(self, message, reply_to):
        resp = self.m.markov(message)
        self.bot.connection.privmsg(reply_to, resp)

    def do_vokram(self, message, reply_to):
        resp = self.m.vokram(message)
        self.bot.connection.privmsg(reply_to, resp)

    def do_markov2(self, message, reply_to):
        resp = self.m.markov2(message)
        self.bot.connection.privmsg(reply_to, resp)

    def on_pubmsg(self, c, e):
        self.m.slurpstring(e.arguments()[0])

    def on_privmsg(self, c, e):
        self.m.slurpstring(e.arguments()[0])

    def load_hook(self):
        if not hasattr(self, 'database'):
            self.database = '.marko.db'
        self.initialize_marko()
