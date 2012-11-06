from util import *
import urllib2

def man(bot, args):
    if len(args) == 2:
        if len(args[1]) < 15:
            url = "http://unixhelp.ed.ac.uk/CGI/man-cgi?%s" % args[1]
            result = urllib2.urlopen(url, timeout = 5)
            if len(result.read(401)) > 400:
                answer(bot, "Linux man page for %s: %s" % (args[1], url))
            else:
                answer(bot, "No man page for '%s' found." % args[1])
        else:
            answer(bot, "That's probably bs.")
    else:
        give_help(bot, args[0], "<binary file>")

register(man, "common", "man")