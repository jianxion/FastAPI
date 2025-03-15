from sqlalchemy.future import select
from sqlalchemy import or_, and_
from sqlalchemy.orm import Session
from .models import Message
from fastapi import status, HTTPException



class MessageRepository:
    def __init__(self, db: Session):
        self.db = db

    def send_message(self, sender_id: int, receiver_id: int, content: str) -> Message:
        try:
            new_message = Message(
                # id=int,
                sender_id=sender_id,
                receiver_id=receiver_id,
                content=content
            )
            self.db.add(new_message)
            self.db.commit()
            self.db.refresh(new_message)
            return new_message
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Error sending message from {sender_id} to {receiver_id}: {str(e)}")
           
