import logging
from .flaskApp.main import app
import azure.functions as func


def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    return func.WsgiMiddleware(app).handle(req, context)
