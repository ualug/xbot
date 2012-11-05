import os
import time
import datetime
import botdb

def log(bot, channel, nick, message):
    if re.search("\\xe2", message):
        message = re.sub("\\x02", '', message.decode('utf8')).encode('utf8')
    
    date = datetime.datetime.now().strftime("%b %d %Y %H:%M:%S")
    file = open('%s.txt' % channel, 'a+')
    if message.startswith("\x01ACTION"):
        file.write("%s * %s %s\r\n" % (date, nick, message[8:-1]))
        action = 1
    else:
        for line in message.split("\n"):
            if line:
                file.write("%s <%s> %s\r\n" % (date, nick, line))
        action = 0
        
    file.close()
    
    db = botdb.BotDB(bot).connect()
    
    if not message.startswith("!quote"):
        if action:
            message = message[8:-1]
        
        q = botdb.Quote()
        q.time = int(time.time())
        q.channel = channel
        q.nick = nick
        q.action = action == 1
        q.message = message
        q.save()