#For Utils 
from ocr import CannetOCR
from layout import JeffLayout
import cv2
import os
import json

#For Celery
from celery import task
from celery.registry import tasks
import celery
from celery import Celery
import urllib.request
from celery.utils.log import get_task_logger
from celery.signals import worker_process_init
from celery import shared_task
from celery.signals import worker_process_init

#For SQL connector 
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from mysqlconnector.database import engine
from mysqlconnector import models, crud, schemas

#Make a session with scope in celery
db_session = scoped_session(sessionmaker(
    autocommit=False, autoflush=False, bind=engine))

#Declare celery app
celery_app = Celery(
    "tasks",
    broker='redis://localhost:6379/0')
logger = get_task_logger(__name__)
celery_app.conf.update(task_track_started=True)

#Delacre global variable
@worker_process_init.connect
def configure_model(**kwargs):
    global ocr_model
    ocr_model = CannetOCR(weights_path='./lib-ocr/models/CannetOCR.pt', device = "-1") 

    global layout_model
    layout_model =  JeffLayout(weights_path='./lib-layout/layout/jeff/assets/General.pth', device = "-1")

class SqlAlchemyTask(celery.Task):
    """An abstract Celery Task that ensures that the connection the the
    database is closed on task completion"""
    abstract = True

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        db_session.remove()

@shared_task
def extract_layout(img_path, file_out_folder):
    """
        Extract layout for an image and store result images into file out folder

        Parameter: 
        ----------
        img_path: str
            Path dir to image 
        file_out_folder: str
            folder's name of folder that will store images
        
        Returns
        ----------
        None
    """
    print('Got task: Extract Layout')
    img = cv2.imread(img_path)
    try:
        res = layout_model.process(img_path)
    except:
        return ''
    #Variable to make sequences number.
    run = 0
    os.mkdir(file_out_folder)
    #print(file_out_folder)
    #Loop through all parts in image and imwrite() it
    print('Go in Extract Layout func')

    for i in res:
        loc =  i['location']
        run += 1
        y1 = loc[0][1]
        y2 = loc[2][1]
        x1 = loc[0][0]
        x2 = loc[1][0]

        #crop original image with cordinate from the output of lib-layout
        cropped_img = img[y1:y2, x1:x2]

        #store a file with different identify-numbers (sequence number)
        path = os.path.join(file_out_folder, str(run) + '.jpg')
        
        if cv2.imwrite(path, cropped_img) == False:
            print('Saved Failed - Filepath: ' + path)
            return '' 
    return file_out_folder


@shared_task(base=SqlAlchemyTask)
def inference_ocr(dir_path,original_image):
    """
        Inference a folder with OCR 
        This function will ioriginal_imagenference Cannet OCR model for the directory.
        The result will be saved in a xlsx file 

        Parameter: 
        ----------
        dir_path: str
            Path dir to all image 
        file_out: str
            Name of file csv  
        
        Returns
        ----------
        None
    """
    res = []
    
    try:
        for filename in os.listdir(dir_path):
            result = ocr_model.process(os.path.join(dir_path, filename))
            res.append([os.path.basename(dir_path), os.path.join(dir_path, filename), result['text']])
    except ValueError:
        print("OCR Error: " + ValueError)
        crud.update_status(db_session, os.path.basename(dir_path),"FAILED")
        return []

    crud.update_status(db_session, os.path.basename(dir_path),"DONE")

    crud.create_result_file(db_session, res)