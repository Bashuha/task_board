from models import *
from my_engine import Session
from sqlalchemy import update, select, delete
from pprint import pprint


def get_project_details(project_id):

    with Session() as session:
        project: Project = session.get(Project, project_id)
        section_dict = dict()
        
        project_dict = {
            "project_id": project_id,
            "project_name": "Входящие",
            "tasks": list()
        }
        if project:
            project_dict["is_favorites"] = project.is_favorites
            project_dict['project_name'] = project.name
        
            for section in project.Sections:
                section: Sections
                section_dict[section.id] = {
                    "id": section.id,
                    "name": section.name,
                    "tasks": list()
                }
        task_list: list[Task] = session.query(Task).filter(Task.project_id==project_id)
        for task in task_list:
            task: Task
            task_dict = {
                "description": task.description,
                "name": task.name,
                "status": task.status,
                "id": task.id,
                "comments_count": len(task.Comments)
            }
            if task.section_id:
                section_dict[task.section_id]['tasks'].append(task_dict)
            else:
                project_dict['tasks'].append(task_dict)

        if project:
            project_dict['sections'] = list(section_dict.values())

    return project_dict, 200


def get_projects():

    with Session() as session:
        projects: list[Project] = session.query(Project)
        project_list = {"projects": list()}
        for project in projects:
            project: Project

            project_dict = {
                "project_name": project.name,
                "is_favorites": project.is_favorites,
                "is_archive": project.is_archive,
                "id": project.id,
                "task_count": len(project.Task),
                "sections": list()
            }

            for section in project.Sections:
                section: Sections
                section_dict = {
                    "id": section.id,
                    "name": section.name,
                    "project_id": section.project_id
                }
                project_dict['sections'].append(section_dict)
            
            project_list['projects'].append(project_dict)

    return project_list, 200


def create_project(args: dict):

    with Session() as session:
        session.add(Project(**args))
        session.commit()
    
    return 200


def edit_project(args: dict):

    with Session() as session:
        project: Project = session.get(Project, args['project_id'])
        if not project:
            return {"message": "Проект не найден"}, 404
        else:
            if args.get('name'):
                project.name = args['name']
            if args.get('is_favorites') != None:
                project.is_favorites = args['is_favorites']

    return {"message": "ok"}, 200


def change_archive_status(args: dict):
    with Session() as session:
        project: Project = session.get(Project, args['project_id'])
        project.is_archive = args['is_archive']
        project.is_favorites = False
        session.commit()

    return 200


def delete_from_archive(project_id):
    with Session() as session:
        project: Project = session.get(Project, project_id)
        if project:
            if project.is_archive:
                session.execute(delete(Project).where(Project.id==project_id))
                session.commit()
            else:
                return {"message": "Проект не в архиве"}, 400

    return {"message": "Проект удален"}, 200


def create_section(args: dict):
    with Session() as session:
        project: Project = session.get(Project, args['project_id'])
        if project:
            args['order_number'] = len(project.Sections) + 1
            session.add(Sections(**args))
            session.commit()
        else:
            return {"message": "Проект не найден"}, 404
        
    return {"message": "ok"}, 200


def edit_section(args: dict):
    with Session() as session:
        section: Sections = session.get(Sections, args['section_id'])
        if section:
            section.name = args['name']
            session.commit()
        else:
            return {"message": "Раздел не найден"}, 404

    return {"message": "ok"}, 200


def delete_section(section_id):
    with Session() as session:
        session.execute(delete(Sections).where(Sections.id==section_id))
        session.commit()

    return 200


def get_task_details(task_id):

    with Session() as session:
        task: Task = session.query(Task).filter(Task.id==task_id).one()

        task_dict = {
            "comments": list(),
            "create_date": task.create_date.strftime('%Y-%m-%d'),
            "description": task.description,
            "project_id": task.project_id,
            "project_name": "Входящие",
            "section_id": None,
            "section_name": None,
            "status": task.status,
            "task_id": task.id,
            "task_name": task.name,
            "task_owner": task.owner
        }

        if task.project_id:
            task_dict['project_name'] = task.Project.name
            if task.section_id:
                task_dict['section_id'] = task.section_id
                task_dict['section_name'] = task.Section.name

        for comment in task.Comments:
            comment = comment._asdict()
            comment.pop("task_id")
            task_dict['comments'].append(comment)

    return task_dict, 200


