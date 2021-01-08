from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


SQLALCHEMY_DATABASE_URL = 'mysql+mysqlconnector://%s:%s@webapp:%s/%s' % (
    'kane',
    '12345678',
    '3306',
    'restapi'
)

#Create engine for connect between session and database
engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

#Create Session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#Now we will use the function declarative_base() that returns a class.
#Later we will inherit from this class to create each of the database models or classes (the ORM models):
Base = declarative_base()