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
8. [Создание комментария](#создание-комментария)

## Получение списка проектов
*GET /to_do_list/projects*

- Статус 200

Ответ 
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

## Создание проекта
*POST /to_do_list/projects*
* Тело запроса на **создание** проекта
```json
{
    "name":"our_project"
    "is_favorites":"false",
}
```
- Статус 200

Ответ
```json
{
    "messege": "ok"
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
* Cтатус 200

Ответ в случае перемещения проекта в архив 
```json
{
    "messege": "project moved to the archive"
}
```
* Cтатус 200

Ответ в случае если мы достаем проект из архива 
```json
{
    "messege": "project moved from archive"
}
```
* Статус 404

Ответ, если проекта в базе нет
```json
{
    "message": "project not found"
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
* Cтатус 200

Ответ в случае успешного удаления 
```json
{
    "messege": "project deleted"
}
```
* Cтатус 400

Ответ на случай попытки удалить проект не в архиве 
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
* Статус 200

Ответ
```json
{
    "project_name": "tomatos",
    "project_id": 7,
    "tasks": [
        {
            "name": "i_have_no_idea",
            "description": "Nothing",
            "owner": "Ilusha Tester",
            "create_date": "2023-07-19",
            "task_id": 2
        },
        {
            "name": "i_have_an_idea",
            "description": "Smth",
            "owner": "Ilusha Tester",
            "create_date": "2023-07-19",
            "task_id": 3
        },
        {
            "name": "idea",
            "description": "empty_field",
            "owner": "Ilusha Tester",
            "create_date": "2023-07-19",
            "task_id": 4
        },
        {
            "name": "I like kelvin",
            "description": "God bless kelvin",
            "owner": "Ilusha Tester",
            "create_date": "2023-07-25",
            "task_id": 45
        }
    ]
}
```

* Статус 200

Если не передавать параметр, то вернется список **входящих** задач

*/to_do_list/tasks*
```json
{
    "project_name": "Входящие",
    "project_id": null,
    "tasks": [
        {
            "name": "i like my job",
            "description": "i am ok",
            "owner": "Ilusha Tester",
            "create_date": "2023-07-19",
            "task_id": 39
        },
        {
            "name": "Artem loves kelvin",
            "description": "Can Artem finish kelvin?",
            "owner": "Ilusha Tester",
            "create_date": "2023-07-25",
            "task_id": 40
        },
        {
            "name": "Kelvin loves Artem",
            "description": "Kelvin > Artem",
            "owner": "Ilusha Tester",
            "create_date": "2023-07-25",
            "task_id": 41
        },
        {
            "name": "Another kelvin",
            "description": "Artem, pls",
            "owner": "Ilusha Tester",
            "create_date": "2023-07-25",
            "task_id": 44
        }
    ]
}
```

* Статус 404

Ответ в случае если соответсвующего проекта в базе нет:
```json
{
    "message": "project not found"
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

* Статус 200

project_id можно не указывать, чтобы создать **входящую** задачу. В обоих случаях ответ будет один
```json
{
    "messege": "ok"
}
```

## Получить детализацию задачи
*GET /to_do_list/comments*

* Параментры получения детализации:
```json
{
    "task_id":35
}
```
* Полный пример */to_do_list/comments/task_id=35*

* Статус 200

Ответ
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



* Статус 200

Если задача не принадлежит ни к одному проекту, то есть находится во **входящих**, ответ будет таким
```json
{
    "project_name": "Входящие",
    "project_id": null,
    "task_name": "Kelvin loves Artem",
    "task_id": "41",
    "task_owner": "Ilusha Tester",
    "description": "Kelvin > Artem",
    "create_date": "2023-07-25",
    "comments": [
        {
            "login": "Ilusha Tester",
            "create_at": "2023-06-30",
            "text": "Every single one Artem loves kelvin"
        },
        {
            "login": "Ilusha Tester",
            "create_at": "2023-06-30",
            "text": "Artem > Kelvin"
        },
        {
            "login": "Ilusha Tester",
            "create_at": "2023-06-30",
            "text": "Can we finish Kelvin?"
        }
    ]
}
```

* Статус 404

Если задача не найдена
```json
{
    "message": "task not found"
}
```

## Создание комментария
* Тело запроса на создание задачи:
```json
{
    "task_id": 40,
    "text": "Zdorova Makson"
}
```
* Статус 200

Ответ
```json
{
    "message": "ok"
}
```
* Статус 404

Ответ если указан несуществующий task_id
```json
{
    "message": "task not found"
}
```

## Изменение комментария
* Тело запроса на изменение комментария
```json
{
    "task_id": 40,
    "text": "This is the new comment text"
}
```
* Статус 200

В ответ придет просто статус