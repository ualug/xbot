import peewee

class BotDB(object):

    def __init__(self, bot):
        dbtype = bot.config.get('module: botdb', 'type')
        if dbtype == "postgresql":
            self.db = peewee.PostgresqlDatabase(
                bot.config.get('module: botdb', 'name'),
                host=bot.config.get('module: botdb', 'host'),
                user=bot.config.get('module: botdb', 'user'),
                passwd=bot.config.get('module: botdb', 'pass')
            )
        elif dbtype == "mysql":
            self.db = peewee.MysqlDatabase(
                bot.config.get('module: botdb', 'name'),
                host=bot.config.get('module: botdb', 'host'),
                user=bot.config.get('module: botdb', 'user'),
                passwd=bot.config.get('module: botdb', 'pass')
            )
        else:
            self.db = peewee.SqliteDatabase(bot.config.get('module: botdb', 'path'))

    def connect(self):
        self.db.connect()
        
        try: Quote.create_table()
        except Exception: pass
        
        try: JsStore.create_table()
        except Exception: pass
    

class Quote(peewee.Model):
    id = peewee.PrimaryKeyField()
    time = peewee.IntegerField(10)
    channel = peewee.CharField(max_length=20)
    nick = peewee.CharField(max_length=20)
    action = peewee.BooleanField()
    message = peewee.TextField()
    
    class Meta:
        db_table = "quotes"

class JsStore(peewee.Model):
    id = peewee.PrimaryKeyField()
    key = peewee.TextField()
    value = peewee.TextField()
    
    class Meta:
        db_table = "js_store"