import util
import urllib2
import json
import datetime

def times(bot, args):

    def plural(word, num):
        return word if num == 1 else word + "s"
    
    error = "%s%s: Invalid bus stop number." % (bot.prefix, args[0])
    
    if len(args) == 2:
        try:
            if len(args[1]) == 4:
                stop = int(args[1])
                if stop < 1 or stop > 9999:
                    raise ValueError
            else:
                raise ValueError
        except ValueError:
            util.answer(bot, error)
            return None
        
        stops = json.loads(urllib2.urlopen('http://www.maxx.co.nz/base/StopInfo/FindStopsByNumber/%d.aspx' % stop).read())
        if not stops['recordcount']:
            util.answer(bot, error)
            return None
            
        raw_services = json.loads(urllib2.urlopen('http://www.maxx.co.nz/base/DepartureBoard2/RealTime/%d.aspx' % stop).read())
        #services = json.loads('[{"route":"974","toLocation":"BEACH HAVEN","scheduledDeparture":"2012-08-13T12:00:00.000Z","estimatedDeparture":"2012-08-13T01:00:00.000Z","timestamp":"2012-08-13T11:52:12.937Z"}]')
        results = []
        
        services = sorted(raw_services, key=lambda d: d['estimatedDeparture'])
        
        if services:
            for service in services:
                dt_shd = datetime.datetime.strptime(service['scheduledDeparture'], '%Y-%m-%dT%H:%M:%S.000Z')
                dt_est = datetime.datetime.strptime(service['estimatedDeparture'], '%Y-%m-%dT%H:%M:%S.000Z')
                dt_dif = dt_est - datetime.datetime.utcnow()
                dt_dly = dt_est - dt_shd
                delay = dt_dly.seconds / 60
                departure = dt_dif.seconds / 60
                
                if dt_dif.seconds > 3600:
                    continue
                
                if dt_dly.seconds > 3600:
                    delay = 1440 - delay
                    offset = '(%d %s early)' % (delay, plural('minute', delay))
                else:
                    if delay != 0:
                        offset = '(%d %s late)' % (delay, plural('minute', delay))
                    else:
                        offset = '(on schedule)'
                
                results.append(("%s: %s %s %s" % (service['route'], service['toLocation'], ('in %d %s' % (departure, plural('minute', departure))) if departure != 0 else 'is DUE', offset)).encode('utf-8'))
        
        util.answer(bot, '\n'.join(results) or "No buses imminent.")
    
    else:
        util.give_help(bot, args[0], "<bus stop number>")

util.register(times, "common", "maxx")