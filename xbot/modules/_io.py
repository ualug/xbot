from util import *
from pubsub import pub
import datetime
import scanner
import re

library = {
    'admin': {},
    'common': {},
    'reset': {},
}

Bot = ""

def debug(msg):
    if Bot != "":
        Bot._debug(msg)
    else:
        print msg

def read(bot):
    global Bot
    Bot = bot
    
    if bot.remote['nick'] and bot.remote['nick'] != bot.nick:
        if bot.remote['message'].startswith(bot.prefix):
            bot._debug("Command received: %s" % bot.remote['message'])
            args = bot.remote['message'][1:].rstrip().split(" ")
            command = args[0].lower()
            
            if bot.remote['nick'].lower() not in bot.inv['banned']:
                if command in library['admin']:
                    bot._debug('This is an admin-only command.')
                    can_do = bot.remote['host'] in [host.strip() for host in bot.config.get(bot.network, 'admin_hostnames').split(',')]
                    can_do = can_do or bot.remote['nick'] in [nick.strip() for nick in bot.config.get(bot.network, 'admin').split(',')]
                    if can_do:
                        bot.previous['user'] = bot.remote['sendee']
                        pub.sendMessage("func.admin.%s" % library['admin'][command], bot=bot, args=args)
                    else:
                        if bot.voice:
                            reply(bot.remote['sendee'], "%s: Can't do that, noob." % bot.remote['nick'])
                elif bot.voice and command in library['common']:
                    bot._debug('This is a common command.')
                    pub.sendMessage("func.common.%s" % library['common'][command], bot=bot, args=args)
                    bot.previous['user'] = bot.remote['sendee']
        
        elif bot.remote['message'].startswith("\x01") and bot.remote['message'].endswith("\x01"):
            type = bot.remote['message'][1:-1].split()[0]
            args = bot.remote['message'][1:-1].split()[1:]
            if type != "ACTION":
                ctcp(type, args)
        
        elif bot.remote['mid'] == "INVITE" and bot.remote['nick'].lower() not in bot.inv['banned']:
            join([bot.remote['mid'], bot.remote['message']])
        
        else:
            if bot.init['registered'] and not bot.init['identified']:
                if bot.remote['nick'] == "NickServ":
                    if "registered" in bot.remote['message']:
                        bot._login()
                    elif "identified" in bot.remote['message']:
                        bot.init['identified'] = True
                        __import__('time').sleep(3)
                        autojoin()
            
            if bot.voice:
                #start scanning messages for certain data
                try: scanner.scan(bot)
                except (__import__('urllib2').URLError, __import__('socket').timeout): answer(bot, "fetch: response timeout exceeded.")

    else:
        if (bot.remote['mid'].startswith("4") or bot.remote['mid'].startswith("5")) and bot.remote['mid'] != "462":
            reply(bot.previous['user'], "Message from %s: Error #%s: %s" % (bot.remote['server'], bot.remote['mid'], bot.remote['message']))
        if not bot.init['joined'] and not bot.init['registered']:
            autojoin()

def lib_register(cat, name, func):
    global library
    library[cat][name] = func
    debug("Register %s command: %s" % (cat, name))
    lib = {}
    for k in library:
        lib[k] = library[k].keys()
    pub.sendMessage("library", lib=lib)

def lib_deregister(cat, name):
    del library[cat][name]
    debug("De-register %s command: %s" % (cat, name))
    lib = {}
    for k in library:
        lib[k] = library[k].keys()
    pub.sendMessage("library", lib=lib)

pub.subscribe(lib_register, 'register')
pub.subscribe(lib_deregister, 'deregister')

def reset(bot, args):
    if len(args) > 1:
        if args[1] in library['reset']:
            pub.sendMessage("func.reset.%s" % library['reset'][args[1]], bot=bot, args=args[2:])
            return None
    
    if len(library['reset']) > 0:
        give_help(bot, args[0], '|'.join(library['reset']))
    else:
        answer(bot, "No resets registered.")

register(reset, "admin", "reset", "reset")

def autojoin():
    channels = Bot.config.get(Bot.network, 'channels').split(",")
    for channel in channels:
        join(Bot, [None, channel.strip()])
    Bot.init['joined'] = True

def ctcp(type, args):
    if type == "VERSION":
        write(("NOTICE", Bot.remote['nick']), "\x01VERSION %s:%s:%s\x01" % (Bot.name, str(Bot.version), Bot.env))
    elif type == "PING":
        write(("NOTICE", Bot.remote['nick']), "\x01PING %s\x01" % args[0])
        
def write(args, message = None):
    Bot._sendq(args, message)

def reply(nick, message):
    write(("PRIVMSG", nick), message)

pub.subscribe(reply, 'reply')


