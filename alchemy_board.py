from models import *
from my_engine import Session
from sqlalchemy import update, select, delete
from pprint import pprint


def get_project_details(project_id):

    with Session() as session:

        sections: Sections = session.query(Sections).filter(Sections.project_id==project_id)
        section_list = list()
        # идем циклом по полученым разделам
        for section in sections:
            section: Sections
            # создаем словарь, куда пихаем нужные нам данные
            section_dict = {
                "id": section.id,
                "name": section.name,
                "tasks": list()
            }
            # далее идем пока задачам текущего раздела
            # для которого также создаем словарь 
            for task in section.Task:
                task: Task
                task_dict = {
                    "description": task.description,
                    "name": task.name,
                    "status": task.status,
                    "task_id": task.id,
                    "comments_count": len(task.Comments)
                }
                # добавляем полученный словарь в список
                # который хранится в предыдущем словаре в ключе "tasks" 
                section_dict['tasks'].append(task_dict)
            # результат добавляем в список разделов
            section_list.append(section_dict)
        # создаем словарь с нужными данными, который отдаем на фронт
        project_dict = {
            "project_id": project_id,
            "project_name": section.Project.name,
            "is_favorites": section.Project.is_favorites,
            "sections":section_list
        }

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
                    "section_id": section.id,
                    "name": section.name,
                    "project_id": section.project_id
                }
                project_dict['sections'].append(section_dict)
            
            project_list['projects'].append(project_dict)

    return project_list, 200


def create_project(args: dict):

    with Session() as session:
        pass



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

        if task.Project:
            task_dict['project_name'] = task.Project.name
            task_dict['section_id'] = task.Section.id
            task_dict['section_name'] = task.Section.name

        for comment in task.Comments:
            comment = comment._asdict()
            comment.pop("task_id")
            task_dict['comments'].append(comment)
        task_dict['comments'] = [comment._asdict() for comment in task.Comments]

    return task_dict, 200


def create_task(args: dict):
    args['owner'] = "Alchemy Ilusha"
    with Session() as session:
        # если нам передали id раздела, то project_id мы подставляем сами
        if args.get('section_id'):
            section: Sections = session.get(Sections, args['section_id'])
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
            # если такой проект есть, то по умолчанию переносить задачу вне разделов
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



test_dict = {
    "task_id": 103,
    "description": "update ",
}

# pprint(get_task_details(88))
# pprint(edit_task(test_dict))
# pprint(get_project_details(32))