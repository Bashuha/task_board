from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
from database.config import API
from projects.route import router as project_router
from tasks.route import router as task_router
from sections.route import router as section_router
from comments.route import router as comment_router
from projects.route import MyException


app = FastAPI(
    title="Task Board"
)

app.include_router(project_router)
app.include_router(task_router)
app.include_router(section_router)
app.include_router(comment_router)


if __name__ == '__main__':
    app.root_path = '/to_do_list'
    uvicorn.run(app, host= API.get('host'), port= API.getint('port'))