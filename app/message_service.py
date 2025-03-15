from sqlalchemy.ext.asyncio import AsyncSession
from .message_repository import MessageRepository
from .notification_repository import NotificationRepository
# from app.repositories.notification_repository import NotificationRepository
# from app.domain.schemas.notification import NotificationCreate
from sqlalchemy.exc import SQLAlchemyError
# from app.core.exceptions.message_exception import MessageCreationError, MessageException
from .schemas import MessageCreate, MessageInDB, NotificationCreate
from typing import List
from fastapi import status, HTTPException


class MessageService:
    def __init__(self, message_repo: MessageRepository, notification_repo: NotificationRepository):
        self.message_repo = message_repo
        self.notification_repo = notification_repo

    def send_message(self, sender_id: int, receiver_id: int, content: str) -> MessageInDB:
        try:
            message = self.message_repo.send_message(sender_id, receiver_id, content)
            
            # Create a notification for the receiver
            notification_data = NotificationCreate(
                user_id=receiver_id,
                message=f"New message from User {sender_id}: {content[:30]}...",  # Preview first 30 chars
                type="message"
            )
            self.notification_repo.create_notification(notification_data)
            
            return MessageInDB.from_orm(message)
        except SQLAlchemyError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Unexpected error sending message {str(e)}")
        