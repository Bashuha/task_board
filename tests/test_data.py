class UserRegister:
    test_login = "first"

    test_data = [
        (
            {
                "login": f"{test_login}",
                "password": "string",
                "first_name": "string",
                "second_name": "string"
            },
            201
        ),
        (
            {
                "login": "second",
                "password": "string",
                "first_name": "string",
                "second_name": "string"
            },
            201
        ),
        (
            {
                "login": "second",
                "password": "string",
                "first_name": "string",
                "second_name": "string"
            },
            400
        )
    ]


class UserLogin:
    login = "first"
    test_data = [
        (
            {
                "login": f"{login}",
                "password": "string",
            },
            200
        ),
    ]


class CreateTask:
    test_data = [
        (
            {
                "name": "first_task",
                "description": "string",
                "to_do_date": "2024-08-23",
                "executor_id": 1,
                "section_id": 3,
                "tag_ids": []
            },
            200
        ),
        (
            {
                "name": "second_task",
                "section_id": 3,
                "tag_ids": []
            },
            200
        )
    ]


class UserCreateProj:
    test_data = [
        (
            {
                "name": "first_proj",
            }
        )
    ]


class UpdateProject:
    test_data = [
        (
            {
                "id": 3,
                "name": "new name",
                "is_favorites": True,
            },
            200
        )
    ]


class CreateComment:
    test_data = [
        (
            {
                "project_id": 3,
                "task_id": 2,
                "text": "test",
            },
            200
        ),
        (
            {
                "project_id": 3,
                "task_id": 1,
                "text": "new_test",
            },
            200
        ),
        (
            {
                "project_id": 3,
                "text": "new_test",
            },
            422
        )
    ]