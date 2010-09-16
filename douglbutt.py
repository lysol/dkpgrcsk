#!/usr/bin/env python

import os
import sys
from ircbot import SingleServerIRCBot
from irclib import nm_to_n, nm_to_h, irc_lower, ip_numstr_to_quad, ip_quad_to_numstr
from optparse import OptionParser
import ConfigParser

class MissingPluginSetting(Exception):

    def __repr__(self, plugin, setting):
        return "%s requires setting '%s'" % (plugin, setting)


class ButtPlugin(object):
    """Provide an abstracted functionality to the IRC bot. Handles IRC events
    if they are defined."""

    # Define a plugin name in lowercase here. This is also the section name in
    # the configuration file.
    __provides__ = None

    # This is a plugin. So it has this attribute.
    yo_mtv_raps = True

    required_settings = ()

    def _error(self, exception):
        print "EXCEPTION: %s %s" % (repr(exception), exception)

    def _command_check(self, c, e, reply_to):
        """Process commands that have corresponding methods."""
        arg = e.arguments()[0]
        cmds = arg.split(' ')
        for cmd in cmds:
            method_name = 'do_%s' % cmd
            if hasattr(self, method_name):
                method = getattr(self, method_name)
                try:
                    method(' '.join(cmds[1:]), reply_to)
                except Exception as e:
                    self._error(e)
                    self.bot.connection.privmsg(reply_to, "An error occurred.")

    def on_pubmsg(self, c, e):
        """This is an example of a hooked event. This is also the default
        method for handling commands, so if you are subclassing this,
        make sure you call the original on_pubmsg."""
        self._command_check(c, e, e.target())

    def on_privmsg(self, c, e):
        """Same thing as on_pubmsg, only for private messages."""
        self._command_check(c, e, nm_to_n(e.source()))

    def timed(self, interval):
        """interval is the interal ticker for the timer. Use modulus to define
        more sparse intervals than 1 per second."""
        pass

    def load_hook(self):
        """Execute something when the plugin is loaded."""
        pass

    def __init__(self, bot, settings):
        self.bot = bot
        for setting in self.required_settings:
            if setting not in settings.keys():
                raise MissingPluginSetting(self, setting)
            setattr(self, setting, settings[setting])
        self.load_hook()


class DouglButt(SingleServerIRCBot):
    """Douglbutt is an IRC bot."""

    def _timed_events(self):
        """Process timed events in plugins."""
        for plugin in self.plugins:
            if hasattr(plugin, 'timed'):
                plugin.timed(self.ticker)
        self.ticker += 1
        self.ircobj.execute_delayed(1.0, self._timed_events)

    def _hook(self, method_name, c, e):
        """Process event hooks."""
        for plugin in self.plugins:
            if hasattr(plugin, method_name):
                method = getattr(plugin, method_name)
                method(c, e)

    def _log(self, channel, nickmask, message):
        nick = nm_to_n(nickmask)
        if channel:
            if not self.log.has_key(channel):
                self.log[channel] = {}
            if not self.log[channel].has_key(nick):
                self.log[channel][nick] = []
            self.log[channel][nick].append(message)
            while len(self.log[channel][nick]) > 100:
                self.log[channel][nick].pop(0)
        else:
            if not self.log.has_key(nick):
                self.log[nick] = []
            self.log[nick].append(message)
            while len(self.log[nick]) > 100:
                self.log[nick].pop(0)


    def __init__(self, settings, plugins=[]):

        if not settings.has_key('port'):
            port = 6667
        else:
            port = settings['port']

        SingleServerIRCBot.__init__(self, [(settings['server'], port)], 
            settings['nick'], settings['user'])
        self.channel = settings['channel']
        self.plugins = []
        for plugin in plugins:
            plugin_class = plugin[0]
            plugin_settings = plugin[1]
            self.plugins.append(plugin_class(self, plugin_settings))

        self.ticker = 0
        self.ircobj.execute_delayed(1.0, self._timed_events)
        self.log = {}
        if settings.has_key('debug'):
            self.debug = True

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")
        self._hook('on_nicknameinuse', c, e)

    def on_welcome(self, c, e):
        if self.debug:
            print e.arguments()[0]
        c.join(self.channel)
        self._hook('on_welcome', c, e)

    def on_privmsg(self, c, e):
        if self.debug:
            print "%s\t%s" % (e.source(), e.arguments()[0])
        self._hook('on_privmsg', c, e)
        self._log(None, e.source(), e.arguments()[0])

    def on_notice(self, c, e):
        if self.debug:
            print "%s: %s" % (e.source(), e.arguments()[0])
        self._hook('on_notice', c, e)

    def on_join(self, c, e):
        if self.debug:
            print "Joined %s" % e.target()
        self._hook('on_join', c, e)

    def on_part(self, c, e):
        if self.debug:
            print "Parted %s" % e.target()
        self._hook('on_part', c, e)
    
    def on_kick(self, c, e):
        if self.debug:
            print "%s kicked from %s by %s" % (e.arguments()[0], e.target(), e.source())
        self._hook('on_kick', c, e)

    def on_pubmsg(self, c, e):
        if self.debug:
            print "%s %s\t%s" % (e.target(), e.source(), e.arguments()[0])
        self._hook('on_pubmsg', c, e)
        self._log(e.target(), e.source(), e.arguments()[0])
        return


def main():
    parser = OptionParser()

    (options, args) = parser.parse_args()

    if len(args) != 1:
        print "Usage: douglputt.py configfile"
        exit(1)

    settings = {} 
    config = ConfigParser.ConfigParser()
    config.read(args[0])
    for option in config.options("douglbutt"):
        settings[option] = config.get("douglbutt", option)

    if not settings.has_key('plugin_dir'):
        settings['plugin_dir'] = 'plugins'

    # Tuple list of plugin classes and their settings to pass to the bot.
    plugins = []

    mod = __import__(settings['plugin_dir'])
    for plugin in filter(lambda y: hasattr(y, 'yo_mtv_raps'),
        mod.__dict__.values()):

        if plugin.__provides__ is not None:
            plugin_settings = {}
            if config.has_section(plugin.__provides__):
                for option in config.options(plugin.__provides__):
                    plugin_settings[option] = config.get(plugin.__provides__,
                        option)
            plugins.append((plugin, plugin_settings))

    bot = DouglButt(settings, plugins=plugins)
    bot.start()

if __name__ == "__main__":
    main()