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

    values = tuple(args.values())
    query_insert = f'''INSERT INTO `Task` 
    {tuple(args)} VALUES '''

    query_insert = query_insert.replace("'", "") + str(values)
    insert(query_insert)

    return {'messege': "ok"}, 200


def get_tasks(args: dict) -> tuple:
    query_select = 'SELECT '
    'name, description, owner, project_id, create_date '
    'FROM `Task`' 
    f'WHERE project_id = {args["project_id"]}'

    project_data_select = ''
    
    table_keys = ['name', 'description', 'owner', 'project_id', 'create_date']
    data_to_show = select(query_select)
    send_list = []
    for el in data_to_show:
        el = list(el)
        el[-1] = el[-1].strftime(('%Y-%m-%d'))
        dict_to_append = dict(zip(table_keys, el))
        send_list.append(dict_to_append)

    tasks = {'tasks':send_list}
    return tasks, 200



def comment(args: dict):
    args['date'] = datetime.today().strftime(('%Y-%m-%d'))
    args['login'] = 'Ilusha Tester'

    values = tuple(args.values())
    query_insert = f'''INSERT INTO `Comments` 
    {tuple(args)} VALUES '''

    query_insert = query_insert.replace("'", "") + str(values)
    insert(query_insert)

    return {'messege': "ok"}, 200



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
    
    match args['is_archive']:
        case False:
            args['is_archive'] = 0
            query_update = f'UPDATE `Project` SET is_archive = {args["is_archive"]} WHERE id = {args["id"]}'
            update(query_update)

            return {'messege': "project moved from archive"}, 200
        
        case True:
            args['is_archive'] = 1
            query_update = f'UPDATE `Project` SET is_archive = {args["is_archive"]}, is_favorites = 0 WHERE id = {args["id"]}'
            update(query_update)

            return {'messege': "project moved to the archive"}, 200

    

def delete_from_archive(args: dict) -> tuple:
    query_select = f'SELECT id FROM `Project` WHERE is_archive = 1 AND id = {args["id"]}'    
    query_delete = f'DELETE FROM `Project` WHERE is_archive = 1 AND id = {args["id"]}'
    check_status = select(query_select)
    match check_status:
        case []:
            return {"messege": "the project is not archived"}, 400
        case _:
            delete(query_delete)
            return {'messege': "project deleted"}, 200



{
    "projects": 
    [
        {
        "project_name": "testing", 
        "is_favorites": "0", 
        "task_count": 2
        }
    ]
}

# create_task({'name':'idea', 'description':'empty_field', 'project_id':7})