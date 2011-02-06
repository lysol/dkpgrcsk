import time
from .._douglbutt import *

class Friend(ButtPlugin):

    __provides__ = 'friend'
    join_pending = None

    def _rejoin(self, channel):
        self.bot.set_callback(self.bot.connection.join, lambda x: None,
            args=[channel])

    def timed(self, ticker):
        if self.join_pending is not None and ticker % 3 == 0:
            self._rejoin(self.join_pending)

    def on_join(self, connection, event):
        self.join_pending = None

    def on_kick(self, connection, event):
        self.join_pending = event.target() 
