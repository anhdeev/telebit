from datetime import datetime,timedelta
from modules.mongodb.mongodb import MongoDatabase

class MostRecentCoin(object):
    def init():
        MongoDatabase.init()

    def get_statistic(time):
        result = {}
        try:
            since = datetime.now() - timedelta(hours=time)
            items =  MongoDatabase.find('coin_statistic', {'time':{"$gte": since}})
        except:
            return "Cannot get correct time"
        # merging
        for item in items:
            if not result.get(item['coin']):
                result[item['coin']] = item['count']
            else:
                result[item['coin']] += item['count']

        result_array=[]
        for key in result:
            result_array.append( {'coin' : key, 'count' : result[key] } )

        result_array.sort(key = lambda c: c['count'], reverse=True)

        print_msg = "Most recent coin (last %d hours):\n" % time
        for index,coin in enumerate(result_array):
            print_msg += '\t' + coin['coin'] + ' : ' + str(coin['count']) + '\n'
            if index == 10:
                break

        return print_msg

