# from flask import Flask, Response, json, send_file
# from flask_restful import Api, reqparse, Resource
# from flask.wrappers import Request
# from werkzeug.datastructures import FileStorage
# from datetime import datetime

# class AnyJsonRequest(Request):
#     def on_json_loading_failed(self, e):
#         if e is not None:
#             return super().on_json_loading_failed(e)


# class _Resource(Resource):
#     parser = reqparse.RequestParser(trim=True)

#     def return_json(self, body, status):
#         return Response(json.dumps(body, ensure_ascii=False), mimetype='application/json', status=status)

#     def return_status(self, status):
#         return Response(status=status)


# app = Flask(__name__)
# api = Api(app, prefix='')
# app.request_class = AnyJsonRequest

from flask import Flask
from functions  import *
from config import API

app = Flask(__name__)

@app.route('/')
def get_proj():
    return get_projects()


if __name__ == '__main__':
    app.run(host= API.get('host'), port= API.getint('port'), debug= API.getboolean('debug'))
