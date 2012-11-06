from util import *
import github
from github import Github
import datetime
import json
import js
import os
import re

def gh_inst(bot, args):
    if not bot.config.has_option('module: github', 'github_auth'):
        return "%s%s: Not configured." % (bot.prefix, args[0])
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
        return "%s%s: Authentication error."  % (bot.prefix, args[0])

def jslib(bot, args):
    if not bot.config.has_option('module: github', 'jslib_gist'):
        return "%s%s: Not configured." % (bot.prefix, args[0])
    
    gh = gh_inst(bot, args)
    if isinstance(gh, basestring):
        return gh
    gi = gh.get_gist(bot.config.get('module: github', 'jslib_gist'))
    
    if len(args) > 1:
        if args[1] == "propose" and len(args) == 3:
            result = js.execute(bot, ["js", args[2]])
            date = datetime.datetime.now().strftime("%b %d %Y %H:%M:%S")
            result = "// Proposed by %s @ %s\n\n%s" % (bot.remote['nick'], date, result)
            
            gi.edit(gi.description, {args[2]: github.InputFileContent(result)})
            return "https://gist.github.com/%s#file_%s" % (gi.id.encode('utf8'), args[2])
        
        if args[1] == "list":
            l = []
            for j in os.listdir(os.path.join(os.path.dirname(__file__), "js")):
                if not re.match(".+\.js$", j):
                    continue
                l.append(j.replace(".js",''))
            
            return ', '.join(l)
        
        if args[1] == "future":
            return "Gist: %s\nProposed: %s" % ("https://gist.github.com/%s" % bot.config.get('module: github', 'jslib_gist'),
                    ', '.join(gi.files).encode('utf8'))
    
    return give_help(bot, args[0], "(propose|list|future) [proposed-func-name]")