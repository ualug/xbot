import util
def tell(bot, args):
    if len(args) >= 4 and args[2] == "about":
        what = ' '.join(args[3:]).lower()
        library = {
                'yourself': "I'm an awesome lil bot n.n",
                'irc': "IRC stands for Internet Relay Chat, and you're using it this very minute! :O",
                'enter': "Stop pressing the Enter key so much! Grrrrr. Rage rage rage.",
                'sleep': "Sleep's pretty good, yep. You should do it sometime.",
                'bacon': "Lemme tell you something. Bacon, is good for you. (see http://www.youtube.com/watch?v=2T_obaO46Bo for details.)",
                'cubestormer': "The CubeStormer II is an awesome LEGO Mindstorms\x99 NXT robot that can solve Rubik's Cubes in a matter of seconds. See http://www.youtube.com/watch?v=_d0LfkIut2M for a video demonstration.",
                'ql': "Quantum Levitation is fecking awesome. See http://www.youtube.com/watch?v=Ws6AAhTw7RA and http://www.youtube.com/watch?v=VyOtIsnG71U"
        }
        if library.get(what):
            if bot.inv['rooms'].get(bot.remote['receiver']):
                if args[1].lower() in [nick.lower() for nick in bot.inv['rooms'].get(bot.remote['receiver'])]:
                    util.answer(bot, "%s: %s" % (args[1], library[what]))
                else:
                    util.answer(bot, "%s: %s isn't in this channel." % (bot.remote['nick'], args[1]))
            else:
                util.answer(bot, "Triggering this command privately is not allowed.")
        else:
            util.answer(bot, "Dunno about that, nigga.")
    else:
        util.give_help(bot, args[0], "<nick> about <item>")

util.register(tell, "common", "tell")