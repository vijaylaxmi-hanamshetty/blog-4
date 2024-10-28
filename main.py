from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship, Session
from passlib.context import CryptContext
from typing import List, Optional

# Database setup
DATABASE_URL = "sqlite:///./blog.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})  # For SQLite
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String)  # admin, author, or reader

class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User")

# Create the database tables
Base.metadata.create_all(bind=engine)

# Security setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# FastAPI app
app = FastAPI()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Utility functions for password management
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# Authentication and role management
def get_current_user(token: str = Depends(oauth2_scheme)):
    # Here, implement your JWT token verification and user extraction logic
    return {"username": "user", "role": "author", "id": 1}  # Placeholder for actual user extraction

def get_current_active_user(current_user: dict = Depends(get_current_user)):
    return current_user

def get_user_role(current_user: dict = Depends(get_current_active_user)):
    return current_user.get("role")

# User Registration
@app.post("/users/", response_model=dict)
def create_user(username: str, password: str, role: str, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(password)
    new_user = User(username=username, hashed_password=hashed_password, role=role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"username": new_user.username, "role": new_user.role}

# User Authentication
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    # Here you should create and return JWT token (for simplicity, returning username)
    return {"access_token": user.username, "token_type": "bearer"}

# CRUD for Posts
@app.post("/posts/", response_model=dict)
def create_post(title: str, content: str, db: Session = Depends(get_db), current_user: dict = Depends(get_current_active_user)):
    role = get_user_role(current_user)
    if role not in ["admin", "author"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    new_post = Post(title=title, content=content, owner_id=current_user["id"])
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return {"title": new_post.title, "content": new_post.content}

@app.get("/posts/", response_model=List[dict])
def read_posts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    posts = db.query(Post).offset(skip).limit(limit).all()
    return [{"id": post.id, "title": post.title, "content": post.content} for post in posts]

@app.get("/posts/{post_id}", response_model=dict)
def read_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"id": post.id, "title": post.title, "content": post.content}

@app.put("/posts/{post_id}", response_model=dict)
def update_post(post_id: int, title: str, content: str, db: Session = Depends(get_db), current_user: dict = Depends(get_current_active_user)):
    role = get_user_role(current_user)
    post = db.query(Post).filter(Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if role == "author" and post.owner_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    post.title = title
    post.content = content
    db.commit()
    return {"id": post.id, "title": post.title, "content": post.content}

@app.delete("/posts/{post_id}")
def delete_post(post_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_active_user)):
    role = get_user_role(current_user)
    post = db.query(Post).filter(Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if role == "author" and post.owner_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    db.delete(post)
    db.commit()
    return {"detail": "Post deleted"}

