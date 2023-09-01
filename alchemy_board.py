from models import *
from my_engine import Session
from sqlalchemy import update, select
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
        projects_id: list = session.scalars(select(Project.id)).all()
        # сначала берем список, где id всех существующих проектов
        # потом проверяем наличие переданного id в нашем списке
        # добавляем в бд только если id проекта есть в нашем списке 
        # или если переданный id == None (это для "входящих" задач)
        if args['project_id'] in projects_id or not args['project_id']:
            # если переданный id == None, у задачи не может быть раздела
            # на всякий случай перезаписываем ключ, отвечающий за привязку задачи к разделу 
            if not args["project_id"]:
                args["section_id"] = None
            session.add(Task(**args))
            session.commit()

    return 200


def edit_task(args: dict):
    with Session() as session:
        task: Task = session.get(Task, args['task_id'])
        sections: list = session.query(Sections)
        sections_id = [sec_id._asdict()['id'] for sec_id in sections]
        projects_id = [proj_id._asdict()['project_id'] for proj_id in sections]
        for key, value in args.items():
            if key == "section_id" and value not in sections_id:
                return {"message": "Раздел не найден"}, 404
            if key == "project_id" and value not in projects_id:
                return {"message": "Проект не найден"}, 404
            if key != 'task_id':
                exec('task.%s = value' % key)

        session.commit()
    return {"message": "ok"}, 200




test_dict = {
    "task_id": 103,
    "description": "update ",
}

# pprint(get_task_details(88))
pprint(edit_task(test_dict))
# pprint(get_project_details(32))