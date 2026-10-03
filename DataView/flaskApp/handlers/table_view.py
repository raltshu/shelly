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

SUN = '☀️'
MOON = '🌙'
ON = '🟢'
OFF = '🔴'
ARROW = '➜'
PENDING = '⏳'
DONE = '✅'
SUCCESS = '✔️'
FAILED = '❌'

def icon(symbol: str, title: str, size: int = 28) -> str:
    return f'<span role="img" aria-label="{title}" title="{title}" style="font-size:{size}px">{symbol}</span>'

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
                'sunrise_sunset':formatsunrisesunset(rec.get('sunrise'), rec.get('sunset'), rec.get('sunrise_offset',0), rec.get('sunset_offset',0)),
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
        return icon(SUN, 'Daytime')
    return icon(MOON, 'Night')

def formatonoff(action: str) -> str:
    if action is None:
        return ''
    if action.lower() == 'on':
        return icon(ON, 'On')
    return icon(OFF, 'Off')

def formatactiontoaction(action:str, to_action:str) -> str:
    return f'<span style="white-space:nowrap">{formatonoff(action)} {icon(ARROW, "to", 22)} {formatonoff(to_action)}</span>'

def formatpendingdone(stat:str) -> str:
    if stat=='PENDING':
        return icon(PENDING, 'Pending')
    elif stat=='DONE':
        return icon(DONE, 'Done')
    return None


def formatactionstatus(stat:str)->str:
    if stat == 'FAILED':
        return icon(FAILED, 'Failed')
    elif stat == 'SUCCESS':
        return icon(SUCCESS, 'Success')
    return stat

def formatshellyresponse(res:str)->str:
    if res is None:
        return res
    
    res = res.replace('<','&lt')
    res = res.replace('>','&gt')
    return res

def formatsunrisesunset(sunrisetime: str, sunsettime:str, sunrise_offset:int, sunset_offset:int) -> str:
    result = f'{sunrisetime} <br/> {sunsettime}'
    try:
        sunrise = datetime.fromisoformat(sunrisetime)
        sunrise = sunrise.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Jerusalem'))
        sunrise_str = sunrise.strftime(f"%H:%M{sunrise_offset:+}")
        sunset = datetime.fromisoformat(sunsettime)
        sunset = sunset.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Jerusalem'))
        sunset_str = sunset.strftime(f"%H:%M{sunset_offset:+} %Z%z")
        sunrise_img = icon(SUN, 'Sunrise', 16)
        sunset_img = icon(MOON, 'Sunset', 16)
        result = f'{sunrise_img} {sunrise_str} <br/>{sunset_img} {sunset_str}'
    except:
        logging.error(f'Failed to format {sunrisetime} and {sunsettime}')
    finally:
        return result
