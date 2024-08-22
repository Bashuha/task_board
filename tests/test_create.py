import pytest
from sqlalchemy import delete, insert, select
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


access_token = None
@pytest.mark.asyncio(scope="session")
class TestLogin(test_data.UserLogin):

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
        # global access_token = response.cookies['access_token']
        assert response.status_code == status_code

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


@pytest.mark.asyncio(scope="session")
class TestDelete(test_data.UserDelete):

    @pytest.mark.parametrize(
        "status_code",
        [(200)]
        # test_data.UserDelete.test_data
    )
    async def test_delete(
        self,
        ac: AsyncClient,
        # body,
        status_code,
    ):
        response = await ac.delete(
            "/delete_user",
            # json=body
        )
        assert response.status_code == status_code

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