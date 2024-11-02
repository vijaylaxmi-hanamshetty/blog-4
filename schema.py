from pydantic import BaseModel

class PostBase(BaseModel):
    title: str
    content: str

class PostCreate(PostBase):
    pass

class Post(PostBase):
    id: int
    
class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    owner_id: int


    class Config:
        from_attribute = True
