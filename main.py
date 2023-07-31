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



class ProjectList(_Resource):

    def get(self):
        body, status = get_projects()
        return self.return_json(body, status)
    

class Project(_Resource):

    parser = reqparse.RequestParser(trim=True)
    parser.add_argument('name', type=str)
    parser.add_argument('is_favorites', type=ParseBool)
    parser.add_argument('project_id', type=int)

    edit_parser = reqparse.RequestParser(trim=True)
    edit_parser.add_argument('project_id', type=int, required=True)
    edit_parser.add_argument('is_favorites', type=ParseBool)
    edit_parser.add_argument('name', type=str)
    edit_parser.add_argument('is_archive', type=ParseBool)


    def get(self):
        args: dict = self.parser.parse_args()
        body, status = get_project_details(args)
        return self.return_json(body, status)


    def post(self):
        args: dict = self.parser.parse_args()
        return self.return_json(*create_projects(args))
    

    def put(self):
        args: dict = self.edit_parser.parse_args()
        return self.return_json(*archive_project(args))
    
    
    def delete(self):
        args: dict = self.edit_parser.parse_args()
        return self.return_json(*delete_from_archive(args))
    

class Tasks(_Resource):
    
    parser = reqparse.RequestParser(trim=True)
    parser.add_argument('name', type=str)
    parser.add_argument('description', type=str)
    parser.add_argument('project_id', type=int)
    parser.add_argument('section_id', type=int)
    
    
    def post(self):
        args: dict = self.parser.parse_args()
        status = create_task(args)
        return self.return_status(status)


class Comments(_Resource):

    parser = reqparse.RequestParser(trim=True)
    parser.add_argument('task_id', type=int, required=True)
    parser.add_argument('text', type=str)

    edit_parser = reqparse.RequestParser(trim=True)
    edit_parser.add_argument('text', type=str)
    edit_parser.add_argument('comment_id', type=int, required=True)


    def get(self):
        args: dict = self.parser.parse_args()
        body, status = get_task_details(args)
        return self.return_json(body, status)
    
    
    def post(self):
        args: dict = self.parser.parse_args()
        body, status = create_comment(args)
        return self.return_json(body, status)
    
    
    def put(self):
        args: dict = self.edit_parser.parse_args()
        status = edit_comment(args)
        return self.return_status(status)
    

    def delete(self):
        args: dict = self.edit_parser.parse_args()
        status = delete_comment(args)
        return self.return_status(status)



class Sections(_Resource):
    
    parser = reqparse.RequestParser(trim=True)
    parser.add_argument('project_id', type=str, required=True)
    parser.add_argument('name', type=str, required=True)

    edit_parser = reqparse.RequestParser(trim=True)
    edit_parser.add_argument('name', type=str)
    edit_parser.add_argument('section_id', type=str, required=True)

    
    def post(self):
        args: dict = self.parser.parse_args()
        status = create_section(args)
        return self.return_status(status)
    

    def put(self):
        args: dict = self.edit_parser.parse_args()
        status = edit_section(args)
        return self.return_status(status)
    

    def delete(self):
        args: dict = self.edit_parser.parse_args()
        status = delete_section(args)
        return self.return_status(status)


api.add_resource(Tasks, '/tasks')
api.add_resource(ProjectList, '/project_list')
api.add_resource(Project, '/project')
api.add_resource(Comments, '/task/details')
api.add_resource(Sections, '/project/sections')


if __name__ == '__main__':
    app.run(host= API.get('host'), port= API.getint('port'), debug= API.getboolean('debug'))
