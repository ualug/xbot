from pubsub import pub

def answer(bot, message):
    pub.sendMessage('reply', nick=bot.remote['sendee'], message=message)

def register(func, cat, name, cmd):
    pub.subscribe(func, "func.%s.%s" % (cat, cmd))
    pub.sendMessage('register', cat=cat, name=name, func=cmd)

def give_help(bot, cmd, text):
    answer(bot, "Usage: %s%s %s" % (bot.prefix, cmd, text))