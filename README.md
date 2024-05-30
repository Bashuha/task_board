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
            "id": 7,
            "is_archive": true,
            "is_favorites": false,
            "project_name": "cucmbers",
            "sections": [
                {
                    "id": 9,
                    "name": "Тест создания раздела",
                    "project_id": 7
                },
                {
                    "id": 20,
                    "name": "Test order number 3",
                    "project_id": 7
                }
            ],
            "task_count": 4
        },
        {
            "id": 27,
            "is_archive": false,
            "is_favorites": true,
            "project_name": "Серёзный проектспасапсапсап",
            "sections": [
                {
                    "id": 23,
                    "name": "First order number",
                    "project_id": 27
                },
                {
                    "id": 24,
                    "name": "New sec name",
                    "project_id": 27
                }
            ],
            "task_count": 3
        },
        {
            "id": 31,
            "is_archive": true,
            "is_favorites": false,
            "project_name": "Нужно больше кельвинов x2",
            "sections": [],
            "task_count": 1
        },
        {
            "id": 37,
            "is_archive": false,
            "is_favorites": false,
            "project_name": "PROJECT",
            "sections": [
                {
                    "id": 31,
                    "name": "111",
                    "project_id": 37
                },
                {
                    "id": 39,
                    "name": "123",
                    "project_id": 37
                }
            ],
            "task_count": 6
        },
        {
            "id": 38,
            "is_archive": false,
            "is_favorites": false,
            "project_name": "Здорова, Айгиз",
            "sections": [
                {
                    "id": 34,
                    "name": "Раздел бананов",
                    "project_id": 38
                },
                {
                    "id": 35,
                    "name": "Раздел энергетиков",
                    "project_id": 38
                },
                {
                    "id": 36,
                    "name": "Раздел Атохиных мониторов",
                    "project_id": 38
                }
            ],
            "task_count": 1
        }
    ]
}
```

## Создание проекта
*POST /to_do_list/project*
* Тело запроса на **создание** проекта
```json
{
    "name": "our_project",      // обязательный аргумент
    "is_favorites": false       // может быть и true
}
```
В ответ приходит только статус
- Статус 200

## Редактирование проекта
*PUT /to_do_list/project*

- Запрос на редактирование проекта.
```json
{
    "id":28,         // обязательный аргумент
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
    "id":"31",      // обязательный аргумент
    "is_archive":true       // обязательный аргумент
}
```
* Статус 200

В ответ придет только статус

* Статус 404

Ответ, при попытке архивировать несуществующий проект
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
    "id": 14
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
* Статус 404
Ответ если проекта в базе нет
```json
{
    "message": "Проект не найден"
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
    "id": 7,
    "name": "cucmbers",
    "sections": [
        {
            "id": 9,
            "name": "Тест создания раздела",
            "tasks": [
                {
                    "comments_count": 0,
                    "description": "ну вот описание",
                    "id": 106,
                    "name": "Ща кое-что попробую",
                    "status": false
                },
                {
                    "comments_count": 0,
                    "description": "fewfwefwe",
                    "id": 107,
                    "name": "few",
                    "status": true
                }
            ]
        },
        {
            "id": 20,
            "name": "Test order number 3",
            "tasks": [
                {
                    "comments_count": 0,
                    "description": null,
                    "id": 113,
                    "name": "Task without proj_id",
                    "status": true
                }
            ]
        }
    ],
    "tasks": [
        {
            "comments_count": 0,
            "description": "is this works?",
            "id": 102,
            "name": "alchemy test",
            "status": true
        }
    ]
}
```

* Статус 200

Если не передавать параметр, то вернется список **входящих** задач

*/to_do_list/project*
```json
{
    "project_id": null,
    "project_name": "Входящие",
    "tasks": [
        {
            "comments_count": 0,
            "description": "Новое описание",
            "id": 61,
            "name": "Измененное название задачи",
            "status": false
        },
        {
            "comments_count": 0,
            "description": null,
            "id": 111,
            "name": "Готово опять?",
            "status": true
        },
        {
            "comments_count": 0,
            "description": "",
            "id": 120,
            "name": "Incoming task, the last one",
            "status": true
        }
    ]
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
    "name": "task_name",  // обязательный аргумент
    "description": "description_text",
    "section_id": 9,     // при передаче этого аргумента, project_id передавать не нужно; если не передавать section_id вовсе, задача будет вне разделов
    "project_id": 7   // передавать только в том случае, если создаешь задачу вне разделов; если не передавать project_id вовсе, создастся входящая задача
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
Ответ, если передан неверный **project_id** или **section_id**
```json
{
    "message": "Проект не найден"
}
```

## Редактировать задачу
*PUT /to_do_list/task*

* Тело запроса на редактирование задачи
```json
{
    "id": 60,      // обязательный аргумент
    "name": "new_task_name",
    "description": "new_description_text",
    "section_id": 9,    // при передаче section_id, project_id передавать не нужно; при значени null задача будет вне разделов.
    "project_id": 7,    // если передать null, задача перейдет во "Входящие", в остальных случаях задача перейдет в другой проект вне разделов
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

* Статус 404

Ответ в случае если указан несуществующий раздел
```json
{
    "message": "Раздел не найден"
}
```
Или несуществующий проект
```json
{
    "message": "Проект не найден"
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
    "id": 60,
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
    "id": 57,
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
    "detail": "Задача не найдена"
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
    "id": 40,       // обязательный аргумент
    "text": "This is the new comment text"
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

Ответ, если комментария в базе нет
```json
{
    "message": "Комментарий не найден"
}
```

## Удаление комментария
*DELETE /to_do_list/comment*
* Тело запроса на удаление комментария
```json
{
    "id": 40
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
* Статус 200

Ответ
```json
{
    "message": "ok"
}
```
* Статус 404

Ответ при попытке создания раздела в несуществующем проекте
```json
{
    "message": "Проект не найден"
}
```
## Редактирование раздела
*PUT /to_do_list/section*
* Тело запроса на редактирование раздела
```json
{
    "id": 7,        // обязательный аргумент
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
