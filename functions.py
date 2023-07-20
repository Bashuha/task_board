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


def create_projects(args: dict) -> tuple:
    args['owner'] = 'Ilusha'
    args['date'] = datetime.today().strftime(('%Y-%m-%d'))

    args['is_favorites'] = 0 if not args['is_favorites'] else 1
    values = tuple(args.values())
    query_insert = f'''
    INSERT INTO `Project` 
    {tuple(args)} VALUES '''

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
    SELECT Project.name, Project.is_favorites, Project.id, COUNT(Task.id) 
    FROM `Project` 
    LEFT JOIN Task 
    ON 
    Project.id = Task.project_id 
    GROUP BY
    Project.name, Project.is_favorites, Project.id
    '''
    table_keys = ['project_name', 'is_favorites', 'id', 'task_count']

    data_to_show = select(query_select)
    send_list = []
    for i in data_to_show:
        i = list(i)
        if i[1] == 0:
            i[1] = False
        else:
            i[1] = True
        dict_to_append = dict(zip(table_keys, i))
        send_list.append(dict_to_append)

    projects = {'projects':send_list}
    return projects, 200


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