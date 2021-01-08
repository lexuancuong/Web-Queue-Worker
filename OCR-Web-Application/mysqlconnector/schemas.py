from typing import List, Optional
from pydantic import BaseModel
#Pydantic's orm_mode will tell the Pydantic model to 
# read the data even if it is not a dict, but an ORM model (or any other arbitrary object with attributes).

class UploadedImage(BaseModel):
    id: str
    url_image: str
    status: str

class ProcessedImage(BaseModel):
    id: str
    url_image: str
    text_result: str
