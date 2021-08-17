import logging
import datetime

import azure.functions as func

def main(req: func.HttpRequest, \
        doc: func.Out[func.Document]) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    action = req.route_params.get('action')
    action_to_take = 'on' if action=='off' else 'off'
    device_id = req.route_params.get('device_id')
    channel_id = req.route_params.get('channel_id')

    current_time = datetime.datetime.utcnow()
    delta = 30 if action=='on' else 10
    time_to_execute = current_time + datetime.timedelta(minutes=delta)

    record = {
        'action':action,
        'action_to_take':action_to_take,
        'deviceId':device_id,
        'channel_id':channel_id,
        'time_insert':current_time.isoformat(),
        'time_to_execute':time_to_execute.isoformat(),
        'execution_status':'PENDING',
        'comment':'None'}

    doc.set(func.Document.from_dict(record))
    
    return func.HttpResponse(
            """This HTTP triggered function executed successfully.
             Pass a name in the query string or in the request body
              for a personalized response.""",
            status_code=200
    )
