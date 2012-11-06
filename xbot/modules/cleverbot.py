import util
from pubsub import pub

import re
import urllib
import urllib2
import hashlib
import HTMLParser
from interruptingcow import timeout

class CleverBot(object):

    def __init__(self):
        self.params = {
            'start': 'y', 'icognoid': 'wsf', 'fno': '0', 'sub': 'Say', 'islearning': '1', 'cleanslate': 'false'
        }
        self.vars = [
            'sessionid', 'logurl', 'vText8', 'vText7', 'vText6', 'vText5', 'vText4', 'vText3', 'vText2', 'prevref',
            'asbotname', 'emotionaloutput', 'ttsLocMP3', 'ttsLocTXT', 'ttsLocTXT3', 'ttsText', 'lineRef', 'lineURL',
            'linePOST', 'lineChoices', 'lineChoicesAbbrev', 'typingData', 'divert'
        ]
    
    def query(self, bot, thought):
        if bot.remote['nick'].lower() in bot.inv['banned']:
            return None
        
        if thought == "help":
            return "Use %shelp" % bot.prefix
        
        self.params['stimulus'] = thought
        data = urllib.urlencode(self.params)
        data += '&icognocheck=' + hashlib.md5(data[9:29]).hexdigest()
        
        try:
            with timeout(25, exception=RuntimeError):
                responses = urllib2.urlopen("http://cleverbot.com/webservicemin", data, timeout = 30).read().split('\r')
        except RuntimeError:
            return "Sorry, I'm a bit slow".encode('utf8')
        
        for n in range(len(responses)):
            try: self.params[self.vars[n]] = responses[n+1]
            except IndexError: pass
        
        h = HTMLParser.HTMLParser()
        return h.unescape(self.params['ttsText']).encode('utf8')


def clever_scan(bot):
    # someone is talking to the bot
    if re.search('^%s(?:\:|,)' % re.escape(bot.nick.lower()), bot.remote['message'].lower()):
        if 'cleverbot' not in bot.inv: bot.inv['cleverbot'] = {}
        if bot.remote['receiver'] not in bot.inv['cleverbot']:
            bot.inv['cleverbot'][bot.remote['receiver']] = CleverBot()
        query = bot.remote['message'][len(bot.nick)+2:].decode('ascii', 'ignore')
        util.answer(bot, "%s: %s" % (bot.remote['nick'], re.compile('cleverbot', re.IGNORECASE).sub(bot.nick, bot.inv['cleverbot'][bot.remote['receiver']].query(bot, query))))
        #bot._sendq(("NOTICE", bot.remote['nick']), "This feature has been disabled.")

pub.subscribe(clever_scan, 'scanner')


def clever_reset(bot, args):
    if 'cleverbot' in bot.inv and bot.remote['receiver'] in bot.inv['cleverbot']:
        del bot.inv['cleverbot'][bot.remote['receiver']]
    util.answer(bot, "Success: %s's cleverbot reset." % bot.remote['receiver'])

util.register(clever_reset, "reset", "cleverbot")