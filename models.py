from sqlalchemy import Column, Integer, String,ForeignKey,Table
from sqlalchemy.orm import relationship
from database import Base

# Many-to-many relationship table for likes
post_likes_table = Table(
    "post_likes",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("post_id", Integer, ForeignKey("posts.id"))
    
)
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String)  
    comments = relationship("Comment", back_populates="user")
    liked_posts = relationship("Post", secondary=post_likes_table, back_populates="liked_by")


class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User")
    comments = relationship("Comment", back_populates="post")
    liked_by = relationship("User", secondary=post_likes_table, back_populates="liked_posts")

# models  on comment
class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    post_id = Column(Integer, ForeignKey("posts.id"))
    
    user = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")
     