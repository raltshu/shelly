import logging
import datetime, pytz, requests
from astral import LocationInfo
from astral.sun import sun

import azure.functions as func

shelly_auth_key = "NzhmNWZ1aWQ1EB2D4305480DC58F8AA62700122CE2D8B6D64BCFAF893ACF19A00684FE3D089F2B0EB004EE821D8"
shelly_endpoint="https://shelly-28-eu.shelly.cloud/device/relay/control"

def main(mytimer: func.TimerRequest, docs: func.DocumentList, db: func.Out[func.Document]):
    logging.info('Python DB trigger function processed a request.')
    city = LocationInfo("Tel-Aviv", "Israel", "Asia/Jerusalem", 32.109333, 34.855499)
    s = sun(city.observer, date=datetime.datetime.utcnow())
    current_time = pytz.timezone("UTC").localize(datetime.datetime.utcnow())

    is_daytime = s['sunrise'] < current_time < s['sunset']

    for doc in docs:
        summary=""
        if (doc['action']=='on' and is_daytime) or\
            (doc['action']=='off' and not is_daytime):

            res = toggle_lights(doc['deviceId'], doc['action_to_take'], doc['channel_id'])
            summary = f"""Action take on device:{doc['deviceId']}.
            Lights were turned {doc['action_to_take']} on channel {doc['channel_id']}.
            res={str(res)}."""
        else:
            summary=f"""No action taken for {doc['deviceId']}.
            Lights were turned {doc['action']} on channel {doc['channel_id']}"""
        
        summary += f" daytime is {is_daytime}"

        doc['execution_status']='DONE'
        doc['handled_at']=current_time.isoformat()
        doc['comment']=summary
     
        db.set(doc)
        print(f'Replaced Item\'s Id is {doc["id"]}')

def toggle_lights(device_id, action, channel_id=None):
    body = {
        'auth_key':shelly_auth_key,
        'id':device_id,
        'turn':action,
    }

    if channel_id:
        body['channel']=channel_id

    x = requests.post(shelly_endpoint, data = body)
    return x