from fastapi import APIRouter, HTTPException, Depends,Response,File,UploadFile,Request,Form
from sqlalchemy.orm import Session
from schemas import  User,UserBase,Userlogin
from crud import get_user_by_email,create_user,update_user,get_user_by_id
from database import get_db
from routes.service.auth import verify_password,create_access_token,create_refresh_token,verify_token,hash_password,verify_refresh_token



router = APIRouter()



def get_token_from_cookie(request: Request):
    token = request._cookies.get('access_token') or  request._headers.get('Authorization').split('Bearer')[1].strip()
    verified_payload = verify_token(token=token)
    return verified_payload



@router.post("/register", response_model=User)
async def register_user(user: UserBase, db: Session = Depends(get_db),response: Response = None):
    if get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user=await create_user(db, user)
    if not new_user:
        raise HTTPException(status_code=500,detail="Failed to create user")
    response.set_cookie('access_token',new_user.access_token)
    response.set_cookie('refersh_token',new_user.refresh_token)
    
    return  new_user


@router.post("/login",response_model=User)
async def login_user(user:Userlogin,db:Session=Depends(get_db),response:Response =None):
    logged_user=  get_user_by_email(db, user.email)
    if not logged_user:
        raise HTTPException(status_code=401,detail="Invalid password or email")
    if not await verify_password(user.password,logged_user.password):
        raise HTTPException(status_code=401,detail="Invalid password or email")
    access_token=await create_access_token(logged_user)
    refresh_token=await create_refresh_token(logged_user)
    await update_user(db=db,refresh_token=refresh_token,access_token=access_token,id=logged_user.id)
    response.set_cookie('access_token',logged_user.access_token)
    response.set_cookie('refersh_token',logged_user.refresh_token)
    return logged_user


@router.patch('/update',response_model=User)
async def update_users(name:str=Form(None),email:str=Form(None),password:str=Form(None),avatar:UploadFile=File,token:str=Depends(get_token_from_cookie),db:Session=Depends(get_db),request:Request=None):
       try:
            token=request._cookies.get('access_token') or request._headers.get('Authorization').split('Bearer')[1].strip()
            payload = verify_token(token)
            user_id = payload.get("sub") 
            user = get_user_by_id(db, user_id)
            if not user:
               raise HTTPException(status_code=404, detail="User not found")

        # Update fields if provided
            if name:
              user.name = name
            if email:
              user.email = email
            if password:
              user.password = await hash_password(password)  # Make sure the password is hashed before saving
            if avatar:
            # Handle avatar saving, e.g. save the file to disk or cloud storage
              user.avatar = avatar.filename  # You can store avatar in the database as a filename or path

        # Commit the changes to the database
            db.commit()
            db.refresh(user)
            return user

       except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post('/logout')
async def logout_user(token:str=Depends(get_token_from_cookie),request:Request=None):
    try:
        request._cookies.clear()
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post('/refresh')
async def refresh_token(request:Request=None,response:Response=None,db:Session=Depends(get_db)):
    try:
      token = request._cookies.get('refersh_token') or  request._headers.get('Authorization').split('Bearer')[1].strip()
      payload=verify_refresh_token(token=token)
      user_id = payload.get("sub")
      user=get_user_by_id(db=db,user_id=user_id)
      if not user:
          raise HTTPException(status_code=404,detail="User not found")
      access_token=await create_access_token(user)
      refresh_token=await create_refresh_token(user)
      await update_user(db=db,refresh_token=refresh_token,access_token=access_token,id=user.id)
      response.set_cookie('access_token',user.access_token)
      response.set_cookie('refersh_token',user.refresh_token)
      return user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.get('/user-details',response_model=User)
def user_detail(token:str=Depends(get_token_from_cookie),request:Request=None,db:Session=Depends(get_db)):
    try:
      token = request._cookies.get('refersh_token') or  request._headers.get('Authorization').split('Bearer')[1].strip()
      payload=verify_refresh_token(token=token)
      user_id = payload.get("sub")
      user=get_user_by_id(db=db,user_id=user_id)
      if not user:
          raise HTTPException(status_code=404,detail="User not found")
      return user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))