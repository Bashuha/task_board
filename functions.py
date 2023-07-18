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


def create_projects(args: dict):
    args['date'] = datetime.today().strftime(('%Y-%m-%d'))
    args['proj_owner'] = 'Ilusha Tester'

    values = tuple(args.values())
    query_insert = f'''INSERT INTO `Project` 
    {tuple(args)} VALUES '''

    query_insert = query_insert.replace("'", "") + str(values)    
    insert(query_insert)

    return {'messege': "ok"}, 200


def create_task(args: dict):
    args['create_date'] = datetime.today().strftime(('%Y-%m-%d'))
    args['owner'] = 'Ilusha Tester'

    values = tuple(args.values())
    query_insert = f'''INSERT INTO `Task` 
    {tuple(args)} VALUES '''

    query_insert = query_insert.replace("'", "") + str(values)
    insert(query_insert)

    return {'messege': "ok"}, 200


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


def get_projects():
    query_select = '''
    SELECT Project.project_name, Project.is_favorites, 
    COUNT(Task.project_name) 
    FROM `Project` JOIN Task ON Project.project_name = Task.project_name 
    WHERE Task.project_name = 'testing' 
    GROUP BY 
    Project.project_name, Project.is_favorites
    '''
    table_keys = ['project_name', 'is_favorites', 'task_count']

    data_to_show = select(query_select)
    send_list = []
    for i in data_to_show:
        dict_to_append = dict(zip(table_keys, i))
        send_list.append(dict_to_append)

    projects = {'projects':send_list}
    return json.dumps(projects), 200

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
