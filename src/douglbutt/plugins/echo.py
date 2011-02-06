from .._douglbutt import *

class EchoPlugin(ButtPlugin):
    
    __provides__ = 'echo'

    def do_echo(self, message, reply_to):
        self.bot.connection.privmsg(reply_to, message)

    #def on_pubmsg(self, c, e):
    #    cmd = e.arguments()[0].split(' ')
    #    if cmd[0] == 'echo':
    #        channel = e.target()
    #        self.bot.connection.privmsg(channel, ' '.join(cmd[1:]))
