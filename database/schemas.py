from __future__ import annotations
from sqlalchemy import Column, ForeignKey, inspect, func
from sqlalchemy.dialects.mysql import (
    INTEGER,
    VARCHAR,
    DATETIME,
    BOOLEAN,
)
import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.orm import Mapped


@as_declarative()
class Base:
    def _asdict(self):
        result = dict()
        for c in inspect(self).mapper.column_attrs:
            value = getattr(self, c.key)
            if isinstance(value, datetime.datetime):
                value = value.strftime('%d.%m.%Y %H:%M')
            elif isinstance(value, datetime.date):
                value = value.strftime('%d.%m.%Y')
            elif isinstance(value, datetime.time):
                value = value.strftime('%H:%M')
            result[c.key] = value
        
        return result
    

class Project(Base):
    __tablename__ = "Project"

    id = Column(INTEGER(), primary_key=True)
    name = Column(VARCHAR(255), nullable=False)
    date = Column(DATETIME(timezone=True), server_default=func.now())
    is_favorites = Column(BOOLEAN(), server_default="0")
    is_archive = Column(BOOLEAN(), server_default="0")

    Task: Mapped[list[Task]] = relationship(lazy='joined')
    Sections: Mapped[list[Sections]] = relationship(lazy='joined')


class Sections(Base):
    __tablename__ = "Sections"

    id = Column(INTEGER(), primary_key=True)
    name = Column(VARCHAR(255), nullable=False)
    project_id = Column(INTEGER(), ForeignKey(Project.id), nullable=False)
    order_number = Column(INTEGER(), nullable=False)

    Project: Mapped[Project] = relationship(lazy='joined')
    Task: Mapped[list[Task]] = relationship(lazy='joined')


class Task(Base):
    __tablename__ = "Task"

    id = Column(INTEGER(), primary_key=True)
    name = Column(VARCHAR(255), nullable=False)
    description = Column(VARCHAR(255), nullable=False)
    owner = Column(VARCHAR(255), nullable=False)
    project_id = Column(INTEGER(), ForeignKey(Project.id), nullable=True)
    create_date = Column(DATETIME(timezone=True), server_default=func.now())
    section_id = Column(INTEGER(), ForeignKey(Sections.id), nullable=True)
    status = Column(BOOLEAN(), server_default="1")

    Project: Mapped[Project] = relationship(lazy='joined')
    Section: Mapped[Sections] = relationship(lazy='joined')
    Comments: Mapped[list[Comments]] = relationship(lazy='joined')


class Comments(Base):
    __tablename__ = "Comments"

    id = Column(INTEGER(), primary_key=True)
    login = Column(VARCHAR(255), nullable=False)
    text = Column(VARCHAR(255), nullable=False)
    create_at = Column(DATETIME(timezone=True), server_default=func.now())
    task_id = Column(INTEGER(), ForeignKey(Task.id), nullable=True)

    Task: Mapped[Task] = relationship()


class Users(Base):
    __tablename__ = "Users"

    id = Column(INTEGER(), primary_key=True)
    login = Column(VARCHAR(255), nullable=False)
    password = Column(VARCHAR(255), nullable=False)
    date_cr = Column(DATETIME(timezone=True), server_default=func.now())
