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


def get_task_details(task_id) -> tuple:

    select_tasks = f'SELECT id, project_id FROM Task WHERE id = {task_id}'
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
        Task.id = {task_id}'''
    

    select_comments = f'''
    SELECT 
        login, 
        create_at, 
        text,
        id 
    FROM 
        `Comments` 
    WHERE 
        Comments.task_id = {task_id}'''


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


def create_task(args: dict):
    args['owner'] = 'Ilusha Tester'

    if not args['project_id']: 
        args.pop('project_id')
        args.pop('section_id')

    elif not args.get('section_id'):
        args.pop('section_id')

    if not args['description']:
        args.pop('description')
    
    values = tuple(args.values())
    query_insert = f'''INSERT INTO `Task` 
    {tuple(args)} VALUES '''

    query_insert = query_insert.replace("'", "") + str(values)
    insert(query_insert)

    return 200


def edit_task(args: dict):

    query_update = "UPDATE `Task` SET"
    query_list = list()

    if args['project_id']:
        query_select = f"SELECT id FROM `Project` WHERE id = {args['project_id']}"
        if not select(query_select):
            return {"message": "Проект не найден"}, 404
        query_list.append(f" project_id = {args['project_id']}")
    else:
        query_list.append(" project_id = NULL")

    if args['name']:
        query_list.append(f" name = '{args['name']}'")

    if args['description'] == "" or args['description']:
        query_list.append(f" description = '{args['description']}'")
    
    if args['section_id']:
        query_list.append(f" section_id = {args['section_id']}")

    query_update += ",".join(query_list)
    query_update += f" WHERE id = {args['task_id']}"

    update(query_update)

    return {"message": "ok"}, 200


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
        if project_data:
            project_data = project_data[0][0]
        else:
            return {'message': 'Проект не найден'}, 404


    select_sections = f'''
    SELECT 
        name, 
        id 
    FROM 
        `Sections` 
    WHERE 
    '''
    
    task_select = f'''
    SELECT
        Task.name,
        Task.section_id,
        Task.id,
        COUNT(Comments.id)
    FROM
        `Task`
    LEFT JOIN `Comments` ON Task.id = Comments.task_id
    WHERE
	    %s
    GROUP BY
        Task.name,
        Task.section_id,
        Task.id 
    '''
    
    section_list = []
    external_tasks = []
    task_keys = ['name', 'section_id', 'task_id', 'comments_count']

    # если указан poject_id, мы проходимся по разделам и задачам
    # если находим совпадения по id раздела, добавляем задачу в список задач этого раздела 
    # если у задачи section_id не указан, мы добавляем ее в список задач ПРОЕКТА вне всех разделов (external_tasks)
    if args['project_id']:
        task_select = task_select % f'project_id = {args["project_id"]}'
        select_sections += f'project_id = {args["project_id"]}'
        sections_data = select(select_sections)
        tasks = select(task_select)

        sections = dict()
        for sec in sections_data:
            sections[sec[1]] = {
                            "id":sec[1],
                            "name":sec[0],
                            "tasks":list()
                               }
        for task in tasks:
            task_dict = dict(zip(task_keys, task))
            if task_dict['section_id']:
                sections[task_dict.pop('section_id')]["tasks"].append(task_dict)
            elif not task_dict['section_id']:
                task_dict.pop('section_id')
                if task_dict not in external_tasks:
                    external_tasks.append(task_dict)
    
        section_list = list(sections.values())
    
    else:
        task_select = task_select % 'project_id IS NULL'
        tasks = select(task_select)

        for task in tasks:
            task_dict = dict(zip(task_keys, task))
            task_dict.pop('section_id')
            external_tasks.append(task_dict)

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


def delete_section(section_id):
    query_delete = f'''
    DELETE
    FROM 
        `Sections` 
    WHERE 
        id = {section_id}
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

    query_select = f'SELECT id FROM `Task` WHERE id = {args["task_id"]}'
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


def delete_comment(comment_id):
    query_delete = f'''
    DELETE
    FROM 
        `Comments` 
    WHERE 
        id = {comment_id}
    '''
    delete(query_delete)

    return 200


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
    query_section = 'SELECT id, name, project_id FROM `Sections` ORDER BY project_id'

    query_project_list = '''
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
    ORDER BY 
        Project.id
    '''
    proj_keys = ['project_name', 'is_favorites', 'id', 'is_archive' , 'task_count']
    section_keys = ['section_id', 'name', 'project_id']

    project_list = select(query_project_list)

    section_list = select(query_section)
    project_dict = dict()
    for proj in project_list:
        custom_project_dict = dict(zip(proj_keys, proj))
        custom_project_dict['is_favorites'] = bool(custom_project_dict['is_favorites'])
        custom_project_dict['is_archive'] = bool(custom_project_dict['is_archive'])
        custom_project_dict['sections'] = list()

        project_dict[proj[2]] = custom_project_dict
        
    for section in section_list:
        section_dict = dict(zip(section_keys, section))
        project_dict[section_dict['project_id']]['sections'].append(section_dict)

    projects = {'projects':list(project_dict.values())}
    return projects, 200


def archive_project(args: dict) -> tuple:
    
    query_update = "UPDATE `Project` SET"
    query_list = list()

    check_project = f'SELECT id FROM Project WHERE id = {args["project_id"]}'
    select_id = select(check_project)
    if not select_id:
        return {'message':'Проект не найден'}, 404

    if args['is_archive']:
        query_update = f'UPDATE `Project` SET is_archive = {int(args["is_archive"])}, is_favorites = 0 WHERE id = {args["project_id"]}'
        update(query_update)
        return {'message': "ok"}, 200

    if args['name']:
        query_list.append(f" name = '{args['name']}'")

    if args['is_favorites']:
        query_list.append(f" is_favorites = {int(args['is_favorites'])}")
    else:
        query_list.append(f" is_favorites = {int(args['is_favorites'])}")

    query_update += ",".join(query_list) + f" WHERE id = {args['project_id']}"

    update(query_update)

    return {'message': "ok"}, 200

    

def delete_from_archive(project_id) -> tuple:
    query_select = f'SELECT id FROM `Project` WHERE is_archive = 1 AND id = {project_id}'    
    query_delete = f'DELETE FROM `Project` WHERE is_archive = 1 AND id = {project_id}'
    check_status = select(query_select)
    if check_status:
        delete(query_delete)
        return {'message': "Проект удален"}, 200
    
    return {"message": "Проект не в архиве"}, 400


