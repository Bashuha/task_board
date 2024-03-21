from fastapi import FastAPI, HTTPException, Request
import uvicorn
from database.config import API
from fastapi.responses import JSONResponse
import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler
from contextlib import asynccontextmanager
from database.schemas import init_models

from projects.route import router as project_router
from tasks.route import router as task_router
from sections.route import router as section_router
from comments.route import router as comment_router
from users.auth import router as user_router
from tags.route import router as tag_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    log = logging.getLogger(__name__)
    log.setLevel(logging.INFO)
    Path('logs').mkdir(mode=0o774, exist_ok=True)
    logger = logging.getLogger("uvicorn.error")
    handler = RotatingFileHandler(
        "logs/unexpected_exceptions.log",
        mode="a",
        maxBytes = 100*1024,
        backupCount = 3,
    )
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)
    await init_models()
    yield


app = FastAPI(
    title="Task Board",
    lifespan=lifespan
)

app.include_router(user_router)
app.include_router(project_router)
app.include_router(task_router)
app.include_router(section_router)
app.include_router(comment_router)
app.include_router(tag_router)


@app.exception_handler(HTTPException)
async def error_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": f'{exc.detail}'}
    )


# port 5017
if __name__ == '__main__':
    app.root_path = '/to_do_list'
    uvicorn.run(app, host= API.get('host'), port= API.getint('port'))
