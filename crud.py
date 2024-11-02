from sqlalchemy.orm import Session
from models import Post
from schema import PostCreate

def create_post(db: Session, post: PostCreate, user_id: int):
    new_post = Post(**post.dict(), owner_id=user_id)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

def get_posts(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Post).offset(skip).limit(limit).all()

def get_post(db: Session, post_id: int):
    return db.query(Post).filter(Post.id == post_id).first()

def update_post(db: Session, post_id: int, post_data: PostCreate, user_id: int):
    post = get_post(db, post_id)
    if post:
        post.title = post_data.title
        post.content = post_data.content
        db.commit()
        return post
    return None

def delete_post(db: Session, post_id: int, user_id: int):
    post = get_post(db, post_id)
    if post:
        db.delete(post)
        db.commit()
        return post
    return None
