from __future__ import annotations
from sqlalchemy import Column, ForeignKey, Table, select, insert, func
from sqlalchemy.dialects.mysql import (
    INTEGER,
    VARCHAR,
    DATETIME,
    TIMESTAMP,
    BOOLEAN,
    TEXT,
    DATE
)
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped
from database.my_engine import engine


class Base(DeclarativeBase):
    pass


tag_task_link = Table(
    'task_tag',
    Base.metadata,
    Column('tag_id', ForeignKey('tag.id', ondelete='cascade'), primary_key=True),
    Column('task_id', ForeignKey('Task.id', ondelete='cascade'), primary_key=True)
)


class User(Base):
    __tablename__ = "user"

    login = Column(VARCHAR(50), primary_key=True)
    password = Column(VARCHAR(255), nullable=False)
    is_active = Column(BOOLEAN(), nullable=False, server_default='1')
    # date_create = Column(DATETIME(timezone=True), server_default=func.now())
    date_create = Column(TIMESTAMP(timezone=True), server_default=func.now())

    user_addition: Mapped[UserInfo] = relationship(
        back_populates='user',
    )


class UserInfo(Base):
    __tablename__ = "user_info"

    id = Column(INTEGER(), primary_key=True)
    login = Column(
        ForeignKey(
            User.login,
            onupdate='cascade',
            ondelete='cascade',
        ),
        nullable=False,
    )
    first_name = Column(VARCHAR(100), nullable=False)
    second_name = Column(VARCHAR(100), nullable=False)

    user: Mapped[User] = relationship(
        # cascade='all, delete-orphan',
        back_populates='user_addition',
        single_parent=True,
    )


class Project(Base):
    __tablename__ = "Project"

    id = Column(INTEGER(), primary_key=True)
    name = Column(VARCHAR(150), nullable=False)
    date = Column(TIMESTAMP(timezone=True), server_default=func.now())
    # date = Column(DATETIME(timezone=True), server_default=func.now())
    is_incoming = Column(BOOLEAN(), server_default="0")
    is_archive = Column(BOOLEAN(), server_default="0")

    tasks: Mapped[list[Task]] = relationship(back_populates="project")
    sections: Mapped[list[Sections]] = relationship(back_populates='project')
    user_link: Mapped[list[ProjectUser]] = relationship(
        back_populates="project_info",
    )


class Sections(Base):
    __tablename__ = "Sections"

    id = Column(INTEGER(), primary_key=True)
    name = Column(VARCHAR(150), nullable=False)
    project_id = Column(
        INTEGER(),
        ForeignKey(
            Project.id,
            ondelete='cascade'
        ),
        nullable=False,
    )
    order_number = Column(INTEGER(), nullable=False)
    is_basic = Column(BOOLEAN(), nullable=False, server_default='0')

    project: Mapped[Project] = relationship(back_populates='sections')
    tasks: Mapped[list[Task]] = relationship(
        back_populates='sections',
    )


class Task(Base):
    __tablename__ = "Task"

    id = Column(INTEGER(), primary_key=True)
    name = Column(VARCHAR(255), nullable=False)
    description = Column(TEXT(), nullable=True)
    owner_id = Column(
        ForeignKey(
            UserInfo.id,
            ondelete='set null'
        ),
        nullable=True
    )
    executor_id = Column(
        ForeignKey(
            UserInfo.id,
            ondelete='set null'
        ),
        nullable=True
    )
    task_giver_id = Column(
        ForeignKey(
            UserInfo.id,
            ondelete='set null'
        ),
        nullable=True
    )
    project_id = Column(ForeignKey(Project.id, ondelete='cascade'))
    create_date = Column(TIMESTAMP(timezone=True), server_default=func.now())
    # create_date = Column(DATETIME(timezone=True), server_default=func.now())
    section_id = Column(ForeignKey(Sections.id, ondelete='cascade'))
    status = Column(BOOLEAN(), server_default="1")
    order_number = Column(INTEGER(), nullable=False)
    to_do_date = Column(DATE(), nullable=True)

    project: Mapped[Project] = relationship(back_populates="tasks")
    sections: Mapped[Sections] = relationship(back_populates="tasks")
    comments: Mapped[list[Comments]] = relationship(back_populates="task", cascade='all, delete-orphan')
    executor_info: Mapped[UserInfo] = relationship(foreign_keys=[executor_id])
    owner_info: Mapped[UserInfo] = relationship(foreign_keys=[owner_id])
    task_giver_info: Mapped[UserInfo] = relationship(foreign_keys=[task_giver_id])
    tag_info: Mapped[list[Tag]] = relationship(
        secondary=tag_task_link,
        back_populates='task_info',
    )


