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


class UserDelete:
    test_login = 'first'
    test_data = [
        (
            200
        )
    ]