from typing import List, Optional
from fastapi import Depends, FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
import uuid 
from mysqlconnector import crud, models, schemas
from mysqlconnector.database import SessionLocal, engine
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
import os
from tasks import extract_layout
from tasks import inference_ocr
from pydantic import BaseModel

#Declare instance of FastAPi App
app = FastAPI()

#make engine work
models.Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="static"), name="static")

# Dependency
def get_db():
    #Make a session for connecting between web server and mysql server
    db = SessionLocal()
    try:
        yield db #It is a new method to create Session in fastapi
    finally:
        db.close()

DESTINATION_DIR_PATH = './static/images/'

@app.post("/api/detect")
async def create_upload_file(file: UploadFile = File(...),  db: Session = Depends(get_db)):
    try:
        print('Got a file request from client for detecting...')
        #Get type of uploaded file
        tail_of_file = file.content_type.split('/')[1]  

        #write file into folder
        contents = await file.read()
        str_id = str(uuid.uuid1())
        filename = ''.join(['static/images/original_images/',str_id ,'.',tail_of_file])
        with open(filename, "wb") as f:
            f.write(contents)
        #Create an instance of uploaded file for database query
        upload_file = schemas.UploadedImage(id = str_id, url_image = filename, status = "PROCESSING")

        #set a row for new uploaded file (through query in crud)
        res = crud.create_upload_file(db, upload_file)

        #Declare dir path for folder that storage cell images
        file_out_folder = os.path.join(DESTINATION_DIR_PATH, ''.join(os.path.basename(filename).split('.')[:-1])) 
        
        #Pass current task to worker
        worker_task = extract_layout.apply_async(args=([filename,file_out_folder]), link=inference_ocr.s(filename))
        #await database.insert_into_result(res, filename)
        print('Ran worker for OCR service....')
    except ValueError as e:
        raise HTTPException(status_code = 404, detail = e.args[0])
    finally:
        return {"id":str_id}

#Model for form that requests result
class FormRequestResult(BaseModel):
    id: str

@app.get("/api/detect", response_model = List[schemas.ProcessedImage])
async def get_file(body: FormRequestResult, db: Session = Depends(get_db)):
    #get id from body form request
    uploaded_id = body.id

    #Get status of the ID
    status = crud.get_status(db, uploaded_id)

    #THe id is not in database
    if status == None:
        raise HTTPException(status_code = 404, detail = "The ID's not found!")

    #Get result images
    if status == 'DONE':
        result = crud.get_result(db, uploaded_id)

        #convert list of Class Object to list of json object
        response = []
        for x in result:
            response.append({'id':x.id, 'url_image': x.url_image, 'text_result': x.text_result})
        return response
    raise HTTPException(status_code = 404, detail = "The image is being processing...")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
