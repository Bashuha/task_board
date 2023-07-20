# Task_board
Создаем свой собственный канбан

### GET /to_do_list/projects
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
}
```
### POST /to_do_list/projects
* Тело запроса на **создание** проекта
```
{
    "name":"our_project"
    "is_favorites":"false",
}
```
### PUT /to_do_list/projects
- Запрос на **изменение статуса** проекта. ```true``` - в архиве, ```false``` - не в архиве
```
{
    "is_archive":true,
    "id":6
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
### DELETE /to_do_list/projects
* Тело запроса на удаление архивированного проекта
```
{
    "id": 14
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

