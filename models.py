from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from sqlalchemy import Table, Column, Integer, ForeignKey, String


todos_students_association = Table(
    'todos_students', Base.metadata,
    Column('todo_id', ForeignKey('todos.id'), primary_key=True),
    Column('student_write_id', ForeignKey('write_students.id'), primary_key=True)
)


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    todos = relationship("Todos", back_populates="owner")


class Todos(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    complete = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("Users", back_populates="todos")

    # 다대다 관계 설정
    students_writes = relationship(
        "Students_write",
        secondary=todos_students_association,
        back_populates="todos"
    )


class Students_write(Base):
    __tablename__ = "write_students"
    id = Column(Integer, primary_key=True, index=True)
    students_name = Column(String)
    text = Column(String)

    # 다대다 관계 설정
    todos = relationship(
        "Todos",
        secondary=todos_students_association,
        back_populates="students_writes"
    )
