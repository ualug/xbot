import util
from pubsub import pub

import re
import time
import random

def scan(bot, message = None):
    if message:
        bot.remote['message'] = message
    
    pub.sendMessage('scanner', bot=bot)


def oooo_scan(bot):
    # per 10% chance, count uppercase and act shocked
    if len(bot.remote['message']) > 2 and random.random() > 0.9:
        if count_upper(bot.remote['message']) > 80:
            time.sleep(4)
            util.answer(bot, random.choice([':' + 'O' * random.randint(1, 10), 'O' * random.randint(1, 10) + ':']))

pub.subscribe(oooo_scan, 'scanner')

def butt_scan(bot):
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
            
                util.answer(bot, ' '.join(words))

pub.subscribe(butt_scan, 'scanner')


def count_upper(str):
    n = s = 0
    for c in str:
        z = ord(c)
        if (z >= 65 and z <= 90) or z == 33:
            n += 1
        if z == 32:
            s += 1

    return float(n) / (len(str)-s) * 100
