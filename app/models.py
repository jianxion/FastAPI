from sqlalchemy import TIMESTAMP, Column, ForeignKey, Integer, String, Boolean, text, DateTime
from datetime import datetime
from sqlalchemy.orm import relationship
from .database import Base

class Post(Base):
    __tablename__ = "posts" # table name in database

    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    published = Column(Boolean, server_default='TRUE', nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    owner = relationship("User") # allow fetching user information when get post


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    phone_number = Column(String, nullable=True)

    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user")

class Vote(Base):
    __tablename__ = "votes"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True)

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, nullable=False)
    document_name = Column(String, nullable=False)
    document_size = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=False)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="documents")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, nullable=False)
    sender_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    receiver_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_messages")
    # receiver = relationship("User", foreign_keys=[receiver_id], back_populates="received_messages")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    message = Column(String, nullable=False)
    broadcast = Column(Boolean, default=False)

    user = relationship("User", back_populates="notifications")



