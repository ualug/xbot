from util import *
from pubsub import pub

library = {
    'admin': [],
    'common': []
}

def update(lib):
    global library
    library = lib

pub.subscribe(update, 'library')


def show_help(bot, args):
    can_do = bot.remote['host'] in [host.strip() for host in bot.config.get(bot.network, 'admin_hostnames').split(',')]
    can_do = can_do or bot.remote['nick'] in [nick.strip() for nick in bot.config.get(bot.network, 'admin').split(',')]
    bot._debug(','.join(library['admin']))
    if can_do:
        coms = library['admin'] + library['common']
    else:
        coms = library['common']
    
    answer(bot, "Available commands: %s" % ', '.join(sorted(coms)))

register(show_help, "common", "help", "help")