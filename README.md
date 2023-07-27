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

### Ответ 
- Статус 200
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
### Ответ
- Статус 200
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
### Ответ в случае перемещения проекта в архив 
* Cтатус 200
```json
{
    "messege": "project moved to the archive"
}
```
### Ответ в случае если мы достаем проект из архива 
* Cтатус 200
```json
{
    "messege": "project moved from archive"
}
```
### Ответ, если проекта в базе нет
* Статус 404
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
### Ответ в случае успешного удаления 
* Cтатус 200
```json
{
    "messege": "project deleted"
}
```
### Ответ на случай попытки удалить проект не в архиве 
* Cтатус 400
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
### Ответ
* Статус 200
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

### Если не передавать параметр, то вернется список **входящих** задач
* Статус 200

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
### Ответ в случае если соответсвующего проекта в базе нет:

* Статус 404
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
### project_id можно не указывать, чтобы создать **входящую** задачу. В обоих случаях ответ будет один

* Статус 200
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

### Ответ
* Статус 200
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


### Если задача не принадлежит ни к одному проекту, то есть находится во **входящих**, ответ будет таким

* Статус 200
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

### Если задача не найдена
* Статус 404
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
### Ответ
* Статус 200
```json
{
    "message": "ok"
}
```
### Ответ если указан несуществующий task_id
* Статус 404
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
### В ответ придет просто статус
* Статус 200