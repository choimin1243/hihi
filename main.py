from fastapi import FastAPI, Depends,Request
import models
from models import Students_write,Todos,todos_students_association
from database import engine
from routers import auth, todos
from starlette.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Depends, HTTPException, status, APIRouter, Request, Response, Form
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI()

models.Base.metadata.create_all(bind=engine)
# app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth.router)
app.include_router(todos.router)


templates=Jinja2Templates(directory="templates")

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

class TodoItem(BaseModel):
    name: str
    todo_title: str
    id: int
@app.get("/",response_class=HTMLResponse)
async def register(request: Request):
    return templates.TemplateResponse("main.html", {"request": request})



@app.get("/students/",response_class=HTMLResponse)
async def students(request:Request):
    return templates.TemplateResponse("students_enter.html",{"request":request})


@app.post("/students/")
async def submit_password(request:Request,password: str = Form(...), db: Session = Depends(get_db)):
    passwords = db.query(models.Users).filter(models.Users.code ==password).first()
    print(passwords)
    if passwords is None:
        msg="참여코드가 존재하지 않습니다."
        return templates.TemplateResponse("students_enter.html", {"request": request, "message": msg})

    else:
        name = passwords.username
        next_page_url = f"/student_detail/{name}"  # 경로에 pass2 값을 포함
        return RedirectResponse(url=next_page_url, status_code=status.HTTP_302_FOUND)


@app.get("/student_detail/{name}")
async def start_write(request: Request, name: str, db: Session = Depends(get_db)):
    print(name)
    user = db.query(models.Users).filter(models.Users.username == name).first()
    todos=db.query(models.Todos).filter(models.Todos.owner_id==user.id).all()
    list=[]
    for Todo in todos:
        if Todo.complete==False:
            list.append(Todo)

    return templates.TemplateResponse("detail.html", {"request": request, "todos": list})


@app.get("/todos/{todo_id}")
async def start_write_detail(request: Request,todo_id:int,db: Session = Depends(get_db)):
    Todos=db.query(models.Todos).filter(models.Todos.id==todo_id).first()
    title=Todos.title
    description=Todos.description
    print(title)
    print(description)

    return templates.TemplateResponse("write.html",{"request":request,"Todos":Todos})


@app.post("/add_write/")
async def add_todo(todo_item: TodoItem):
    db = SessionLocal()
    name = todo_item.name
    todo_title = todo_item.todo_title
    id=todo_item.id

    # 새로운 Students_write 객체 생성
    new_student = Students_write(students_name=name, text=todo_title)

    print(id)
    todo = db.query(Todos).filter(Todos.id == id).first()

    if todo:
        todo.students_writes.append(new_student)

        # 세션에 추가하고 커밋
        db.add(new_student)
        db.commit()
        print("Students_write 객체가 성공적으로 추가되었습니다.")

    return {"name": name, "todo_title": todo_title, "message": "데이터가 성공적으로 전송되었습니다."}


@app.get("/watchall/{todo_id}")
async def watch_all(request: Request,todo_id:int,db: Session = Depends(get_db)):
    db = SessionLocal()
    stmt = select(todos_students_association.c.student_write_id).where(todos_students_association.c.todo_id == todo_id)
    result = db.execute(stmt)

    student_write_ids = [row[0] for row in result.fetchall()]
    students_write_objects = db.query(Students_write).filter(Students_write.id.in_(student_write_ids)).all()

    print(students_write_objects)

    return templates.TemplateResponse("show.html", {"request": request, "todos": students_write_objects})

