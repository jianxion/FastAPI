from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from .. import models, schemas, oauth2
from ..database import get_db

router = APIRouter(
    prefix="/document",
    tags=["Document"]
)

@router.post("/", response_model=schemas.DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user)
):
    # Check if the file is not empty
    if file.size == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File is empty")

    # Create a new document entry
    new_document = models.Document(
        document_name=file.filename,
        document_size=file.size,
        user_id=current_user.id,
        is_active=True
    )

    # Add and commit the new document to the database
    db.add(new_document)
    db.commit()
    db.refresh(new_document)

    return new_document