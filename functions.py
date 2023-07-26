from mysql.connector import connect, Error
from config import MYSQL
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json


def insert(query):
    try:
        with connect(
            host = MYSQL.get('host'),
            user = MYSQL.get('user'),
            password = MYSQL.get('password'),
            database = MYSQL.get('database')
        ) as connection:
            cursor = connection.cursor()
            cursor.execute(query)
            connection.commit()
    except Error as e:
        print(e)
    finally:
        cursor.close()
        connection.close()


def update(query):
    try:
        connection = connect(
            host = MYSQL.get('host'),
            user = MYSQL.get('user'),
            password = MYSQL.get('password'),
            database = MYSQL.get('database')
        )
        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()
    except Error as e:
        print(e)
    finally:
        cursor.close()
        connection.close()


def delete(query):
    try:
        connection = connect(
            host = MYSQL.get('host'),
            user = MYSQL.get('user'),
            password = MYSQL.get('password'),
            database = MYSQL.get('database')
        )
        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()
    except Error as e:
        print(e)
    finally:
        cursor.close()
        connection.close()


def select(query):
    try:
        with connect(
            host = MYSQL.get('host'),
            user = MYSQL.get('user'),
            password = MYSQL.get('password'),
            database = MYSQL.get('database')
        ) as connection:
            cursor = connection.cursor()
            cursor.execute(query)
            return cursor.fetchall()
    except Error as e:
        print(e)
    finally:
        cursor.close()
        connection.close()


def create_projects(args: dict) -> tuple:
    args['date'] = datetime.today().strftime(('%Y-%m-%d'))

    args['is_favorites'] = 0 if not args['is_favorites'] else 1
    values = tuple(args.values())
    query_insert = f'''
    INSERT INTO `Project` 
    {tuple(args)} VALUES 
    '''
    query_insert = query_insert.replace("'", "") + str(values)    
    insert(query_insert) 

    return {'messege': "ok"}, 200


def project_list(user='Ilusha'):

    query_select = f'SELECT id, name FROM Project WHERE owner = {user}'
    select_proj = select(query_select)
    send_list = []
    table_keys = ['id', 'name']
    for i in select_proj:
        dict_to_append = dict(zip(table_keys, i))
        send_list.append(dict_to_append)

    send_dict = {'project_list':send_list}

    return send_dict, 200


def create_task(args: dict):
    args['create_date'] = datetime.today().strftime(('%Y-%m-%d'))
    args['owner'] = 'Ilusha Tester'
    
    if not args['project_id']: 
        args.pop('project_id')
    
    values = tuple(args.values())
    query_insert = f'''INSERT INTO `Task` 
    {tuple(args)} VALUES '''

    query_insert = query_insert.replace("'", "") + str(values)
    insert(query_insert)

    return {'messege': "ok"}, 200


def get_tasks(args: dict) -> tuple:

    select_project_info = f'''SELECT name, id FROM Project
    WHERE id = {args['project_id']}'''

    project_data = select(select_project_info)

    if not project_data and args['project_id']:
        return {'message': 'project not found'}, 404

    query_select = f'''
    SELECT  
    name, 
    description, 
    owner, 
    create_date, 
    id  
    FROM `Task` 
    WHERE project_id = {args["project_id"]}
    '''

    select_incoming = '''SELECT 
    name, 
    description, 
    owner, 
    create_date, 
    id  
    FROM `Task` 
    WHERE project_id IS NULL''' 

    table_keys = ['name', 'description', 'owner', 'create_date', 'task_id']
    if args['project_id']:
        data_to_show = select(query_select)
    else:
        data_to_show = select(select_incoming)
    
    task_list = []
    for task in data_to_show:
        dict_to_append = dict(zip(table_keys, task))
        dict_to_append['create_date'] = dict_to_append['create_date'].strftime(('%Y-%m-%d'))
        task_list.append(dict_to_append)

    # делаю через условие, потому что если project_data пустой, то будет ошибка при попытке обратиться по индексу
    if args['project_id']:
        final_result = {'project_name':project_data[0][0], 'project_id':args['project_id'], 'tasks':task_list}
    else:
        final_result = {'project_name':'Входящие', 'project_id':None, 'tasks': task_list}

    return final_result, 200


def comment(args: dict):
    args['date'] = datetime.today().strftime(('%Y-%m-%d'))
    args['login'] = 'Ilusha Tester'

    values = tuple(args.values())
    query_insert = f'''INSERT INTO `Comments` 
    {tuple(args)} VALUES '''

    query_insert = query_insert.replace("'", "") + str(values)
    insert(query_insert)

    return {'messege': "ok"}, 200


