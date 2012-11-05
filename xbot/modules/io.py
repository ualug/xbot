from util import *
import datetime
import scanner

# user modules
import wolframalpha, googleapi, dnstools, tell
import fun, man, quotes, lotto, eval, imdb, usage, maxx, js

def read(bot):
    global Bot
    Bot = bot
    if bot.remote['nick'] and bot.remote['nick'] != bot.nick:
        if bot.remote['message'].startswith(bot.prefix):
            args = bot.remote['message'][1:].rstrip().split(" ")
            command = args[0].lower()
            alibrary = {
                'reload':       lambda: bot._reload(args),
                'voice':        lambda: voice(args),
                'nick':         lambda: cnick(args),
                'release':      lambda: release(args),
                'identify':     lambda: ident(),
                'join':         lambda: join(args),
                'part':         lambda: part(args),
                'kick':         lambda: kick(args),
                'mode':         lambda: mode(args),
                'perms':        lambda: perms(args),
                'eval':         lambda: reply(bot.remote['sendee'], eval.parse(bot, args)),
                'raw':          lambda: raw(args),
                'prefix':       lambda: set_prefix(bot, args),
                'jsreset':      lambda: js.js_reset(bot)
            }
            clibrary = {
                'topic':        lambda: topic(bot, args),
                'help':         lambda: show_help(bot, alibrary, clibrary),
                'time':         lambda: time(bot, args),
                'say':          lambda: say(bot, args),
                'calc':         lambda: wolframalpha.wa(bot, args),
                'go':           lambda: googleapi.search(bot, args),
                'lookup':       lambda: dnstools.lookup(bot, args),
                'wiki':         lambda: dnstools.wiki(bot, args),
                'tell':         lambda: tell.answer(bot, args),
                'twss':         lambda: fun.twss(bot, args),
                'cookie':       lambda: fun.cookie(bot, args),
                'spin':         lambda: fun.spin(bot, args),
                'man':          lambda: man.man(bot, args),
                'choose':       lambda: fun.choose(bot, args),
                '8ball':        lambda: fun.m8b(bot, args),
                'ghetto':       lambda: fun.ghetto(bot, args),
                'sortinghat':   lambda: fun.sorting_hat(bot, args),
                'lotto':        lambda: lotto.get_results(bot, args),
                'quotes':       lambda: quotes.get_quote(bot, args),
                'imdb':         lambda: imdb.info(bot, args),
                'usage':        lambda: usage.usage(bot, args),
                'maxx':         lambda: maxx.times(bot, args),
                'js':           lambda: js.execute(bot, args),
                'cs':           lambda: js.execute(bot, args)
            }
            if bot.remote['nick'].lower() not in bot.inv['banned']:
                if command in alibrary:
                    if bot.remote['host'] in [host.strip() for host in bot.config.get(bot.network, 'admin_hostnames').split(',')]:
                        result = alibrary[command]()
                        bot.previous['user'] = bot.remote['sendee']
                        if result:
                            reply(bot.remote['sendee'], result)
                    else:
                        if bot.voice:
                            reply(bot.remote['sendee'], "%s: Can't do that, noob." % bot.remote['nick'])
                elif bot.voice and command in clibrary:
                    try: result = clibrary[command]()
                    except __import__('urllib2').HTTPError: result = "!%s: derping the herp" % args[0]
                    except (__import__('urllib2').URLError, __import__('socket').timeout): result = "!%s: response timeout exceeded." % args[0]
                    bot.previous['user'] = bot.remote['sendee']
                    if result:
                        reply(bot.remote['sendee'], result)
        elif bot.remote['message'].startswith("\x01") and bot.remote['message'].endswith("\x01"):
            type = bot.remote['message'][1:-1].split()[0]
            args = bot.remote['message'][1:-1].split()[1:]
            if type != "ACTION":
                ctcp(type, args)
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
                # start scanning messages for certain data
                try: response = scanner.scan(bot)
                except (__import__('urllib2').URLError, __import__('socket').timeout): response = "fetch: response timeout exceeded."
                if response:
                    reply(bot.remote['sendee'], response)

    else:
        if (bot.remote['mid'].startswith("4") or bot.remote['mid'].startswith("5")) and bot.remote['mid'] != "462":
            reply(bot.previous['user'], "Message from %s: Error #%s: %s" % (bot.remote['server'], bot.remote['mid'], bot.remote['message']))
        if not bot.init['joined'] and not bot.init['registered']:
            autojoin()

