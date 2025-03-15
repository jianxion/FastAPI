from sqlalchemy.future import select
from sqlalchemy import or_, and_
from sqlalchemy.orm import Session
from .models import Message, Notification
from .schemas import NotificationCreate
from fastapi import status, HTTPException


class NotificationRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create_notification(self, notification_data: NotificationCreate) -> Notification:
        try:
            notification = Notification(**notification_data.dict())
            self.db.add(notification)

            self.db.commit()
            self.db.refresh(notification)
            return notification
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Error creating notification")