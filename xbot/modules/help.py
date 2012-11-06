import util
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
    #can_do = can_do or bot.remote['nick'] in [nick.strip() for nick in bot.config.get(bot.network, 'admin').split(',')]
    if can_do:
        if len(args) == 2 and args[1] == "admin":
            coms = library['admin']
        else:
            coms = library['common']
    else:
        coms = library['common']
    
    util.answer(bot, "Available commands: %s" % ', '.join(sorted(coms)))

util.register(show_help, "common", "help", "help")