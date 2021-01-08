from sqlalchemy.orm import Session
from . import models, schemas

def get_status(db: Session, id: str):
    res = db.query(models.UploadedImage).filter(models.UploadedImage.id == id).first()
    if res != None:
        return res.status
    else:
        return None
def get_result(db: Session, id: str):
    res = db.query(models.ProcessedImage).filter(models.ProcessedImage.id == id).all()
    return res

def create_upload_file(db: Session, uploaded_image: schemas.UploadedImage):
    print('Got query created Uploaded-File ...')
    db_uploaded_file = models.UploadedImage(**uploaded_image.dict())
    db.add(db_uploaded_file)
    db.commit()
    db.refresh(db_uploaded_file)

def update_status(db: Session, id: str, status: str):
    return db.query(models.UploadedImage).filter(models.UploadedImage.id == id).update({models.UploadedImage.status: status}, synchronize_session = False)

def create_result_file(db: Session, result):
    db_result_file = [models.ProcessedImage(id = x[0], url_image = x[1], text_result = x[2]) for x in result] 
    db.add_all(db_result_file)
    db.commit()
    for x in db_result_file:
        db.refresh(x)
