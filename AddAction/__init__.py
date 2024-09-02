import logging
import datetime
from dataclasses import dataclass
import uuid

import azure.functions as func

@dataclass
class Device:
    device_name:str
    sunrise_offset:int
    sunset_offset:int

device_names = {
    '083af201e040_0':Device('תאורת חוץ מרכז',-30,-20),
    '3ce90e30ffb8_0':Device('תאורה נסתרת',50,-60),
    '3ce90e30ffb8_1':Device('גינה',-55,0),
    '3ce90e2f815c_0':Device('פנים',30,-40),
    '3ce90e2f815c_1':Device('אפלייט חוץ',-60,15)
}

def main(req: func.HttpRequest, \
        doc: func.Out[func.Document]) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    print("start")
    action = req.route_params.get('action')
    action_to_take = 'on' if action=='off' else 'off'
    device_id = req.route_params.get('device_id')
    channel_id = req.route_params.get('channel_id')

    current_time = datetime.datetime.utcnow()
    delta = 30 if action=='on' else 10
    time_to_execute = current_time + datetime.timedelta(minutes=delta)
    my_id=str(uuid.uuid4())


    device = device_names.get(f'{device_id.lower()}_{channel_id}',Device(f'{device_id.lower()}_{channel_id}',0,0))
    print(device)
    
    record = {
        'id': my_id,
        'action':action,
        'action_to_take':action_to_take,
        'deviceId':device_id,
        'channel_id':channel_id,
        'time_insert':current_time.isoformat(),
        'time_to_execute':time_to_execute.isoformat(),
        'execution_status':'PENDING',
        'device_name':device.device_name,
        'sunrise_offset':device.sunrise_offset,
        'sunset_offset':device.sunset_offset,
        'comment':'None'}
    print(record)

    doc.set(func.Document.from_dict(record))
    
    return func.HttpResponse(
            """This HTTP triggered function executed successfully.
             Pass a name in the query string or in the request body
              for a personalized response.""",
            status_code=200
    )
