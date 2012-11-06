import util
from pubsub import pub

import github
from github import Github
import datetime
import json
import os
import re

def gh_inst(bot):
    if not bot.config.has_option('module: github', 'github_auth'):
        return "Github: Not configured."
    try:
        bot._debug('Trying to auth into GitHub...')
        ga = bot.config.get('module: github', 'github_auth')
        if len(ga.split(":")) == 2:
            ga = ga.split(":")
            bot._debug("Password auth: %s,%s" % (ga[0], ga[1]))
            return Github(ga[0], ga[1])
        else:
            bot._debug("Token auth: %s" %ga)
            return Github(ga)
    except:
        return "Github: Authentication error."


def propose(bot, result, options = []):
    if result == False:
        util.answer(bot, "Took too long, nigga.")
    else:
        date = datetime.datetime.now().strftime("%b %d %Y %H:%M:%S")
        result = "// Proposed by %s @ %s\n\n%s" % (options[0], date, result)
        
        gh = gh_inst(bot)
        if isinstance(gh, basestring):
            util.answer(bot, gh)
            return None
        gi = gh.get_gist(bot.config.get('module: github', 'jslib_gist'))
        
        gi.edit(gi.description, {options[1]: github.InputFileContent(result)})
        util.answer(bot, "https://gist.github.com/%s#file_%s" % (gi.id.encode('utf8'), options[1]))

pub.subscribe(propose, 'js.callback.propose')

def jslib(bot, args):
    if not bot.config.has_option('module: github', 'jslib_gist'):
        util.answer(bot, "%s%s: Not configured." % (bot.prefix, args[0]))
        return None
    
    if len(args) > 1:
        if args[1] == "propose" and len(args) == 3:
            pub.sendMessage('js.eval', bot=bot, callback="propose|%s|%s" % (bot.remote['nick'], args[2]), command=args[2], filters=['pretty'])
            return None
            
        elif args[1] == "list":
            l = []
            for j in os.listdir(os.path.join(os.path.dirname(__file__), "js")):
                if not re.match(".+\.js$", j):
                    continue
                l.append(j.replace(".js",''))
            
            util.answer(bot, ', '.join(l))
            return None
            
        elif args[1] == "future":
            gh = gh_inst(bot)
            if isinstance(gh, basestring):
                util.answer(bot, gh)
                return None
            gi = gh.get_gist(bot.config.get('module: github', 'jslib_gist'))
            
            util.answer(bot, "Gist: %s\nProposed: %s" % ("https://gist.github.com/%s" % bot.config.get('module: github', 'jslib_gist'),
                    ', '.join(gi.files).encode('utf8')))
            return None
    else:
        util.give_help(bot, args[0], "(propose|list|future) [proposed-func-name]")

util.register(jslib, "common", "jslib")