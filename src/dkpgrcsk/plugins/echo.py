from .._dkpgrcsk import *


class EchoPlugin(DPlugin):

    __provides__ = 'echo'

    def do_echo(self, message, reply_to):
        self.bot.connection.privmsg(reply_to, message)
