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

 - peewee
   
   ```
   pip install peewee
   ```

- dnspython
   
   ```
   pip install dnspython
   # or use package manager
   ```

 - lxml
   
   ```
   pip install lxml
   # or use package manager
   ```

 - pyv8
   
   On Windows, use the [precompiled package](https://code.google.com/p/pyv8/downloads/list).  
   On Linux, either [compile it](https://code.google.com/p/pyv8/wiki/HowToBuild) or use your package manager.  
   On OS X, either compile it (see above) or use [brokenseal's binary](https://github.com/brokenseal/PyV8-OS-X).

 - interruptingcow

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