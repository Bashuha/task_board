from fastapi import APIRouter, FastAPI, HTTPException, Query, Request, WebSocket, WebSocketDisconnect
import uvicorn
from database.config import API
from fastapi.responses import JSONResponse
import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from database.schemas import init_models

from projects.route import router as project_router
from tasks.route import router as task_router
from tasks.route import websocket_route as ws_task_router
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
    # await init_models()
    yield


app = FastAPI(
    title="Task Board",
    lifespan=lifespan
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.add_websocket_route("/ws", ws_task_router)
app.include_router(ws_task_router)
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


# class ConnectionManager:
#     def __init__(self):
#         self.active_connections: list[WebSocket] = []

#     async def connect(self, websocket: WebSocket):
#         await websocket.accept()
#         self.active_connections.append(websocket)

#     def disconnect(self, websocket: WebSocket):
#         self.active_connections.remove(websocket)

#     async def send_personal_message(self, message: str, websocket: WebSocket):
#         await websocket.send_text(message)

#     async def broadcast(self, json_data: dict):
#         for connection in self.active_connections:
#             await connection.send_text(json_data)
            # await connection.send_json(json_data)


# manager = ConnectionManager()
# new_router = APIRouter()
# from typing import Optional

# @new_router.websocket("/ws")
# async def websocket_try(
#     # task: CreateTask,
#     websocket: WebSocket,
#     prefix: Optional[str] = Query(None)
#     # session: AsyncSession = Depends(get_db),
#     # user: UserInfo = Depends(get_current_user)
# ):
#     await manager.connect(websocket)
#     try:
#         while True:
#             data = await websocket.receive_text()
#             # await websocket.send_text(f"Message text was: {data}")
#             await manager.broadcast(f"New client says: {data}")
#     except WebSocketDisconnect:
#         manager.disconnect(websocket)
#         await manager.broadcast(f"Somebody left the chat")

# app.include_router(new_router)


# port 5017
if __name__ == '__main__':
    app.root_path = '/to_do_list'
    # uvicorn.run(app, host="127.0.0.1", port=5588)
    uvicorn.run(app, host=API.get('host'), port=API.getint('port'))
