import os
import sys
import socket
import time
import datetime
import traceback
import modules

class Client(object):
    def __init__(self, config):
        self.config = config
        self.prefix = config.get('general', 'prefix')
        self.sendq = []
        self.recvq = []
        self.termop = "\r\n"
        self.verbose = True
        self.closing = False
        self.version = 2.4
        self.env = sys.platform

    def connect(self, server, port):
        socket.setdefaulttimeout(300)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((server, port))
        self.sock = socket.ssl(self.socket)
        
        self._loop()

    def disconnect(self, n, frame):
        self.socket.setblocking(0)
        self.closing = True
        self._sendq(['QUIT'], "See ya~")
        self._send()
        
    def _recv(self, bytes):
        buffer = []
        while True:
            data = self.sock.read(bytes)
            if data:
                if data.endswith(self.termop):
                    if buffer:
                        self.recvq.append(''.join(buffer) + data)
                    else:
                        self.recvq.append(data)
                    if self.verbose:
                        self._log('in', ''.join(self.recvq))
                    return True
                else:
                    buffer.append(data)
            else:
                break
        del buffer[:]

    def _sendq(self, left, right = None):
        if right:
            limit = 445
            for line in right.splitlines():
                if line:
                    lines = [line[i:i+limit] for i in range(0, len(line), limit)]
                    for n in range(len(lines)):
                        self.sendq.append("%s :%s%s" % (' '.join(left), lines[n], self.termop))
        else:
            self.sendq.append("%s%s" % (' '.join(left), self.termop))

    def _send(self):
        lines = len(self.sendq)
        burst = 5
        delay = 2
        for i in range(0, lines, delay):
            if i == 0:
                buffer = ''.join(self.sendq[:burst])
                del self.sendq[:burst]
            elif lines > 0:
                buffer = ''.join(self.sendq[:delay])
                del self.sendq[:delay]
                time.sleep(delay)
            if self.verbose:
                self._log('out', buffer)
            self.sock.write(buffer)
            if not self.sendq: break
        del self.sendq[:]

    def _loop(self):
        p = Parser(self.config)
        while True:
            if len(self.sendq) > 0:
                self._send()
                del p.sendq[:]
            if self.closing:
                self.socket.close()
                sys.exit()
            if not self._recv(4096): break
            for bytes in self.recvq:
                for line in ''.join(bytes).split(self.termop):
                    if line:
                        p.interpret(line)
            if not self.closing: self.sendq = p.sendq
            del self.recvq[:]

    def _log(self, flow, buffer):
        log = datetime.datetime.now().strftime("%b %d %Y %H:%M:%S")
        if flow == "out":
            _pad = "<<<"
        elif flow == "in":
            _pad = ">>>"
        for index, line in enumerate(buffer.split(self.termop)[:-1]):
            if index == 0:
                pad = _pad
            else:
                pad = "   "
            print "%s %s %s" % (log, pad, line.encode('string_escape').replace("\\'", "'").replace("\\\\", "\\"))

