from douglbutt import ButtPlugin

class EchoPlugin(ButtPlugin):
    
    __provides__ = 'echo'

    def on_pubmsg(self, c, e):
        cmd = e.arguments()[0].split(' ')
        if cmd[0] == 'echo':
            channel = e.target()
            self.bot.connection.privmsg(channel, ' '.join(cmd[1:]))
