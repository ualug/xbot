import util
import sys
import urllib
import urllib2
import cookielib
import lxml.html
import re

def usage(bot, args):
    if len(args) == 1:
        result = ""
        
        if not re.match("(off|false|disabled|n)", bot.config.get('module: usage', 'two_degrees')):
            session = cookielib.CookieJar()
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(session))
            opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:11.0) Gecko/20100101 Firefox/11.0')]
            
            form = lxml.html.fromstring(opener.open('https://secure.2degreesmobile.co.nz/web/ip/login').read()).xpath("//form[@name='loginFrm']")
            
            if not form:
                result += "2degrees: Error, cannot find login form."
            else:
                account = opener.open(form[0].get('action'), urllib.urlencode(
                    {
                        'userid': bot.config.get('module: usage', 'td_login'),
                        'password': bot.config.get('module: usage', 'td_pass'),
                        'hdnAction': 'login',
                        'hdnAuthenticationType': 'M'
                    }
                )).read()
                remaining = lxml.html.fromstring(account).xpath("//td[@class='tableBillamount']/text()")
                
                if not remaining:
                    result += "2degrees: Error, cannot get remaining data.\n"
                else:
                    result += "3G: %s remaining\n" % ', '.join(remaining).encode('utf-8')
        
        
        if not re.match("(off|false|disabled|n)", bot.config.get('module: usage', 'orcon')):
            orcon = lxml.html.fromstring(opener.open('http://www.orcon.net.nz/modules/usagemeter/view/CosmosController.php').read()).xpath('//dd[last()]/text()')
            if not orcon:
                result += "Orcon: Error, cannot fetch details."
            else:
                result += "ADSL: %s used" % orcon[0].encode('utf-8')
        
        if len(result) > 0:
            util.answer(bot, result)
        else:
            util.answer(bot, "%s%s: Not configured." % (bot.prefix, args[0]))
    else:
        util.give_help(bot, args[0], "")

util.register(usage, "common", "usage")