def create_task(args: dict):
    args['owner'] = "Alchemy Ilusha"
    with Session() as session:
        # если нам передали id раздела, то project_id мы подставляем сами
        if args.get('section_id'):
            section: Sections = session.get(Sections, args['section_id'])
            # если такой раздел существует, то берем оттуда project_id
            if section:
                args["project_id"] = section.project_id
            else:
                {'message': 'Проект не найден'}, 404
        # если передали только project_id, то мы просто проверяем его наличие
        elif args.get('project_id'):
            project: Project = session.get(Project, args['project_id'])
            if not project:
                return {'message': 'Проект не найден'}, 404
           
        session.add(Task(**args))
        session.commit()

    return {"message": "ok"}, 200


def edit_task(args: dict):
    with Session() as session:
        task: Task = session.get(Task, args['task_id'])
        # если нам передают id раздела, то id проекта мы присваиваем сами
        if args.get('section_id'):
            # обработка идет только в случае если передали не None
            # в таком случае мы обращаемся к указанному разделу и берем оттуда id проекта
            section: Sections = session.get(Sections, args['section_id'])
            if section:
                args["project_id"] = section.project_id
            # если запрос вернул None, значит такого раздела в базе нет
            else:
                return {"message": "Раздел не найден"}, 404
        # если id раздела не передают, то нужно проверить существование переданного проекта
        elif args.get('project_id'):
            project: Project = session.get(Project, args['project_id'])
            # если такой проект есть, то по умолчанию переносим задачу вне разделов
            if project:
                args['section_id'] = None
            else:
                return {"message": "Проект не найден"}, 404
        # далее просто обновляем все данные в объекте Task и комитим
        for key, value in args.items():
            if key != 'task_id':
                exec('task.%s = value' % key)

        session.commit()

    return {"message": "ok"}, 200


def delete_task(task_id):
    with Session() as session:
        session.execute(delete(Task).where(Task.id == task_id))
        session.commit()

    return 200


def create_comment(args: dict):
    with Session() as session:
        task: Task = session.get(Task, args['task_id'])
        if task:
            args['login'] = "Ilusha"
            session.add(Comments(**args))
            session.commit()
        else:
            return {"message": "Задача не найдена"}, 404
        
    return {"message": "ok"}, 200


def edit_comment(args: dict):
    with Session() as session:
        comment: Comments = session.get(Comments, args['comment_id'])
        if comment:
            comment.text = args['text']
            session.commit()
        else:
            return {"message": "Комментарий не найден"}, 404
    
    return {"message": "ok"}, 200


def delete_comment(comment_id):
    with Session() as session:
        session.execute(delete(Comments).where(Comments.id==comment_id))
        session.commit()

    return 200


def change_section_order(args: dict):
    with Session() as session:
        new_order_list = list()
        # создаем словарь из нового списка id и генерируем новый порядковый номер
        for number, sec_id in enumerate(args['sections'], start=1):
            order_dict = {"id": sec_id['id'], "order_number": number}
            # добавляем полученный словарь в список для UPDATE
            new_order_list.append(order_dict)
        # одним запросом обновляем порядок, используя наш список словарей
        session.execute(update(Sections).where(Sections.project_id==args['project_id']), new_order_list, execution_options={"synchronize_session": None})
        session.commit()
        # мы исользовали "массовое обновление по первичному ключу" и из-за того, что мы 
        # добавили дополнительный "where" критерий в виде project_id, нам необходимо
        # прописать execution_options

    return 200



test_dict = {
    "sections":
    [
    {"id":20},
    {"id":19},
    {"id":9}
    ],
    "project_id":7
}

# pprint(change_section_order(test_dict))
# pprint(get_task_details(88))
# pprint(create_section(test_dict))
# pprint(get_project_details(7))