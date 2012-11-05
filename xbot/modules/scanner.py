import re
import time
import random
import cleverbot

def scan(bot, message = None):
    results = []
    
    if message:
        bot.remote['message'] = message
        
    message_lowercase = bot.remote['message'].lower()
    
    # scan for youtube links and show title
    for code in re.findall('(?:youtube\.com\/watch\?|youtu\.be/)(?:[A-Za-z0-9-_\.&%#=]*v=)?([A-Za-z0-9-_]+)', bot.remote['message']):
        results.append(youtube_title(code))
    
    # someone is talking to the bot
    if re.search('^%s(?:\:|,)' % re.escape(bot.nick.lower()), message_lowercase):
        if 'cleverbot' not in bot.inv: bot.inv['cleverbot'] = {}
        if bot.remote['receiver'] not in bot.inv['cleverbot']:
            bot.inv['cleverbot'][bot.remote['receiver']] = cleverbot.CleverBot()
        query = bot.remote['message'][len(bot.nick)+2:].decode('ascii', 'ignore')
        results.append("%s: %s" % (bot.remote['nick'], re.compile('cleverbot', re.IGNORECASE).sub(bot.nick, bot.inv['cleverbot'][bot.remote['receiver']].query(bot, query))))
        #bot._sendq(("NOTICE", bot.remote['nick']), "This feature has been disabled.")
    
    # per 10% chance, count uppercase and act shocked
    if len(bot.remote['message']) > 2 and random.random() > 0.9:
        if count_upper(bot.remote['message']) > 80:
            time.sleep(4)
            results.append(random.choice([':' + 'O' * random.randint(1, 10), 'O' * random.randint(1, 10) + ':']))
    
    # per 1% chance, butt into someone's conversation
    if random.random() > 0.99:
        if not bot.remote['message'].startswith("\x01"):
            words = bot.remote['message'].split()
            if len(words) > 2:
                for n in range(random.randint(1, 3)):
                    if random.random() > 0.5:
                        words[random.randint(1, len(words)-1)] = "butt"
                    else:
                        for m, word in enumerate(words):
                            if len(word) > 4 and m > 0:
                                if random.random() > 0.3:
                                    words[m] = words[m][:-4] + "butt"
            
                results.append(' '.join(words))
    
    results = [result for result in results if result is not None]
    try: return '\n'.join(results)
    except TypeError: return None

def youtube_title(code):
    import urllib2, simplejson

    try:
        # try with embed json data (fast)
        title = simplejson.load(urllib2.urlopen('http://www.youtube.com/oembed?url=http%%3A//www.youtube.com/watch?v%%3D%s&amp;format=json' % code, timeout = 5))['title']
    except simplejson.JSONDecodeError:
        # json data didn't return a title? forget about it
        title = None
    except urllib2.HTTPError as error:
        # embed request not allowed? fallback to HTML (slower)
        if error.code == 401:
            import lxml.html
            title = lxml.html.document_fromstring(urllib2.urlopen('http://www.youtube.com/watch?v=%s' % code, timeout = 5).read().decode('utf-8')).xpath("//title/text()")[0].split("\n")[1].strip()
        else:
            title = None
            if error.code != 404:
                raise
    
    if title:
        if title != "YouTube - Broadcast Yourself.":
            return "YouTube: \x02%s\x02" % title.encode('utf-8')
            
    return None

def count_upper(str):
    n = s = 0
    for c in str:
        z = ord(c)
        if (z >= 65 and z <= 90) or z == 33:
            n += 1
        if z == 32:
            s += 1

    return float(n) / (len(str)-s) * 100
