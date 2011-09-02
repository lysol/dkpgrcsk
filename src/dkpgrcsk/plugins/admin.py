from .._dkpgrcsk import *

class AdminPlugin(DPlugin):
    
    __provides__ = 'admin'

    required_settings = ()

    @admin_command
    def do_reloadall(self, message, reply_to):
        self.bot.reload()

    @admin_command
    def do_reloadplugins(self, message, reply_to):
        self.bot.reload_plugins()

    @admin_command
    def do_reloadsettings(self, message, reply_to):
        self.bot.reload_settings()