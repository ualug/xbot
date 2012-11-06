import util

import urllib2
import json

def search(bot, args):
    if len(args) >= 2:
        title = ""
        
        if args[1].startswith("cr="):
            expr = __import__('re').search('cr=([a-zA-Z]{2})$', args[1])
            if expr:
                country = expr.group(1).upper()
                if country == "CN":
                    util.answer(bot, "google.cn? hah.")
                    return None
            else:
                util.answer(bot, "Invalid country code.")
                return None
            terms = ' '.join(args[2:])
        else:
            country = ""
            terms = ' '.join(args[1:])
        result = urllib2.urlopen("http://ajax.googleapis.com/ajax/services/search/web?v=1.0&safe=off&q=%s&gl=%s" % (urllib2.quote(terms), country), timeout = 5)
        jsondata = json.load(result)
        try:
            url = jsondata['responseData']['results'][0]['unescapedUrl'].encode('utf-8')
            if url.startswith("http://www.youtube.com/"):
                import scanner
                title = "\n" + scanner.scan(bot, url)
            if country:
                util.answer(bot, "From %s only: %s%s" % (country, url, title))
            else:
                util.answer(bot, "%s%s" % (url, title))
        except IndexError:
            util.answer(bot, "Your search did not return any results.")
    else:
        util.give_help(bot, args[0], "[cr=<2-letter country code>] <query>")


util.register(search, "common", "go", "google")