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

    args['is_favorites'] = int(args['is_favorites'])
    values = tuple(args.values())
    query_insert = f'''
    INSERT INTO `Project` 
    {tuple(args)} VALUES 
    '''
    query_insert = query_insert.replace("'", "") + str(values)    
    insert(query_insert) 

    return {'message': "ok"}, 200


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
    args['owner'] = 'Ilusha Tester'

# вот тут хотелось бы покрсоте сделать, но пока до этого не добрался
# можно сказать, что это набросок
    if not args['project_id']: 
        args.pop('project_id')
        args.pop('section_id')

    if not args['section_id']:
        args.pop('section_id')

    if not args['description']:
        args.pop('description')
    
    values = tuple(args.values())
    query_insert = f'''INSERT INTO `Task` 
    {tuple(args)} VALUES '''

    query_insert = query_insert.replace("'", "") + str(values)
    insert(query_insert)

    return 200


def get_project_details(args: dict) -> tuple:

    select_project_info = f'''
    SELECT 
        name, 
        id 
    FROM 
        `Project`
    WHERE 
        id = {args['project_id']}
    '''

    project_data = None
    if args['project_id']:
        project_data = select(select_project_info)
        project_data = project_data[0][0] if project_data else None

    if not project_data and args['project_id']:
        return {'message': 'Проект не найден'}, 404

    select_sections = f'''
    SELECT 
        name, 
        id 
    FROM 
        `Sections` 
    WHERE 
    '''
    
    query_select = f'''
    SELECT  
        name, 
        description, 
        owner, 
        create_date, 
        section_id, 
        id 
    FROM 
        `Task` 
    WHERE 
    '''
    
    section_list = []
    external_tasks = []
    table_keys = ['name', 'description', 'owner', 'create_date', 'section_id', 'task_id']

    # если указан poject_id, мы проходимся по разделам и задачам
    # если находим совпадения по id раздела, добавляем задачу в список задач этого раздела 
    # если у задачи section_id не указан, мы добавляем ее в список задач ПРОЕКТА вне всех разделов (external_tasks)
    if args['project_id']:
        query_select += f'project_id = {args["project_id"]}'
        select_sections += f'project_id = {args["project_id"]}'
        sections_data = select(select_sections)
        data_to_show = select(query_select)

        for section in sections_data:
            section_dict = {}
            task_list = []
            for task in data_to_show:
                dict_to_append = dict(zip(table_keys, task))
                dict_to_append['create_date'] = dict_to_append['create_date'].strftime(('%Y-%m-%d'))
            
                if section[1] == dict_to_append['section_id']:
                    task_list.append(dict_to_append)
                elif not dict_to_append['section_id'] and dict_to_append not in external_tasks:
                    external_tasks.append(dict_to_append)

            section_dict = {'section_name': section[0], 'section_id': section[1], 'tasks': task_list}
            section_list.append(section_dict)

    else:
        query_select += 'project_id IS NULL'
        data_to_show = select(query_select)

        for task in data_to_show:
            dict_to_append = dict(zip(table_keys, task))
            dict_to_append['create_date'] = dict_to_append['create_date'].strftime(('%Y-%m-%d'))
            external_tasks.append(dict_to_append)
        

    final_result = {'project_name': project_data or 'Входящие', 
                    'project_id': args['project_id'],
                    'tasks': external_tasks,  
                    'sections': section_list}

    return final_result, 200


def create_section(args: dict):

    values = tuple(args.values())
    query_insert = f'INSERT INTO `Sections` {tuple(args)} VALUES '
    query_insert = query_insert.replace("'", "") + str(values)
    
    insert(query_insert)

    return 200


def delete_section(args: dict):
    query_delete = f'''
    DELETE
    FROM 
        `Sections` 
    WHERE 
        id = {args["section_id"]}
    '''
    delete(query_delete)

    return 200


def edit_section(args: dict):
    query_update = f'''
    UPDATE 
        `Sections` 
    SET 
        name = "{args['name']}" 
    WHERE 
        id = {args['section_id']}
    '''
    
    update(query_update)

    return 200


