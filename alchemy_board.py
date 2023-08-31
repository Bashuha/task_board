from models import *
from my_engine import Session
from sqlalchemy import update, select
from pprint import pprint


def get_project_details(project_id):

    with Session() as session:

        sections: Sections = session.query(Sections).filter(Sections.project_id==project_id)
        section_list = list()
        for section in sections:
            section: Sections
            section_dict = {
                "id": section.id,
                "name": section.name,
                "tasks": list()
            }

            for task in section.Task:
                task: Task
                task_dict = {
                    "description": task.description,
                    "name": task.name,
                    "status": task.status,
                    "task_id": task.id,
                    "comments_count": len(task.Comments)
                }
                section_dict['tasks'].append(task_dict)
            
            section_list.append(section_dict)

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

        # for comment in task.Comments:
        #     comment = comment._asdict()
        #     comment.pop("task_id")
        #     task_dict['comments'].append(comment)
        # task_dict['comments'] = [comment._asdict() for comment in task.Comments]
        task_dict['comments'] = [lambda comment: comment.asdict() for comment in task.Comments]

    return task_dict


pprint(get_task_details(88))
# pprint(get_project_details(32))