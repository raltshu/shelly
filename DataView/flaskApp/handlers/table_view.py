import logging
from flask_classful import FlaskView, route
from flask import render_template
from azure.cosmos import CosmosClient
import os
from datetime import datetime
import pytz

connectionString = os.environ['CosmosDbConnectionString'].split(';')
endpoint = connectionString[0][len('AccountEndpoint='):]
key = connectionString[1][len('AccountKey='):]

class TableView(FlaskView):
  
    @route('/', methods=['GET'])
    def index(self):
        client = CosmosClient(endpoint, key)
        database_name = 'shellyAction'
        database = client.get_database_client(database_name)
        container_name = 'buttonOnOff'
        container = database.get_container_client(container_name)

        res = container.query_items("SELECT * FROM c ORDER BY c.time_insert desc", enable_cross_partition_query=True)
        display_list = list()
        for rec in res:
            display_rec = {
                'time': formattime(rec.get('time_insert')),
                'device_name': rec.get('device_name'),
                'status':formatpendingdone(rec.get('execution_status')),
                'action':formatactiontoaction(rec.get('action'),rec.get('action_to_take')),
                # 'switch_action':formatonoff(rec.get('action')),
                # 'action_to_take':formatonoff(rec.get('action_to_take')),
                'action_taken':formatactionstatus(rec.get('action_taken')),
                'time_to_execute':formattime(rec.get('time_to_execute')),
                'handled_at':formattime(rec.get('handled_at')),
                'daylight':formatdaylight(rec.get('is_daytime')),
                'sunrise_sunset':formatsunrisesunset(rec.get('sunrise'), rec.get('sunset')),
                'shelly_response':formatshellyresponse(rec.get('response')),
                'device_id':f"{rec.get('deviceId')}_{rec.get('channel_id')}",
                # 'channel_id':rec.get('channel_id'),
                'msg':rec.get('comment')
            }
            display_list.append(display_rec)
        
        return render_template('show_table.html', data_table = display_list)
    
def formattime(isotimestr: str) -> str:
    result = isotimestr
    try:
        t = datetime.fromisoformat(isotimestr)
        t = t.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Jerusalem'))
        result = t.strftime("%a %d-%b-%Y %H:%M:%S %Z%z")
    except:
        logging.error(f'Failed to format {isotimestr}')
    finally:
        return result

def formatdaylight(is_daylight: bool) -> str:
    if is_daylight is None:
        return None

    if is_daylight:
        src= "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fc/Sun_icon.svg/1020px-Sun_icon.svg.png"
    else:
        src = "https://img.flaticon.com/icons/png/512/196/196685.png?size=40x40&pad=1,1,1,1&ext=png&bg=FFFFFFFF"

    return f'<img src={src} alt="sun or moon" width="40" height="40">'

def formatonoff(action: str) -> str:
    if action.lower() == 'on':
        src = 'https://icons.iconarchive.com/icons/hopstarter/soft-scraps/256/Button-Turn-On-icon.png'
    else:
        src = 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/7c/OOjs_UI_icon_moon.svg/1200px-OOjs_UI_icon_moon.svg.png'

    return f'<img src={src} alt="sun or moon" width="40" height="40">'

def formatactiontoaction(action:str, to_action:str) -> str:
    src = 'https://www.iconninja.com/files/247/447/813/right-arrows-direction-arrow-icon.svg'
    img = f'<img src={src} alt="sun or moon" width="40" height="40">'
    return formatonoff(action) + img + formatonoff(to_action)

def formatpendingdone(stat:str) -> str:
    if stat=='PENDING':
        src = 'https://t3.ftcdn.net/jpg/01/82/45/90/360_F_182459037_Z5oMYBIAJRKrGG8D6xkxtXErXJ0HT8Vs.jpg'
    elif stat=='DONE':
        src = 'https://cdn3.vectorstock.com/i/1000x1000/45/22/done-rubber-stamp-vector-11314522.jpg'
    else:
        return None
    
    img = f'<img src={src} alt="sun or moon" width="70" height="50">'
    return img


def formatactionstatus(stat:str)->str:
    if stat == 'FAILED':
        src = 'https://image.pngaaa.com/350/3604350-middle.png'
    elif stat == 'SUCCESS':
        src = 'https://image.pngaaa.com/179/4681179-middle.png'
    else:
        return stat

    img = f'<img src={src} alt="sun or moon" width="70" height="50">'
    return img

def formatshellyresponse(res:str)->str:
    if res is None:
        return res
    
    res = res.replace('<','&lt')
    res = res.replace('>','&gt')
    return res

def formatsunrisesunset(sunrisetime: str, sunsettime:str) -> str:
    result = f'{sunrisetime} <br/> {sunsettime}'
    try:
        sunrise = datetime.fromisoformat(sunrisetime)
        sunrise = sunrise.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Jerusalem'))
        sunrise_str = sunrise.strftime("%H:%M")
        sunset = datetime.fromisoformat(sunsettime)
        sunset = sunset.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Jerusalem'))
        sunset_str = sunset.strftime("%H:%M %Z%z")
        sunrise_img_src = "https://img.flaticon.com/icons/png/512/169/169367.png?size=40x40&pad=1,1,1,1&ext=png&bg=FFFFFFFF"
        sunrise_img = f'<img src={sunrise_img_src} alt="sun or moon" width="20" height="20">'
        sunset_img_src = "https://img.flaticon.com/icons/png/512/196/196685.png?size=40x40&pad=1,1,1,1&ext=png&bg=FFFFFFFF"
        sunset_img = f'<img src={sunset_img_src} alt="sun or moon" width="20" height="20">'
        result = f'{sunrise_img} {sunrise_str} <br/>{sunset_img} {sunset_str}'
    except:
        logging.error(f'Failed to format {sunrisetime} and {sunsettime}')
    finally:
        return result
