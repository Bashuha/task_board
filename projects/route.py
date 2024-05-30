from database.my_engine import get_db
from database.schemas import UserInfo
from fastapi import APIRouter, Depends, WebSocketDisconnect, status, WebSocket, WebSocketException
from sqlalchemy.ext.asyncio import AsyncSession
import projects.functions as project_func
import projects.admin_func as admin_func
from projects.model import (
    ProjectList,
    CreateProject,
    EditProject,
    ChangeArchiveStatus,
    NotFoundError,
    BadRequestError,
    TodayTaskList,
    ProjectDetails,
    ProjectUserList
)
from users.functions import get_current_user
from fastapi.responses import HTMLResponse


router = APIRouter(tags=["Projects"])


responses_dict = {
    404: {
        "model": NotFoundError,
        "description": "Введен не верный id проекта"
    },
    400: {
        "model": BadRequestError,
        "description": "Попытка удалить не архивированный проект"
    }
}


@router.get(
    '/project_details',
    status_code=status.HTTP_200_OK,
    response_model=ProjectDetails,
    responses={404: responses_dict[404]},
    summary='Получение детализации проекта'
)
async def project_details(
    project_id: int = None,
    session: AsyncSession = Depends(get_db),
    user: UserInfo = Depends(get_current_user)
):
    return await project_func.project_details(project_id, session, user)


@router.post(
    '/project',
    status_code=status.HTTP_200_OK,
    responses={404: responses_dict[404]},
    summary='Создание нового проекта'
)
async def create_project(
    project: CreateProject,
    session: AsyncSession = Depends(get_db),
    user: UserInfo = Depends(get_current_user)
):
    return await project_func.create_project(project, user, session)


@router.patch(
    '/project',
    status_code=status.HTTP_200_OK,
    summary='Редактирование проекта'
)
async def edit_project(
    project: EditProject,
    session: AsyncSession = Depends(get_db),
    user: UserInfo = Depends(get_current_user)
):
    return await project_func.edit_project(project, session, user)


@router.put(
    '/change_archive_status',
    status_code=status.HTTP_200_OK,
    responses={404: responses_dict[404]},
    summary='Перемещение проекта в архив/из архива'
)
async def change_archive_status(
    project: ChangeArchiveStatus,
    session: AsyncSession = Depends(get_db),
    user: UserInfo = Depends(get_current_user)
):
    return await admin_func.change_archive_status(project, session, user)


@router.delete(
    '/project',
    status_code=status.HTTP_200_OK,
    responses={
        404: responses_dict[404],
        400: responses_dict[400]
    },
    summary='Удаление своего проекта'
)
async def delete_from_archive(
    project_id: int,
    session: AsyncSession = Depends(get_db),
    user: UserInfo = Depends(get_current_user)
):
    return await admin_func.delete_from_archive(project_id, session, user)


@router.get(
    '/project_list',
    status_code=status.HTTP_200_OK,
    response_model=ProjectList,
    summary='Получение своих проектов'
)
async def get_projects(
    session: AsyncSession = Depends(get_db),
    user: UserInfo = Depends(get_current_user)
):
    return await project_func.get_projects(user, session)


@router.get(
    '/today_tasks',
    status_code=status.HTTP_200_OK,
    response_model=TodayTaskList,
    summary='Получение своих задач на сегодня'
)
async def get_today_tasks(
    session: AsyncSession = Depends(get_db),
    user: UserInfo = Depends(get_current_user)    
):
    return await project_func.get_today_tasks(session, user)


@router.post(
    '/add_user',
    status_code=status.HTTP_200_OK,
    summary='Добавление пользователя в проект'
)
async def add_user_to_project(
    login: str,
    project_id: int,
    session: AsyncSession = Depends(get_db),
    user: UserInfo = Depends(get_current_user)
):
    return await admin_func.add_user_to_project(
        login, project_id, session, user
    )


@router.delete(
    '/remove_user',
    status_code=status.HTTP_200_OK,
    summary="Удаление пользователя из проекта"
)
async def remove_user_from_project(
    user_id: int,
    project_id: int,
    session: AsyncSession = Depends(get_db),
    user: UserInfo = Depends(get_current_user)
):
    return await admin_func.remove_user_from_project(
        project_id=project_id, user_id=user_id, session=session, user=user
    )


@router.get(
    '/project_users',
    status_code=status.HTTP_200_OK,
    summary="Получить список всех пользователей проекта",
    response_model=ProjectUserList
)
async def project_user_list(
    project_id: int,
    session: AsyncSession = Depends(get_db),
    user: UserInfo = Depends(get_current_user),
):
    return await admin_func.project_user_list(project_id, user, session)


@router.put(
    '/change_admin',
    status_code=status.HTTP_200_OK,
    summary="Дать/забрать права админа проекта"
)
async def change_admin(
    project_id: int,
    user_id: int,
    is_owner: bool,
    user: UserInfo = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    return await admin_func.change_admin(
        project_id,
        user_id,
        is_owner,
        user,
        session
    )


@router.delete(
    '/exit_project',
    status_code=status.HTTP_200_OK,
    summary='Выйти из проекта'
)
async  def exit_project(
    project_id: int,
    session: AsyncSession = Depends(get_db),
    user: UserInfo = Depends(get_current_user)
):
    return await project_func.exit_project(project_id, session, user)


# @router.websocket('/ws')
# async def websocket_try(
#     websocket: WebSocket,
#     manager: ConnectionManager,
#     session: AsyncSession = Depends(get_db),
#     user: UserInfo = Depends(get_current_user)
# ):
#     await manager.connect(websocket)
#     try:
#         while True:
#             await websocket.receive_json(await project_func.get_projects(user, session))
#     except WebSocketException:
#         pass


# class ConnectionManager:
#     def __init__(self):
#         self.active_connections: list[WebSocket] = []

#     async def connect(self, websocket: WebSocket):
#         await websocket.accept()
#         self.active_connections.append(websocket)

#     def disconnect(self, websocket: WebSocket):
#         self.active_connections.remove(websocket)

#     async def send_personal_message(self, message: str, websocket: WebSocket):
#         await websocket.send_text(message)

#     async def broadcast(self, json_data: dict):
#         for connection in self.active_connections:
#             # await connection.send_text(message)
#             await connection.send_json(json_data)


# manager = ConnectionManager()


# @router.websocket("/ws")
# async def websocket_try(
#     websocket: WebSocket,
#     session: AsyncSession = Depends(get_db),
#     user: UserInfo = Depends(get_current_user)
# ):
#     await manager.connect(websocket)
#     try:
#         while True:
#             # data = await websocket.receive_json()
#             await manager.broadcast(await project_func.get_projects(user, session))
#     except WebSocketDisconnect:
#         manager.disconnect(websocket)

# @router.websocket('/ws')
# async def websocket_try(
#     websocket: WebSocket,
#     session: AsyncSession = Depends(get_db),
#     user: UserInfo = Depends(get_current_user)
# ):
#     try:
#         await websocket.accept()
#         while True:
#             data = await websocket.receive_json(await project_func.get_projects(user, session))
#             await websocket.send_json(data)
#     except WebSocketException as e:
#         print(e)