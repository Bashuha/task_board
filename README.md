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
*GET /to_do_list/project_list*

- Статус 200

Ответ 
```json
{
    "projects": [
        {
            "project_name": "second_project",
            "is_favorites": false,
            "id": 2,
            "is_archive": true,
            "task_count": 2
        },
        {
            "project_name": "Серёзный проект",
            "is_favorites": false,
            "id": 27,
            "is_archive": false,
            "task_count": 0
        },
        {
            "project_name": "Нужно больше кельвинов",
            "is_favorites": true,
            "id": 29,
            "is_archive": false,
            "task_count": 3
        },
        {
            "project_name": "Пожалуйста, работай",
            "is_favorites": true,
            "id": 32,
            "is_archive": false,
            "task_count": 3
        }
    ]
}
```

## Создание проекта
*POST /to_do_list/project*
* Тело запроса на **создание** проекта
```json
{
    "name": "our_project",
    "is_favorites": false       // может быть и true
}
```
- Статус 200

Ответ
```json
{
    "message": "ok"
}
```

## Архивация проекта
*PUT /to_do_list/project*

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
    "message": "ok"
}
```
* Cтатус 200

Ответ в случае если мы достаем проект из архива 
```json
{
    "message": "ok"
}
```
* Статус 404

Ответ, если проекта в базе нет
```json
{
    "message": "Проект не найден"
}
```

## Удаление проекта из архива
*DELETE /to_do_list/project*

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
    "message": "Проект удален"
}
```
* Cтатус 400

Ответ на случай попытки удалить проект не в архиве 
```json
{
    "message": "Проект не в архиве"
}
```
## Получить детализацию проекта
*GET /to_do_list/project*

* Параметр запроса на получение детализации нужного проекта
```json
{
    "project_id":32
}
```
Полный пример: 

*/to_do_list/project?project_id=32*
* Статус 200

Ответ
```json
{
    "project_name": "Пожалуйста, работай",
    "project_id": 32,
    "tasks": [
        {
            "name": "Задача без раздела",
            "description": "Тут совершенно не обязательно что-то писать",
            "owner": "Ilusha Tester",
            "create_date": "2023-07-31",
            "section_id": null,
            "task_id": 54
        }
    ],
    "sections": [
        {
            "section_name": "Раздел для теста 1",
            "section_id": 7,
            "tasks": [
                {
                    "name": "Задача для теста",
                    "description": "Тут совершенно не обязательно что-то писать",
                    "owner": "Ilusha Tester",
                    "create_date": "2023-07-31",
                    "section_id": 7,
                    "task_id": 55
                }
            ]
        },
        {
            "section_name": "Раздел для теста 2",
            "section_id": 8,
            "tasks": [
                {
                    "name": "Задача для теста 2",
                    "description": "Тут совершенно не обязательно что-то писать",
                    "owner": "Ilusha Tester",
                    "create_date": "2023-07-31",
                    "section_id": 8,
                    "task_id": 56
                }
            ]
        }
    ]
}
```

* Статус 200

Если не передавать параметр, то вернется список **входящих** задач

*/to_do_list/project*
```json
{
    "project_name": "Входящие",
    "project_id": null,
    "tasks": [
        {
            "name": "Задача без проекта",
            "description": "Типа опписание задаи",
            "owner": "Ilusha Tester",
            "create_date": "2023-07-31",
            "section_id": null,
            "task_id": 57
        },
        {
            "name": "И еще одна такая же",
            "description": "Нет тут описания",
            "owner": "Ilusha Tester",
            "create_date": "2023-07-31",
            "section_id": null,
            "task_id": 58
        }
    ],
    "sections": []
}
```

* Статус 404

Ответ в случае если соответсвующего проекта в базе нет:
```json
{
    "message": "Проект не найден"
}
```


## Создать задачу
*POST /to_do_list/tasks*

* Тело запроса на создание задачи:
```json
{
    "name": "task_name",
    "description": "description_text",
    "project_id": 7    // если этот параметр не указать, создастся входящая задача
}
```

* Статус 200
Ответ
```json
{
    "message": "ok"
}
```

## Получить детализацию задачи
*GET /to_do_list/task/details*

* Параментры получения детализации:
```json
{
    "task_id":35
}
```
Полный пример: 

*/to_do_list/task/details?task_id=57*

* Статус 200

Ответ
```json
{
    "project_name": "Пожалуйста, работай",
    "project_id": 32,
    "task_name": "Задача для теста 2",
    "task_id": 56,
    "task_owner": "Ilusha Tester",
    "description": "Тут совершенно не обязательно что-то писать",
    "create_date": "2023-07-31",
    "section_id": 8,
    "comments": [
        {
            "login": "Ilusha Tester",
            "create_at": "2023-07-31",
            "text": "Коммент для теста",
            "id": 21
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
    "task_name": "Задача без проекта",
    "task_id": 57,
    "task_owner": "Ilusha Tester",
    "description": "Типа опписание задаи",
    "create_date": "2023-07-31",
    "section_id": null,
    "comments": [
        {
            "login": "Ilusha Tester",
            "create_at": "2023-07-31",
            "text": "комент у задачи без раздела",
            "id": 24
        },
        {
            "login": "Ilusha Tester",
            "create_at": "2023-07-31",
            "text": "и без проекта",
            "id": 25
        }
    ]
}
```

* Статус 404

Если задача не найдена
```json
{
    "message": "Задача не найдена"
}
```

## Создание комментария
*POST /to_do_list/task/details*
* Тело запроса на создание комментария:
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
    "message": "Задача не найдена"
}
```

## Изменение комментария
*PUT /to_do_list/task/details*
* Тело запроса на изменение комментария
```json
{
    "task_id": 40,
    "text": "This is the new comment text"
}
```
* Статус 200

В ответ придет просто статус