def create_comment(args: dict):
    args['login'] = 'Ilusha Tester'

    query_select = f'''SELECT id FROM `Task` WHERE id = {args["task_id"]}'''
    check_task_id = select(query_select)

    if not check_task_id:
        return {'message':'Задача не найдена'}, 404
    

    values = tuple(args.values())
    query_insert = f'''INSERT INTO `Comments` 
    {tuple(args)} VALUES '''

    query_insert = query_insert.replace("'", "") + str(values)
    insert(query_insert)

    return {'message':'ok'}, 200


def edit_comment(args: dict):
    query_update = f'''
    UPDATE 
        `Comments` 
    SET 
        text = "{args['text']}" 
    WHERE 
        id = {args['comment_id']}
    '''
    
    update(query_update)

    return 200


def delete_comment(args: dict):
    query_delete = f'''
    DELETE
    FROM 
        `Comments` 
    WHERE 
        id = {args['comment_id']}
    '''
    delete(query_delete)

    return 200



def get_task_details(args: int) -> tuple:

    select_tasks = f'SELECT id, project_id FROM Task WHERE id = {args["task_id"]}'
    check_project_id = select(select_tasks)

    if not check_project_id:
        return {'message': 'Задача не найдена'}, 404

    select_task_info = f'''
    SELECT 
        Project.name, 
        Task.project_id, 
        Task.name, 
        Task.id, 
        Task.owner, 
        Task.description, 
        Task.create_date,
        Task.section_id 
    FROM 
        `Task` 
    LEFT JOIN 
        `Project` 
    ON 
        Project.id = Task.project_id 
    WHERE 
        Task.id = {args["task_id"]}'''
    

    select_comments = f'''
    SELECT 
        login, 
        create_at, 
        text,
        id 
    FROM 
        `Comments` 
    WHERE 
        Comments.task_id = {args["task_id"]}'''


    # создаем два списка ключей для дальнейшего преобразования в словари
    table_keys = ['login', 'create_at', 'text', 'id']
    
    project_keys = ['project_name', 'project_id', 'task_name', 'task_id', 'task_owner', 'description', 'create_date', 'section_id']
    task_info = select(select_task_info)
    comments_to_send = dict(zip(project_keys, task_info[0]))
    
    # делаем запрос в таблицу для получения комментов и из каждой строки создаем словарь для отправки на фронт
    # словари в свою очередь добавляем в список comment_list
    tasks_comments = select(select_comments)
    comment_list = []
    for comment in tasks_comments:
        dict_to_append = dict(zip(table_keys, comment))
        dict_to_append['create_at'] = dict_to_append['create_at'].strftime(('%Y-%m-%d'))
        comment_list.append(dict_to_append)

    comments_to_send['comments'] = comment_list
    comments_to_send['project_name'] = comments_to_send['project_name'] or 'Входящие'
    
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

    return {'message': "ok"}, 200


def get_projects() -> tuple:
    query_select = '''
    SELECT 
        Project.name, 
        Project.is_favorites, 
        Project.id, 
        Project.is_archive, 
        COUNT(Task.id) 
    FROM 
        `Project` 
    LEFT JOIN 
        `Task` 
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
        return {'message':'Проект не найден'}, 404

    query_update = f'UPDATE `Project` SET is_archive = {int(args["is_archive"])}, is_favorites = 0 WHERE id = {args["project_id"]}'
    update(query_update)

    return {'message': "ok"}, 200

    

def delete_from_archive(args: dict) -> tuple:
    query_select = f'SELECT id FROM `Project` WHERE is_archive = 1 AND id = {args["project_id"]}'    
    query_delete = f'DELETE FROM `Project` WHERE is_archive = 1 AND id = {args["project_id"]}'
    check_status = select(query_select)
    match check_status:
        case []:
            return {"message": "Проект не в архиве"}, 400
        case _:
            delete(query_delete)
            return {'message': "Проект удален"}, 200


