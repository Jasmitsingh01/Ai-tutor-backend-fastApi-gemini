from sqlalchemy.orm import Session
from models import User
from schemas import UserBase, UserUpdate
from routes.service.auth import hash_password, create_refresh_token, create_access_token
from fastapi import HTTPException


def get_user_by_email(db: Session, email: str):
    user = db.query(User).filter(User.email == email).first()
    return user


def get_user_by_id(db:Session,user_id:int):
     user = db.query(User).filter(User.id == user_id).first()
     return user

async def update_user(
    db: Session,
    id: int,
    access_token: str = None,
    refresh_token: str = None,
    name: str = None,
    email: str = None,
    avatar: str = None,
    password: str = None,
):
    update_user = db.query(User).filter(User.id == id).first()
    if not update_user:
        raise HTTPException(status_code=404, detail="No user Found")
    if name:
        update_user.name = name
    if email:
        update_user.email = email
    if avatar:
        update_user.avtar = avatar
    if password:
        update_user.password = password
    if refresh_token:
        update_user.refresh_token = refresh_token
    if access_token:
        update_user.access_token = access_token

    db.commit()  ## save the user
    db.refresh(update_user)
    return update_user


async def create_user(db: Session, user: UserBase):
    newPassword = await hash_password(user.password)
    db_user = User(name=user.name, email=user.email, password=newPassword)
    refresh_token = await create_refresh_token(db_user)
    access_token = await create_access_token(db_user)
    db_user.refresh_token = refresh_token
    db_user.access_token = access_token
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
