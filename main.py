from flask import Flask, Response, json
from flask_restful import Api, reqparse, Resource
from flask.wrappers import Request
from functions  import *
from config import API

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

class ParseBool():
    def __new__(cls, x: str) -> bool:
        if x.lower() == 'true':
            return True
        return False



class Project(_Resource):
    """Загрузить данные из файла и отправка их в верном формате в таблицу (на фронт)"""
    parser = reqparse.RequestParser(trim=True)
    parser.add_argument('name', type=str)
    parser.add_argument('is_favorites', type=ParseBool)


    def get(self):
        body, status = get_projects()
        return self.return_json(body, status)
    

    def post(self):
        args: dict = self.parser.parse_args()
        return self.return_json(*create_projects(args))


api.add_resource(Project, '/projects')



if __name__ == '__main__':
    app.run(host= API.get('host'), port= API.getint('port'), debug= API.getboolean('debug'))
