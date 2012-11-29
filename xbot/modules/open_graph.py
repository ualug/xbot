import util
from pubsub import pub

import re
import opengraph
import lxml.html
import urllib2

class HeadRequest(urllib2.Request):
    def get_method(self):
        return "HEAD"

def open_graph(bot, url):
    if url[1] == 'www.':
        url = 'http://%s' % url[0]
    
    if re.search("sprunge\.us", url):
        return None
    
    bot._debug('Sending HEAD request...')
    response = urllib2.urlopen(HeadRequest(url), timeout = 2)
    conttype = response.info().getheader('Content-Type')
    bot._debug("Content-type: %s" % conttype.encode('utf8'))
    if not re.search("html", conttype):
        bot._debug('Abort OpenGraph scan.')
        return None
    
    bot._debug('Fetching OpenGraph data...')
    try:
        og = opengraph.OpenGraph(url=url)
    except:
        og = False
    
    if og and og.is_valid() and 'title' in og:
        bot._debug('Found some metadata.')
        
        if 'site_name' in og:
            return "%s: \x02%s\x02" % (og['site_name'], og['title'])
        else:
            return "\x02%s\x02" % og['title']
    else:
        bot._debug('Fall back to plain HTML.')
        title = ""
        try:
            bot._debug('Fetching document title...')
            title = lxml.html.document_fromstring(urllib2.urlopen(url, timeout = 5).read()).xpath("//title/text()")[0]
            title = re.sub("[^a-zA-Z0-9\\.\-\|\s\\\\\\/!@#\$%|^&*(){}\[\]_+=<>,\?'\":;\~\`]", '', title).encode('utf8')
            title = title.strip()
        except:
            return None
        if title == "Google":
            bot._debug('This looks like google.')
            return "That's Google, why not search with !go <keywords>?"
        else:
            return "\x02%s\x02" % title
    return None

def og_scan(bot):
    # scan for urls, check to see if OpenGraph validity and return site name and page title.
    # if OpenGraph not found, tries <title> tag.
    for url in re.findall('(?P<url>(https?://|www.)[^\s]+)', bot.remote['message']):
        bot._debug("Found a URL: %s" % url[0])
        try:
            util.answer(bot, open_graph(bot, url[0]).encode('utf8'))
        except AttributeError:
            pass
        except ValueError:
            pass

pub.subscribe(og_scan, 'scanner')
