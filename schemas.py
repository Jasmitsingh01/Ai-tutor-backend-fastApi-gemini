from pydantic import BaseModel
from typing import Optional, List





class Userlogin(BaseModel):
       email:str
       password:str
       class Config:
         from_attributes = True 




class UserBase(Userlogin):
    name: str
   
    class Config:
        from_attributes = True 
 


class User(BaseModel):
    name: str
    email: str
    avtar:str
    access_token:Optional[str]=None
    refresh_token:Optional[str]=None
    class Config:
        from_attributes = True 
    
class UserUpdate(User):
    score:Optional [int]=None
   
    class Config:
        from_attributes=True