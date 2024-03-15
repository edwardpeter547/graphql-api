from graphene import List, ObjectType, Int, Field
from app.gql.types import JobObject, EmployerObject, UserObject, JobApplicationObject
from app.db.database import Session
from app.db.models import Job, Employer, User, JobApplication
from sqlalchemy.orm import joinedload


class Query(ObjectType):
    jobs = List(JobObject)
    employers = List(EmployerObject)
    users = List(UserObject)
    job = Field(JobObject, id=Int(required=True))
    employer = Field(EmployerObject, id=Int(required=True))
    applications = List(JobApplicationObject)

    @staticmethod
    def resolve_jobs(root, info):
        return Session().query(Job).all()
        # return Session().query(Job).options(joinedload(Job.employer)).all()

    @staticmethod
    def resolve_job(root, info, id):
        with Session() as session:
            return session.query(Job).filter(Job.id == id).first()

    @staticmethod
    def resolve_employers(root, info):
        return Session().query(Employer).all()

    @staticmethod
    def resolve_employer(root, info, id):
        with Session() as session:
            return session.query(Employer).filter(Employer.id == id).first()

    @staticmethod
    def resolve_users(root, info):
        with Session() as session:
            return session.query(User).all()

    @staticmethod
    def resolve_applications(root, info):
        with Session() as session:
            return session.query(JobApplication).all()
