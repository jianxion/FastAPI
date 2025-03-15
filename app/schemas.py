from datetime import datetime
from pydantic import BaseModel, EmailStr, conint
from typing import Optional
from datetime import datetime
# Schema/Pydantic Models define the structure of a request & response
# This ensure that when a user wants to create a post, the request will
#  only go through if it has a “title” and “content” in the body"



class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: str
    created_at: datetime

    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True



# for each different request
class PostCreate(PostBase):
    pass

# define what the response looks like inherit from postbase class
class PostResponse(PostBase):
    id: int
    created_at: datetime
    owner_id: int
    owner: UserOut

    # tell pydantic this can be converted to a dict
    class Config:
        orm_mode = True

class PostOut(BaseModel):
    Post: PostResponse
    votes: int

    class Config:
        orm_mode = True
        from_attributes = True


class UpdatePostPublished(PostBase):
    published: bool



class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[int] = None


class Vote(BaseModel):
    post_id: int
    dir: conint(le=1)


class DocumentBase(BaseModel):
    id: int
    document_name: str
    document_size: int


class DocumentCreate(DocumentBase):
    user_id: int
    is_active: bool


class DocumentInDB(DocumentBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentResponse(DocumentInDB):
    pass


class MessageBase(BaseModel):
    sender_id: int
    receiver_id: int
    content: str
    

class MessageCreate(MessageBase):
    pass

class MessageInDB(MessageBase):
    id: int
    created_at: datetime
    class Config:
        orm_mode = True
        from_attributes = True

class MessageResponse(MessageInDB):
    class Config:
        orm_mode = True




class NotificationBase(BaseModel):
    message: str
    is_read: bool

class NotificationCreate(NotificationBase):
    user_id: int
    broadcast: bool = False  # indicate if the notification is for all users
    is_read: bool = False

    class Config:
        orm_mode = True
        from_attributes = True

class NotificationInDb(NotificationBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        orm_mode = True
        from_attributes = True

class NotificationResponse(NotificationInDb):
    class Config:
        orm_mode = True
        from_attributes = True