class Comments(Base):
    __tablename__ = "Comments"

    id = Column(INTEGER(), primary_key=True)
    # переделать привязку комментария к пользователю, сменить на user_id
    user_id = Column(ForeignKey(UserInfo.id, ondelete='set null'), nullable=True)
    text = Column(VARCHAR(1024), nullable=False)
    # create_at = Column(DATETIME(timezone=True), server_default=func.now())
    create_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    task_id = Column(ForeignKey(Task.id, ondelete='cascade'), nullable=False)

    task: Mapped[Task] = relationship(back_populates='comments')


class ProjectUser(Base):
    __tablename__ = 'project_user'

    project_id = Column(
        ForeignKey(
            Project.id,
            ondelete='cascade'
        ),
        primary_key=True,
        nullable=False
    )
    user_id = Column(
        ForeignKey(
            UserInfo.id,
            ondelete='cascade'
        ),
        primary_key=True,
        nullable=False
    )
    is_favorites = Column(BOOLEAN(), nullable=False, server_default="0")
    is_owner = Column(BOOLEAN(), nullable=False, server_default="0")

    project_info: Mapped[Project] = relationship(back_populates="user_link",)
    user_info: Mapped[UserInfo] = relationship()


class TagColor(Base):
    __tablename__ = "tag_color"

    id = Column(INTEGER(), primary_key=True, autoincrement=True)
    name = Column(VARCHAR(50), nullable=False)
    color = Column(VARCHAR(7), nullable=False)


class Tag(Base):
    __tablename__ = "tag"

    id = Column(INTEGER(), primary_key=True, autoincrement=True)
    name = Column(VARCHAR(255), nullable=False)
    project_id = Column(
        ForeignKey(
            Project.id,
            ondelete='cascade'
        ),
        nullable=False
    )
    color_id = Column(ForeignKey(TagColor.id), nullable=False, server_default="1")

    color_info: Mapped[TagColor] = relationship()
    project: Mapped[Project] = relationship()
    task_info: Mapped[Task] = relationship(
        secondary=tag_task_link,
        back_populates='tag_info'
    )


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with engine.begin() as session:
        color_dict = {
            "1": {
                "id": 1,
                "name": "серый",
                "color": "#C0C0C0"
            },
            "2": {
                "id": 2,
                "name": "зелёный",
                "color": "#72A25A"
            },
            "3": {
                "id": 3,
                "name": "оранжевый",
                "color": "#F19A47"
            },
            "4": {
                "id":4,
                "name": "красный",
                "color": "#E75555"
            },
            "5": {
                "id":5,
                "name": "синий",
                "color": "#567BE2"
            },
            "6": {
                "id":6,
                "name": "голубой",
                "color": "#80C9D9"
            },
            "7": {
                "id":7,
                "name": "фиолетовый",
                "color": "#A873BB"
            },
            "8": {
                "id":8,
                "name": "желтый",
                "color": "#FBBF24"
            },
            "9": {
                "id":9,
                "name": "розовый",
                "color": "#FB82E0"
            },
            "10": {
                "id":10,
                "name": "коричневый",
                "color": "#8F5F41"
            },
        }
        color_ids_query = await session.execute(
            select(TagColor.id)
        )
        color_ids_list = color_ids_query.scalars().all()
        for color_id in color_ids_list:
            color_dict.pop(str(color_id), None)
        
        if color_dict:
            await session.execute(
                insert(TagColor).
                values(list(color_dict.values()))
            )
            await session.commit()