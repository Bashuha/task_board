from flask import Flask, Response, json, send_file
from flask_restful import Api, reqparse, Resource
from flask.wrappers import Request
from config import API
from werkzeug.datastructures import FileStorage
from functions  import *
from datetime import datetime

class AnyJsonRequest(Request):
    def on_json_loading_failed(self, e):
        if e is not None:
            return super().on_json_loading_failed(e)


class _Resource(Resource):
    parser = reqparse.RequestParser(trim=True)

    def return_json(self, body, status):
        return Response(json.dumps(body, ensure_ascii=False), mimetype='application/json', status=status)

    def return_status(self, status):
        return Response(status=status)


app = Flask(__name__)
api = Api(app, prefix='')
app.request_class = AnyJsonRequest