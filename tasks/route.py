from sqlalchemy import select
from database.my_engine import get_db
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, status, WebSocketException
from sqlalchemy.ext.asyncio import AsyncSession
import tasks.functions as task_func
from tasks.model import Task, CreateTask, EditTask, ErrorNotFound, DeleteTask, TaskList, ChangeTaskStatus, TaskOrder, UpdateModelForSocket
from users.functions import get_current_user, websocket_user, get_socket_token
from database.schemas import ProjectUser, UserInfo
import projects.functions as project_func
import json
from datetime import datetime


router = APIRouter(
    tags=['Task']
)
websocket_route = APIRouter(
    tags=['WSRoute']
)


error_description = """
Причины возникновения

1. Введен неверный **id** задачи
2. Введен неверный **id** проекта
3. Введен неверный **id** раздела
"""


responses_dict = {
    404: {
        "model": ErrorNotFound,
        "description": "The task not found"
    }
}


@router.get(
    '/task',
    status_code=status.HTTP_200_OK,
    response_model=Task,
    responses={404: responses_dict[404]},
    summary='Получение детализации задачи, к которой у тебя есть доступ (ты есть в том проекте)'    
)
async def get_task_details(
    task_id: int,
    session: AsyncSession = Depends(get_db),
    user: UserInfo = Depends(get_current_user)
):
    return await task_func.get_task_details(task_id, session, user)


@router.get(
    '/task_list',
    status_code=status.HTTP_200_OK,
    response_model=TaskList,
    summary='Получение всех твоих задач'
)
async def get_task_list(
    session: AsyncSession = Depends(get_db),
    user: UserInfo = Depends(get_current_user)
):
    return await task_func.get_task_list(session, user)



@router.post(
    '/task',
    status_code=status.HTTP_200_OK,
    responses={404: responses_dict[404]},
    summary='Создание задачи'
)
async def create_task(
    task: CreateTask,
    session: AsyncSession = Depends(get_db),
    user: UserInfo = Depends(get_current_user)
):
    return await task_func.create_task(task, session, user)


@router.patch(
    '/task',
    status_code=status.HTTP_200_OK,
    responses={404: {
        "model": ErrorNotFound,
        "description": error_description
    }},
    summary='Редактирование своей задачи'
)
async def edit_task(
    task: EditTask,
    session: AsyncSession = Depends(get_db),
    user: UserInfo = Depends(get_current_user)
):
    return await task_func.edit_task(task, session, user)


@router.put(
    '/change_task_status',
    status_code=status.HTTP_200_OK,
    summary="Изменение статуса задачи"
)
async def change_task_status(
    task_model: ChangeTaskStatus,
    session: AsyncSession = Depends(get_db),
    user: UserInfo = Depends(get_current_user)
):
    return await task_func.change_task_status(task_model, user, session)


@router.delete(
    '/task',
    status_code=status.HTTP_200_OK,
    responses={404: responses_dict[404]},
    summary='Удаление своей задачи'    
)
async def delete_task(
    task: DeleteTask,
    session: AsyncSession = Depends(get_db),
    user: UserInfo = Depends(get_current_user)
):
    return await task_func.delete_task(task, session, user)


@router.put(
    '/task_order',
    status_code=status.HTTP_200_OK,
    summary='Изменение порядка своих задач'    
)
async def change_task_order(
    task_order: TaskOrder,
    session: AsyncSession = Depends(get_db),
    user: UserInfo = Depends(get_current_user)
):
    return await task_func.change_task_order(task_order, session, user)


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.users_id_connections: dict[int:WebSocket] = dict()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    async def add_user_connection(self, websocket: WebSocket, user_id):
        self.users_id_connections[user_id] = websocket

    def disconnect(self, websocket: WebSocket, user_id):
        self.active_connections.remove(websocket)
        self.users_id_connections.pop(user_id, None)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, data: dict, recipients: list[WebSocket]):
        for connection in recipients:
            await connection.send_text(data)
            # await connection.send_text(data)


manager = ConnectionManager()


@websocket_route.websocket("/ws")
async def websocket_try(
    websocket: WebSocket,
    token: str = Depends(get_socket_token),
    session: AsyncSession = Depends(get_db)
):
    await manager.connect(websocket)
    user: UserInfo = await websocket_user(token)
    await manager.add_user_connection(websocket, user.id)
    print(manager.users_id_connections)
    # token = websocket.cookies.get("access_token")
    try:
        while True:
            # принимаем json с ключами, который скажут нам что делать
            data_json = await websocket.receive_json()
            print(data_json)
            # ключи этого объекта скорее всего меняться не будут, только из значения
            # в зависимости от комад, которые пришлет нам фронт
            final_object = UpdateModelForSocket(
                project_details=None,
                project_list=None
            )
            # ключ чтобы обновить детализацию проекта
            if data_json['action'] == 'upd_pr_detail':
                # нужно сбросить сессию перед каждым запросом, поэтому тут rollback
                await session.rollback()
                project_id = data_json.get('project_id')
                # но обновлять мы будем только у тех пользователей, кто есть в этом проекте
                users_ids_query = await session.execute(
                    select(ProjectUser.user_id).
                    where(ProjectUser.project_id == project_id)
                )
                users_ids = users_ids_query.scalars().all()
                broadcast_users = list()
                # этих пользователей мы ищем среди подключенных (и добавляем в список получаетелей)
                # но отправляем мы всем, кроме себя самого
                for user_id in users_ids:
                    if user_id in manager.users_id_connections and user_id != user.id:
                        broadcast_users.append(manager.users_id_connections[user_id])
                # далее просто делаем запрос в базу на нужный нам проект
                project_model = await project_func.project_details(project_id, session, user)
                final_object.project_details = project_model
            # ключ обновления списка проктов (bool)
            if data_json['upd_pr_list']:
                await session.rollback()
                project_list_model = await project_func.get_projects(user, session)
                final_object.project_list = project_list_model
            
            final_json = final_object.model_dump_json()
            await manager.broadcast(data=final_json, recipients=broadcast_users)
    except WebSocketDisconnect:
        manager.disconnect(websocket, user.id)
        print(f"{user.id} disconnect")
