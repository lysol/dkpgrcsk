FREDERICK DOUGLBUTT
===================

This is an ultra-simple (sorta) IRC bot that uses irclib. A little messy,
but I'm ok with it. You can write new plugins pretty simply.

  * Subclass ButtPlugin
  * define \_\_provides\_\_
  * define do_commands and optionally on_events
  * define timed events (good example is twitter.py)
  * edit plugins/\_\_init\_\_.py

But, honestly, this bot isn't really suitable for anyone without a decent
chunk of Python knowledge.
