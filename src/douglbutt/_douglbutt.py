#!/usr/bin/env python

import os
import sys
from ircbot import SingleServerIRCBot
from irclib import nm_to_n, nm_to_h, irc_lower, \
    ip_numstr_to_quad, ip_quad_to_numstr
from optparse import OptionParser
import ConfigParser
import pyfiurl
import threading
import urllib2
import Queue
import random
import re


def host_matches(host, mask):
    """Check if a mask matches a mask.

    Returns true if the mask matches, otherwise false.
    """
    newmask = re.sub('\*', '.*', re.sub('\?', '.', mask))
    r = re.compile(newmask, re.IGNORECASE)
    return r.match(host) is not None


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
        cmd = cmds[0]
        message = ' '.join(cmds[1:])
        full_message = ' '.join(cmds)
        method_name = 'do_%s' % cmd
        sender = e.source()
        if hasattr(self, method_name):
            method = getattr(self, method_name)
            try:
                method(message, reply_to)
            except Exception as e:
                self._error(e)
                self.bot.connection.privmsg(reply_to, "An error occurred.")

        if hasattr(self, 'handle_url'):
            urls = pyfiurl.grab(full_message)
            if urls:
                for url in urls:
                    self.handle_url(full_message, reply_to, url, sender)

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
        for setting in settings:
            setattr(self, setting, settings[setting])
        self.load_hook()


class DouglButt(SingleServerIRCBot):
    """Douglbutt is an IRC bot."""

    queue = Queue.Queue()
    threads = []
    callbacks = {}

    def _handle_callback(self, func, tid, args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except Exception, e:
            result = e
        self.queue.put((tid, result))

    def set_callback(self, func, callback, args=[], kwargs={}):
        tid = random.randint(0, 65535)
        self.threads.append(threading.Thread(target=self._handle_callback,
            args=[func, tid, args], kwargs=kwargs))
        self.threads[-1].start()
        self.callbacks[tid] = callback

    def _timed_events(self):
        """Process timed events in plugins, and thread callbacks."""
        try:
            result = self.queue.get(False)
            if result[0] in self.callbacks.keys():
                self.callbacks[result[0]](result[1])
                del(self.callbacks[result[0]])
        except Queue.Empty:
            pass
        for plugin in self.plugins:
            if hasattr(plugin, 'timed'):
                plugin.timed(self.ticker)
        self.ticker += 1
        self.ircobj.execute_delayed(1.0, self._timed_events)

    def _hook(self, method_name, c, e):
        """Process event hooks."""
        for plugin in self.plugins:
            the_class = type(plugin)
            if method_name == 'on_pubmsg':
                plugin._command_check(c, e, e.target())
            elif method_name == 'on_privmsg':
                plugin._command_check(c, e, nm_to_n(e.source()))

            if hasattr(plugin, method_name):
                #method = getattr(plugin, method_name)
                method = getattr(the_class, method_name)
                method(plugin, c, e)

    def _log(self, channel, nickmask, message):
        nick = nm_to_n(nickmask)
        if channel:
            if channel not in self.log:
                self.log[channel] = {}
            if nick not in self.log[channel]:
                self.log[channel][nick] = []
            self.log[channel][nick].append(message)
            while len(self.log[channel][nick]) > 100:
                self.log[channel][nick].pop(0)
        else:
            if nick not in self.log:
                self.log[nick] = []
            self.log[nick].append(message)
            while len(self.log[nick]) > 100:
                self.log[nick].pop(0)

    def register_plugin(self, bpclass):

        plugin_settings = self.settings[bpclass.__provides__]
        self.plugins.append(bpclass(self, plugin_settings))

    def __init__(self, settings, plugins=[]):

        if 'port' not in settings:
            port = 6667
        else:
            port = settings['port']

        self.settings = settings

        SingleServerIRCBot.__init__(self, [(settings['server'], port)],
            settings['nick'], settings['user'])
        self.channel = settings['channel']
        self.plugins = []
        for plugin in plugins:
            self.register_plugin(plugin)

        self.ticker = 0
        self.ircobj.execute_delayed(1.0, self._timed_events)
        self.log = {}
        if 'debug' in settings:
            self.debug = True

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")
        self._hook('on_nicknameinuse', c, e)

    def on_welcome(self, c, e):
        if self.debug:
            print e.arguments()[0]
        if 'pass' in self.settings:
            c.privmsg('nickserv', 'identify ' + self.settings['pass'])
        if 'key' in self.settings:
            c.join(self.channel, self.settings['key'])
        else:
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
        if e.target() not in self.log:
            self.log[e.target()] = {}
        self._hook('on_join', c, e)

    def on_part(self, c, e):
        if self.debug:
            print "Parted %s" % e.target()
        self._hook('on_part', c, e)

    def on_kick(self, c, e):
        if self.debug:
            print "%s kicked from %s by %s" % (e.arguments()[0], e.target(),
                e.source())
        self._hook('on_kick', c, e)

    def on_pubmsg(self, c, e):
        if self.debug:
            print "%s %s\t%s" % (e.target(), e.source(), e.arguments()[0])
        self._hook('on_pubmsg', c, e)
        self._log(e.target(), e.source(), e.arguments()[0])
        return


def main():
    import plugins
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

    if 'load_plugins' in settings.keys():
        settings['load_plugins'] = settings['load_plugins'].split(' ')
    else:
        settings['load_plugins'] = []

    # Tuple list of plugin classes and their settings to pass to the bot.
    load_plugins = []

    for plugin in filter(lambda y: hasattr(y, 'yo_mtv_raps'),
        plugins.__dict__.values()):
        if plugin.__provides__ is not None and plugin.__provides__ in \
            settings['load_plugins']:
            print 'Loading plugin %s' % plugin.__name__
            plugin_settings = {}
            if config.has_section(plugin.__provides__):
                for option in config.options(plugin.__provides__):
                    plugin_settings[option] = config.get(plugin.__provides__,
                        option)
            settings[plugin.__provides__] = plugin_settings
            load_plugins.append(plugin)

    bot = DouglButt(settings, plugins=load_plugins)
    bot.start()

if __name__ == "__main__":
    main()
