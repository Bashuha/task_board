# Task_board
Создаем свой собственный канбан

# Оглавление
1. [Получение списка проектов](#получение-списка-проектов)
2. [Создание проекта](#создание-проекта)
3. [Редактирование проекта](#редактирование-проекта)
4. [Архивация проекта](#архивация-проекта)
5. [Удаление проекта из архива](#удаление-проекта-из-архива)
6. [Получить детализацию проекта](#получить-детализацию-проекта)
7. [Создать задачу](#создать-задачу)
8. [Редактировать задачу](#редактировать-задачу)
9. [Получить детализацию задачи](#получить-детализацию-задачи)
10. [Создание комментария](#создание-комментария)
11. [Удаление комментария](#удаление-комментария)
12. [Создание раздела](#создание-раздела)
13. [Редактирование раздела](#редактирование-раздела)
14. [Удаление раздела](#удаление-раздела)
15. [Изменение порядка разделов](#изменение-порядка-разделов)
16. [Удаление задачи](#удаление-задачи)

## Получение списка проектов
*GET /to_do_list/project_list*

- Статус 200

Ответ 
```json
{
    "projects": [
        {
            "project_name": "tomatos",
            "is_favorites": false,
            "id": 7,
            "is_archive": false,
            "task_count": 3,
            "sections": [
                {
                    "section_id": 9,
                    "name": "Тест создания раздела",
                    "project_id": 7
                }
            ]
        },
        {
            "project_name": "Серёзный проект",
            "is_favorites": false,
            "id": 27,
            "is_archive": false,
            "task_count": 0,
            "sections": []
        },
        {
            "project_name": "i76r76rf",
            "is_favorites": false,
            "id": 28,
            "is_archive": false,
            "task_count": 0,
            "sections": []
        },
        {
            "project_name": "Нужно больше кельвинов",
            "is_favorites": true,
            "id": 29,
            "is_archive": false,
            "task_count": 2,
            "sections": [
                {
                    "section_id": 3,
                    "name": "Раздел Артема и Кельвина",
                    "project_id": 29
                },
                {
                    "section_id": 4,
                    "name": "Измененное имя раздела",
                    "project_id": 29
                }
            ]
        },
        {
            "project_name": "Нужно больше кельвинов x2",
            "is_favorites": false,
            "id": 31,
            "is_archive": false,
            "task_count": 0,
            "sections": []
        },
        {
            "project_name": "Пожалуйста, работай",
            "is_favorites": false,
            "id": 32,
            "is_archive": true,
            "task_count": 5,
            "sections": [
                {
                    "section_id": 7,
                    "name": "Раздел для теста 1",
                    "project_id": 32
                },
                {
                    "section_id": 11,
                    "name": "Тест создания второго раздела",
                    "project_id": 32
                }
            ]
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

## Редактирование проекта
*PUT /to_do_list/project*

- Запрос на редактирование проекта.
```json
{
    "project_id":28,         // обязательный аргумент
    "name":"new project name",
    "is_favorites":false
}
```

* Cтатус 200

Ответ когда все хорошо 
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

## Архивация проекта
*PUT /to_do_list/change_archive_status*
- Тело запроса на **изменение статуса** проекта. ```true``` - в архиве, ```false``` - не в архиве
```json
{
    "project_id":"31",      // обязательный аргумент
    "is_archive":true       // обязательный аргумент
}
```
В ответ придет только статус
* Статус 200

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
    "is_favorites": false,
    "project_id": 32,
    "project_name": "New archive name",
    "sections": [
        {
            "id": 7,
            "name": "Раздел для теста 1",
            "tasks": [
                {
                    "comments_count": 2,
                    "description": "Тут совершенно не обязательно что-то писать",
                    "name": "Задача для теста",
                    "status": true,
                    "task_id": 55
                },
                {
                    "comments_count": 0,
                    "description": "Новое описание",
                    "name": "Измененное название задачи",
                    "status": true,
                    "task_id": 61
                }
            ]
        },
        {
            "id": 16,
            "name": "Test order number",
            "tasks": []
        },
        {
            "id": 11,
            "name": "Тест создания второго раздела",
            "tasks": []
        },
        {
            "id": 12,
            "name": "",
            "tasks": []
        }
    ],
    "tasks": [
        {
            "comments_count": 0,
            "description": "Тут совершенно не обязательно что-то писать",
            "name": "Задача без раздела",
            "status": true,
            "task_id": 54
        },
        {
            "comments_count": 0,
            "description": "Тут совершенно не обязательно что-то писать",
            "name": "Еще одна такая же",
            "status": true,
            "task_id": 62
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
            "task_id": 57
        },
        {
            "name": "И еще одна такая же",
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
*POST /to_do_list/task*

* Тело запроса на создание задачи:
```json
{
    "name": "task_name",
    "description": "description_text",
    "project_id": 7,   // если в этот аргумент передать None (null), создастся входящая задача
    "section_id": 9     // если этот параметр не указать, в проекте создастся задача без раздела
}
```

* Статус 200
Ответ
```json
{
    "message": "ok"
}
```

## Редактировать задачу
*POST /to_do_list/task*

* Тело запроса на редактирование задачи
```json
{
    "task_id": 60,      // обязательный аргумент
    "name": "new_task_name",
    "description": "new_description_text",
    "project_id": 7,    // если не передавать этот аргумент или передать None (null), то задача переместится во входящие
    "section_id": 9,     // если не передавать этот аргумент или передать None (null), то задача будет вне разделов
    "status": false
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
*GET /to_do_list/task*

* Параментры получения детализации:
```json
{
    "task_id":60
}
```
Полный пример: 

*/to_do_list/task?task_id=60*

* Статус 200

Ответ
```json
{
    "comments": [
        {
            "create_at": "2023-08-15",
            "id": 34,
            "login": "Ilusha Tester",
            "text": "и без проекта"
        }
    ],
    "create_date": "2023-07-31",
    "description": "new_description_text",
    "project_id": 7,
    "project_name": "cucmbers",
    "section_id": 9,
    "section_name": null,
    "status": true,
    "task_id": 60,
    "task_name": "new_task_name",
    "task_owner": "Ilusha Tester"
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
*POST /to_do_list/comment*
* Тело запроса на создание комментария:
```json
{
    "task_id": 40,          // обязательный аргумент
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
*PUT /to_do_list/comment*
* Тело запроса на изменение комментария
```json
{
    "comment_id": 40,       // обязательный аргумент
    "text": "This is the new comment text"
}
```
В ответ придет только статус
* Статус 200


## Удаление комментария
*DELETE /to_do_list/comment*
* Тело запроса на удаление комментария
```json
{
    "comment_id": 40
}
```
В ответ придет только статус
* Статус 200

## Создание раздела
*POST /to_do_list/section*
* Тело запроса на создание раздела
```json
{
    "project_id": 7,        // обязательный аргумент
    "name": "section_name"  // обязательный аргумент, но можно передать пустую строку
}
```
В ответ приходит только статус
* Статус 200

## Редактирование раздела
*PUT /to_do_list/section*
* Тело запроса на редактирование раздела
```json
{
    "section_id": 7,        // обязательный аргумент
    "name": "new_section_name"
}
```
В ответ приходит только статус
* Статус 200

## Удаление раздела
*DELETE /to_do_list/section*
* Тело запроса на удаление раздела
```json
{
    "section_id": 7
}
```
В ответ приходит только статус
* Статус 200

## Изменение порядка разделов
*PUT /to_do_list/section_order*
* Тело запроса на изменение порядка
```json
{
    "sections":
    [
    {"id":15},
    {"id":14},
    {"id":13},
    {"id":4},
    {"id":3}
    ],
    "project_id":29
}
```
В ответ приходит только статус
* Статус 200

## Удаление задачи
*DELETE /to_do_list/task*
* Тело запроса на удаление задачи
```json
{
    "task_id": 7
}
```
В ответ приходит только статус
* Статус 200