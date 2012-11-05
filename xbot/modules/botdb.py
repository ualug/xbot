import peewee

class BotDB(object):

    def __init__(self, bot):
        self.db = {
            'sqlite'     : lambda:
                peewee.SqliteDatabase(bot.config.get('module: botdb', 'path')),        
            'postgresql' : lambda:
                peewee.PostgresqlDatabase(
                    bot.config.get('module: botdb', 'name'),
                    host=bot.config.get('module: botdb', 'host'),
                    user=bot.config.get('module: botdb', 'user'),
                    passwd=bot.config.get('module: botdb', 'pass')
                ),
            'postgresql' : lambda:
                peewee.MysqlDatabase(
                    bot.config.get('module: botdb', 'name'),
                    host=bot.config.get('module: botdb', 'host'),
                    user=bot.config.get('module: botdb', 'user'),
                    passwd=bot.config.get('module: botdb', 'pass')
                )
        }[bot.config.get('module: botdb', 'type')]()

    def connect(self):
        self.db.connect()
        
        try:
            Quote.create_table()
        except Exception:
            pass
    

class Quote(peewee.Model):
    id = peewee.PrimaryKeyField()
    time = peewee.IntegerField(10)
    channel = peewee.CharField(max_length=20)
    nick = peewee.CharField(max_length=20)
    action = peewee.BooleanField()
    message = peewee.TextField()
    
    class Meta:
        db_table = "quotes"