def get_comments(args: dict) -> tuple:
    args['login'] = 'Ilusha Tester'

    select_tasks = f'SELECT id, project_id FROM Task WHERE id = {args["task_id"]}'
    check_project_id = select(select_tasks)

    if not check_project_id:
        return {'message': 'task not found'}, 404

    select_task_info = f'''
    SELECT Task.owner, 
    Task.name, 
    Task.description, 
    Task.create_date, 
    Task.project_id, 
    Project.name 
    FROM `Task` 
    JOIN `Project` 
    ON Project.id = Task.project_id 
    WHERE Task.id = {args['task_id']}'''

    select_incoming_info = f'''SELECT 
    Task.owner, 
    Task.name, 
    Task.description, 
    Task.create_date 
    FROM `Task` 
    WHERE Task.id = {args["task_id"]}'''

    select_comments = f'''SELECT 
    Comments.login, 
    Comments.create_at, 
    Comments.text 
    FROM `Comments` 
    JOIN `Task` 
    ON Comments.task_id = Task.id 
    WHERE Comments.task_id = {args['task_id']}'''


    if check_project_id[0][1]:
        task_details = select(select_task_info)
    else:
        task_details = select(select_incoming_info)

    tasks_comments = select(select_comments)

    table_keys = ['login', 'create_at', 'text']
    
    comment_list = []
    for comment in tasks_comments:
        dict_to_append = dict(zip(table_keys, comment))
        dict_to_append['create_at'] = dict_to_append['create_at'].strftime(('%Y-%m-%d'))
        comment_list.append(dict_to_append)

    if check_project_id[0][1]:
        comments_to_send = {'project_name':task_details[0][5],
                            'project_id':task_details[0][4],
                            'task_name':task_details[0][1], 
                            'task_id':args['task_id'], 
                            'task_owner':task_details[0][0], 
                            'description':task_details[0][2], 
                            'create_date':task_details[0][3], 
                            'comments':comment_list}
    else:
        comments_to_send = {'project_name':'Входящие',
                            'project_id':None,
                            'task_name':task_details[0][1], 
                            'task_id':args['task_id'], 
                            'task_owner':task_details[0][0], 
                            'description':task_details[0][2], 
                            'create_date':task_details[0][3], 
                            'comments':comment_list}
    
    comments_to_send['create_date'] = comments_to_send['create_date'].strftime(('%Y-%m-%d'))

    return comments_to_send, 200



def user(args: dict):
    hash_psw = generate_password_hash(args['password'])
    args['password'] = hash_psw

    args['date_cr'] = datetime.today().strftime(('%Y-%m-%d'))

    values = tuple(args.values())
    query_insert = f'''INSERT INTO `Users` 
    {tuple(args)} VALUES '''

    query_insert = query_insert.replace("'", "") + str(values)
    insert(query_insert)

    return {'messege': "ok"}, 200


def get_projects() -> tuple:
    query_select = '''
    SELECT Project.name, Project.is_favorites, Project.id, Project.is_archive, COUNT(Task.id) 
    FROM `Project` 
    LEFT JOIN Task 
    ON 
    Project.id = Task.project_id 
    GROUP BY
    Project.name, Project.is_favorites, Project.id, Project.is_archive
    '''
    table_keys = ['project_name', 'is_favorites', 'id', 'is_archive' , 'task_count']

    data_to_show = select(query_select)
    send_list = []
    for el in data_to_show:
        el = list(el)
        el[1] = bool(el[1])

        el[-2] = bool(el[-2])

        dict_to_append = dict(zip(table_keys, el))
        send_list.append(dict_to_append)

    projects = {'projects':send_list}
    return projects, 200


def archive_project(args: dict) -> tuple:
    
    check_project = f'SELECT id FROM Project WHERE id = {args["project_id"]}'
    select_id = select(check_project)
    if not select_id:
        return {'message':'project not found'}, 404

    match args['is_archive']:
        case False:
            args['is_archive'] = 0
            query_update = f'UPDATE `Project` SET is_archive = {args["is_archive"]} WHERE id = {args["project_id"]}'
            update(query_update)

            return {'messege': "project moved from archive"}, 200
        
        case True:
            args['is_archive'] = 1
            query_update = f'UPDATE `Project` SET is_archive = {args["is_archive"]}, is_favorites = 0 WHERE id = {args["project_id"]}'
            update(query_update)

            return {'messege': "project moved to the archive"}, 200

    

def delete_from_archive(args: dict) -> tuple:
    query_select = f'SELECT id FROM `Project` WHERE is_archive = 1 AND id = {args["project_id"]}'    
    query_delete = f'DELETE FROM `Project` WHERE is_archive = 1 AND id = {args["project_id"]}'
    check_status = select(query_select)
    match check_status:
        case []:
            return {"messege": "the project is not archived"}, 400
        case _:
            delete(query_delete)
            return {'messege': "project deleted"}, 200


