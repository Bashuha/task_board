# Task_board
Создаем свой собственный канбан

# Оглавление
1. [Получение списка проектов](#получение-списка-проектов)
2. [Создание проекта](#создание-проекта)
3. [Архивировать/разархивировать проект](#архивация-проекта)
4. [Удаление проекта из архива](#удаление-проекта-из-архива)
5. [Получить детализацию проекта](#получить-детализацию-проекта)
6. [Создать задачу](#создать-задачу)
7. [Получить детализацию задачи](#получить-детализацию-задачи)

## Получение списка проектов
*GET /to_do_list/projects*

- Ответ, статус 200
```json
{
    "projects": [
        {
            "project_name": "fitst_project",
            "is_favorites": false,
            "id": 1,
            "task_count": 0
        }
                ]
}
```

## Создание прокта
*POST /to_do_list/projects*
* Тело запроса на **создание** проекта
```json
{
    "name":"our_project"
    "is_favorites":"false",
}
```

## Архивация проекта
*PUT /to_do_list/projects*

- Запрос на **изменение статуса** проекта. ```true``` - в архиве, ```false``` - не в архиве
```json
{
    "is_archive":true,
    "project_id":6
}
```
* Ответ в случае перемещения проекта в архив, статус 200
```json
{
    "messege": "project moved to the archive"
}
```
* Ответ в случае если мы достаем проект из архива, статус 200
```json
{
    "messege": "project moved from archive"
}
```

## Удаление проекта из архива
*DELETE /to_do_list/projects*

* Тело запроса на удаление архивированного проекта
```json
{
    "project_id": 14
}
```
- Ответ в случае успешного удаления, статус 200
```json
{
    "messege": "project deleted"
}
```
- Ответ на случай попытки удалить проект не в архиве, статус 400
```json
{
    "messege": "the project is not archived"
}
```
## Получить детализацию проекта
*GET /to_do_list/tasks*

* Параметр запроса на получение детализации нужного проекта
```json
{
    "project_id":7
}
```
Полный пример:
*/to_do_list/tasks?project_id=7*
* Ответ:
```json
{
    "project_name": "tomatos",
    "project_id": 7,
    "tasks": [
        {
            "name": "i_have_no_idea",
            "description": "Nothing",
            "owner": "Ilusha Tester",
            "create_date": "2023-07-19"
        },
        {
            "name": "i_have_an_idea",
            "description": "Smth",
            "owner": "Ilusha Tester",
            "create_date": "2023-07-19"
        },
        {
            "name": "idea",
            "description": "empty_field",
            "owner": "Ilusha Tester",
            "create_date": "2023-07-19"
        },
        {
            "name": "I like kelvin",
            "description": "God bless kelvin",
            "owner": "Ilusha Tester",
            "create_date": "2023-07-25"
        }
            ]
}
```

- Если не передавать параметр, то вернется список **входящих** задач
```json
{
    "tasks": [
        {
            "name": "i like my job",
            "description": "i am ok",
            "owner": "Ilusha Tester",
            "create_date": "2023-07-19"
        },
        {
            "name": "Artem loves kelvin",
            "description": "Can Artem finish kelvin?",
            "owner": "Ilusha Tester",
            "create_date": "2023-07-25"
        }
            ]
}
```

## Создать задачу
*POST /to_do_list/tasks*

* Тело запроса на создание задачи:
```json
{
    "name": "task_name",
    "description": "description_text",
    "project_id": 7
}
```
- project_id можно не указывать, чтобы создать **входящую** задачу. В обоих случаях ответ будет один:
```json
{
    "messege": "ok"
}
```

## Получить детализацию задачи
*GET /to_do_list/comments*

* Параментры получения комментариев:
```json
{
    "task_id":35
}
```
* Полный пример */to_do_list/comments/task_id=35*

- Ответ:
```json
{
    "project_name": "second_project",
    "project_id": 2,
    "task_name": "test_comment",
    "task_id": "35",
    "task_owner": "Ilusha Tester",
    "description": "empty",
    "create_date": "2023-07-19",
    "comments": [
        {
            "login": "Ilusha Tester",
            "create_at": "2023-06-30",
            "text": "you can do this"
        },
        {
            "login": "Ilusha Tester",
            "create_at": "2023-06-30",
            "text": "Just do it!"
        },
        {
            "login": "Ilusha Tester",
            "create_at": "2023-06-30",
            "text": "Artem, kelvin waits for you"
        }
    ]
}
```

