from util import *
from pyv8 import PyV8
from interruptingcow import timeout
import subprocess
import json
import re
import os


def execute(bot, args):
    if len(args) > 1:
        if 'js' not in bot.inv:
            bot.inv['js'] = PyV8.JSContext()
            
            bot.inv['js'].enter()
            for j in os.listdir(os.path.join(os.path.dirname(__file__), "js")):
                if not re.match(".+\.js$", j):
                    continue
                f = open(os.path.join(os.path.dirname(__file__), "js", j), 'r')
                bot.inv['js'].eval(f.read())
            bot.inv['js'].leave()
        
        botenv = json.dumps({
            'version':  bot.version,
            'users':    bot.inv['rooms'].get(bot.remote['receiver']),
            'rooms':    bot.inv['rooms'].keys(),
            'prefix':   bot.prefix
        })
        
        if args[0] == "js":
            command = "(function(){return %s}(this))" % ' '.join(args[1:])
        elif args[0] == "cs":
            command = "CoffeeScript.eval('%s')" % ' '.join(args[1:])
        
        #bot.inv['js'].add_global('hashlib', __import__('hashlib'))
        
        
        bot.inv['js'].enter()
        
        try:
            bot.inv['js'].eval("this.bot = %s" % botenv)
            with timeout(10, exception=RuntimeError):
                result = bot.inv['js'].eval(command)
        except RuntimeError:
            return "Took too long, nigga."
        except PyV8.JSError as e:
            result = str(e)
        
        bot.inv['js'].leave()
        
        if result is not None:
            result = unicode(result).encode('utf8')
            if len(result.split('\n')) > 4 or len(result) > 445:
                service = ['curl', '-F', 'sprunge=<-', 'http://sprunge.us']
                for n in range(2):
                    p = subprocess.Popen(service, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                    paste = p.communicate(input=">>> %s\n\n%s" % (command, result))[0]
                    try:
                        return "%s?js" % re.findall('(http://.*)', paste, re.S)[0].strip()
                    except IndexError:
                        pass
                return "!%s: error pasting output." % args[0]
            else:    
                return result
        else:
            return None
    if args[0] == "js":
        return give_help(bot, args[0], "<js_expr>|//reset")
    elif args[0] == "cs":
        return give_help(bot, args[0], "<coffee_expr>")

def js_reset(bot):
    del bot.inv['js']
    return "Success: Javascript context reset."