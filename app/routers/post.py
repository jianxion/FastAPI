from typing import Optional, List
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter

from sqlalchemy.orm import Session
from sqlalchemy import func
from .. import models, schemas, utils, oauth2
from ..database import engine, get_db

router = APIRouter(
    prefix="/posts", # prefix of all paths in this router
    tags=["Posts"] # for documentation
)

# / is equal to /posts because of prefix
@router.get('/', response_model=List[schemas.PostOut])
async def get_posts(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user),
                   limit: Optional[int] = 10, skip: Optional[int] = 0, search: Optional[str] = ""):
    # cursor.execute(""" SELECT * FROM posts """)
    # posts = cursor.fetchall()
    posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    # posts = db.query(models.Post).filter(models.Post.owner_id == current_user.id).all() # get all posts from the specifc logged in user
    # print(posts)

    results = db.query(models.Post, func.count(models.Vote.post_id).label("votes")) \
    .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True) \
    .group_by(models.Post.id).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    print(results)
    return results




# response model to define the returned data fields to the user. original is a pydantic model, use orm_mode = True to convert to a dict
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse) # when creating a post, change default status code to 201
async def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)): # post is the pydantic model posted by the client/fromt end
                                                                                                # this depends call the function to valideate the user using the token got from the
                                                                                                # login url bearer . login only after the user login so the program can get a token
    # cursor.execute(""" INSERT INTO posts (title, content, published)                          
    #                VALUES (%s, %s, %s) RETURNING * """, (post.title, post.content, post.pulished))
    # new_post = cursor.fetchone()
    # conn.commit() # commit after change database
    # print(current_user.id)
    new_post = models.Post(owner_id = current_user.id, **post.dict()) # get a dictionary and extract content
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post



# http://127.0.0.1:8000/posts/2 path paremeter
# id is a string, remember to convert it to int (pydantic do this for us)
@router.get("/{id}", response_model=schemas.PostOut)
async def get_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)): # pydantic to convert str to int valid user typed an int
    # cursor.execute(""" SELECT * FROM posts WHERE id = %s """, (str(id))) # id is an int, convert to str to allow sql
    # got_post = cursor.fetchone()
    got_post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")) \
    .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True) \
    .group_by(models.Post.id).first()
    
    if not got_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Post with {id} was not found")  # raise http exception
    
    return got_post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)  
async def delete_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute(""" DELETE FROM posts WHERE id = %s RETURNING * """, (str(id)))
    # deleted_post = cursor.fetchone()
    delete_post_query = db.query(models.Post).filter(models.Post.id == id)

    post = delete_post_query.first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Post with {id} does not exist")
    
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized user for action")
    
    delete_post_query.delete(synchronize_session=False)
    db.commit()
    # conn.commit() # commit db
    return Response(status_code=status.HTTP_204_NO_CONTENT)  # delete something should return 204 response code

@router.put("/{id}")
async def update_post(id: int, updated_post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute(""" UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING * """,
    #             (post.title, post.content, post.pulished, str(id)))
    # updated_post = cursor.fetchone()
    # conn.commit()
    post_query = db.query(models.Post).filter(models.Post.id == id) # this is just to convert sql code

    found_post = post_query.first()

    if not found_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with {id} not found")
    
    if found_post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized user for action")
    
    post_query.update(updated_post.dict(), synchronize_session=False)
    db.commit()
    return post_query.first()

@router.get('/hello')
async def hello():
    return {"message": "Hello World"}