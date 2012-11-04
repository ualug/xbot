from util import *
import datetime
import peewee
from botdb import *
import re

def get_quote(bot, args):

    db = BotDB(bot).connect()
    
    def gen_kw(keywords):
        result = ""
        for keyword in keywords:
            result += (" AND message LIKE '%%%s%%'" % re.escape(keyword)).replace("%", "%%")
        return result
        
        
    if len(args) > 1:
    
        channel = bot.remote['receiver']
        nick = bot.remote['nick']
        
        if args[1].lower() != bot.nick.lower():
            if len(args) == 2:
                if args[1] != "*":
                    quotes = Quote.select().where(Quote.channel == channel, Quote.nick ** ("%%%s%%" % args[1]))
                    
                    if quotes.count() > 0:
                        return output_quote(bot, quotes)
                    else:
                        return "No quotes from %s found." % args[1]
                else:
                    quotes = Quote.select().where(Quote.channel == channel, Quote.nick != re.escape(bot.nick))
                    
                    if quotes.count() > 0:
                        return output_quote(bot, quotes)
                    else:
                        return "No quotes in database yet."
                        
            elif len(args) >= 3:
                search = ' '.join(args[2:])
                if args[1] != "*":
                    if search.startswith("/") and search.endswith("/"):
                        return "No regexp for you."
                        #type = "regexp"
                        #sql = "SELECT * FROM quotes WHERE channel = ? AND nick REGEXP ? AND message REGEXP ?"
                        #quotes = peewee.RawQuery(botdb.Quote, sql, channel, args[1], search[1:-1])
                    else:
                        type = "keywords"
                        quotes = Quote.select().where(Quote.channel == channel, Quote.nick ** "%"+args[1]+"%", Quote.message ** ("%%%s%%" % search[1:-1]))
                else:
                    if search.startswith("/") and search.endswith("/"):
                        return "No regexp for you."
                        #type = "regexp"
                        #sql = "SELECT * FROM quotes WHERE channel = ? AND nick != ? AND message REGEXP ?"
                        #quotes = peewee.RawQuery(botdb.Quote, sql, channel, re.escape(bot.nick), search[1:-1])
                    else:
                        type = "keywords"
                        quotes = Quote.select().where(Quote.channel == channel, Quote.nick != re.escape(bot.nick), Quote.message ** ("%%%s%%" % search[1:-1]))
                
                num = quotes.count()
                if num > 0 and num <= 15:
                    if num > 1:
                        bot._sendq(("PRIVMSG", channel), '%s result%s sent.' % (num, '' if num == 1 else 's'))
                    return output_quote(bot, quotes)
                elif num > 15:
                    if type == "keywords":
                        return "%d quotes found." % num
                    elif type == "regexp":
                        return "%d quotes matched." % num
                else:
                    if type == "keywords":
                        return "No quotes with keywords |%s| found." % search
                    elif type == "regexp":
                        return "No quotes with regexp %s matched." % search
        else:
            return "Nah. My own quotes are too contaminated."
    else:
        return give_help(bot, args[0], "<nick|*> [<keywords|/regexp/>]")

def output_quote(bot, quotes):
    import scanner
    from random import choice
    
    ids = []
    for q in quotes.naive():
        ids.append(q.id)
    quote = Quote.get(Quote.id == choice(ids))

    fmt = "%s | "
    if quote.action:
        fmt += "* %s"
    else:
        fmt += "<%s>"
    fmt += " %s"
    
    output = fmt % (str(datetime.datetime.fromtimestamp(int(quote.time))), quote.nick, quote.message)
    output = output.encode('utf8')
    result = scanner.scan(bot, output) or ''
    
    return '\n'.join([output, result])