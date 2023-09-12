from fastapi import FastAPI
import uvicorn
from database.config import API
from routers.project import router


app = FastAPI(
    title="Task Board"
)


app.include_router(router)


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