def voice(bot, args):
    args = [arg.lower() for arg in args]
    if len(args) == 2:
        if args[1] == "off":
            write(("PRIVMSG", Bot.remote['sendee']), "\x01ACTION stays quiet.\x01")
            Bot.voice = False
            return None
        elif args[1] == "on":
            write(("PRIVMSG", Bot.remote['sendee']), "\x01ACTION resumes normal operation.\x01")
            Bot.voice = True
            return None
    
    give_help(bot, args[0], "on|off")

register(voice, "admin", "voice", "voice")

def cnick(bot, args):
    if len(args) == 2:
        write(("NICK", args[1]))
        Bot.nick = args[1]
    else:
        give_help(bot, args[0], "<new-nick>")

register(cnick, "admin", "nick", "change_nick")

def release(bot, args):
    if len(args) == 1:
        write(("PRIVMSG", "NickServ"), "RELEASE %s %s" % (Bot.name, Bot.config.get(Bot.network, 'password')))
        write(("PRIVMSG", Bot.remote['sendee']), "Nick released.")

register(release, "admin", "release", "release")

def ident():
    Bot._ident(Bot.name)
    Bot._login()

register(ident, "admin", "identify", "ident")

def join(bot, args):
    if len(args) == 2:
        if args[1] not in Bot.inv['rooms']:
            write(("JOIN", args[1]))
        else:
            answer(bot, "I'm already in that channel, noob.")
    else:
        give_help(bot, args[0], "<channel>")

register(join, "admin", "join", "join")

def part(bot, args):
    if len(args) == 1:
        channel = Bot.remote['sendee']
    elif len(args) == 2:
        channel = args[1]
    else:
        give_help(bot, args[0], "[channel]")
        return None
    
    if channel in Bot.inv['rooms']:
        write(("PART", channel))
    else:
        answer("I'm not in that channel, noob.")

register(part, "admin", "part", "part")

def kick(bot, args):
    if len(args) >= 2:
        if args[1].lower() == Bot.nick.lower():
            reply(Bot.remote['sendee'], ":(")
        else:
            if Bot.inv['rooms'][Bot.remote['receiver']][Bot.nick]['mode'] == "o":
                write(("KICK", Bot.remote['sendee'], args[1]), ' '.join(args[2:]))
            else:
                answer("No ops lol.")
    else:
        give_help(bot, args[0], "<nick>")

register(kick, "admin", "kick", "kick")

def topic(bot, args):
    if len(args) >= 2:
        topic = ' '.join(args[1:])
        if Bot.remote['sendee'] == "#ualug":
            if len(topic) <= 250:
                write(("TOPIC", Bot.remote['sendee']), 'UALUG: %s [/%s] | UALUG website: http://ualug.ece.auckland.ac.nz/' % (topic, Bot.remote['nick']))
            else:
                reply(Bot.remote['sendee'], "Sorry %s that topic is too long." % Bot.remote['nick'])
        else:
            write(("TOPIC", Bot.remote['sendee']), ' '.join(args[1:]))
    else:
        give_help(bot, args[0], "<topic>")

register(topic, "common", "topic", "topic")

def mode(bot, args):
    if len(args) >= 2:
        write(("MODE", Bot.remote['sendee']), ' '.join(args[1:]))
    else:
        give_help(bot, args[0], "<mode>")

register(topic, "admin", "mode", "mode")

def perms(bot, args):
    if len(args) == 3:
        user = args[2].lower()
        if args[1] == "deny":
            if user not in Bot.inv['banned']:
                Bot.inv['banned'].append(user)
            else:
                reply(Bot.remote['sendee'], "User already denied.")
        elif args[1] == "allow":
            if user in Bot.inv['banned']:
                Bot.inv['banned'].remove(user)
            else:
                reply(Bot.remote['sendee'], "User wasn't denied to start with.")
    else:
        give_help(bot, args[0], "allow|deny <nick>")

register(perms, "admin", "perms", "perms")

def list(nick):
    return write(("PRIVMSG", Bot.remote['sendee']), str(Bot.inv['rooms'][Bot.remote['sendee']]))

def say(bot, args):
    if len(args) >= 2:
        if len(args) >= 3:
            if args[1].startswith("#") and not Bot.remote['sendee'].startswith("#"):
                if Bot.inv['rooms'].get(args[1]):
                    if Bot.remote['nick'] in Bot.inv['rooms'][args[1]] or Bot.remote['host'] == 'pdpc/supporter/student/milos':
                        if args[2].startswith("/me"):
                            return write(("PRIVMSG", args[1]), "\x01ACTION %s\x01" % ' '.join(args[3:]))
                        else:
                            return write(("PRIVMSG", args[1]), ' '.join(args[2:]))
                    else:
                        return write(("PRIVMSG", Bot.remote['sendee']), "You're not even in that channel.")
                else:
                    return write(("PRIVMSG", Bot.remote['sendee']), "I'm not even in that channel.")
            else:
                if args[1].startswith("/me"):
                    return write(("PRIVMSG", Bot.remote['sendee']), "\x01ACTION %s\x01" % ' '.join(args[2:]))
        if not args[1].startswith("!"):
            write(("PRIVMSG", Bot.remote['sendee']), ' '.join(args[1:]))
        else:
            write(("PRIVMSG", Bot.remote['sendee']), 'o_O')
    else:
        return give_help(bot, args[0], "[#channel] [/me] <message>")

