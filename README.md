# Task_board
Создаем свой собственный канбан

# Оглавление
1. [Получение списка проектов](#получение-списка-проектов)
2. [Создание проекта](#создание-проекта)
3. [Архивировать/разархивировать проект](#архивация-проекта)
4. [Удаление проекта из архива](#удаление-проекта-из-архива)

## Получение списка проектов
*GET /to_do_list/projects*

- Ответ, статус 200
```
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
```
{
    "name":"our_project"
    "is_favorites":"false",
}
```

## Архивация проекта
*PUT /to_do_list/projects*

- Запрос на **изменение статуса** проекта. ```true``` - в архиве, ```false``` - не в архиве
```
{
    "is_archive":true,
    "project_id":6
}
```
* Ответ в случае перемещения проекта в архив, статус 200
```
{
    "messege": "project moved to the archive"
}
```
* Ответ в случае если мы достаем проект из архива, статус 200
```
{
    "messege": "project moved from archive"
}
```

## Удаление проекта из архива
*DELETE /to_do_list/projects*

* Тело запроса на удаление архивированного проекта
```
{
    "project_id": 14
}
```
- Ответ в случае успешного удаления, статус 200
```
{
    "messege": "project deleted"
}
```
- Ответ на случай попытки удалить проект не в архиве, статус 400
```
{
    "messege": "the project is not archived"
}
```
## Получить задачи по project_id
*GET /to_do_list/tasks*

* Параметры запроса на получение списка задач у нужного проекта
```
project_id=7
```
Полный пример:
*/to_do_list/tasks?project_id=7*

## Создать задачу с указанием project_id
*POST /to_do_list/tasks*

* Тело запроса на создание задачи
```
{
    "name": "task_name",
    "description": "description_text",
    "project_id": 7
}
```