from util import *
import urllib, urllib2
import json

def info(bot, args):
    if len(args) > 1:
        title = ' '.join(args[1:])
        data = json.load(urllib2.urlopen('http://www.imdbapi.com/?%s' % urllib.urlencode({'t': title}), timeout = 45))
        if 'Plot' in data:
            response = "%s (%s): %s\n%s, %s/10, %s. %s" % (data['Title'], data['Year'], data['Plot'],
                                                            data['Rated'] if data['Rated'] != 'N/A' else 'Unrated',
                                                            data['imdbRating'] if data['imdbRating'] != 'N/A' else '?',
                                                            data['Genre'], 'http://www.imdb.com/title/%s/' % data['imdbID'])
            return response.encode('utf-8')
        else:
            return '%s%s: No such movie found.' % (bot.prefix, args[0])
    else:
        return give_help(bot, args[0], "<movie title>")