register(say, "common", "say", "say")

def raw(bot, args):
    if len(args) > 1:
        arguments = ' '.join(args[1:]).split(" :")
        left = arguments[0].split()
        try: message = arguments[1]
        except: message = None
        Bot._sendq(left, message)
    else:
        give_help(bot, args[0], "<raw command>")

register(raw, "admin", "raw", "raw")

def _reload(bot, args):
    bot._reload(args)

register(_reload, "admin", "reload", "reload")

def set_prefix(bot, args):
    if len(args) > 1:
        if not re.match("^[!@#\\$%^&*()\[\]{}\\\\|:;\"'<>.,?~`\\-_=+]$", args[1]):
            return "Invalid prefix."
        old = bot.prefix
        bot.prefix = args[1]
        answer(bot, "Prefix set to %s (was %s)." % (args[1], old))
    else:
        give_help(bot, args[0], "<one of: !@#$%^&*()[]{}\\|:;\"'<>.,?~`-_=+>")

register(set_prefix, "admin", "prefix", "set_prefix")

def set_debug(bot, args):
    result = []
    if len(args) > 2:
        if re.search("(on|yes|true|1)", args[2]):
            bot.verbose = True
            result.append("Verbose logging: on")
        else:
            bot.verbose = False
            result.append("Verbose logging: off")
    if len(args) > 1:
        if re.search("(on|yes|true|1)", args[1]):
            bot.debug = True
            result.append("Debug: on")
        else:
            bot.debug = False
            result.append("Debug: off")
        
        answer(bot, "\n".join(result))
    else:
        give_help(bot, args[0], "on|off [verbose?(on|off)]")

register(set_debug, "admin", "debug", "set_debug")

def admin(bot, args):
    diff = lambda l1,l2: filter(lambda x: x not in l2, l1)
    
    if len(args) > 1:
        admins = [nick.strip() for nick in bot.config.get(bot.network, 'admin').split(',')]
        if args[1] == "list":
            answer(bot, "Admin%s: %s" % ('' if len(admins) == 1 else 's', ', '.join(admins)))
            return None
        if args[1] == "add":
            if len(args) > 2:
                bot._debug("Adding %d admins: %s." % (len(args[2:]), ', '.join(args[2:])))
                admins += args[2:]
                bot.config.set(bot.network, 'admin', ', '.join(admins))
                return None
        if args[1] == "remove":
            if len(args) > 2:
                if bot.admin in args[2:]:
                    answer(bot, "Can't remove root, noob.")
                
                bot._debug("Removing %d admins: %s." % (len(args[2:]), ', '.join(args[2:])))
                admins = diff(admins, args[2:])
                bot.config.set(bot.network, 'admin', ', '.join(admins))
                return None
    
    give_help(bot, args[0], "list|add|remove [nick]")

register(admin, "admin", "admin", "set_admin")


######################################################################
'''

            clibrary = {
                #'topic':        lambda: topic(bot, args),
                #'help':         lambda: show_help(bot, alibrary, clibrary),
                #'time':         lambda: time(bot, args),
                #'say':          lambda: say(bot, args),
                #'calc':         lambda: wolframalpha.wa(bot, args),
                #'go':           lambda: googleapi.search(bot, args),
                #'lookup':       lambda: dnstools.lookup(bot, args),
                #'wiki':         lambda: dnstools.wiki(bot, args),
                #'tell':         lambda: tell.answer(bot, args),
                #'twss':         lambda: fun.twss(bot, args),
                #'cookie':       lambda: fun.cookie(bot, args),
                #'spin':         lambda: fun.spin(bot, args),
                #'man':          lambda: man.man(bot, args),
                #'choose':       lambda: fun.choose(bot, args),
                #'8ball':        lambda: fun.m8b(bot, args),
                #'ghetto':       lambda: fun.ghetto(bot, args),
                #'sortinghat':   lambda: fun.sorting_hat(bot, args),
                #'lotto':        lambda: lotto.get_results(bot, args),
                #'quotes':       lambda: quotes.get_quote(bot, args),
                #'imdb':         lambda: imdb.info(bot, args),
                #'usage':        lambda: usage.usage(bot, args),
                #'maxx':         lambda: maxx.times(bot, args),
                'js':           lambda: js.execute(bot, args),
                'cs':           lambda: js.execute(bot, args),
                'ts':           lambda: js.execute(bot, args),
                'jslib':        lambda: hub.jslib(bot, args)
            }
'''