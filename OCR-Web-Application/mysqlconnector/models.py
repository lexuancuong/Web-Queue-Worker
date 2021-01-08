from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base

class UploadedImage(Base):
    __tablename__ = "UploadedImage"
    id = Column(String(30), primary_key = True)
    url_image = Column(String(255))
    status = Column(String(255))

class ProcessedImage(Base):
    __tablename__ = "ProcessedImage"
    id = Column(String(30), primary_key = True)
    url_image = Column(String(255), primary_key = True)
    text_result = Column(String(255))