import logging
import datetime, pytz, requests, time
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

    for index, doc in enumerate(docs):
        summary=""
        new_status='DONE'

        if (doc['action']=='on' and is_daytime) or\
            (doc['action']=='off' and not is_daytime):

            res, request_body = toggle_lights(doc['deviceId'], doc['action_to_take'], doc['channel_id'])
            if res.status_code < 300:
                summary = f"""Action take on device:{doc['deviceId']}.
                Lights were turned {doc['action_to_take']} on channel {doc['channel_id']}."""
                doc['action_taken']='SUCCESS'
            else:
                summary = f"""Action attempt failed for device:{doc['deviceId']}.
                Lights were not turned {doc['action_to_take']} on channel {doc['channel_id']}."""
                new_status='PENDING'
                doc['action_taken']='FAILED'

            doc["body"]=request_body
            doc["response"]=str(res)
        else:
            summary=f"""No action taken for {doc['deviceId']}.
            Lights were turned {doc['action']} on channel {doc['channel_id']}"""
            doc['action_taken']='NOT NEEDED'
        
        summary += f" daytime is {is_daytime}"
        
        doc["is_daytime"]=is_daytime
        doc['execution_status']=new_status
        doc['handled_at']=current_time.isoformat()
        doc['comment']=summary
        doc['doc_index_in_batch']=index
        doc['docs_in_batch']=len(docs)
     
        db.set(doc)
        print(f'Replaced Item\'s Id is {doc["id"]}')
        time.sleep(2) # Shelly API doesn't allow frequent calls

def toggle_lights(device_id, action, channel_id=0):
    body = {
        'auth_key':shelly_auth_key,
        'id':device_id,
        'turn':action,
        'channel':channel_id
    }

    x = requests.post(shelly_endpoint, data = body)
    return x, body