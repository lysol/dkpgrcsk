dkpgrcsk
===================

This is an ultra-simple (sorta) IRC bot that uses irclib. A little messy,
but I'm ok with it. You can write new plugins pretty simply.

REQUIREMENTS
============

Main requirements: irclib. The plugins have their own requirements.

Tumblr support requires:

  * [pymblr](http://github.com/lysol/pymblr "pymblr")

Markov support requires:

  * [marko](http://github.com/rupa/marko "marko")

INSTALLATION AND USE
====================
    git clone git@github.com:lysol/dkpgrcsk.git
    cd dkpgrcsk
    python setup.py install
    cp src/dkpgrcsk.conf-sample ~/dkpgrcsk.conf
    vim ~/dkpgrcsk.conf
    python -m dkpgrcsk.__init__ ~/dkpgrcsk.conf
