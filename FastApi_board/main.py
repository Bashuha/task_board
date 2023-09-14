from fastapi import FastAPI
import uvicorn
from database.config import API
from projects.route import router as project_router
from tasks.route import router as task_router

app = FastAPI(
    title="Task Board"
)

app.include_router(project_router)
app.include_router(task_router)


# @app.get("/")
# def project():
#     return "Here the place for json"


# @app.get("/project")
# def get_project(porject_id: int):
#     pass


# @app.post("/project")
# def create_project(args: dict):
#     pass 


uvicorn.run(app, host= API.get('host'), port= API.getint('port'))