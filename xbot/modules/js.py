'''
from util import *
from pyv8 import PyV8
from interruptingcow import timeout
import jsbeautifier
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
            'prefix':   bot.prefix,
            'caller':   bot.remote['nick']
        })
        
        if args[1] == "pretty:":
            rawcmd = args[2:]
        else:
            rawcmd = args[1:]
        rawcmd = ' '.join(rawcmd)
        
        command = "((function(){try {\n"
        if args[0] == "js":
            command += "return %s" % rawcmd
        elif args[0] == "cs":
            command += "return CoffeeScript.eval('%s')" % rawcmd
        elif args[0] == "ts":
            command += "return TypeScript.eval('%s')" % rawcmd
        command += "\n} catch (e) { return e.toString(); } }(this)) || '').toString()"
        
        bot._debug(command)
        #bot.inv['js'].add_global('hashlib', __import__('hashlib'))
        
        bot._debug('Entering JS context...')
        bot.inv['js'].enter()
        
        try:
            bot.inv['js'].eval("this.bot = %s" % botenv)
            with timeout(10, exception=RuntimeError):
                bot._debug('Running command...')
                result = bot.inv['js'].eval(command)
        except RuntimeError:
            bot._debug('Timeout.')
            return "Took too long, nigga."
        except PyV8.JSError as e:
            bot._debug('JS error.')
            result = str(e)
        bot._debug('Ran fine.')
        
        bot._debug('Leaving JS context...')
        bot.inv['js'].leave()
        
        if result is not None:
            bot._debug('Command has result.')
            bot._debug('Converting to str...')
            result = str(result)
            bot._debug('Encoding to UTF-8...')
            result = unicode(result).encode('utf8')
            
            if re.search("^JSError:", result):
                bot._debug('Post-processing error message.')
                result = re.sub("^JSError:\\s", '', result)
                result = re.sub("\\s[(]\\s+@.+$", '', result)
            
            
            if args[1] == "pretty:":
                result = jsbeautifier.beautify(re.sub("^pretty:", '', result))
            
            if len(result.split('\n')) > 4 or len(result) > 200:
                bot._debug('Going to upload to sprunge...')
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
                bot._debug('Returning locally...')
                return result
        else:
            bot._debug('Nothing to return.')
            return None
    if args[0] == "js":
        return give_help(bot, args[0], "<js_expr>")
    elif args[0] == "cs":
        return give_help(bot, args[0], "<coffee_expr>")
    elif args[0] == "ts":
        return give_help(bot, args[0], "<typescript_expr>")

def js_reset(bot):
    bot._debug('Destroying JS context...')
    del bot.inv['js']
    return "Success: Javascript context reset."
'''