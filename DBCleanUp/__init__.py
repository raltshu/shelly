import logging
import os

import azure.functions as func
from azure.cosmos import CosmosClient

connectionString = os.environ['CosmosDbConnectionString'].split(';')
endpoint = connectionString[0][len('AccountEndpoint='):]
key = connectionString[1][len('AccountKey='):]

def main(mytimer: func.TimerRequest, docs: func.DocumentList):
    logging.info('Python Cleanup trigger function processed a request.')
    
    client = CosmosClient(endpoint, key)
    database_name = 'shellyAction'
    database = client.get_database_client(database_name)
    container_name = 'buttonOnOff'
    container = database.get_container_client(container_name)

    for doc in docs:
        container.delete_item(item=doc['id'],partition_key=doc['deviceId'])
        
        print(f'Deleted Item\'s Id is {doc["id"]}')