from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from sqlalchemy.orm import Session
from . import models
from .database import engine, get_db


models.Base.metadata.create_all(bind = engine)


app = FastAPI()

class Post(BaseModel):
    title: str
    content: str
    pulished: bool = True


while True: # keep trying to connect to database
    try:
        conn = psycopg2.connect(host = 'localhost', database = 'fastapi', user = 'postgres', password = 'sjx990617',
                                cursor_factory=RealDictCursor)  # hardcode password is bad
        cursor = conn.cursor()
        print("Database connection was successful")
        break
    except Exception as error:
        print("Connecting the database failed")
        print("Error", error)
        time.sleep(2) # if connection failed sleep for 2 seconds


my_posts = []

# from top to down, get the first match of the path
@app.get('/')
async def root():
    return {"message": "hello world!123"}


@app.get('/sqlalchemy')
def test_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()

    return {"data": posts}
    

@app.get('/posts')
async def get_posts():
    cursor.execute(""" SELECT * FROM posts """)
    posts = cursor.fetchall()
    print(posts)
    return {"data": posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED) # when creating a post, change default status code to 201
async def create_posts(post: Post): # post is the pydantic model posted by the client/fromt end
    cursor.execute(""" INSERT INTO posts (title, content, published) 
                   VALUES (%s, %s, %s) RETURNING * """, (post.title, post.content, post.pulished))
    new_post = cursor.fetchone()
    conn.commit() # commit after change database

    return {"data": new_post}


# http://127.0.0.1:8000/posts/2 path paremeter
# id is a string, remember to convert it to int (pydantic do this for us)
@app.get("/posts/{id}")
async def get_post(id: int): # pydantic to convert str to int valid user typed an int
    cursor.execute(""" SELECT * FROM posts WHERE id = %s """, (str(id))) # id is an int, convert to str to allow sql
    got_post = cursor.fetchone()
    
    if not got_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Post with {id} was not found")  # raise http exception
    
    return {"Post": got_post}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)  
async def delete_post(id: int):
    cursor.execute(""" DELETE FROM posts WHERE id = %s RETURNING * """, (str(id)))
    deleted_post = cursor.fetchone()
    if not deleted_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Post with {id} does not exist")
    conn.commit() # commit db
    return Response(status_code=status.HTTP_204_NO_CONTENT)  # delete something should return 204 response code

@app.put("/posts/{id}")
async def update_post(id: int, post: Post):
    cursor.execute(""" UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING * """,
                (post.title, post.content, post.pulished, str(id)))
    updated_post = cursor.fetchone()
    conn.commit()
    if not updated_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with {id} not found")
    return {"message": updated_post}
