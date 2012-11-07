import util
from pubsub import pub

import datetime

def time(bot, args):
    if len(args) == 1:
        now = datetime.datetime.now()
        hour = int(now.strftime("%H"))
        bedtime = " (bedtime)" if hour >= 0 and hour <= 7 else ''
        util.answer(bot, "It is now %s%s on %s NZT." % (now.strftime("%I:%M%p"), bedtime, now.strftime("%A, %d %B %Y")))
    else:
        util.give_help(bot, args[0], "")

util.register(time, "common", "time", "time")