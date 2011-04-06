from .._douglbutt import *


class EchoPlugin(ButtPlugin):

    __provides__ = 'echo'

    def do_echo(self, message, reply_to):
        self.bot.connection.privmsg(reply_to, message)
