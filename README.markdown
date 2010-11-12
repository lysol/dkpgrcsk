FREDERICK DOUGLBUTT
===================

![Douglbutt](http://a3.twimg.com/profile_images/338240875/225px-Frederick_Douglass_portrait.jpg "Douglbutt")

This is an ultra-simple (sorta) IRC bot that uses irclib. A little messy,
but I'm ok with it. You can write new plugins pretty simply.

  * Subclass ButtPlugin
  * define \_\_provides\_\_
  * define do_commands and optionally on_events
  * define timed events (good example is twitter.py)
  * edit plugins/\_\_init\_\_.py

But, honestly, this bot isn't really suitable for anyone without a decent
chunk of Python knowledge.

REQUIREMENTS
============

Tumblr support requires:

  * [pymblr](http://github.com/lysol/pymblr "pymblr")
  * [poster](http://atlee.ca/software/poster/ "poster")
  * [elementtree](http://effbot.org/zone/element-index.htm "elementree")
  * [mechanize](http://wwwsearch.sourceforge.net/mechanize/ "mechanize")

All but poster and pymblr should be available via easy_install. Tumblr support
relies on pymblr's autopost\_url, so any of the forks should be ok, and I try to
merge in improvements from the forks.

Twitter support requires nothing! That's because I just copied the API module
into the plugin directory. It's also oauthified, so you don't have to freak
out about your twitter anymore.
