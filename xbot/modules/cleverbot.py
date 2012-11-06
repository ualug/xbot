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