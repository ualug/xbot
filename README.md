```
  .,::      .::::::::.      ...   ::::::::::::
  `;;;,  .,;;  ;;;'';;'  .;;;;;;;.;;;;;;;;''''
    '[[,,[['   [[[__[[\.,[[     \[[,   [[     
     Y$$$P     $$""""Y$$$$$,     $$$   $$     
   oP"``"Yo,  _88o,,od8P"888,_ _,88P   88,    
,m"       "Mm,""YUMMMP"   "YMMMMMP"    MMM    
```


[xBot](//github.com/milosivanovic/xbot) - the modularised Python IRC bot. Woot!

## DEPENDENCIES

- [peewee](http://peewee.readthedocs.org/)
   
   ```
   pip install peewee
   ```

- [pubsub](http://pubsub.sourceforge.net/)
   
   ```
   pip install pypubsub
   ```

- [js-beautifier](http://jsbeautifier.org/)
   
   ```
   pip install git+git://github.com/passcod/js-beautify-python.git
   ```

- [opengraph](https://github.com/erikriver/opengraph)
   
   ```
   pip install opengraph
   ```

- [PyGithub](https://github.com/jacquev6/PyGithub)
   
   ```
   pip install PyGithub
   ```

- [dnspython](http://www.dnspython.org/)
   
   ```
   pip install dnspython
   # or use package manager
   ```

- [json](http://simplejson.readthedocs.org)
   
   ```
   pip install simplejson
   # or use package manager
   ```
   
- [lxml](http://lxml.de/)
   
   ```
   pip install lxml
   # or use package manager
   ```

- [pyv8](https://code.google.com/p/pyv8/)
   
   On Windows, use the [precompiled package](https://code.google.com/p/pyv8/downloads/list).  
   On Linux, either [compile it](https://code.google.com/p/pyv8/wiki/HowToBuild) or use your package manager.  
   On OS X, either compile it (see above) or use [brokenseal's binary](https://github.com/brokenseal/PyV8-OS-X).

- [interruptingcow](https://bitbucket.org/evzijst/interruptingcow)

   ```
   pip install interruptingcow
   ```

All dependencies except **pyv8** can be install through a simple

    pip install -r requirements.txt


## INSTALL

1. Clone repo
2. Rename xbot.sample.conf to xbot.conf, and edit it
3. Give 'bot' file execute permissions, and run ./bot
4. Enjoy!


## JS ENV

All files in `modules/js` will be loaded into the JS environment at creation
time. This can be used to easily create a library of useful functions that
are kept even when the JS environment is reset.

There is a special `bot` variable available in JS which contains:

 - The bot's version.
 - The current prefix.
 - The current nicks in the caller's channel and their modes.
 - All channels the bot is in.


## CHANGELOG

Historical changes by Milos Ivanovic are in [CHANGELOG](https://github.com/milosivanonic/xbot/blob/master/CHANGELOG).  
Revision.io changelog: http://revision.io/xbot