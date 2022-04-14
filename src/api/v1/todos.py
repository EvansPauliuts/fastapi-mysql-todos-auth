from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional

from api.v1.auth import get_user_exception, get_current_user
from src.models import todos
from src.database.db import get_db


router = APIRouter(
    prefix="/todos", tags=["todos"], responses={401: {"description": "Not found"}}
)


class Todo(BaseModel):
    title: str
    description: Optional[str]
    priority: int = Field(gt=0, lt=6, description="The priority must  be between 1-5")
    complete: bool


@router.get("/")
async def read_all(db: Session = Depends(get_db)):
    return db.query(todos.Todos).all()


@router.get("/user")
async def read_all_by_user(
    user: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    if user is None:
        raise get_user_exception()

    return db.query(todos.Todos).filter(todos.Todos.owner_id == user.get("id")).all()


@router.get("/todo/{todo_id}")
async def read_todo(
    todo_id: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    if user is None:
        raise get_user_exception()

    todo_model = (
        db.query(todos.Todos)
        .filter(todos.Todos.id == todo_id)
        .filter(todos.Todos.owner_id == user.get("id"))
        .first()
    )

    if todo_model is not None:
        return todo_model

    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")


@router.get("/{todo_id}")
async def read_todo(todo_id: int, db: Session = Depends(get_db)):
    todo_model = db.query(todos.Todos).filter(todos.Todos.id == todo_id).first()

    if todo_model is not None:
        return todo_model

    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")


@router.post("/")
async def create_todo(
    todo: Todo, user: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    if user is None:
        raise get_user_exception()

    todo_model = todos.Todos()
    todo_model.title = todo.title
    todo_model.description = todo.description
    todo_model.priority = todo.priority
    todo_model.complete = todo.complete
    todo_model.owner_id = user.get("id")

    db.add(todo_model)
    db.commit()

    return {"status": status.HTTP_201_CREATED, "transaction": "Successful"}


@router.put("/{todo_id}")
async def update_todo(
    todo_id: int,
    todo: Todo,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user is None:
        raise get_user_exception()

    todo_model = (
        db.query(todos.Todos)
        .filter(todos.Todos.id == todo_id)
        .filter(todos.Todos.owner_id == user.get("id"))
        .first()
    )

    if todo_model is None:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found"
        )

    todo_model.title = todo.title
    todo_model.description = todo.description
    todo_model.priority = todo.priority
    todo_model.complete = todo.complete

    db.add(todo_model)
    db.commit()

    return {"status": status.HTTP_200_OK, "transaction": "Successful"}


@router.delete("/{todo_id}")
async def delete_todo(
    todo_id: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    if user is None:
        raise get_user_exception()

    todo_model = (
        db.query(todos.Todos)
        .filter(todos.Todos.id == todo_id)
        .filter(todos.Todos.owner_id == user.get("id"))
        .first()
    )

    if todo_model is None:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found"
        )

    db.query(todos.Todos).filter(todos.Todos.id == todo_id).delete()
    db.commit()

    return {"status": status.HTTP_201_CREATED, "transaction": "Successful"}
