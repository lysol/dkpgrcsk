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

    __provides__ = None

    # This is a plugin. So it has this attribute.
    yo_mtv_raps = True

    required_settings = ()

    def load_hook(self):
        pass

    def __init__(self, bot, settings):
        self.bot = bot
        for setting in self.required_settings:
            if setting not in settings.keys():
                raise MissingPluginSetting(self, setting)
            setattr(self, setting, settings[setting])
        self.load_hook()


class DouglButt(SingleServerIRCBot):

    def _hook(self, method_name, c, e):
        for plugin in self.plugins:
            if hasattr(plugin, method_name):
                method = getattr(plugin, method_name)
                method(c, e)

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

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")
        self._hook('on_nicknameinuse', c, e)

    def on_welcome(self, c, e):
        c.join(self.channel)
        self._hook('on_welcome', c, e)

    def on_privmsg(self, c, e):
        self._hook('on_privmsg', c, e)

    def on_pubmsg(self, c, e):
        self._hook('on_pubmsg', c, e)
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