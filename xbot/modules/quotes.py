from util import *
from botdb import *
from random import choice
import datetime
import peewee
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
        
        if not args[1].lower() in bot.nick.lower():
            if len(args) == 2:
                if args[1] != "*":
                    quotes = Quote.select().where(Quote.channel == channel, Quote.nick ** ("%%%s%%" % args[1]))
                    
                    if quotes.count() > 0:
                        answer(bot, output_quote(bot, quotes))
                    else:
                        answer(bot, "No quotes from %s found." % args[1])
                else:
                    quotes = Quote.select().where(Quote.channel == channel, Quote.nick != re.escape(bot.nick))
                    
                    if quotes.count() > 0:
                        answer(bot, output_quote(bot, quotes))
                    else:
                        answer(bot, "No quotes in database yet.")
                        
            elif len(args) >= 3:
                search = ' '.join(args[2:])
                if args[1] != "*":
                    if search.startswith("/") and search.endswith("/"):
                        type = "regexp"
                        quotes = Quote.select().where(Quote.channel == channel, Quote.nick ** ("%%%s%%" % args[1]))
                        regexp = search[1:-1]
                    else:
                        type = "keywords"
                        quotes = Quote.select().where(Quote.channel == channel, Quote.nick ** ("%%%s%%" % args[1]), Quote.message ** ("%%%s%%" % search[1:-1]))
                else:
                    if search.startswith("/") and search.endswith("/"):
                        type = "regexp"
                        quotes = Quote.select().where(Quote.channel == channel, Quote.nick != re.escape(bot.nick))
                        regexp = search[1:-1]
                    else:
                        type = "keywords"
                        quotes = Quote.select().where(Quote.channel == channel, Quote.nick != re.escape(bot.nick), Quote.message ** ("%%%s%%" % search[1:-1]))
                
                if type == "regexp":
                    answer(bot, output_quote(bot, quotes, regexp))
                else:
                    answer(bot, output_quote(bot, quotes))
        else:
            answer(bot, "Nah. My own quotes are too contaminated.")
    else:
        give_help(bot, args[0], "<nick|*> [<keywords|/regexp/>]")

register(get_quote, "common", "quotes")

def output_quote(bot, quotes, regexp =  False):
    import scanner
    
    ids = []
    if regexp != False:
        regexp = re.compile(regexp, re.L | re.M | re.U)
    for q in quotes.naive():
        if regexp != False and regexp.search(q.message) == None:
            continue
        ids.append(q.id)
    
    if len(ids) == 0:
        return "No matching quotes were found."
        
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