def show_help(bot, a, c):
    if bot.remote['host'] in [host.strip() for host in bot.config.get(bot.network, 'admin_hostnames').split(',')]:
        coms = a.keys() + c.keys()
    else:
        coms = c.keys()
    
    return "Available commands: %s" % ', '.join(sorted(coms))

def autojoin():
    channels = Bot.config.get(Bot.network, 'channels').split(",")
    for channel in channels:
        join([None, channel.strip()])
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

def time(bot, args):
    if len(args) == 1:
        now = datetime.datetime.now()
        hour = int(now.strftime("%H"))
        bedtime = " (bedtime)" if hour >= 0 and hour <= 7 else ''
        return "It is now %s%s on %s NZT." % (now.strftime("%I:%M%p"), bedtime, now.strftime("%A, %d %B %Y"))
    else:
        return give_help(bot, args[0], "")

def voice(args):
    args = [arg.lower() for arg in args]
    if len(args) == 2:
        if args[1] == "off":
            write(("PRIVMSG", Bot.remote['sendee']), "\x01ACTION stays quiet.\x01")
            Bot.voice = False
        elif args[1] == "on":
            write(("PRIVMSG", Bot.remote['sendee']), "\x01ACTION resumes normal operation.\x01")
            Bot.voice = True

def cnick(args):
    if len(args) == 2:
        write(("NICK", args[1]))
        Bot.nick = args[1]

def release(args):
    if len(args) == 1:
        write(("PRIVMSG", "NickServ"), "RELEASE %s %s" % (Bot.name, Bot.config.get(Bot.network, 'password')))
        write(("PRIVMSG", Bot.remote['sendee']), "Nick released.")

def ident():
    Bot._ident(Bot.name)
    Bot._login()

def join(args):
    if len(args) == 2:
        if args[1] not in Bot.inv['rooms']:
            write(("JOIN", args[1]))
        else:
            write(("PRIVMSG", Bot.remote['sendee']), "I'm already in that channel, noob.")
def part(args):
    if len(args) == 1:
        channel = Bot.remote['sendee']
    elif len(args) == 2:
        channel = args[1]
    if channel in Bot.inv['rooms']:
        write(("PART", channel))
    else:
        write(("PRIVMSG", Bot.remote['sendee']), "I'm not in that channel, noob.")
    
def kick(args):
    if len(args) >= 2:
        if args[1].lower() == Bot.nick.lower():
            reply(Bot.remote['sendee'], ":(")
        else:
            if Bot.inv['rooms'][Bot.remote['receiver']][Bot.nick]['mode'] == "o":
                write(("KICK", Bot.remote['sendee'], args[1]), ' '.join(args[2:]))
            else:
                write(("PRIVMSG", Bot.remote['sendee']), "No ops lol.")

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
        reply(Bot.remote['sendee'], "Usage: %s%s <topic>" % (bot.prefix, args[0]))

def mode(args):
    if len(args) >= 2:
        write(("MODE", Bot.remote['sendee']), ' '.join(args[1:]))

def perms(args):
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
        
def raw(args):
    arguments = ' '.join(args[1:]).split(" :")
    left = arguments[0].split()
    try: message = arguments[1]
    except: message = None
    Bot._sendq(left, message)

def set_prefix(bot, args):
    if len(args) > 1:
        bot.prefix = args[1]
    else:
        return give_help(bot, args[0], "<char>")