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

    edit_parser = reqparse.RequestParser(trim=True)
    edit_parser.add_argument('project_id', type=int, required=True)
    edit_parser.add_argument('is_favorites', type=ParseBool)
    edit_parser.add_argument('name', type=str)


    def get(self):
        args: dict = self.edit_parser.parse_args()
        body, status = get_project_details(args['project_id'])
        return self.return_json(body, status)


    def post(self):
        args: dict = self.parser.parse_args()
        return self.return_json(*create_projects(args))
    

    def put(self):
        args: dict = self.edit_parser.parse_args()
        return self.return_json(*edit_project(args))
    
    
    def delete(self):
        args: dict = self.edit_parser.parse_args()
        return self.return_json(*delete_from_archive(args['project_id']))
    

class Tasks(_Resource):
    
    parser = reqparse.RequestParser(trim=True)
    parser.add_argument('name', type=str, required=True)
    parser.add_argument('description', type=str)
    parser.add_argument('project_id', type=int)
    parser.add_argument('section_id', type=int)

    edit_parser = reqparse.RequestParser(trim=True)
    edit_parser.add_argument('task_id', type=int, required=True)
    edit_parser.add_argument('name', type=str)
    edit_parser.add_argument('description', type=str)
    edit_parser.add_argument('project_id', type=int)
    edit_parser.add_argument('section_id', type=int)
    edit_parser.add_argument('status', type=ParseBool)

    
    def post(self):
        args: dict = self.parser.parse_args()
        status = create_task(args)
        return self.return_status(status)
    

    def get(self):
        args: dict = self.edit_parser.parse_args()
        body, status = get_task_details(args['task_id'])
        return self.return_json(body, status)
    

    def put(self):
        args: dict = self.edit_parser.parse_args()
        body, status = edit_task(args)
        return self.return_json(body, status)
    

    def delete(self):
        args: dict = self.edit_parser.parse_args()
        status = delete_task(args['task_id'])
        return self.return_status(status)


class Comments(_Resource):

    parser = reqparse.RequestParser(trim=True)
    parser.add_argument('task_id', type=int, required=True)
    parser.add_argument('text', type=str)

    edit_parser = reqparse.RequestParser(trim=True)
    edit_parser.add_argument('text', type=str)
    edit_parser.add_argument('comment_id', type=int, required=True)
    
    
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
        status = delete_comment(args['comment_id'])
        return self.return_status(status)



class Sections(_Resource):
    
    parser = reqparse.RequestParser(trim=True)
    parser.add_argument('project_id', type=int, required=True)
    parser.add_argument('name', type=str, required=True)

    edit_parser = reqparse.RequestParser(trim=True)
    edit_parser.add_argument('name', type=str)
    edit_parser.add_argument('section_id', type=int, required=True)

    
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
        status = delete_section(args['section_id'])
        return self.return_status(status)
    

class ChangeSectionOrder(_Resource):

    parser = reqparse.RequestParser(trim=True)
    parser.add_argument('project_id', type=int, required=True)
    parser.add_argument('sections', type=dict, action='append')

    def put(self):
        args: dict = self.parser.parse_args()
        status = change_section_order(args)
        return self.return_status(status)
    

class ChangeArchiveStatus(_Resource):

    parser = reqparse.RequestParser(trim=True)
    parser.add_argument('project_id', type=int, required=True)
    parser.add_argument('is_archive', type=ParseBool, required=True)
    
    def put(self):
        args: dict = self.parser.parse_args()
        status = change_archive_status(args)
        return self.return_status(status)


api.add_resource(Tasks, '/task')
api.add_resource(ProjectList, '/project_list')
api.add_resource(Project, '/project')
api.add_resource(Comments, '/comment')
api.add_resource(Sections, '/section')
api.add_resource(ChangeSectionOrder, '/section_order')
api.add_resource(ChangeArchiveStatus, '/change_archive_status')


if __name__ == '__main__':
    app.run(host= API.get('host'), port= API.getint('port'), debug= API.getboolean('debug'))
