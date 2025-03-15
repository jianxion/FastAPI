from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from .. import models, schemas, oauth2
from ..message_service import MessageService
from ..message_repository import MessageRepository
from ..notification_repository import NotificationRepository
from ..database import get_db

router = APIRouter(
    prefix="/message",
    tags=["Message"]
)

@router.post("/", response_model=schemas.MessageResponse)
async def send_message(message: schemas.MessageCreate, db: Session = Depends(get_db)):
    message_service = MessageService(MessageRepository(db), NotificationRepository(db))
    return message_service.send_message(message.sender_id, message.receiver_id, message.content)


   