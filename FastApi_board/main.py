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


@app.exception_handler(MyException)
async def my_exception_handler(request: Request, exc: MyException):
    return JSONResponse(status_code=404, content={"message": f"not like this, {exc.name}"})


uvicorn.run(app, host= API.get('host'), port= API.getint('port'))