from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
import enum

Base = declarative_base()

class LinkPrecedence(enum.Enum):
    PRIMARY = "primary"
    SECONDARY = "secondary"

class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    phoneNumber = Column(String, nullable=True)
    email = Column(String, nullable=True)
    linkedId = Column(Integer, ForeignKey("contacts.id"), nullable=True)
    linkPrecedence = Column(Enum(LinkPrecedence), nullable=False, default=LinkPrecedence.PRIMARY)
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deletedAt = Column(DateTime, nullable=True)

    secondary_contacts = relationship("Contact", remote_side=[id])

    def __repr__(self):
        return f"<Contact(id={self.id}, email={self.email}, phoneNumber={self.phoneNumber}, " \
               f"linkPrecedence={self.linkPrecedence})>"
