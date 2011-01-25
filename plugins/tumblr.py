from douglbutt import ButtPlugin
from pymblr import Api, TumblrError
from ircbot import nm_to_n
import cgi
from mechanize._mechanize import BrowserStateError
from time import sleep
from urllib2 import URLError

class TumblrPlugin(ButtPlugin):

    __provides__ = 'tumblr'

    required_settings = (
        'email',
        'password',
        'tumblog'
        )

    def do_quote(self, message, reply_to):
        new_args = message.strip().split(' ')
        user = new_args[0]
        tag_args = filter(
            lambda arg: len(arg) > 0 and arg[0] == '#'
            ,new_args
        )
        real_args = filter(
            lambda arg: len(arg) > 0 and arg[0] != '#'
            ,new_args
        )
        # remove hash
        tag_args = [arg[1:] for arg in tag_args]
        
        print "real args: %s\ntag args: %s" % (real_args, tag_args)
        
        if len(real_args) == 1:
            # quote a single person
            last_said = self.bot.log[reply_to][user][-1].strip()
            if last_said != None:
                try:
                    api = Api(self.tumblog, self.email, self.password)
                    post = api.write_regular(body = cgi.escape(last_said),
                        tags = tag_args, slug = 'quote')
                    print "Quoted %s as %s" % (user,
                        post['url'])
                    
                    #bot.say(channel, "Your quote: %s" % post['url'])
                except TumblrError, e:
                    self.bot.connection.privmsg(reply_to, "Tumblr posting " + \
                    "failed due to a temporary error.")
                    print TumblrError, e
                except Exception, e:
                    #bot.say(channel, "Something horrible happened.")
                    print e
            else:
                self.bot.connection.privmsg(reply_to,
                    "That person hasn't said anything, according to my " + \
                    "recollection. Or perhaps you are fat.")


    def handle_url(self, message, reply_to, url, sender, times=0):
        new_args = message.strip().split(' ')
        
        tag_args = filter(
            lambda arg: len(arg) > 0 and arg[0] == '#'
            ,new_args
        )

        real_args = filter(
            lambda arg: len(arg) > 0 and arg[0] != '#'
            ,new_args
        ) 

        filtered_msg = ' '.join(real_args).replace(url,'').replace(':','')

        times = times + 1
        print "Attempting to post %s for the #%i time" % (url, times)
        nick = nm_to_n(sender)
        api = Api(self.tumblog, self.email, self.password)
        caption = '%s\nvia %s' % (filtered_msg, nick)
        try:
            try:
                urls = api.readurls()
                if url not in api.readurls():
                    post = api.autopost_url(url, caption, tag_args)
                    print "%s posted a %s to %s" % (nick, post['type'], post['url'])
            except BrowserStateError:
                # Skipping because of a mechanize error.
                return
            except URLError:
                return

        except TumblrError, e:
            return
            if (times < 3):
                print e
                print "Error encountered, trying it again."
                # try it again, a couple of times.
                sleep(3)
                self.handle_url(self, message, reply_to, url, sender, times=times)
            else:
                print e
                #bot.say(channel, "Something horrible happened.")