class Parser(Client):
    def __init__(self, config):
        super(Parser, self).__init__(config)
        self.network = config.active_network
        self.init = {
            'ident': 0, 'retries': 0, 'ready': False, 'log': True,
            'registered': True if config.get(self.network, 'password') else False,
            'identified': False, 'joined': False
        }
        self.inv = {
            'rooms': {},
            'banned': []
        }
        self.remote = {}
        self.previous = {}
        self.voice = True
        self.name = config.get(self.network, 'nick')
        self.admin = config.get(self.network, 'admin')

    def interpret(self, line):
        self.remote['server'] = None
        self.remote['nick'] = None
        self.remote['user'] = None
        self.remote['host'] = None
        self.remote['misc'] = None
        self.remote['message'] = None
        self.remote['receiver'] = None
        
        if line.startswith(":"):
            _args = ''.join(line.split(":", 1)[1]).split(" :", 1)
            args = _args[0].split()
            self.remote['mid'] = args[1]
            
            if "@" in args[0]:
                _temp = args[0].split("@")
                self.remote['nick'] = _temp[0].split("!")[0]
                self.remote['user'] = _temp[0].split("!")[1]
                self.remote['host'] = _temp[1]
            else:
                self.remote['server'] = args[0]
                
            try: self.remote['misc'] = args[3:]
            except IndexError: pass
            try: self.remote['message'] = _args[1]
            except IndexError: pass
            try: self.remote['receiver'] = args[2]
            except IndexError: pass
            self._init()

            if self.init['ident'] and self.remote['mid'] in ['376', '422']:
                self.init['ready'] = True
                
            if self.init['ready']:
                if self.remote['message']:
                    self.remote['sendee'] = self.remote['receiver'] if self.remote['receiver'] != self.nick else self.remote['nick']
                    try:
                        if self.init['log'] and self.init['joined'] and self.remote['mid'] == "PRIVMSG":
                            modules.logger.log(self, self.remote['sendee'], self.remote['nick'], self.remote['message'])
                        modules.io.read(self)
                    except:
                        error_message = "Traceback (most recent call last):\n" + '\n'.join(traceback.format_exc().split("\n")[-4:-1])
                        self._sendq(("NOTICE", self.remote['sendee'] or self.admin), error_message)
                if self.init['joined']:
                    self._updateNicks()                
        else:
            arg    = line.split(" :")[0]
            message = line.split(" :", 1)[1]
            self._init()

            if arg == "PING":
                self._sendq(['PONG'], message)

    def _sendq(self, left, right = None):
        if self.init['log'] and self.init['joined'] and left[0] == "PRIVMSG":
            if self.remote['receiver'] == self.nick: self.remote['receiver'] = self.remote['nick']
            if type(right) != str: raise AssertionError("send queue must be <type 'str'> but was found as %s" % type(right))
            modules.logger.log(self, left[1], self.nick, right)
        Client._sendq(self, left, right)
    
    def _init(self):
        if self.remote['message'] and self.init['ident'] is not True:
            if self.remote['message']:
                self.init['ident'] += 1
        if self.init['ident'] > 1:
            while not self.init['retries'] or self.remote['mid'] in ['433', '437']:
                self._ident()
                break
            if self.remote['mid'] == "001":
                self.init['ident'] = True

    def _ident(self):
        self.nick = self.name + "_" * self.init['retries']
        self._sendq(("NICK", self.nick))
        self._sendq(("USER", self.nick, self.nick, self.nick), self.nick)
        self.init['retries'] += 1
    
    def _login(self):
        self._sendq(("PRIVMSG", "NickServ"), "IDENTIFY %s" % self.config.get(self.network, 'password'))
    
    def _updateNicks(self):
        if self.remote['mid'] == "JOIN":
            if self.remote['nick'] == self.nick:
                self.inv['rooms'][self.remote['receiver']] = {}
            else:
                if self.remote['receiver']:
                    self.inv['rooms'][self.remote['receiver']][self.remote['nick']] = {}
                else:
                    self.inv['rooms'][self.remote['message']][self.remote['nick']] = {}
        elif self.remote['mid'] == "353":
            for user in self.remote['message'].split():
                self.inv['rooms'][self.remote['misc'][1]][user.lstrip("~.@%+")] = {}
                if __import__('re').search('^[~\.@%\+]', user):
                    if user[0] in ['~', '.']:
                        mode = 'q'
                    elif user[0] == '@':
                        mode = 'o'
                    elif user[0] == '%':
                        mode = 'h'
                    elif user[0] == '+':
                        mode = 'v'
                    self.inv['rooms'][self.remote['misc'][1]][user[1:]]['mode'] = mode or None
                else:
                    self.inv['rooms'][self.remote['misc'][1]][user]['mode'] = None
        elif self.remote['mid'] == "PART":
                if self.remote['nick'] == self.nick:
                    del self.inv['rooms'][self.remote['receiver']]
                else:
                    del self.inv['rooms'][self.remote['receiver']][self.remote['nick']]
        elif self.remote['mid'] == "KICK":
            if self.remote['misc'][0].lower() != self.nick.lower():
                del self.inv['rooms'][self.remote['receiver']][self.remote['misc'][0]]
            else:
                del self.inv['rooms'][self.remote['receiver']]
        elif self.remote['mid'] == "NICK":
            for room in self.inv['rooms']:
                if self.remote['nick'] in self.inv['rooms'][room]:
                    self.inv['rooms'][room][self.remote['message']] = self.inv['rooms'][room][self.remote['nick']]
                    del self.inv['rooms'][room][self.remote['nick']]
            if self.remote['nick'].lower() in self.inv['banned']:
                self.inv['banned'][self.inv['banned'].index(self.remote['nick'].lower())] = self.remote['message'].lower()
        elif self.remote['mid'] == "QUIT":
            for room in self.inv['rooms']:
                if self.remote['nick'] in self.inv['rooms'][room]:
                    del self.inv['rooms'][room][self.remote['nick']]
        elif self.remote['mid'] == "MODE":
            if len(self.remote['misc']) == 2:
                if self.remote['misc'][0].startswith("+") and self.remote['misc'][0][1] in ['o', 'h', 'v']:
                    self.inv['rooms'][self.remote['receiver']][self.remote['misc'][1]]['mode'] = self.remote['misc'][0][1]
                elif self.remote['misc'][0].startswith("-") and self.remote['misc'][0][1] in ['o', 'h', 'v']:
                    self.inv['rooms'][self.remote['receiver']][self.remote['misc'][1]]['mode'] = None

    def _reload(self, args):
        if len(args) == 1:
            reload(modules)
            response = "Success: Reloaded all submodules."
        elif len(args) == 2:
            if os.path.exists("%s/modules/%s.py" % (os.path.dirname(__file__), args[1])):
                reload(__import__('modules.' + args[1], globals(), locals(), fromlist = [], level = 1))
                response = "Success: Reloaded '%s' submodule." % args[1]
            else:
                response = "Failure: No such module '%s'." % args[1]
        elif len(args) > 2:
            affected, unaffected = [], []
            for module in args[1:]:
                if os.path.exists("%s/modules/%s.py" % (os.path.dirname(__file__), module)):
                    reload(__import__('modules.' + module, globals(), locals(), fromlist = [], level = 1))
                    affected.append(module)
                else:
                    unaffected.append(module)
            if (len(args[1:]) - len(unaffected)) == len(args[1:]):
                response = "Success: Reloaded %s submodules." % ', '.join(args[1:])
            elif len(unaffected) < len(args[1:]):
                pl1 = "" if len(unaffected) == 1 else "s"
                pl2 = "was" if len(affected) == 1 else "were"
                response = "Partial: Could not reload %s submodule%s but %s %s ok." % (', '.join(unaffected), pl1, ', '.join(affected), pl2)
            else:
                response = "Failure: No such modules."
            del affected, unaffected
        
        self._sendq(("PRIVMSG", self.remote['sendee']), response)