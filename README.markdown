FREDERICK DOUGLBUTT
===================

This is an ultra-simple (sorta) IRC bot that uses irclib. A little messy,
but I'm ok with it. You can write new plugins pretty simply.

REQUIREMENTS
============

Tumblr support requires:

  * [pymblr](http://github.com/lysol/pymblr "pymblr")
  * [poster](http://atlee.ca/software/poster/ "poster")
  * [elementtree](http://effbot.org/zone/element-index.htm "elementree")
  * [mechanize](http://wwwsearch.sourceforge.net/mechanize/ "mechanize")

All but pymblr should be available via easy_install. Tumblr support
relies on pymblr's autopost\_url, so any of the forks should be ok, and I try to
merge in improvements from the forks.

Twitter support requires nothing! That's because I just copied the API module
into the plugin directory. It's also oauthified, so you don't have to freak
out about your twitter anymore.

INSTALLATION AND USE
====================
    git clone git@github.com:lysol/douglbutt.git
    cd douglbutt
    python setup.py install
    cp src/douglbutt.conf-dist ~/douglbutt.conf
    vim ~/douglbutt.conf
    python -m douglbutt.__init__ ~/douglbutt.conf
