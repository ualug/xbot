from util import *

def twss(bot, args):
    if len(args) > 1:
        quote = ' '.join(args[1:])
        if quote.startswith('"') and quote.endswith('"'):
            answer(bot, "%s <- that's what she said." % quote)
        else:
            give_help(bot, args[0], "<quote>")
    else:
        answer(bot, "That's what she said.")

register(twss, "common", "twss")

def spin(bot, args):
    nicks = bot.inv['rooms'].get(bot.remote['receiver'])
    if nicks:
        if len(nicks) > 2:
            message = ' '.join(args[1:])
            if not message:
                    message = "nothing"
            if message.lower() != bot.nick.lower():
                _nicks = list(nicks)
                _nicks.remove(bot.remote['nick'])
                _nicks.remove(bot.nick)
                winner = __import__('random').choice(_nicks)
                answer(bot, "The winner of %s is %s. Congratulations %s!" % (message, winner, winner))
            else:
                answer(bot, "You want to spin me? Ok. Wheeeeeeee~")
        else:
            answer(bot, "Not enough winrars!")
    else:
        answer(bot, "Triggering this command privately is not allowed.")

register(spin, "common", "spin")

def cookie(bot, args):
    if len(args) == 2:
        nicks = bot.inv['rooms'].get(bot.remote['receiver'])
        if nicks:
            if args[1].lower() in [nick.lower() for nick in nicks]:
                if args[1].lower() != bot.name.lower():
                    answer(bot, "\x01ACTION gives %s a cookie.\x01" % args[1])
                else:
                    answer(bot, "OM NOM NOM NOM.")
            else:
                answer(bot, "Who?")
        else:
            answer(bot, "Triggering this command privately is not allowed.")
    else:
        give_help(bot, args[0], "<nick>")

register(cookie, "common", "cookie")

def choose(bot, args):
    import random
    args_ = list(set(' '.join([arg.lower() if arg.lower() == 'or' else arg for arg in args[1:]]).split(' or ')))
    args__ = list(set([arg.lower() for arg in args_]))
    if len(args_) > 1 and len(args_) == len(args__):
        ans = random.choice([
            'Defs', 'Totes', 'I reckon', 'Why not', 'I like *', 'DEFINITELY',
            'Without a doubt', 'Always', 'A must-choose: *', 'You could ^',
            'I recommend *', 'Perhaps', 'Blimey,', 'How about *', 'HAHA,',
            'I say', 'Something tells me', 'Try *', 'Go with *', 'I highly recommend *'
        ])
        choice = random.choice(args_)
        intermediary = "choose " if random.random() > 0.5 else ''
        if '*' in ans:
            intermediary = ''
            ans = ans[:-2]
        elif '^' in ans:
            intermediary = "choose "
            ans = ans[:-2]
        if choice.endswith("?") and len(choice) > 1:
            choice = choice[:-1]
        answer(bot, "%s %s%s." % (ans, intermediary, choice))
    else:
        give_help(bot, args[0], "<item 1> or <item 2> [or <item n>] where 1 != 2 != n")

register(choose, "common", "choose")

def m8b(bot, args):
    if len(args) > 1:
        responses = [
            "It is certain.", "It is decidedly so.", "Without a doubt.", "Yes - definitely.", "You may rely on it.", "As I see it, yes.", "Most likely.", "Outlook good.", "Signs point to yes.", "Yes.",
            "Reply hazy, try again.", "Ask again later.", "Better not tell you now.", "Cannot predict now.", "Concentrate and ask again.",
            "Don't count on it.", "My reply is no.", "My sources say no.", "Outlook not so good.", "Very doubtful."
        ]
        answer(bot, __import__('random').choice(responses))
    else:
        give_help(bot, args[0], "<herp>")

register(m8b, "common", "8ball", "eight_ball")

def ghetto(bot, args):
    if len(args) == 2:
        real_name = args[1].lower()
        ghetto_name = ""
        
        table = {
                    'a': 'sha', 'b': 'ni', 'c': 'ki', 'd': 'que',
                    'e': 'nay', 'f': 'qui', 'g': 'ti', 'h': 'la',
                    'i': 'kay', 'j': 'ri', 'k': 'barack', 'l': 'obama',
                    'm': 'di', 'n': 'ta', 'o': 'ee', 'p': 'ray',
                    'q': 'cli', 'r': 'gurl', 's': 'na', 't': 'qua',
                    'u': 'kwa', 'v': 'ise', 'w': 'fi', 'x': 'quee',
                    'y': 'mi', 'z': 'si'
        }
        
        for letter in real_name:
            try: ghetto_name += table[letter] + "-"
            except KeyError: return "Invalid name."
        
        answer(bot, ghetto_name[:-1])
    else:
        give_help(bot, args[0], "<first name>")

register(ghetto, "common", "ghetto")

def sorting_hat(bot, args):
    if len(args) == 2:
        nicks = bot.inv['rooms'].get(bot.remote['receiver'])
        if nicks:
            if args[1].lower() in [nick.lower() for nick in nicks]:
                houses = ['Gryffindor', 'Hufflepuff', 'Ravenclaw', 'Slytherine']
                answer(bot, houses[sum(ord(c) for c in args[1]) % 4] + '!')
            else:
                answer(bot, "But they're not here!")
        else:
            answer(bot, "It's a secret.")
    else:    
        give_help(bot, args[0], "<nick>")

register(sorting_hat, "common", "sortinghat")

def lotto(bot, args):
    import random
    balls = random.sample(range(1, 41), 7)
    answer(bot, "Winning lotto numbers are: %s & bonus ball %d with powerball %d" % (', '.join(str(s) for s in balls[:-1]), balls[6], random.randint(1, 10)))

#register(lotto, "common", "lotto")