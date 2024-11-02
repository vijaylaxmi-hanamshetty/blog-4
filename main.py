from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, init_db
from crud import  get_post,get_posts,delete_post
from auth import get_current_active_user,get_password_hash,get_db,verify_password 
from fastapi.security import  OAuth2PasswordRequestForm

from models import User, Post
from schema import PostResponse
from typing import List
app = FastAPI()

# Initialize the database
init_db()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# User Registration endpoint
@app.post("/users/")
def create_user(username: str, password: str, role: str, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(password)
    new_user = User(username=username, hashed_password=hashed_password, role=role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"username": new_user.username, "role": new_user.role}

# User Authentication endpoint
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    # Here you should create and return JWT token (for simplicity, returning username)
    return {"access_token": user.username, "token_type": "bearer"}

# CRUD for Posts
@app.post("/posts/", response_model=dict)
def create_post_route(title: str, content: str, db: Session = Depends(get_db), current_user: dict = Depends(get_current_active_user)):
    if not isinstance(current_user, dict):
        raise HTTPException(status_code=500, detail="Current user data is invalid")
    
    new_post = Post(title=title, content=content, owner_id=current_user["id"])
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return {"title": new_post.title, "content": new_post.content}


@app.get("/posts/", response_model=List[dict])
def read_posts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    posts = get_posts(db, skip, limit)
    return [{"id": post.id, "title": post.title, "content": post.content} for post in posts]

@app.get("/posts/{post_id}", response_model=dict)
def read_post(post_id: int, db: Session = Depends(get_db)):
    post = get_post(db, post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"id": post.id, "title": post.title, "content": post.content}

@app.put("/posts/{post_id}", response_model=PostResponse)
def update_post(post_id: int, post_data: dict, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    
    for key, value in post_data.items():
        setattr(post, key, value)
    db.commit()
    db.refresh(post)
    
    return post

@app.delete("/posts/{post_id}")
def delete_post_route(post_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_active_user)):
    deleted_post = delete_post(db, post_id, current_user["id"])
    if deleted_post is None:
        raise HTTPException(status_code=404, detail="Post not found or not enough permissions")
    return {"detail": "Post deleted"}
