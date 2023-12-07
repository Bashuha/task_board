from fastapi import FastAPI, HTTPException, Request
import uvicorn
from database.config import API
from fastapi.responses import JSONResponse

from projects.route import router as project_router
from tasks.route import router as task_router
from sections.route import router as section_router
from comments.route import router as comment_router
from users.route import router as user_router


app = FastAPI(
    title="Task Board"
)

app.include_router(user_router)
app.include_router(project_router)
app.include_router(task_router)
app.include_router(section_router)
app.include_router(comment_router)


@app.exception_handler(HTTPException)
async def error_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code,
                        content={"message": f'{exc.detail}'})

# port 5017
if __name__ == '__main__':
    # app.root_path = '/to_do_list'
    uvicorn.run(app, host= API.get('host'), port= API.getint('port'))