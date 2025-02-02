from sqlalchemy import Column, Integer, String,ARRAY


from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    avtar = Column(String,default="Please upload your avatar")
    score = Column(Integer,default=0)
    history=Column(ARRAY(dict))
    access_token = Column(String)
    refresh_token = Column(String)