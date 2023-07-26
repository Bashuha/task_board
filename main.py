from flask import Flask, Response, json
from flask_restful import Api, reqparse, Resource
from flask.wrappers import Request
from functions  import *
from config import API
from flask_cors import CORS

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
CORS(app, supports_credentials=True)
api = Api(app, prefix='/to_do_list')
app.request_class = AnyJsonRequest


class ParseBool():
    def __new__(cls, x: str | bool) -> bool:
        if isinstance(x, bool):
            return x
        if x.lower() == 'true':
            return True
        return False



class Project(_Resource):

    parser = reqparse.RequestParser(trim=True)
    parser.add_argument('name', type=str)
    parser.add_argument('is_favorites', type=ParseBool)
    parser.add_argument('is_archive', type=ParseBool)
    parser.add_argument('project_id', type=int)


    def get(self):
        body, status = get_projects()
        return self.return_json(body, status)
    

    def post(self):
        args: dict = self.parser.parse_args()
        return self.return_json(*create_projects(args))
    

    def put(self):
        args: dict = self.parser.parse_args()
        return self.return_json(*archive_project(args))
    
    
    def delete(self):
        args: dict = self.parser.parse_args()
        return self.return_json(*delete_from_archive(args))
    

class Tasks(_Resource):
    
    parser = reqparse.RequestParser(trim=True)
    parser.add_argument('name', type=str)
    parser.add_argument('description', type=str)
    parser.add_argument('project_id', type=str)


    def get(self):
        args: dict = self.parser.parse_args()
        body, status = get_project_details(args)
        return self.return_json(body, status)
    
    
    def post(self):
        args: dict = self.parser.parse_args()
        return self.return_json(*create_task(args))


class Comments(_Resource):

    parser = reqparse.RequestParser(trim=True)
    parser.add_argument('task_id', type=str)

    def get(self):
        args: dict = self.parser.parse_args()
        body, status = get_task_details(args)
        return self.return_json(body, status)    


api.add_resource(Tasks, '/tasks')
api.add_resource(Project, '/projects')
api.add_resource(Comments, '/comments')


if __name__ == '__main__':
    app.run(host= API.get('host'), port= API.getint('port'), debug= API.getboolean('debug'))
