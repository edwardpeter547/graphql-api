import datetime
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.dataset import employer_data, job_data, users_data, application_data
from app.db.models import Employer, Job, User, JobApplication, Base
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DB_URL")


engine = create_engine(DB_URL)
conn = engine.connect()
Session = sessionmaker(bind=engine)


def add_employers_list(session):
    for employer in employer_data:
        session.add(Employer(**employer))


def add_job_list(session):
    for job in job_data:
        session.add(Job(**job))


def add_users_list(session):
    # import moved here to avoid circular imports
    from app.utils import hash_password

    for user in users_data:
        user["password_hash"] = hash_password(user["password"])
        del user["password"]
        session.add(User(**user))


def add_application_list(session):
    from app.utils import generate_reference

    for application in application_data:
        reference = generate_reference()
        session.add(JobApplication(reference=reference, **application))


def prepare_database():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    session = Session()
    add_employers_list(session=session)
    add_job_list(session=session)
    add_users_list(session=session)
    add_application_list(session=session)
    session.commit()
