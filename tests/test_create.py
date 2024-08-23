import pytest
from sqlalchemy import delete, insert, select, or_
from httpx import AsyncClient
import database.schemas as db_schema
import tests.test_data as test_data
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from contextlib import nullcontext as does_not_raise

import users.model as user_model
from conftest import asyns_connection


@pytest.mark.asyncio(scope="session")
class TestRegister(test_data.UserRegister):

    @pytest.mark.parametrize(
        "body, status_code",
        test_data.UserRegister.test_data
    )
    async def test_register(
        self,
        ac: AsyncClient,
        body,
        status_code,
    ):
        response = await ac.post(
            "/auth/register",
            json=body
        )
        assert response.status_code == status_code

    async def test_user(self):
        async with asyns_connection() as session:
            query = await session.execute(
                select(db_schema.User.login).
                where(db_schema.User.login == test_data.UserRegister.test_login)
            )
            result = query.scalar_one_or_none()
            assert result == test_data.UserRegister.test_login

            query = await session.execute(
                select(db_schema.UserInfo.id).
                where(db_schema.UserInfo.login == test_data.UserRegister.test_login)
            )
            result = query.scalar_one_or_none()
            assert result is not None


section_id_glob = None
project_id_glob = None
@pytest.mark.asyncio(scope="session")
class TestLogin:
    # пытаемся залогиниться, получить токены
    @pytest.mark.parametrize(
        "body, status_code",
        test_data.UserLogin.test_data
    )
    async def test_login(
        self,
        ac: AsyncClient,
        body,
        status_code,
    ):
        response = await ac.post(
            "/auth/login",
            json=body
        )
        assert response.status_code == status_code
    

@pytest.mark.asyncio(scope="session")
class TestCreateProj:
    # создаем проект для создания в нем задач и добавления туда другого юзера
    async def test_create_proj(
        self,
        ac: AsyncClient,
    ):
        body = {
            "name": "first_proj",
        }
        response = await ac.post(
            "project",
            json=body
        )
        global project_id_glob
        project_id_glob = int(response.text)
        assert response.status_code == 200
        assert project_id_glob == int(response.text)

    # берем id раздела
    async def test_check_proj_section(self):
        async with asyns_connection() as session:
            session: AsyncSession
            # берем id раздела этого проекта
            query = await session.execute(
                select(db_schema.Sections.id).
                where(
                    db_schema.Sections.project_id == project_id_glob,
                )
            )
            sec_id = query.scalar_one_or_none()
        assert sec_id is not None
        global section_id_glob
        section_id_glob = sec_id
        assert section_id_glob == sec_id


@pytest.mark.asyncio(scope="session")
class TestAddUserToProj:
    # добавляем еще одного пользователя в проект
    async def test_add_user(
        self,
        ac: AsyncClient,
    ):
        response = await ac.post(
            "/add_user",
            params={
                "login": ["second"],
                "project_id": [project_id_glob]
            }
        )
        assert response.status_code == 200
    

@pytest.mark.asyncio(scope="session")
class TestCreateTask:
    @pytest.mark.parametrize(
        "body, status_code",
        test_data.CreateTask.test_data
    )
    async def test_create_tasks(
        self,
        ac: AsyncClient,
        body,
        status_code,
    ):
        response = await ac.post(
            "/task",
            json=body
        )
        assert response.status_code == status_code


@pytest.mark.asyncio(scope="session")
class TestCreateComment:
    @pytest.mark.parametrize(
        "body, status_code",
        test_data.CreateComment.test_data
    )
    async def test_create_comments(
        self,
        ac: AsyncClient,
        body,
        status_code,
    ):
        response = await ac.post(
            "/comment",
            json=body
        )
        assert response.status_code == status_code


@pytest.mark.asyncio(scope="session")
class TestDeleteUser:
    # удаляем пользователя и проверяем удаление связаных с ним сущностей
    async def test_delete(
        self,
        ac: AsyncClient,
    ):
        async with asyns_connection() as session:
            session: AsyncSession
            # берем id пользователя
            query = await session.execute(
                select(db_schema.UserInfo.id).
                where(db_schema.UserInfo.login == test_data.UserLogin.login)
            )
            user_id = query.scalar_one_or_none()
            assert user_id is not None
        # удаляем пользователя
        response = await ac.delete(
            "/delete_user",
        )
        assert response.status_code == 200
        
        async with asyns_connection() as session:
            session: AsyncSession
            # проверяем чтобы все связи удалились
            query = await session.execute(
                select(db_schema.ProjectUser.project_id).
                where(db_schema.ProjectUser.user_id == user_id)
            )
            proj_list = query.scalars().all()
            assert proj_list == []
            # проверка на очищение всех полей в задачах
            query = await session.execute(
                select(db_schema.Task)
            )
            task_list = query.scalars().all()
            assert len(task_list) == 2
            for task in task_list:
                assert task.executor_id is None
                assert task.owner_id is None
                assert task.task_giver_id is None
            # проверка на очищение всех полей в коментах
            query = await session.execute(
                select(db_schema.Comments)
            )
            comments = query.scalars().all()
            assert len(comments) == 2
            for comment in comments:
                assert comment.user_id is None
            # проверка удаления пользователя
            query = await session.execute(
                select(db_schema.User.login).
                where(db_schema.User.login == test_data.UserLogin.login)
            )
            result = query.scalar_one_or_none()
            assert result is None
            
            query = await session.execute(
                select(db_schema.UserInfo.id).
                where(db_schema.UserInfo.login == test_data.UserLogin.login)
            )
            result = query.scalar_one_or_none()
            assert result is None

    # async def test_delete(self):
    #     async with asyns_connection() as session:
    #         query = await session.execute(
    #             delete(db_schema.User).
    #             where(db_schema.User.login == self.login)
    #         )
    #         await session.commit()

    #         query = await session.execute(
    #             select(db_schema.User.login).
    #             where(db_schema.User.login == self.login)
    #         )
    #         result = query.scalar_one_or_none()
    #         assert result is None

    #         query = await session.execute(
    #             select(db_schema.UserInfo.id).
    #             where(db_schema.UserInfo.login == self.login)
    #         )
    #         result = query.scalar_one_or_none()
    #         assert result is None


# @pytest.mark.asyncio(scope="session")
# class TestDelete(test_data.UserDelete):

#     @pytest.mark.parametrize(
#         "status_code",
#         [(200)]
#         # test_data.UserDelete.test_data
#     )
#     async def test_delete(
#         self,
#         ac: AsyncClient,
#         # body,
#         status_code,
#     ):
#         response = await ac.delete(
#             "/delete_user",
#             # json=body
#         )
#         assert response.status_code == status_code

# @pytest.mark.asyncio(scope="session")
# class TestLogin:

#     @pytest.mark.parametrize(
#         "body, status_code",
#         test_data.UserDelete.test_data
#     )
#     async def test_delete(
#         self,
#         ac: AsyncClient,
#         body,
#         status_code,
#     ):
#         response = await ac.post(
#             "/auth/login",
#             json=body
#         )
#         assert response.status_code == status_code